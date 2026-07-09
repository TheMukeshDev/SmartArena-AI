from flask import Blueprint, request, jsonify
from app.services.ai_service import AIService
from app.utils.response import success_response, error_response
from app.middleware.auth import require_auth
from app.models.schemas import (
    IncidentRequest, CrowdAnalyzeRequest, VolunteerAssignRequest,
    SustainabilityOptimizeRequest, ChatRequest
)
from pydantic import ValidationError

ai_ops_bp = Blueprint("ai_ops", __name__)

@ai_ops_bp.route("/incident", methods=["POST"])
@require_auth
async def report_incident():
    """Receive an incident description, classify with AI, and return action plan."""
    from flask import g
    try:
        data = IncidentRequest(**request.get_json())
    except ValidationError as e:
        return error_response(str(e.errors()), 400)
        
    classification = await AIService.process_incident(data.description, g.user["uid"])
    
    return success_response({
        "original_description": data.description,
        "classification": classification
    }, "Incident processed.")

@ai_ops_bp.route("/crowd/analyze", methods=["POST"])
@require_auth
async def analyze_crowd():
    """Analyze real-time crowd data and provide routing advice."""
    from flask import g
    try:
        data = CrowdAnalyzeRequest(**request.get_json())
    except ValidationError as e:
        return error_response(str(e.errors()), 400)
    
    analysis = await AIService.process_crowd_analysis(data.zones, g.user["uid"])
    
    return success_response(analysis, "Crowd analysis complete.")

@ai_ops_bp.route("/volunteer/assign", methods=["POST"])
@require_auth
async def assign_task():
    """Assign a task to a volunteer based on location."""
    from flask import g
    try:
        data = VolunteerAssignRequest(**request.get_json())
    except ValidationError as e:
        return error_response(str(e.errors()), 400)
    
    assignment = await AIService.process_volunteer_assignment(data.location, g.user["uid"])
    
    return success_response(assignment, "Task assigned.")

@ai_ops_bp.route("/sustainability/optimize", methods=["POST"])
@require_auth
async def optimize_sus():
    """Get AI sustainability recommendations."""
    from flask import g
    try:
        data = SustainabilityOptimizeRequest(**request.get_json())
    except ValidationError as e:
        return error_response(str(e.errors()), 400)
    
    optimization = await AIService.process_sustainability(data.metrics, g.user["uid"])
        
    return success_response(optimization, "Sustainability optimized.")

@ai_ops_bp.route("/assistant/chat", methods=["POST"])
@require_auth
async def chat():
    """Chat with the AI assistant."""
    try:
        data = ChatRequest(**request.get_json())
    except ValidationError as e:
        return error_response(str(e.errors()), 400)
        
    reply = await AIService.process_chat(data.query, data.context)
    return success_response({"reply": reply}, "Chat response.")
