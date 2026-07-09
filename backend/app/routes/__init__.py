"""
SmartArena AI — Blueprint Registry
====================================

Central registry for all Flask Blueprints.
Each feature module registers its own Blueprint here.
"""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints.

    Args:
        app: Flask application instance.
    """
    from app.routes.health import health_bp
    from app.routes.api import api_bp
    from app.routes.config import config_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(config_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    app.logger.info(
        "Registered %d blueprints",
        len(app.blueprints),
    )
