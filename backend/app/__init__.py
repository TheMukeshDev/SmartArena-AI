"""
SmartArena AI — Flask Application Factory
==========================================

Creates and configures the Flask application using the factory pattern.
This enables multiple configurations (dev, prod, test) and simplifies testing.
"""

from flask import Flask, jsonify
from flask_compress import Compress
from flask_wtf.csrf import CSRFProtect, generate_csrf

from app.config.settings import get_config
from app.config.firebase import init_firebase
from app.config.logging import setup_logging
from app.middleware.cors import init_cors
from app.middleware.ratelimit import init_ratelimit
from app.middleware.security import init_security_headers
from app.routes import register_blueprints
from app.routes.auth import auth_bp
from app.routes.ai_ops import ai_ops_bp
from app.routes.events import events_bp
from app.routes.admin import admin_bp
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

    # ── Initialize Security Headers ─────────────────────────────────────
    init_security_headers(app)

    # ── Initialize Rate Limiter ─────────────────────────────────────────
    init_ratelimit(app)

    # ── Register Blueprints ─────────────────────────────────────────────
    register_blueprints(app)

    # ── Initialize CSRF Protection ──────────────────────────────────────
    # All blueprints using @require_auth are exempt from CSRF because
    # Firebase Bearer tokens provide CSRF protection (not sent automatically
    # by browsers). CSRF is only needed for session/cookie-based auth.
    csrf = CSRFProtect(app)
    csrf.exempt(auth_bp)
    csrf.exempt(ai_ops_bp)
    csrf.exempt(events_bp)
    csrf.exempt(admin_bp)

    # ── Initialize Compression ──────────────────────────────────────────
    Compress(app)

    @app.route("/api/v1/csrf-token", methods=["GET"])
    def get_csrf():
        return jsonify({"csrf_token": generate_csrf()})

    # ── Register Error Handlers ─────────────────────────────────────────
    register_error_handlers(app)

    app.logger.info("SmartArena AI initialized successfully")
    return app
