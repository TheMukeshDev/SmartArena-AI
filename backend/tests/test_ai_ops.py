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


# ── Boundary Validation Tests ───────────────────────────────────────────


class TestBoundaryValidation:
    """Verify Pydantic field constraints are enforced."""

    def test_incident_rejects_short_description(self, client):
        """Incident description must be at least 10 characters."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/incident",
                json={"description": "Short"},
            )
            assert res.status_code in (400, 422)

    def test_volunteer_rejects_short_location(self, client):
        """Volunteer location must be at least 2 characters."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/volunteer/assign",
                json={"location": "X"},
            )
            assert res.status_code in (400, 422)

    def test_chat_rejects_empty_query(self, client):
        """Chat query must be at least 2 characters."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/assistant/chat",
                json={"query": "a"},
            )
            assert res.status_code in (400, 422)

    def test_chat_rejects_long_query(self, client):
        """Chat query must not exceed 1000 characters."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/assistant/chat",
                json={"query": "x" * 1001},
            )
            assert res.status_code in (400, 422)

    def test_chat_rejects_invalid_language(self, client):
        """Chat preferred_language must be in the allowlist."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/assistant/chat",
                json={"query": "hello", "preferred_language": "zz"},
            )
            assert res.status_code in (400, 422)

    def test_chat_accepts_hindi(self, client):
        """Chat should accept Hindi as a valid language."""
        client.set_cookie("session", "fake")
        with (
            patch(
                "app.middleware.auth.auth.verify_session_cookie",
                return_value={"uid": "123"},
            ),
            patch("app.services.ai_service.AIService.process_chat") as mock_chat,
        ):
            mock_chat.return_value = ("Namaste", None)
            res = client.post(
                "/api/v1/ai/assistant/chat",
                json={"query": "Hello", "preferred_language": "hi"},
            )
            assert res.status_code == 200

    def test_transport_rejects_empty_gate(self, client):
        """Transport gate must be at least 1 character."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            res = client.post(
                "/api/v1/ai/transport/suggest",
                json={"gate": "", "arrival_time": "3:00 PM"},
            )
            assert res.status_code in (400, 422)

    def test_admin_gate_rejects_invalid_status(self, client):
        """Gate status must be open, closed, or maintenance."""
        client.set_cookie("session", "fake")
        with patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123", "role": "admin"},
        ):
            res = client.post(
                "/api/v1/admin/gates",
                json={"name": "Gate A", "status": "invalid_status"},
            )
            assert res.status_code in (400, 422)

    def test_admin_announcement_rejects_invalid_priority(self, client):
        """Announcement priority must be normal or urgent."""
        client.set_cookie("session", "fake")
        with (
            patch(
                "app.middleware.auth.auth.verify_session_cookie",
                return_value={"uid": "123", "role": "admin"},
            ),
            patch("app.routes.admin.get_firestore_client") as mock_db,
        ):
            mock_db.return_value = None
            res = client.post(
                "/api/v1/admin/announcements",
                json={
                    "title": "Test",
                    "message": "Test announcement",
                    "priority": "critical",
                },
            )
            assert res.status_code in (400, 422)


# ── Multilingual Crowd Analysis Tests ─────────────────────────────────────


class TestMultilingualCrowdAnalysis:
    """Verify multilingual recommended_action is parsed and surfaced correctly."""

    def test_crowd_analysis_returns_multilingual_action(self, client):
        """Crowd analysis endpoint returns recommended_action as a language-keyed dict."""
        multilingual_response = {
            "global_status": "Congested",
            "insights": ["Gate C is overcrowded", "Food court is filling up"],
            "routing_advice": "Redirect fans to Gate D",
            "predicted_status_15min": {"Gate A": "Moderate", "Gate C": "Critical"},
            "recommended_action": {
                "en": "Open Gate D early and redirect fans from Zone 3",
                "es": "Abre la Puerta D temprano y redirige a los aficionados de la Zona 3",
                "fr": "Ouvrez la Porte D plus tôt et redirigez les supporters de la Zone 3",
                "ar": "افتح البوتة D مبكراً ووجّه المشجعين من المنطقة 3",
                "hi": "गेट D जल्दी खोलें और ज़ोन 3 से प्रशंसकों को पुनर्निर्देशित करें",
            },
        }

        with (
            patch(
                "app.services.ai_service.AIService.process_crowd_analysis"
            ) as mock_process,
            patch("app.services.ai_service.get_firestore_client"),
        ):
            mock_process.return_value = multilingual_response

            client.set_cookie("session", "fake")
            with patch(
                "app.middleware.auth.auth.verify_session_cookie",
                return_value={"uid": "123"},
            ):
                res = client.post("/api/v1/ai/crowd/analyze", json={"zones": []})
                assert res.status_code == 200
                data = json.loads(res.data)

                action = data["data"]["recommended_action"]
                assert isinstance(action, dict)
                assert "en" in action
                assert "es" in action
                assert "fr" in action
                assert "ar" in action
                assert "hi" in action
                assert "Gate D" in action["en"]

    def test_crowd_analysis_fallback_has_multilingual_keys(self, client):
        """Gemini fallback dict contains all 5 language keys."""
        from app.ai.gemini import analyze_crowd_data
        import asyncio

        async def _run():
            return await analyze_crowd_data([])

        with patch("app.ai.gemini._get_client", return_value=None):
            result = asyncio.run(_run())

        assert isinstance(result["recommended_action"], dict)
        for lang in ["en", "es", "fr", "ar", "hi"]:
            assert lang in result["recommended_action"]
