"""
SmartArena AI — SQLite-backed Rate Limiting
=============================================

Replaces Flask-Limiter with a fixed-window rate limiter backed by SQLite.
WAL journal mode allows safe concurrent reads/writes from multiple Gunicorn workers.
"""

import sqlite3
import time
import logging
from flask import Flask, request, g
from app.utils.response import error_response

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS rate_limit_windows (
    bucket_key TEXT,
    window_start INTEGER,
    request_count INTEGER,
    PRIMARY KEY (bucket_key, window_start)
)
"""


def _get_db_path(app: Flask) -> str:
    """Return the filesystem path for the SQLite rate limit database."""
    return app.config.get("RATE_LIMIT_DB_PATH", "ratelimit.db")


def _get_client_ip() -> str:
    """Extract the real client IP, preferring X-Forwarded-For in production."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _ensure_db(app: Flask) -> sqlite3.Connection:
    """Return the per-request SQLite connection, creating it if necessary."""
    if "ratelimit_db" not in g:
        db_path = _get_db_path(app)
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=NORMAL")
        g.ratelimit_db = db
    return g.ratelimit_db


def _cleanup_expired_windows(app: Flask) -> None:
    """Remove rate limit windows older than 2x the window duration."""
    try:
        db_path = _get_db_path(app)
        conn = sqlite3.connect(db_path)
        window = app.config.get("RATE_LIMIT_WINDOW_SECONDS", 3600)
        cutoff = int(time.time()) - (2 * window)
        conn.execute("DELETE FROM rate_limit_windows WHERE window_start < ?", (cutoff,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("Rate limiter cleanup failed: %s", str(e))


def init_ratelimit(app: Flask) -> None:
    """Initialize the SQLite-backed rate limiter and register request hooks.

    Creates the rate limit table if it does not exist, runs initial
    cleanup of expired windows, and registers ``before_request`` /
        ``after_request`` hooks to enforce and report rate limits.
    """
    db_path = _get_db_path(app)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()
    logger.info("Rate limiter initialized (SQLite, db=%s)", db_path)

    _cleanup_expired_windows(app)

    @app.before_request
    def _check_rate_limit():  # type: ignore[return]
        if request.path.startswith("/health"):
            return None

        limit = app.config.get("RATE_LIMIT_DEFAULT", 100)
        window = app.config.get("RATE_LIMIT_WINDOW_SECONDS", 3600)

        client_ip = _get_client_ip()
        now = int(time.time())
        window_start = now - (now % window)

        bucket_key = f"{client_ip}:{request.path}"

        db = _ensure_db(app)

        # Atomic upsert: INSERT OR REPLACE avoids the TOCTOU race condition
        # that existed with the previous SELECT-then-UPDATE pattern.
        db.execute(
            "INSERT INTO rate_limit_windows (bucket_key, window_start, request_count) "
            "VALUES (?, ?, 1) "
            "ON CONFLICT(bucket_key, window_start) "
            "DO UPDATE SET request_count = request_count + 1",
            (bucket_key, window_start),
        )
        db.commit()

        row = db.execute(
            "SELECT request_count FROM rate_limit_windows "
            "WHERE bucket_key = ? AND window_start = ?",
            (bucket_key, window_start),
        ).fetchone()
        current_count = row["request_count"] if row else 1

        g.rate_limit = limit
        g.rate_remaining = max(0, limit - current_count)

        if current_count > limit:
            return error_response(
                message="Rate limit exceeded.",
                error_type="Too Many Requests",
                status_code=429,
            )

        return None

    @app.after_request
    def _set_ratelimit_headers(response):
        rl = getattr(g, "rate_limit", None)
        rr = getattr(g, "rate_remaining", None)
        if rl is not None:
            response.headers["X-RateLimit-Limit"] = str(rl)
        if rr is not None:
            response.headers["X-RateLimit-Remaining"] = str(rr)
        return response

    @app.teardown_appcontext
    def _close_db(exc):
        db = g.pop("ratelimit_db", None)
        if db is not None:
            db.close()
