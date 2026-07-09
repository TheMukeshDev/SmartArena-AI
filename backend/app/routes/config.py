"""
SmartArena AI — Config Routes
================================

Serves non-sensitive configuration to the frontend.
Firebase client-side config (API key, authDomain, etc.) is public
by design — it's used by the Firebase JS SDK in the browser.
"""

import logging
import os

from flask import Blueprint, current_app
from flask.wrappers import Response

from app.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

config_bp = Blueprint("config", __name__)


@config_bp.route("/config/firebase", methods=["GET"])
def get_firebase_client_config() -> tuple[Response, int]:
    """Serve Firebase client-side configuration.

    These values are intentionally public — they are required by the
    Firebase JS SDK to initialize in the browser. Security is enforced
    by Firebase Security Rules and Firebase Auth, not by hiding the config.

    Returns:
        JSON response with Firebase client configuration.
    """
    api_key = os.getenv("FIREBASE_API_KEY", "")
    if not api_key:
        logger.warning("FIREBASE_API_KEY not set in environment")
        return error_response(
            message="Firebase client config not available",
            error_type="Configuration Error",
            status_code=503,
        )

    firebase_config = {
        "apiKey": api_key,
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
    }

    return success_response(
        data=firebase_config,
        message="Firebase client configuration",
    )
