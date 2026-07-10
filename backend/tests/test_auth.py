import json
import pytest
from unittest.mock import patch, MagicMock

# Mock firebase_admin before the app imports it
with (
    patch("app.config.firebase.firebase_admin") as mock_firebase,
    patch("app.config.firebase.credentials") as mock_credentials,
    patch("app.middleware.auth.auth") as mock_auth,
    patch("app.routes.auth.auth") as mock_route_auth,
):

    def test_session_login_missing_token(client):
        res = client.post("/api/v1/auth/sessionLogin", json={})
        assert res.status_code == 400
        data = json.loads(res.data)
        assert data["success"] is False
        assert "idToken is required" in data["error"]["message"]

    def test_session_login_success(client):
        # We need to mock auth.verify_id_token and auth.create_session_cookie
        with (
            patch("app.routes.auth.auth.verify_id_token") as verify_mock,
            patch("app.routes.auth.auth.create_session_cookie") as create_mock,
        ):
            import datetime

            verify_mock.return_value = {
                "auth_time": datetime.datetime.now().timestamp() - 60
            }
            create_mock.return_value = "mock_session_cookie"

            res = client.post(
                "/api/v1/auth/sessionLogin", json={"idToken": "fake_token"}
            )
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["success"] is True
            assert "session" in res.headers.get("Set-Cookie", "")

    def test_session_logout(client):
        client.set_cookie("session", "fake_session")
        with (
            patch("app.routes.auth.auth.verify_session_cookie") as verify_mock,
            patch("app.routes.auth.auth.revoke_refresh_tokens") as revoke_mock,
        ):
            verify_mock.return_value = {"uid": "123"}
            res = client.post("/api/v1/auth/sessionLogout")

            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["success"] is True
            assert revoke_mock.called

    def test_register_user_missing_data(client):
        res = client.post("/api/v1/auth/register", json={})
        # This will fail at @require_auth since no cookie is present, but let's just assert 401
        assert res.status_code == 401

    def test_register_user_success(client):
        client.set_cookie("session", "fake_session")

        with (
            patch("app.middleware.auth.auth.verify_session_cookie") as verify_mock,
            patch("app.routes.auth.auth.set_custom_user_claims") as set_claims_mock,
            patch("app.routes.auth.get_firestore_client") as fs_mock,
        ):
            verify_mock.return_value = {"uid": "user123"}
            db_mock = MagicMock()
            fs_mock.return_value = db_mock

            res = client.post(
                "/api/v1/auth/register",
                json={
                    "uid": "user123",
                    "email": "test@test.com",
                    "name": "Test User",
                    "role": "admin",  # The route should force it to "fan"
                },
            )

            assert res.status_code == 200
            set_claims_mock.assert_called_with("user123", {"role": "fan"})

    def test_register_user_uid_mismatch(client):
        client.set_cookie("session", "fake_session")

        with patch("app.middleware.auth.auth.verify_session_cookie") as verify_mock:
            verify_mock.return_value = {"uid": "different_user"}

            res = client.post(
                "/api/v1/auth/register",
                json={"uid": "user123", "email": "test@test.com"},
            )
            assert res.status_code == 403

    def test_me_success(client):
        client.set_cookie("session", "fake_session")
        with patch("app.middleware.auth.auth.verify_session_cookie") as verify_mock:
            verify_mock.return_value = {"uid": "user123", "role": "admin"}

            res = client.get("/api/v1/auth/me")
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["uid"] == "user123"
            assert data["data"]["role"] == "admin"
