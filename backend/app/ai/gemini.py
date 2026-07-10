"""Gemini AI integration module for SmartArena.

Provides functions for incident classification, crowd analysis,
volunteer task assignment, sustainability optimization, transport
suggestions, and a conversational assistant powered by Google Gemini.
"""

import json
import re
import logging
import threading
from google import genai
from flask import current_app
from app.config.prompts import (
    INCIDENT_PROMPT,
    CROWD_PROMPT,
    VOLUNTEER_PROMPT,
    SUSTAINABILITY_PROMPT,
    ASSISTANT_PROMPT,
    TRANSPORT_PROMPT,
)

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.5-flash"

PROMPT_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+(all\s+)?previous\s+(instructions|directions|prompts))"
    r"|(system:\s*(prompt|message|instruction))"
    r"|(you\s+are\s+now)"
    r"|(override\s+(your\s+)?instructions)"
    r"|(forget\s+(everything|all))"
    r"|(new\s+instructions?:)",
    re.IGNORECASE,
)

_client = None
_client_lock = threading.Lock()


def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """Sanitize and truncate user input, redacting prompt injections."""
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    text = text[:max_length]
    text = PROMPT_INJECTION_PATTERNS.sub("[REDACTED]", text)
    return text


def _get_client() -> genai.Client | None:
    """Return the Gemini API client, creating it lazily if needed."""
    global _client
    with _client_lock:
        if _client is None:
            api_key = current_app.config.get("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY is not set.")
                return None
            _client = genai.Client(api_key=api_key)
        return _client


def _call_gemini_json(prompt: str, fallback: dict, label: str) -> dict:
    """Call Gemini generate_content and parse the JSON response.

    Returns the fallback dict if the client is unavailable or any
    error occurs during the API call or JSON parsing.
    """
    client = _get_client()
    if not client:
        return fallback
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        text: str | None = response.text
        if not text:
            logger.error("Gemini %s returned empty response", label)
            return fallback
        return json.loads(text)
    except Exception as e:
        logger.error("Gemini %s failed: %s", label, str(e))
        return fallback


async def classify_incident(description: str) -> dict:
    """Classify an incident by category, priority, and action."""
    fallback = {
        "category": "General",
        "priority": "Medium",
        "action": "Dispatch staff to investigate.",
        "announcement": "",
    }
    safe_desc = sanitize_user_input(description)
    prompt = INCIDENT_PROMPT.format(description=safe_desc)
    return _call_gemini_json(prompt, fallback, "incident classification")


async def analyze_crowd_data(
    zones_data: list,
    history: list | None = None,
    weather: str = "Unknown",
) -> dict:
    """Analyze crowd zone data and return status and routing advice."""
    fallback = {
        "global_status": "Normal",
        "insights": ["Crowd flow is normal across most zones."],
        "routing_advice": "Proceed to designated gates.",
        "predicted_status_15min": {},
        "recommended_action": {
            "en": "Continue normal operations.",
            "es": "Continuar operaciones normales.",
            "fr": "Continuer les opérations normales.",
            "ar": "استمر في العمليات الطبيعية.",
            "hi": "सामान्य संचालन जारी रखें।",
        },
    }
    safe_data = json.dumps(zones_data, default=str)[:5000]
    history_str = json.dumps(history or [], default=str)[:3000]
    safe_weather = sanitize_user_input(str(weather), max_length=200)[:200]
    prompt = CROWD_PROMPT.format(
        data=safe_data, history=history_str, weather=safe_weather
    )
    return _call_gemini_json(prompt, fallback, "crowd analysis")


async def assign_volunteer_task(location: str) -> dict:
    """Assign a volunteer task for the given location."""
    fallback = {
        "task": "Monitor designated area",
        "priority": "Medium",
        "description": ("Keep an eye on the crowd flow and report any issues."),
    }
    safe_loc = sanitize_user_input(location)
    prompt = VOLUNTEER_PROMPT.format(location=safe_loc)
    return _call_gemini_json(prompt, fallback, "volunteer assignment")


async def optimize_sustainability(metrics: dict, weather: str = "Unknown") -> dict:
    """Optimize sustainability metrics and return recommendations."""
    fallback = {
        "status": "Optimization Failed",
        "recommendations": ["Dim stadium lights in empty zones to save power."],
    }
    safe_metrics = json.dumps(metrics, default=str)[:5000]
    safe_weather = sanitize_user_input(str(weather), max_length=200)[:200]
    prompt = SUSTAINABILITY_PROMPT.format(metrics=safe_metrics, weather=safe_weather)
    return _call_gemini_json(prompt, fallback, "sustainability")


async def ask_assistant(
    query: str,
    context: dict,
    language: str = "English",
    previous_interaction_id: str | None = None,
) -> tuple:
    """Query the conversational Gemini assistant."""
    client = _get_client()
    if not client:
        return "I am currently offline. Please try again later.", None

    safe_query = sanitize_user_input(query)
    sanitized_context = {
        k: sanitize_user_input(str(v), max_length=200) for k, v in context.items()
    }
    safe_context = json.dumps(sanitized_context, default=str)[:5000]
    prompt = ASSISTANT_PROMPT.format(
        context=safe_context, query=safe_query, language=language
    )

    try:
        interaction = client.interactions.create(  # type: ignore
            model=GEMINI_MODEL,
            input=prompt,
            previous_interaction_id=previous_interaction_id
            if previous_interaction_id
            else None,
        )
        return interaction.output_text.strip(), interaction.id  # type: ignore
    except Exception as e:
        logger.error("Gemini assistant failed: %s", str(e))
        return "I'm having trouble processing that right now.", None


async def suggest_transport(
    gate: str, arrival_time: str, weather: str = "Unknown"
) -> dict:
    """Suggest the best transport mode for a given gate and time."""
    fallback = {
        "recommended_mode": "Parking",
        "estimated_travel_time_minutes": 15,
        "directions": ("Proceed to the parking lot nearest to your gate."),
        "alternative": ("Consider rideshare drop-off at the main entrance."),
    }
    safe_gate = sanitize_user_input(gate)
    safe_time = sanitize_user_input(arrival_time)
    safe_weather = sanitize_user_input(str(weather), max_length=200)[:200]
    prompt = TRANSPORT_PROMPT.format(
        gate=safe_gate, arrival_time=safe_time, weather=safe_weather
    )
    return _call_gemini_json(prompt, fallback, "transport suggestion")
