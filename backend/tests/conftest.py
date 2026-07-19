"""
SmartArena AI — Test Configuration
====================================

Shared test fixtures and configuration for pytest.
"""

import sqlite3

import pytest
from app import create_app


@pytest.fixture
def app(tmp_path):
    """Create application for testing.

    Uses a temporary directory for the rate-limit and cache SQLite databases
    so each test session starts with clean state and avoids cross-run
    rate-limit exhaustion.
    """
    app = create_app("testing")
    app.config["RATE_LIMIT_DB_PATH"] = str(tmp_path / "ratelimit.db")
    app.config["CACHE_DB_PATH"] = str(tmp_path / "cache.db")

    conn = sqlite3.connect(str(tmp_path / "ratelimit.db"))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS rate_limit_windows ("
        "  bucket_key TEXT,"
        "  window_start INTEGER,"
        "  request_count INTEGER,"
        "  PRIMARY KEY (bucket_key, window_start)"
        ")"
    )
    conn.commit()
    conn.close()

    yield app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a CLI test runner."""
    return app.test_cli_runner()
