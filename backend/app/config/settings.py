"""
SmartArena AI — Configuration Classes
======================================

Provides environment-specific configuration using the class inheritance pattern.
All sensitive values are loaded from environment variables.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class BaseConfig:
    """Base configuration shared across all environments."""

    # ── Application ─────────────────────────────────────────────────────
    APP_NAME: str = "SmartArena AI"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # ── Firebase ────────────────────────────────────────────────────────
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json"
    )

    # ── Gemini AI ───────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # ── CORS ────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5500"
        ).split(",")
    ]

    # ── Rate Limiting ───────────────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100/hour")

    # ── Logging ─────────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    ENV_NAME: str = "development"
    DEBUG: bool = True
    TESTING: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")


class ProductionConfig(BaseConfig):
    """Production environment configuration."""

    ENV_NAME: str = "production"
    DEBUG: bool = False
    TESTING: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "WARNING")


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    ENV_NAME: str = "testing"
    DEBUG: bool = True
    TESTING: bool = True
    LOG_LEVEL: str = "DEBUG"
    FIREBASE_PROJECT_ID: str = "test-project"


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

    return config_class()
