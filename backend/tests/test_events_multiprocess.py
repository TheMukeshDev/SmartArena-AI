"""
Multi-process SSE test — proves SQLite-backed incident queue works
across separate Python processes (simulating gunicorn workers).
"""

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time


def _init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS incidents ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "incident_json TEXT NOT NULL,"
        "created_at INTEGER NOT NULL)"
    )
    conn.commit()
    conn.close()


def _push_incident_subprocess(db_path, incident):
    """Push an incident from a subprocess (simulates a different worker)."""
    code = f"""
import json, sqlite3, time
db_path = {db_path!r}
incident = {json.dumps(incident)}
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute(
    "INSERT INTO incidents (incident_json, created_at) VALUES (?, ?)",
    (json.dumps(incident), int(time.time())),
)
conn.commit()
conn.close()
"""
    subprocess.run([sys.executable, "-c", code], check=True, timeout=10)


def test_multiprocess_incident_delivery():
    """A subprocess pushes an incident; the main process polls and sees it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "events_test.db")
        _init_db(db_path)

        incident = {
            "description": "Flood in concourse B",
            "category": "Maintenance",
            "priority": "High",
        }

        _push_incident_subprocess(db_path, incident)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        rows = conn.execute(
            "SELECT id, incident_json FROM incidents WHERE id > 0 ORDER BY id"
        ).fetchall()
        conn.close()

        assert len(rows) == 1
        fetched = json.loads(rows[0][1])
        assert fetched["description"] == "Flood in concourse B"
        assert fetched["category"] == "Maintenance"


def test_multiprocess_sequential_delivery():
    """Multiple subprocesses push incidents; main process sees all of them."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "events_test.db")
        _init_db(db_path)

        incidents = [
            {"description": f"Incident {i}", "category": "General", "priority": "Low"}
            for i in range(5)
        ]

        for inc in incidents:
            _push_incident_subprocess(db_path, inc)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        rows = conn.execute(
            "SELECT id, incident_json FROM incidents WHERE id > 0 ORDER BY id"
        ).fetchall()
        conn.close()

        assert len(rows) == 5
        for i, (_, raw) in enumerate(rows):
            assert json.loads(raw)["description"] == f"Incident {i}"


def test_multiprocess_sse_generator_receives_cross_process_push():
    """Simulate the SSE flow: subprocess pushes, main process polls via the
    same SQLite query pattern used in the SSE generate() loop."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "events_test.db")
        _init_db(db_path)

        incident = {
            "description": "Smoke detected in Section 12",
            "category": "Security",
            "priority": "Critical",
        }

        _push_incident_subprocess(db_path, incident)

        last_seen_id = 0
        received = []

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        rows = conn.execute(
            "SELECT id, incident_json FROM incidents WHERE id > ? ORDER BY id",
            (last_seen_id,),
        ).fetchall()
        conn.close()

        for row_id, incident_json in rows:
            received.append(json.loads(incident_json))
            last_seen_id = row_id

        assert len(received) == 1
        assert received[0]["description"] == "Smoke detected in Section 12"
        assert received[0]["priority"] == "Critical"
