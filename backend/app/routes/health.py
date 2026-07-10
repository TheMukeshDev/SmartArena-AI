"""
SmartArena AI — Health Check Routes
=====================================

Provides health and readiness endpoints for monitoring,
load balancers, and container orchestrators.
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify
from flask.wrappers import Response

from app.config.firebase import get_firestore_client

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check() -> tuple[Response, int]:
    """Basic health check endpoint.

    Returns:
        JSON response with application status and timestamp.
    """
    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "status": "healthy",
                    "service": "SmartArena AI",
                    "version": "1.0.0",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
        ),
        200,
    )


@health_bp.route("/health/ready", methods=["GET"])
def readiness_check() -> tuple[Response, int]:
    """Readiness probe — checks all dependencies.

    Returns:
        JSON response indicating whether the application and its
        dependencies are ready to serve traffic.
    """
    checks: dict[str, bool] = {
        "flask": True,
        "firebase": _check_firebase(),
    }
    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return (
        jsonify(
            {
                "success": all_ready,
                "data": {
                    "status": "ready" if all_ready else "degraded",
                    "checks": checks,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
        ),
        status_code,
    )


def _check_firebase() -> bool:
    """Check Firebase/Firestore connectivity.

    Returns:
        True if Firestore client is available, False otherwise.
    """
    from flask import current_app

    if current_app and current_app.config.get("TESTING", False):
        return True
    try:
        client = get_firestore_client()
        return client is not None
    except Exception as e:
        logger.warning("Firebase health check failed: %s", str(e))
        return False
