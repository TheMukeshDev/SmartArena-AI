import pytest
from app import create_app
from app.utils.response import success_response, error_response
import json


@pytest.fixture
def app():
    return create_app("testing")


def test_success_response(app):
    with app.app_context():
        resp, code = success_response(
            data={"foo": "bar"}, message="Ok", status_code=201
        )
    assert code == 201

    data = json.loads(resp.data)
    assert data["success"] is True
    assert data["message"] == "Ok"
    assert data["data"]["foo"] == "bar"


def test_error_response(app):
    with app.app_context():
        resp, code = error_response(error_type="Bad Request", status_code=400)
    assert code == 400

    data = json.loads(resp.data)
    assert data["success"] is False
    assert data["error"]["type"] == "Bad Request"
    assert "data" not in data
