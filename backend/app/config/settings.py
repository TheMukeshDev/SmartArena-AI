"""
SmartArena AI — Configuration Classes
======================================

Provides environment-specific configuration using the class inheritance pattern.
All sensitive values are loaded from environment variables.
"""

import os
import logging
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

logger = logging.getLogger(__name__)


def _parse_limit(default: str) -> int:
    raw = os.getenv("RATE_LIMIT_DEFAULT", default)
    if "/" in raw:
        raw = raw.split("/")[0]
    return int(raw)


class BaseConfig:
    """Base configuration shared across all environments."""

    # ── Application ─────────────────────────────────────────────────────
    APP_NAME: str = "SmartArena AI"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SESSION_COOKIE_NAME: str = "smartarena_csrf_token"

    # ── Firebase ────────────────────────────────────────────────────────
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json"
    )
    FIREBASE_CLIENT_EMAIL: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    FIREBASE_PRIVATE_KEY: str = os.getenv("FIREBASE_PRIVATE_KEY", "")

    # ── Gemini AI ───────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # ── CORS ────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5500"
        ).split(",")
    ]

    # ── Rate Limiting (SQLite-backed) ───────────────────────────────────
    RATE_LIMIT_DEFAULT: int = _parse_limit("100")
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))
    # nosec B108 - non-sensitive local SQLite cache/rate-limit file, not a credential
    RATE_LIMIT_DB_PATH: str = os.getenv("RATE_LIMIT_DB_PATH", "ratelimit.db")

    # ── Caching (SQLite-backed) ─────────────────────────────────────────
    # nosec B108 - non-sensitive local SQLite cache/rate-limit file, not a credential
    CACHE_DB_PATH: str = os.getenv("CACHE_DB_PATH", "cache.db")
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # ── Events / Incident Queue (SQLite-backed) ─────────────────────────
    # nosec B108 - non-sensitive local SQLite incident queue file, not a credential
    EVENTS_DB_PATH: str = os.getenv("EVENTS_DB_PATH", "events.db")
    EVENTS_POLL_INTERVAL: float = float(os.getenv("EVENTS_POLL_INTERVAL", "1"))

    # ── Security ────────────────────────────────────────────────────────
    FORCE_HTTPS: bool = os.getenv("FORCE_HTTPS", "1") == "1"
    WTF_CSRF_SSL_STRICT: bool = (
        False  # Disable strict referer check for cross-origin frontend
    )
    WTF_CSRF_CHECK_DEFAULT: bool = (
        True  # CSRF enforced on all POST/PUT/DELETE by default
    )

    # ── Logging ─────────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    ENV_NAME: str = "development"
    DEBUG: bool = True
    TESTING: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    FORCE_HTTPS: bool = False


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    ENV_NAME: str = "production"
    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "WARNING")

    def __init__(self):
        super().__init__()
        if not os.getenv("SECRET_KEY"):
            raise ValueError(
                "SECRET_KEY environment variable is required in production."
            )


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    ENV_NAME: str = "testing"
    DEBUG: bool = True
    TESTING: bool = True
    LOG_LEVEL: str = "DEBUG"
    FIREBASE_PROJECT_ID: str = "test-project"
    WTF_CSRF_ENABLED: bool = False
    FORCE_HTTPS: bool = False


# ── Configuration Map ───────────────────────────────────────────────────
_config_map: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(config_name: str | None = None) -> BaseConfig:
    """Retrieve configuration object by environment name.

    Args:
        config_name: Environment name. Falls back to FLASK_ENV env var,
                     then defaults to 'development'.

    Returns:
        Configuration instance for the specified environment.

    Raises:
        ValueError: If the config_name is not recognized.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    config_class = _config_map.get(config_name)
    if config_class is None:
        valid = ", ".join(_config_map.keys())
        raise ValueError(
            f"Unknown configuration: '{config_name}'. Valid options: {valid}"
        )

    instance = config_class()

    if instance.SECRET_KEY == "dev-secret-key-change-me":
        logger.warning(
            "SECRET_KEY is still set to the default value. "
            "Set SECRET_KEY in your .env file for any non-development environment."
        )

    return instance
