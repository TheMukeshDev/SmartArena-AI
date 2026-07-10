"""
SmartArena AI — API Blueprint
===============================

Root API blueprint that serves as namespace for versioned API routes.
Sub-modules will register under /api/v1/*.
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify
from flask.wrappers import Response

from app.config.settings import BaseConfig

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


@api_bp.route("/", methods=["GET"])
def api_index() -> tuple[Response, int]:
    """API root — returns available endpoints and version info.

    Returns:
        JSON response with API metadata.
    """
    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "service": "SmartArena AI API",
                    "version": BaseConfig.VERSION,
                    "endpoints": {
                        "health": "/health",
                        "readiness": "/health/ready",
                        "api_root": "/api/v1/",
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }
        ),
        200,
    )
