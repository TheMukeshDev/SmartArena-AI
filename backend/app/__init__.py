"""
SmartArena AI — Flask Application Factory
==========================================

Creates and configures the Flask application using the factory pattern.
This enables multiple configurations (dev, prod, test) and simplifies testing.
"""

from flask import Flask

from app.config.settings import get_config
from app.config.firebase import init_firebase
from app.config.logging import setup_logging
from app.middleware.cors import init_cors
from app.routes import register_blueprints
from app.routes.errors import register_error_handlers


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration environment name.
                     Options: 'development', 'production', 'testing'.
                     Defaults to FLASK_ENV environment variable.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder="../frontend",
        template_folder="templates",
    )

    # ── Load Configuration ──────────────────────────────────────────────
    config = get_config(config_name)
    app.config.from_object(config)

    # ── Initialize Logging ──────────────────────────────────────────────
    setup_logging(app)
    app.logger.info(
        "SmartArena AI starting in %s mode",
        app.config.get("ENV_NAME", "unknown"),
    )

    # ── Initialize Firebase ─────────────────────────────────────────────
    init_firebase(app)

    # ── Initialize CORS ─────────────────────────────────────────────────
    init_cors(app)

    # ── Register Blueprints ─────────────────────────────────────────────
    register_blueprints(app)

    # ── Register Error Handlers ─────────────────────────────────────────
    register_error_handlers(app)

    app.logger.info("SmartArena AI initialized successfully")
    return app
