import pytest
from app.utils.response import success_response, error_response
import json

def test_success_response():
    resp, code = success_response(data={"foo": "bar"}, message="Ok", status_code=201)
    assert code == 201
    
    data = json.loads(resp.data)
    assert data["success"] is True
    assert data["message"] == "Ok"
    assert data["data"]["foo"] == "bar"

def test_error_response():
    resp, code = error_response(error="Bad Request", status_code=400)
    assert code == 400
    
    data = json.loads(resp.data)
    assert data["success"] is False
    assert data["error"] == "Bad Request"
    assert data["data"] is None
