from unittest.mock import patch
from flask import abort

from app.routes.health import _check_firebase
from app.routes.errors import _error_response


def test_check_firebase_exception(app):
    with app.test_request_context():
        with patch("flask.current_app.config", {"TESTING": False}):
            with patch(
                "app.routes.health.get_firestore_client",
                side_effect=Exception("DB Error"),
            ):
                assert _check_firebase() is False


def test_check_firebase_coverage(app):
    with app.test_request_context():
        with patch("flask.current_app.config", {"TESTING": False}):
            with patch("app.routes.health.get_firestore_client", return_value="mock"):
                assert _check_firebase() is True


def test_error_handlers(app, client):
    @app.route("/test_400")
    def t400():
        abort(400)

    @app.route("/test_401")
    def t401():
        abort(401)

    @app.route("/test_403")
    def t403():
        abort(403)

    @app.route("/test_429")
    def t429():
        abort(429)

    @app.route("/test_500")
    def t500():
        raise Exception("test")

    assert client.get("/test_400").status_code == 400
    assert client.get("/test_401").status_code == 401
    assert client.get("/test_403").status_code == 403
    assert client.get("/test_429").status_code == 429
    assert client.get("/test_500").status_code == 500


def test_error_handlers_extra(app):
    @app.route("/test_501")
    def t501():
        raise NotImplementedError("test 501")

    @app.route("/test_500_err")
    def t500_err():
        try:
            1 / 0
        except ZeroDivisionError:
            abort(500)

    app.config["TESTING"] = False
    client = app.test_client()
    assert client.get("/test_501").status_code == 500
    assert client.get("/test_500_err").status_code == 500
    app.config["TESTING"] = True

    with app.test_request_context():
        r, c = _error_response(400, "Test", "Test Message", details={"foo": "bar"})
        assert r.json["error"]["details"]["foo"] == "bar"


def test_auth_direct(app):
    from firebase_admin import auth
    from app.routes.auth import session_login, session_logout, register_user

    with app.test_request_context(json={"idToken": "bad"}):
        with patch(
            "app.routes.auth.auth.verify_id_token",
            side_effect=auth.InvalidIdTokenError("test"),
        ):
            r, c = session_login()
            assert c == 401

        with patch(
            "app.routes.auth.auth.verify_id_token", side_effect=Exception("test")
        ):
            r, c = session_login()
            assert c == 500

        with patch(
            "app.routes.auth.auth.verify_id_token",
            return_value={"uid": "123", "auth_time": 0},
        ):
            r, c = session_login()
            assert c == 401

    with app.test_request_context(json={"uid": "123", "email": "a@b.com"}):
        from flask import g

        g.user = {"uid": "123"}
        with patch(
            "app.routes.auth.auth.set_custom_user_claims",
            side_effect=Exception("test"),
        ):
            r, c = register_user()
            assert c in [401, 500]

    with app.test_request_context(
        json={"uid": "", "email": ""}, headers={"Authorization": "Bearer test"}
    ):
        with patch(
            "app.routes.auth.auth.verify_id_token",
            return_value={"uid": "123", "auth_time": 9999999999},
        ):
            r, c = register_user()
            assert c == 400

    with app.test_request_context():
        from flask import request

        request.cookies = {"session": "bad"}
        with patch(
            "app.routes.auth.auth.verify_session_cookie",
            side_effect=auth.InvalidSessionCookieError("test"),
        ):
            r, c = session_logout()
            assert c == 200

        request.cookies = {"session": "valid"}
        with patch(
            "app.routes.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ):
            with patch(
                "app.routes.auth.auth.revoke_refresh_tokens",
                side_effect=Exception("test error"),
            ):
                r, c = session_logout()
                assert c == 200


def test_logging_coverage(app):
    from app.config.logging import setup_logging

    app.config["LOG_FORMAT"] = "text"
    setup_logging(app)
    app.logger.error("Test error")

    app.config["LOG_FORMAT"] = "json"
    setup_logging(app)
    try:
        1 / 0
    except ZeroDivisionError:
        app.logger.exception("Exception occurred")
