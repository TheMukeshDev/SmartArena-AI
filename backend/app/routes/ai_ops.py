from flask import Blueprint, request, jsonify
from app.ai.gemini import classify_incident, analyze_crowd_data, assign_volunteer_task, optimize_sustainability, ask_assistant
from app.utils.responses import success_response, error_response
# In a real app, you would use firestore to save these, but we'll return them directly for now.

ai_ops_bp = Blueprint("ai_ops", __name__)

@ai_ops_bp.route("/incident", methods=["POST"])
def report_incident():
    """Report a new incident and get AI classification."""
    data = request.get_json()
    description = data.get("description")
    
    if not description:
        return error_response("Missing incident description", 400)
        
    # Phase 6: AI Incident Management
    classification = classify_incident(description)
    
    incident = {
        "description": description,
        "classification": classification,
        "status": "Active"
    }
    
    return success_response(incident, "Incident reported and analyzed.")

@ai_ops_bp.route("/crowd/analyze", methods=["POST"])
def analyze_crowd():
    """Analyze current crowd data using AI."""
    data = request.get_json()
    zones = data.get("zones", [])
    
    if not zones:
        return error_response("No zone data provided", 400)
        
    # Phase 5: AI Crowd Intelligence
    analysis = analyze_crowd_data(zones)
    
    return success_response(analysis, "Crowd analysis complete.")

@ai_ops_bp.route("/volunteer/assign", methods=["POST"])
def assign_task():
    """Assign a task to a volunteer based on location."""
    data = request.get_json()
    location = data.get("location", "Unknown Location")
    
    # Phase 7: AI Volunteer Management
    assignment = assign_volunteer_task(location)
    
    return success_response(assignment, "Task assigned.")

@ai_ops_bp.route("/sustainability/optimize", methods=["POST"])
def optimize_sus():
    """Get AI sustainability recommendations."""
    data = request.get_json()
    metrics = data.get("metrics", {})
    
    # Phase 8: Sustainability
    optimization = optimize_sustainability(metrics)
    return success_response(optimization, "Sustainability optimized.")

@ai_ops_bp.route("/assistant/chat", methods=["POST"])
def chat():
    """Chat with the AI assistant."""
    data = request.get_json()
    query = data.get("query", "")
    context = data.get("context", {"occupancy": 45231, "status": "Event Active"})
    
    if not query:
        return error_response("Query missing", 400)
        
    # Phase 9: AI Assistant
    reply = ask_assistant(query, context)
    return success_response({"reply": reply}, "Chat response.")
