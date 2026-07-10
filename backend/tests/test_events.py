import json
import time


def test_sse_streams_incident(app, client):
    from app.routes.events import push_incident

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
