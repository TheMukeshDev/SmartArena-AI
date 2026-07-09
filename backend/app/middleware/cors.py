"""
SmartArena AI — CORS Configuration
====================================

Configures Cross-Origin Resource Sharing for the Flask application.
"""

import logging

from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)


def init_cors(app: Flask) -> None:
    """Initialize CORS with application-specific origins.

    Args:
        app: Flask application instance.
    """
    origins: list[str] = app.config.get("CORS_ORIGINS", ["*"])

    CORS(
        app,
        origins=origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    logger.info("CORS initialized for origins: %s", origins)
