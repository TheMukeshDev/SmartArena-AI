from unittest.mock import patch
from flask import Flask
from app.config.firebase import init_firebase, get_firestore_client


def test_firebase_already_initialized():
    app = Flask(__name__)
    app.config["TESTING"] = False

    with patch("firebase_admin._apps", ["dummy"]):
        with patch("firebase_admin.firestore.client", return_value="mock_client"):
            init_firebase(app)
            assert get_firestore_client() == "mock_client"


def test_firebase_init_with_credentials():
    app = Flask(__name__)
    app.config["TESTING"] = False
    app.config["FIREBASE_PROJECT_ID"] = "test-proj"
    app.config["FIREBASE_CLIENT_EMAIL"] = "test@example.com"
    app.config["FIREBASE_PRIVATE_KEY"] = "dummy_key"

    with patch("firebase_admin.credentials.Certificate"):
        with patch("firebase_admin.initialize_app") as mock_init:
            with patch("firebase_admin.firestore.client", return_value="mock_client2"):
                init_firebase(app)
                assert mock_init.called
                assert get_firestore_client() == "mock_client2"


def test_firebase_init_adc():
    app = Flask(__name__)
    app.config["TESTING"] = False
    app.config["FIREBASE_PROJECT_ID"] = "test-proj"
    app.config["FIREBASE_CLIENT_EMAIL"] = ""
    app.config["FIREBASE_PRIVATE_KEY"] = ""

    with patch("firebase_admin.initialize_app") as mock_init:
        with patch("firebase_admin.firestore.client", return_value="mock_client3"):
            init_firebase(app)
            assert mock_init.called
            assert get_firestore_client() == "mock_client3"


def test_firebase_not_configured():
    app = Flask(__name__)
    app.config["TESTING"] = False
    app.config["FIREBASE_PROJECT_ID"] = ""

    with patch("app.config.firebase.logger.warning") as mock_warn:
        init_firebase(app)
        assert mock_warn.called


def test_firebase_init_error():
    app = Flask(__name__)
    app.config["TESTING"] = False
    app.config["FIREBASE_PROJECT_ID"] = "test-proj"

    with patch("firebase_admin.initialize_app", side_effect=Exception("Test Error")):
        with patch("app.config.firebase.logger.error") as mock_err:
            init_firebase(app)
            mock_err.assert_called_once()
