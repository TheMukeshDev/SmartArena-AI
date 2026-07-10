"""
SmartArena AI — SQLite-based Cache
====================================

Provides a persistent, multi-worker-safe cache using SQLite with WAL mode.
Replaces the previous Redis-based caching approach.
"""

import sqlite3
import time
import json
import threading
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS response_cache (
    cache_key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    expires_at INTEGER NOT NULL
)
"""

CLEANUP_SQL = "DELETE FROM response_cache WHERE expires_at < ?"


class SQLiteCache:
    def __init__(self, db_path: str = "cache.db", ttl_seconds: int = 3600):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return self._local.conn

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
        conn.close()

    def _cleanup_expired(self) -> None:
        conn = self._get_conn()
        try:
            conn.execute(CLEANUP_SQL, (int(time.time()),))
            conn.commit()
        except Exception as e:
            logger.debug("Cache cleanup error: %s", e)

    def get(self, key: str) -> Optional[Any]:
        conn = self._get_conn()
        now = int(time.time())
        row = conn.execute(
            "SELECT value, expires_at FROM response_cache WHERE cache_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        if row["expires_at"] <= now:
            conn.execute("DELETE FROM response_cache WHERE cache_key = ?", (key,))
            conn.commit()
            return None
        try:
            return json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            return row["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = int(time.time()) + (ttl if ttl is not None else self.ttl_seconds)
        serialized = json.dumps(value, default=str)
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO response_cache (cache_key, value, expires_at) "
            "VALUES (?, ?, ?)",
            (key, serialized, expires_at),
        )
        conn.commit()
        self._cleanup_expired()

    def delete(self, key: str) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM response_cache WHERE cache_key = ?", (key,))
        conn.commit()

    def clear(self) -> None:
        conn = self._get_conn()
        conn.execute("DELETE FROM response_cache")
        conn.commit()
