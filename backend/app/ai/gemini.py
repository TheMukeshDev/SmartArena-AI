import json
import re
import logging
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

PROMPT_INJECTION_PATTERNS = re.compile(
    r"(ignore\s+(all\s+)?previous\s+(instructions|directions|prompts))"
    r"|(system:\s*(prompt|message|instruction))"
    r"|(you\s+are\s+now)"
    r"|(override\s+(your\s+)?instructions)"
    r"|(forget\s+(everything|all))"
    r"|(new\s+instructions?:)",
    re.IGNORECASE,
)


def sanitize_user_input(text: str, max_length: int = 500) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = text.strip()
    text = text[:max_length]
    text = PROMPT_INJECTION_PATTERNS.sub("[REDACTED]", text)
    return text


_client = None

def _get_client():
    global _client
    if _client is None:
        api_key = current_app.config.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set.")
            return None
        _client = genai.Client(api_key=api_key)
    return _client


async def classify_incident(description: str) -> dict:
    fallback = {
        "category": "General",
        "priority": "Medium",
        "action": "Dispatch staff to investigate.",
        "announcement": "",
    }
    client = _get_client()
    if not client:
        return fallback

    safe_desc = sanitize_user_input(description)
    prompt = INCIDENT_PROMPT.format(description=safe_desc)

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini incident classification failed: %s", str(e))
        return fallback


async def analyze_crowd_data(
    zones_data: list, history: list | None = None, weather: str = "Unknown"
) -> dict:
    fallback = {
        "global_status": "Normal",
        "insights": ["Crowd flow is normal across most zones."],
        "routing_advice": "Proceed to designated gates.",
        "predicted_status_15min": {},
        "recommended_action": "Continue normal operations.",
    }
    client = _get_client()
    if not client:
        return fallback

    safe_data = json.dumps(zones_data, default=str)[:5000]
    history_str = json.dumps(history or [], default=str)[:3000]
    safe_weather = sanitize_user_input(str(weather), max_length=200)[:200]
    prompt = CROWD_PROMPT.format(
        data=safe_data, history=history_str, weather=safe_weather
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini crowd analysis failed: %s", str(e))
        return fallback


async def assign_volunteer_task(location: str) -> dict:
    fallback = {
        "task": "Monitor designated area",
        "priority": "Medium",
        "description": "Keep an eye on the crowd flow and report any issues.",
    }
    client = _get_client()
    if not client:
        return fallback

    safe_loc = sanitize_user_input(location)
    prompt = VOLUNTEER_PROMPT.format(location=safe_loc)

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini volunteer assignment failed: %s", str(e))
        return fallback


async def optimize_sustainability(metrics: dict, weather: str = "Unknown") -> dict:
    fallback = {
        "status": "Optimization Failed",
        "recommendations": ["Dim stadium lights in empty zones to save power."],
    }
    client = _get_client()
    if not client:
        return fallback

    safe_metrics = json.dumps(metrics, default=str)[:5000]
    safe_weather = sanitize_user_input(str(weather), max_length=200)[:200]
    prompt = SUSTAINABILITY_PROMPT.format(metrics=safe_metrics, weather=safe_weather)

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini sustainability failed: %s", str(e))
        return fallback


async def ask_assistant(query: str, context: dict, language: str = "English", previous_interaction_id: str = None) -> tuple:
    client = _get_client()
    if not client:
        return "I am currently offline. Please try again later.", None

    safe_query = sanitize_user_input(query)
    safe_context = json.dumps(context, default=str)[:5000]
    prompt = ASSISTANT_PROMPT.format(
        context=safe_context, query=safe_query, language=language
    )

    try:
        kwargs = {
            "model": "gemini-3.5-flash",
            "input": prompt
        }
        if previous_interaction_id:
            kwargs["previous_interaction_id"] = previous_interaction_id
            
        interaction = client.interactions.create(**kwargs)
        return interaction.output_text.strip(), interaction.id
    except Exception as e:
        logger.error("Gemini assistant failed: %s", str(e))
        return "I'm having trouble processing that right now.", None


async def suggest_transport(
    gate: str, arrival_time: str, weather: str = "Unknown"
) -> dict:
    fallback = {
        "recommended_mode": "Parking",
        "estimated_travel_time_minutes": 15,
        "directions": "Proceed to the parking lot nearest to your gate.",
        "alternative": "Consider rideshare drop-off at the main entrance.",
    }
    client = _get_client()
    if not client:
        return fallback

    safe_gate = sanitize_user_input(gate)
    safe_time = sanitize_user_input(arrival_time)
    safe_weather = sanitize_user_input(str(weather), max_length=200)[:200]
    prompt = TRANSPORT_PROMPT.format(
        gate=safe_gate, arrival_time=safe_time, weather=safe_weather
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini transport suggestion failed: %s", str(e))
        return fallback
