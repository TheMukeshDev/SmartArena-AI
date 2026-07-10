import json
import os
import pytest
from unittest.mock import patch


@pytest.fixture
def ratelimit_app(tmp_path):
    db_path = str(tmp_path / "test_ratelimit.db")
    from app import create_app

    app = create_app("testing")
    app.config["RATE_LIMIT_DB_PATH"] = db_path
    app.config["RATE_LIMIT_DEFAULT"] = 5
    app.config["RATE_LIMIT_WINDOW_SECONDS"] = 60
    import sqlite3
    from app.middleware.ratelimit import CREATE_TABLE_SQL

    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()
    yield app


@pytest.fixture
def rl_client(ratelimit_app):
    return ratelimit_app.test_client()


class TestRateLimit:
    def test_health_never_rate_limited(self, rl_client):
        for _ in range(20):
            res = rl_client.get("/health")
            assert res.status_code == 200

    def test_health_ready_never_rate_limited(self, rl_client):
        for _ in range(20):
            res = rl_client.get("/health/ready")
            assert res.status_code == 200

    def test_rate_limit_exceeded_returns_429(self, rl_client):
        rl_client.set_cookie("session", "fake")
        with (
            patch(
                "app.middleware.auth.auth.verify_session_cookie",
                return_value={"uid": "test123"},
            ),
            patch(
                "app.services.ai_service.AIService.process_chat",
                return_value="fake response",
            ),
        ):
            url = "/api/v1/ai/assistant/chat"
            payload = {"query": "Hello", "context": {}}
            for i in range(7):
                res = rl_client.post(url, json=payload)
                if i >= 5:
                    assert res.status_code == 429, f"Request {i} should be 429"
                else:
                    assert res.status_code in (200, 429), (
                        f"Request {i} unexpected status"
                    )

    def test_rate_limit_has_correct_error_shape(self, rl_client):
        rl_client.set_cookie("session", "fake")
        with (
            patch(
                "app.middleware.auth.auth.verify_session_cookie",
                return_value={"uid": "test123"},
            ),
            patch(
                "app.services.ai_service.AIService.process_chat",
                return_value="fake response",
            ),
        ):
            url = "/api/v1/ai/assistant/chat"
            payload = {"query": "Hello", "context": {}}
            for _ in range(6):
                rl_client.post(url, json=payload)
            res = rl_client.post(url, json=payload)
            assert res.status_code == 429
            data = json.loads(res.data)
            assert data["success"] is False
            assert data["error"]["type"] == "Too Many Requests"
            assert data["error"]["code"] == 429

    def test_rate_limit_headers_present(self, rl_client):
        rl_client.set_cookie("session", "fake")
        with (
            patch(
                "app.middleware.auth.auth.verify_session_cookie",
                return_value={"uid": "test123"},
            ),
            patch(
                "app.services.ai_service.AIService.process_chat",
                return_value="fake response",
            ),
        ):
            res = rl_client.post(
                "/api/v1/ai/assistant/chat", json={"query": "Hello", "context": {}}
            )
            assert "X-RateLimit-Limit" in res.headers
            assert "X-RateLimit-Remaining" in res.headers
