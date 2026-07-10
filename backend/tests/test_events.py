import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import textwrap


def test_sse_streams_incident(app, client):
    from app.routes.events import push_incident
    from unittest.mock import patch

    push_incident(
        {
            "description": "Test fire near Gate A",
            "classification": {
                "category": "Security",
                "priority": "High",
                "action": "Dispatch team",
                "announcement": "Please avoid Gate A",
            },
            "reporter_uid": "test123",
        }
    )

    with patch(
        "app.middleware.auth.auth.verify_session_cookie",
        return_value={"uid": "test123", "role": "admin"},
    ):
        client.set_cookie("session", "fake")
        res = client.get("/api/v1/events/incidents")
        assert res.status_code == 200
        assert res.mimetype == "text/event-stream"
        data = res.get_data(as_text=True)
        assert "event: incident" in data
        assert "Test fire near Gate A" in data
        assert "Security" in data


def test_weather_endpoint_returns_data(app, client):
    from unittest.mock import patch, MagicMock

    mock_data = {
        "current": {
            "temperature_2m": 25.0,
            "precipitation": 0.0,
            "weather_code": 0,
            "wind_speed_10m": 10.0,
        }
    }
    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "test123"},
        ),
    ):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_data).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        client.set_cookie("session", "fake")
        res = client.get("/api/v1/ai/weather")
        assert res.status_code == 200
        body = json.loads(res.data)
        assert body["success"] is True
        assert body["data"]["temperature_c"] == 25.0


# ---------------------------------------------------------------------------
# Cross-process regression tests
#
# These prove the SQLite-backed incident queue works across separate Python
# processes (simulating gunicorn workers).  A subprocess calls the real
# push_incident() inside a Flask app context against a shared DB; the main
# test process then reads those rows back via direct SQLite queries using
# the same pattern as the SSE generate() loop.
#
# If anyone reverts events.py to an in-memory list, every test below will
# FAIL — the subprocess's push_incident() writes only to its process-local
# list, invisible to the parent process.
# ---------------------------------------------------------------------------


def _push_via_app_subprocess(db_path, incident):
    """Spawn a subprocess that calls the real push_incident() with a Flask
    app context, writing to *db_path*."""
    code = textwrap.dedent(
        f"""\
        import sys, os, json
        sys.path.insert(0, {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))!r})
        os.environ["EVENTS_DB_PATH"] = {db_path!r}
        os.environ["FLASK_ENV"] = "testing"
        from app import create_app
        from app.routes.events import push_incident
        app = create_app("testing")
        app.config["EVENTS_DB_PATH"] = {db_path!r}
        with app.app_context():
            push_incident({json.dumps(incident)})
    """
    )
    subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        timeout=15,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )


def test_cross_process_incident_delivery():
    """Subprocess calls push_incident(); main process reads the row from SQLite."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "events_test.db")

        incident = {
            "description": "Flood in concourse B",
            "category": "Maintenance",
            "priority": "High",
        }

        _push_via_app_subprocess(db_path, incident)

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


def test_cross_process_sequential_delivery():
    """Multiple subprocesses each call push_incident(); main process sees all."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "events_test.db")

        incidents = [
            {"description": f"Incident {i}", "category": "General", "priority": "Low"}
            for i in range(5)
        ]

        for inc in incidents:
            _push_via_app_subprocess(db_path, inc)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        rows = conn.execute(
            "SELECT id, incident_json FROM incidents WHERE id > 0 ORDER BY id"
        ).fetchall()
        conn.close()

        assert len(rows) == 5
        for i, (_, raw) in enumerate(rows):
            assert json.loads(raw)["description"] == f"Incident {i}"


def test_cross_process_sse_poll_pattern():
    """Subprocess pushes via push_incident(); main process polls with the
    exact same WHERE id > ? query used by the SSE generate() loop."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "events_test.db")

        incident = {
            "description": "Smoke detected in Section 12",
            "category": "Security",
            "priority": "Critical",
        }

        _push_via_app_subprocess(db_path, incident)

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
