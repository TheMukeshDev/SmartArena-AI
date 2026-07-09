"""
SmartArena AI — Rate Limiting
===============================

Configures Flask-Limiter to protect the API from brute force attacks.
"""

import logging
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.utils.response import error_response

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
)

def init_ratelimit(app: Flask) -> None:
    """Initialize Rate Limiting on the application."""
    app.config['RATELIMIT_STORAGE_URI'] = app.config.get("REDIS_URL") or "memory://"
    limiter.init_app(app)
    
    # Customize the rate limit exceeded error response
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return error_response(
            message=f"Rate limit exceeded: {e.description}",
            error_type="Too Many Requests",
            status_code=429
        )
    
    logger.info("Rate limiting initialized")
