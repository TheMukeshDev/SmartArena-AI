import pytest
from app.middleware.auth import require_auth, require_role
from flask import Flask, jsonify, g
from unittest.mock import patch
from firebase_admin import auth


def test_require_auth_missing_cookie(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_require_auth_invalid_cookie(client):
    client.set_cookie("session", "invalid_session_cookie")
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_require_auth_bearer_token(app, client):
    with patch("firebase_admin.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "123", "role": "admin"}
        res = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer testtoken"}
        )
        assert res.status_code == 200
        mock_verify.assert_called_once_with("testtoken", check_revoked=True)


def test_require_auth_revoked_token(client):
    with patch("firebase_admin.auth.verify_session_cookie") as mock_verify:
        mock_verify.side_effect = auth.RevokedIdTokenError("Revoked")
        client.set_cookie("session", "revoked_session_cookie")
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401
        assert "revoked" in res.json["error"]["message"].lower()


def test_require_auth_invalid_session_cookie(client):
    with patch("firebase_admin.auth.verify_session_cookie") as mock_verify:
        mock_verify.side_effect = auth.InvalidSessionCookieError("Invalid")
        client.set_cookie("session", "invalid_session_cookie")
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401
        assert "invalid session" in res.json["error"]["message"].lower()


def test_require_role_success(app):
    with app.test_request_context():
        g.user = {"uid": "123", "role": "admin"}

        @require_role(["admin"])
        def dummy_route():
            return "OK"

        res = dummy_route()
        assert res == "OK"


def test_require_role_denied(app):
    with app.test_request_context():
        g.user = {"uid": "123", "role": "fan"}

        @require_role(["admin"])
        def dummy_route():
            return "OK"

        res = dummy_route()
        assert res[1] == 403


def test_require_role_no_user(app):
    with app.test_request_context():

        @require_role(["admin"])
        def dummy_route():
            return "OK"

        res = dummy_route()
        assert res[1] == 401
