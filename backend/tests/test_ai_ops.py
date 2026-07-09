import json
from unittest.mock import patch

def test_incident_classification(client):
    with patch("app.ai.gemini.genai.GenerativeModel") as mock_model, \
         patch("app.ai.gemini._init_gemini") as mock_init, \
         patch("app.services.ai_service.get_firestore_client") as mock_fs:
        
        mock_init.return_value = True
        mock_response = mock_model.return_value.generate_content_async.return_value
        mock_response.text = '{"category": "Medical", "priority": "High", "action": "Dispatch medics", "announcement": ""}'
        
        client.set_cookie("localhost", "session", "fake")
        with patch("app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}):
            res = client.post("/api/v1/ai/incident", json={"description": "Someone passed out"})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["classification"]["category"] == "Medical"
            assert data["data"]["classification"]["priority"] == "High"

def test_crowd_analysis(client):
    with patch("app.ai.gemini.genai.GenerativeModel") as mock_model, \
         patch("app.ai.gemini._init_gemini") as mock_init, \
         patch("app.services.ai_service.get_firestore_client") as mock_fs:
        
        mock_init.return_value = True
        mock_response = mock_model.return_value.generate_content_async.return_value
        mock_response.text = '{"global_status": "Congested", "insights": ["Issue"], "routing_advice": "Go left"}'
        
        client.set_cookie("localhost", "session", "fake")
        with patch("app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}):
            res = client.post("/api/v1/ai/crowd/analyze", json={"zones": []})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["global_status"] == "Congested"

def test_volunteer_assign(client):
    with patch("app.ai.gemini.genai.GenerativeModel") as mock_model, \
         patch("app.ai.gemini._init_gemini") as mock_init, \
         patch("app.services.ai_service.get_firestore_client") as mock_fs:
        
        mock_init.return_value = True
        mock_response = mock_model.return_value.generate_content_async.return_value
        mock_response.text = '{"task": "Clean spill", "priority": "Low", "description": "Clean it"}'
        
        client.set_cookie("localhost", "session", "fake")
        with patch("app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}):
            res = client.post("/api/v1/ai/volunteer/assign", json={"location": "East Gate"})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["task"] == "Clean spill"

def test_sustainability_optimize(client):
    with patch("app.ai.gemini.genai.GenerativeModel") as mock_model, \
         patch("app.ai.gemini._init_gemini") as mock_init, \
         patch("app.services.ai_service.get_firestore_client") as mock_fs:
        
        mock_init.return_value = True
        mock_response = mock_model.return_value.generate_content_async.return_value
        mock_response.text = '{"status": "Good", "recommendations": ["Dim lights"]}'
        
        client.set_cookie("localhost", "session", "fake")
        with patch("app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}):
            res = client.post("/api/v1/ai/sustainability/optimize", json={"metrics": {}})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["status"] == "Good"

def test_assistant_chat(client):
    with patch("app.ai.gemini.genai.GenerativeModel") as mock_model, \
         patch("app.ai.gemini._init_gemini") as mock_init:
        
        mock_init.return_value = True
        mock_response = mock_model.return_value.generate_content_async.return_value
        mock_response.text = 'This is a test response.'
        
        client.set_cookie("localhost", "session", "fake")
        with patch("app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}):
            res = client.post("/api/v1/ai/assistant/chat", json={"query": "Hello"})
            assert res.status_code == 200
            data = json.loads(res.data)
            assert data["data"]["reply"] == "This is a test response."
        
def test_assistant_chat_missing_query(client):
    client.set_cookie("localhost", "session", "fake")
    with patch("app.middleware.auth.auth.verify_session_cookie", return_value={"uid": "123"}):
        res = client.post("/api/v1/ai/assistant/chat", json={})
        assert res.status_code == 400
