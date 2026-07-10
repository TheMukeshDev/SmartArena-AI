"""
SmartArena AI — Authentication Middleware
===========================================

Provides decorators to secure routes using Firebase Session Cookies
or Bearer JWTs, and enforce Role-Based Access Control (RBAC).
"""

import functools
import logging
from typing import Any, Callable

from firebase_admin import auth
from flask import request, g

from app.utils.response import error_response

logger = logging.getLogger(__name__)


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require a valid Firebase session cookie or ID token.

    Sets g.user with the decoded token payload.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 1. Try to get Session Cookie
        session_cookie = request.cookies.get("session")

        # 2. Try to get Bearer Token
        auth_header = request.headers.get("Authorization")
        bearer_token = None
        if auth_header and auth_header.startswith("Bearer "):
            bearer_token = auth_header.split("Bearer ")[1]

        decoded_claims = None

        try:
            if session_cookie:
                decoded_claims = auth.verify_session_cookie(
                    session_cookie, check_revoked=True
                )
            elif bearer_token:
                decoded_claims = auth.verify_id_token(bearer_token, check_revoked=True)
            else:
                return error_response(
                    message="Authentication required. No token or session cookie provided.",
                    error_type="Unauthorized",
                    status_code=401,
                )

            # Store user claims in Flask global context
            g.user = decoded_claims
            return func(*args, **kwargs)

        except auth.RevokedIdTokenError:
            logger.warning("Revoked token used")
            return error_response(
                message="Session has been revoked. Please log in again.",
                error_type="Unauthorized",
                status_code=401,
            )
        except auth.InvalidSessionCookieError:
            logger.warning("Invalid session cookie")
            return error_response(
                message="Invalid session. Please log in again.",
                error_type="Unauthorized",
                status_code=401,
            )
        except Exception as e:
            logger.error("Auth error: %s", str(e))
            return error_response(
                message="Authentication failed",
                error_type="Unauthorized",
                status_code=401,
            )

    return wrapper


def require_role(allowed_roles: list[str]) -> Callable[..., Any]:
    """Decorator to enforce RBAC based on Firebase Custom Claims.

    Must be used AFTER @require_auth.

    Args:
        allowed_roles: List of role strings (e.g., ['admin', 'volunteer'])
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            user = getattr(g, "user", None)
            if not user:
                return error_response(
                    message="Authentication required for role check.",
                    error_type="Unauthorized",
                    status_code=401,
                )

            user_role = user.get("role")
            if not user_role or user_role not in allowed_roles:
                logger.warning(
                    "Access denied for user %s. Role '%s' not in %s",
                    user.get("uid"),
                    user_role,
                    allowed_roles,
                )
                return error_response(
                    message="You do not have permission to access this resource.",
                    error_type="Forbidden",
                    status_code=403,
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
