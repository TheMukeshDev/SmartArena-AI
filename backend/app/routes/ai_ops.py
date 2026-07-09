from flask import Blueprint, request, jsonify
from app.services.ai_service import AIService
from app.utils.response import success_response, error_response
from app.middleware.auth import require_auth

ai_ops_bp = Blueprint("ai_ops", __name__)

@ai_ops_bp.route("/incident", methods=["POST"])
@require_auth
def report_incident():
    """Receive an incident description, classify with AI, and return action plan."""
    from flask import g
    data = request.get_json()
    desc = data.get("description", "")
    
    if not desc:
        return error_response("Description is required", 400)
        
    classification = AIService.process_incident(desc, g.user["uid"])
    
    return success_response({
        "original_description": desc,
        "classification": classification
    }, "Incident processed.")

@ai_ops_bp.route("/crowd/analyze", methods=["POST"])
@require_auth
def analyze_crowd():
    """Analyze real-time crowd data and provide routing advice."""
    from flask import g
    data = request.get_json()
    zones = data.get("zones", [])
    
    analysis = AIService.process_crowd_analysis(zones, g.user["uid"])
    
    return success_response(analysis, "Crowd analysis complete.")

@ai_ops_bp.route("/volunteer/assign", methods=["POST"])
@require_auth
def assign_task():
    """Assign a task to a volunteer based on location."""
    from flask import g
    data = request.get_json()
    location = data.get("location", "Unknown Location")
    
    assignment = AIService.process_volunteer_assignment(location, g.user["uid"])
    
    return success_response(assignment, "Task assigned.")

@ai_ops_bp.route("/sustainability/optimize", methods=["POST"])
@require_auth
def optimize_sus():
    """Get AI sustainability recommendations."""
    from flask import g
    data = request.get_json()
    metrics = data.get("metrics", {})
    
    optimization = AIService.process_sustainability(metrics, g.user["uid"])
        
    return success_response(optimization, "Sustainability optimized.")

@ai_ops_bp.route("/assistant/chat", methods=["POST"])
@require_auth
def chat():
    """Chat with the AI assistant."""
    data = request.get_json()
    query = data.get("query", "")
    context = data.get("context", {"occupancy": 45231, "status": "Event Active"})
    
    if not query:
        return error_response("Query missing", 400)
        
    reply = AIService.process_chat(query, context)
    return success_response({"reply": reply}, "Chat response.")
