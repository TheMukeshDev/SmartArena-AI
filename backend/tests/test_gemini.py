import pytest
from unittest.mock import patch, MagicMock
from app.ai.gemini import (
    classify_incident,
    analyze_crowd_data,
    assign_volunteer_task,
    optimize_sustainability,
    ask_assistant,
    _parse_json_response
)

def test_parse_json_response():
    assert _parse_json_response('```json\n{"a":1}\n```') == {"a": 1}
    assert _parse_json_response('```\n{"a":1}\n```') == {"a": 1}
    assert _parse_json_response('{"a":1}') == {"a": 1}

def test_classify_incident_fallback():
    with patch("app.ai.gemini._init_gemini", return_value=False):
        res = classify_incident("test")
        assert res["category"] == "General"

def test_analyze_crowd_data_fallback():
    with patch("app.ai.gemini._init_gemini", return_value=False):
        res = analyze_crowd_data([])
        assert res["global_status"] == "Normal"

def test_assign_volunteer_task_fallback():
    with patch("app.ai.gemini._init_gemini", return_value=False):
        res = assign_volunteer_task("Gate A")
        assert res["priority"] == "Medium"

def test_optimize_sustainability_fallback():
    with patch("app.ai.gemini._init_gemini", return_value=False):
        res = optimize_sustainability({})
        assert res["status"] == "Optimization Failed"

def test_ask_assistant_fallback():
    with patch("app.ai.gemini._init_gemini", return_value=False):
        res = ask_assistant("Hello", {})
        assert "offline" in res.lower()

def test_classify_incident_exception():
    with patch("app.ai.gemini._init_gemini", return_value=True), \
         patch("app.ai.gemini.genai.GenerativeModel") as mock_model:
        mock_model.return_value.generate_content.side_effect = Exception("API Error")
        res = classify_incident("test")
        assert res["category"] == "General"
