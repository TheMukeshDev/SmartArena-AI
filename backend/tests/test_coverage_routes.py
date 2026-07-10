from unittest.mock import patch
import functools

from firebase_admin import auth


def dummy_require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import g

        g.user = {"uid": "123", "role": "admin"}
        return f(*args, **kwargs)

    return decorated


def test_config_public(client):
    res = client.get("/api/v1/config/firebase")
    assert res.status_code in [200, 503]


def test_ai_ops_errors_with_auth(client):
    with patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "123", "auth_time": 9999999999},
    ):
        headers = {"Authorization": "Bearer test"}

        res = client.post("/api/v1/ai/incident", json={}, headers=headers)
        assert res.status_code == 400

        res = client.post("/api/v1/ai/assistant/chat", json={}, headers=headers)
        assert res.status_code == 400

        res = client.post(
            "/api/v1/ai/crowd/analyze", json={"zones": "not_a_list"}, headers=headers
        )
        assert res.status_code == 400

        res = client.post("/api/v1/ai/volunteer/assign", json={}, headers=headers)
        assert res.status_code == 400

        res = client.post(
            "/api/v1/ai/sustainability/optimize",
            json={"metrics": "not_a_dict"},
            headers=headers,
        )
        assert res.status_code == 400

        res = client.post("/api/v1/ai/transport/suggest", json={}, headers=headers)
        assert res.status_code == 400

        res = client.get("/api/v1/ai/navigation/path", headers=headers)
        assert res.status_code == 400

        res = client.get(
            "/api/v1/ai/navigation/path?start=A&end=Unknown", headers=headers
        )
        assert res.status_code == 404

        res = client.get(
            "/api/v1/ai/navigation/path?start=Gate A&end=Concourse North",
            headers=headers,
        )
        assert res.status_code == 200

        res = client.get("/api/v1/ai/navigation/zones", headers=headers)
        assert res.status_code == 200


def test_auth_errors(client):
    res = client.post("/api/v1/auth/sessionLogin", json={})
    assert res.status_code == 400

    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("Invalid")):
        res = client.post("/api/v1/auth/sessionLogin", json={"idToken": "bad"})
        assert res.status_code == 500

    with patch(
        "firebase_admin.auth.verify_id_token",
        side_effect=auth.InvalidIdTokenError("Invalid"),
    ):
        res = client.post("/api/v1/auth/sessionLogin", json={"idToken": "bad"})
        assert res.status_code == 401

    with patch(
        "firebase_admin.auth.verify_id_token",
        return_value={"uid": "123", "auth_time": 9999999999},
    ):
        headers = {"Authorization": "Bearer test"}
        with patch(
            "app.routes.auth.get_firestore_client", side_effect=Exception("DB Error")
        ):
            res = client.post(
                "/api/v1/auth/register",
                json={"uid": "123", "email": "a@b.com"},
                headers=headers,
            )
            assert res.status_code == 500


def test_config_errors(client):
    with patch.dict("os.environ", clear=True):
        res = client.get("/api/v1/config/firebase")
        assert res.status_code == 503


def test_health_ready_returns_503_when_firebase_unavailable(client):
    with patch("app.routes.health._check_firebase", return_value=False):
        res = client.get("/health/ready")
        assert res.status_code == 503


def test_health_ready_returns_200_when_firebase_available(client):
    with patch("app.routes.health._check_firebase", return_value=True):
        res = client.get("/health/ready")
        assert res.status_code == 200


def test_404_and_405(client):
    res = client.get("/non_existent_route")
    assert res.status_code == 404

    res = client.post("/health/ready")
    assert res.status_code == 405
