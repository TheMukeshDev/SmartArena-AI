import json
import time
import datetime
import logging
import sqlite3

from flask import Blueprint, Response, stream_with_context
from app.middleware.auth import require_auth, require_role

logger = logging.getLogger(__name__)

events_bp = Blueprint("events", __name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_json TEXT NOT NULL,
    created_at INTEGER NOT NULL
)
"""


def _get_db_path() -> str:
    from flask import current_app

    return current_app.config.get("EVENTS_DB_PATH", "events.db")


def _init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def push_incident(incident: dict) -> None:
    from flask import current_app

    db_path = current_app.config.get("EVENTS_DB_PATH", "events.db")
    _init_db(db_path)
    conn = _get_db(db_path)
    try:
        conn.execute(
            "INSERT INTO incidents (incident_json, created_at) VALUES (?, ?)",
            (json.dumps(incident), int(time.time())),
        )
        conn.commit()
    finally:
        conn.close()


def _get_db(db_path: str) -> sqlite3.Connection:
    _init_db(db_path)
    return _get_conn(db_path)


@events_bp.route("/incidents", methods=["GET"])
@require_auth
@require_role(["admin", "volunteer"])
def stream_incidents():
    from flask import current_app

    testing = current_app.config.get("TESTING", False)
    db_path = _get_db_path()
    poll_interval = current_app.config.get("EVENTS_POLL_INTERVAL", 1.0)

    def generate():
        last_seen_id = 0
        while True:
            conn = _get_db(db_path)
            try:
                rows = conn.execute(
                    "SELECT id, incident_json FROM incidents WHERE id > ? ORDER BY id",
                    (last_seen_id,),
                ).fetchall()
            finally:
                conn.close()

            for row_id, incident_json in rows:
                data = json.dumps(
                    {
                        "id": row_id,
                        "incident": json.loads(incident_json),
                        "timestamp": datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                    }
                )
                yield f"event: incident\ndata: {data}\n\n"
                last_seen_id = row_id

            if testing:
                break
            time.sleep(poll_interval)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
