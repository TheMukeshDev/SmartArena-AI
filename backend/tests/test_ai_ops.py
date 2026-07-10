import json
from unittest.mock import patch


def test_incident_classification(client):
    with (
        patch("app.services.ai_service.AIService.process_incident") as mock_process,
        patch("app.services.ai_service.get_firestore_client"),
    ):
        mock_process.return_value = {
            "category": "Medical",
            "priority": "High",
            "action": "Dispatch medics",
            "announcement": "",
        }

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/incident", json={"description": "Someone passed out"}
            )
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["classification"]["category"] == "Medical"
            assert data["data"]["classification"]["priority"] == "High"


def test_crowd_analysis(client):
    with (
        patch(
            "app.services.ai_service.AIService.process_crowd_analysis"
        ) as mock_process,
        patch("app.services.ai_service.get_firestore_client"),
    ):
        mock_process.return_value = {
            "global_status": "Congested",
            "insights": ["Issue"],
            "routing_advice": "Go left",
        }

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post("/api/v1/ai/crowd/analyze", json={"zones": []})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["global_status"] == "Congested"


def test_volunteer_assign(client):
    with (
        patch(
            "app.services.ai_service.AIService.process_volunteer_assignment"
        ) as mock_process,
        patch("app.services.ai_service.get_firestore_client"),
    ):
        mock_process.return_value = {
            "task": "Clean spill",
            "priority": "Low",
            "description": "Clean it",
        }

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/volunteer/assign", json={"location": "East Gate"}
            )
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["task"] == "Clean spill"


def test_sustainability_optimize(client):
    with (
        patch(
            "app.services.ai_service.AIService.process_sustainability"
        ) as mock_process,
        patch("app.services.ai_service.get_firestore_client"),
    ):
        mock_process.return_value = {
            "status": "Good",
            "recommendations": ["Dim lights"],
        }

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/sustainability/optimize", json={"metrics": {}}
            )
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["status"] == "Good"


def test_assistant_chat(client):
    with patch("app.services.ai_service.AIService.process_chat") as mock_process:
        mock_process.return_value = ("This is a test response.", "mock_id")

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post("/api/v1/ai/assistant/chat", json={"query": "Hello"})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["reply"] == "This is a test response."


def test_assistant_chat_missing_query(client):
    client.set_cookie("session", "fake")
    with patch(
        "app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}
    ):
        res = client.post("/api/v1/ai/assistant/chat", json={})
        assert res.status_code == 400


def test_assistant_chat_with_nested_context(client):
    with patch("app.services.ai_service.AIService.process_chat") as mock_process:
        mock_process.return_value = ("Response with nested context", "mock_id")

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/assistant/chat",
                json={
                    "query": "where is gate c",
                    "context": {
                        "zones": [{"name": "North", "occupancy": 45}],
                        "gates": {"A": "open", "B": "closed"},
                    },
                },
            )
            assert res.status_code == 200
            data = json.loads(res.data)
            assert "nested context" in data["data"]["reply"]


def test_transport_suggest(client):
    with patch(
        "app.services.ai_service.AIService.process_transport_suggestion"
    ) as mock_process:
        mock_process.return_value = {
            "recommended_mode": "Transit",
            "estimated_travel_time_minutes": 20,
            "directions": "Take the shuttle from Gate A",
            "alternative": "Walk to Metro",
        }

        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/transport/suggest",
                json={"gate": "Gate A", "arrival_time": "3:00 PM"},
            )
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["recommended_mode"] == "Transit"
