import asyncio
from flask import Blueprint, request
from app.services.ai_service import AIService
from app.services.navigation import (
    ZONE_ADJACENCY,
    SENSORY_FRIENDLY_ZONES,
    find_path,
    find_accessible_path,
    get_navigation_context,
)
from app.services.weather import fetch_weather
from app.utils.response import success_response, error_response
from app.middleware.auth import require_auth
from app.models.schemas import (
    IncidentRequest,
    CrowdAnalyzeRequest,
    VolunteerAssignRequest,
    SustainabilityOptimizeRequest,
    ChatRequest,
    TransportSuggestRequest,
)
from pydantic import ValidationError

ai_ops_bp = Blueprint("ai_ops", __name__)


def _run(coro):
    return asyncio.run(coro)


@ai_ops_bp.route("/incident", methods=["POST"])
@require_auth
def report_incident():
    from flask import g

    try:
        data = IncidentRequest(**request.get_json())
    except ValidationError as e:
        return error_response(message=str(e.errors()), status_code=400)

    classification = _run(AIService.process_incident(data.description, g.user["uid"]))

    return success_response(
        {"original_description": data.description, "classification": classification},
        "Incident processed.",
    )


@ai_ops_bp.route("/crowd/analyze", methods=["POST"])
@require_auth
def analyze_crowd():
    from flask import g

    try:
        data = CrowdAnalyzeRequest(**request.get_json())
    except ValidationError as e:
        return error_response(message=str(e.errors()), status_code=400)

    analysis = _run(AIService.process_crowd_analysis(data.zones, g.user["uid"]))

    return success_response(analysis, "Crowd analysis complete.")


@ai_ops_bp.route("/volunteer/assign", methods=["POST"])
@require_auth
def assign_task():
    from flask import g

    try:
        data = VolunteerAssignRequest(**request.get_json())
    except ValidationError as e:
        return error_response(message=str(e.errors()), status_code=400)

    assignment = _run(
        AIService.process_volunteer_assignment(data.location, g.user["uid"])
    )

    return success_response(assignment, "Task assigned.")


@ai_ops_bp.route("/sustainability/optimize", methods=["POST"])
@require_auth
def optimize_sus():
    from flask import g

    try:
        data = SustainabilityOptimizeRequest(**request.get_json())
    except ValidationError as e:
        return error_response(message=str(e.errors()), status_code=400)

    optimization = _run(AIService.process_sustainability(data.metrics, g.user["uid"]))

    return success_response(optimization, "Sustainability optimized.")


@ai_ops_bp.route("/assistant/chat", methods=["POST"])
@require_auth
def chat():
    try:
        data = ChatRequest(**request.get_json())
    except ValidationError as e:
        return error_response(message=str(e.errors()), status_code=400)

    enhanced_context = {
        **data.context,
        **get_navigation_context(data.context.get("current_zone")),
    }
    reply, interaction_id = _run(
        AIService.process_chat(
            data.query,
            enhanced_context,
            language=data.preferred_language,
            previous_interaction_id=data.previous_interaction_id,
        )
    )
    return success_response(
        {"reply": reply, "interaction_id": interaction_id}, "Chat response."
    )


@ai_ops_bp.route("/transport/suggest", methods=["POST"])
@require_auth
def transport_suggest():
    try:
        data = TransportSuggestRequest(**request.get_json())
    except ValidationError as e:
        return error_response(message=str(e.errors()), status_code=400)

    suggestion = _run(
        AIService.process_transport_suggestion(data.gate, data.arrival_time)
    )
    return success_response(suggestion, "Transport suggestion ready.")


@ai_ops_bp.route("/navigation/zones", methods=["GET"])
@require_auth
def get_zones():
    return success_response(
        {
            "zones": list(ZONE_ADJACENCY.keys()),
            "adjacency": ZONE_ADJACENCY,
            "sensory_friendly_zones": list(SENSORY_FRIENDLY_ZONES),
        },
        "Zone map retrieved.",
    )


@ai_ops_bp.route("/navigation/path", methods=["GET"])
@require_auth
def get_path():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    if not start or not end:
        return error_response(
            message="start and end query parameters required.", status_code=400
        )
    path = find_path(start, end)
    if not path:
        return error_response(
            message=f"No path found between '{start}' and '{end}'.", status_code=404
        )
    return success_response({"path": path, "start": start, "end": end}, "Path found.")


@ai_ops_bp.route("/weather", methods=["GET"])
@require_auth
def get_weather():
    w = _run(fetch_weather())
    if not w:
        return error_response(message="Weather data unavailable.", status_code=503)
    return success_response(
        {
            "temperature_c": w.temperature_c,
            "precipitation_mm": w.precipitation_mm,
            "wind_speed_kmh": w.wind_speed_kmh,
            "weather_code": w.weather_code,
            "summary": w.summary,
            "operational_note": w.operational_note,
        },
        "Weather data fetched.",
    )


@ai_ops_bp.route("/navigation/path/accessible", methods=["GET"])
@require_auth
def get_accessible_path():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    if not start or not end:
        return error_response(
            message="start and end query parameters required.", status_code=400
        )
    path = find_accessible_path(start, end)
    if not path:
        return error_response(
            message=f"No accessible path found between '{start}' and '{end}'.",
            status_code=404,
        )
    return success_response(
        {"path": path, "start": start, "end": end}, "Accessible path found."
    )
