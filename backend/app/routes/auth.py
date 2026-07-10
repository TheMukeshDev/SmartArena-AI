"""
SmartArena AI — Authentication Routes
=======================================

Handles session cookie creation, destruction, and user registration
(setting custom claims/roles).
"""

import datetime
import logging

from firebase_admin import auth
from flask import Blueprint, request, jsonify
from flask.wrappers import Response

from app.middleware.auth import require_auth
from app.utils.response import success_response, error_response
from app.config.firebase import get_firestore_client

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Session cookie expires in 5 days
SESSION_EXPIRES_IN = datetime.timedelta(days=5)


@auth_bp.route("/sessionLogin", methods=["POST"])
def session_login() -> tuple[Response, int]:
    """Create a Firebase Session Cookie from a client ID token.

    Expects JSON body with 'idToken'.
    """
    data = request.get_json(silent=True)
    if not data or "idToken" not in data:
        return error_response("idToken is required", status_code=400)

    id_token = data["idToken"]

    if not id_token or not isinstance(id_token, str):
        return error_response("idToken must be a non-empty string", status_code=400)

    try:
        # Verify the ID token first
        decoded_claims = auth.verify_id_token(id_token)

        # Only process if the user recently signed in (within last 5 mins)
        if datetime.datetime.now().timestamp() - decoded_claims["auth_time"] < 5 * 60:
            # Create session cookie
            session_cookie = auth.create_session_cookie(
                id_token, expires_in=SESSION_EXPIRES_IN
            )

            # Build response
            response = jsonify(
                {"success": True, "message": "Session created successfully"}
            )

            # Set HttpOnly cookie
            response.set_cookie(
                "session",
                session_cookie,
                max_age=int(SESSION_EXPIRES_IN.total_seconds()),
                httponly=True,
                samesite="None",
                secure=True,
            )
            return response, 200
        else:
            return error_response("Recent sign in required", status_code=401)

    except auth.InvalidIdTokenError:
        return error_response("Invalid ID token", status_code=401)
    except Exception as e:
        logger.error("Session login error: %s", str(e))
        return error_response("Internal Server Error", status_code=500)


@auth_bp.route("/sessionLogout", methods=["POST"])
def session_logout() -> tuple[Response, int]:
    """Revoke session and clear cookie."""
    session_cookie = request.cookies.get("session")

    response = jsonify({"success": True, "message": "Logged out successfully"})

    response.set_cookie(
        "session", expires=0, httponly=True, samesite="None", secure=True
    )

    if session_cookie:
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie)
            auth.revoke_refresh_tokens(decoded_claims["uid"])
        except auth.InvalidSessionCookieError:
            pass  # Cookie already invalid
        except Exception as e:
            logger.error("Error revoking tokens: %s", str(e))

    return response, 200


@auth_bp.route("/register", methods=["POST"])
@require_auth
def register_user() -> tuple[Response, int]:
    """Register a new user, set their role in Firestore and Custom Claims."""
    from flask import g

    data = request.get_json()

    uid = data.get("uid")
    email = data.get("email")
    name = data.get("name", "")

    if not uid or not email:
        return error_response("uid and email are required", status_code=400)

    if g.user["uid"] != uid:
        return error_response("Cannot register a different user", status_code=403)

    requested_role = data.get("role", "fan")
    allowed_roles = ["fan", "volunteer", "admin"]
    role = requested_role if requested_role in allowed_roles else "fan"

    try:
        # 1. Set Custom Claims for RBAC
        auth.set_custom_user_claims(uid, {"role": role})

        # 2. Save user profile to Firestore
        db = get_firestore_client()
        if db:
            db.collection("users").document(uid).set(
                {
                    "email": email,
                    "name": name,
                    "role": role,
                    "createdAt": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                },
                merge=True,
            )

        return success_response(message=f"User registered successfully as {role}")

    except Exception as e:
        logger.error("Error registering user: %s", str(e))
        return error_response("Registration failed. Please try again later.", status_code=500)


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_current_user() -> tuple[Response, int]:
    """Get the current authenticated user's profile."""
    from flask import g

    return success_response(data=g.user)
