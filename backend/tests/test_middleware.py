import pytest
from app.middleware.auth import require_auth
from flask import Flask, jsonify

def test_require_auth_missing_cookie(client):
    # App is already set up with test routes, but let's test the middleware directly via /me
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

def test_require_auth_invalid_cookie(client):
    client.set_cookie("localhost", "session", "invalid_session_cookie")
    res = client.get("/api/v1/auth/me")
    # without mocking verify_session_cookie, it will fail and return 401
    assert res.status_code == 401
