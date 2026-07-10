import json
import re
import logging
import google.generativeai as genai
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


def _init_gemini():
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set.")
        return False
    genai.configure(api_key=api_key)
    return True


async def classify_incident(description: str) -> dict:
    fallback = {
        "category": "General",
        "priority": "Medium",
        "action": "Dispatch staff to investigate.",
        "announcement": "",
    }

    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel("gemini-1.5-flash")
    safe_desc = sanitize_user_input(description)
    prompt = INCIDENT_PROMPT.format(description=safe_desc)

    try:
        response = await model.generate_content_async(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini incident classification failed: %s", str(e))
        return fallback


async def analyze_crowd_data(zones_data: list) -> dict:
    fallback = {
        "global_status": "Normal",
        "insights": ["Crowd flow is normal across most zones."],
        "routing_advice": "Proceed to designated gates.",
    }

    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel("gemini-1.5-flash")
    safe_data = json.dumps(zones_data, default=str)[:5000]
    prompt = CROWD_PROMPT.format(data=safe_data)

    try:
        response = await model.generate_content_async(
            prompt, generation_config={"response_mime_type": "application/json"}
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

    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel("gemini-1.5-flash")
    safe_loc = sanitize_user_input(location)
    prompt = VOLUNTEER_PROMPT.format(location=safe_loc)

    try:
        response = await model.generate_content_async(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini volunteer assignment failed: %s", str(e))
        return fallback


async def optimize_sustainability(metrics: dict) -> dict:
    fallback = {
        "status": "Optimization Failed",
        "recommendations": ["Dim stadium lights in empty zones to save power."],
    }

    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel("gemini-1.5-flash")
    safe_metrics = json.dumps(metrics, default=str)[:5000]
    prompt = SUSTAINABILITY_PROMPT.format(metrics=safe_metrics)

    try:
        response = await model.generate_content_async(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini sustainability failed: %s", str(e))
        return fallback


async def ask_assistant(query: str, context: dict, language: str = "English") -> str:
    if not _init_gemini():
        return "I am currently offline. Please try again later."

    model = genai.GenerativeModel("gemini-1.5-flash")
    safe_query = sanitize_user_input(query)
    safe_context = json.dumps(context, default=str)[:5000]
    prompt = ASSISTANT_PROMPT.format(
        context=safe_context, query=safe_query, language=language
    )

    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error("Gemini assistant failed: %s", str(e))
        return "I'm having trouble processing that right now."


async def suggest_transport(gate: str, arrival_time: str) -> dict:
    fallback = {
        "recommended_mode": "Parking",
        "estimated_travel_time_minutes": 15,
        "directions": "Proceed to the parking lot nearest to your gate.",
        "alternative": "Consider rideshare drop-off at the main entrance.",
    }

    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel("gemini-1.5-flash")
    safe_gate = sanitize_user_input(gate)
    safe_time = sanitize_user_input(arrival_time)
    prompt = TRANSPORT_PROMPT.format(gate=safe_gate, arrival_time=safe_time)

    try:
        response = await model.generate_content_async(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini transport suggestion failed: %s", str(e))
        return fallback
