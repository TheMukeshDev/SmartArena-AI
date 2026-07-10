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
    from app.routes.ai_ops import ai_ops_bp
    from app.routes.events import events_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(config_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(ai_ops_bp, url_prefix="/api/v1/ai")
    app.register_blueprint(events_bp, url_prefix="/api/v1/events")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    app.logger.info(
        "Registered %d blueprints",
        len(app.blueprints),
    )
