import json
import logging
import google.generativeai as genai
from flask import current_app
from app.config.prompts import (
    INCIDENT_PROMPT, CROWD_PROMPT, VOLUNTEER_PROMPT, 
    SUSTAINABILITY_PROMPT, ASSISTANT_PROMPT
)

logger = logging.getLogger(__name__)

def _init_gemini():
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set.")
        return False
    genai.configure(api_key=api_key)
    return True

async def classify_incident(description: str) -> dict:
    """Classifies an incident using Gemini asynchronously."""
    fallback = {
        "category": "General",
        "priority": "Medium",
        "action": "Dispatch staff to investigate.",
        "announcement": ""
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = INCIDENT_PROMPT.format(description=description)
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini incident classification failed: %s", str(e))
        return fallback

async def analyze_crowd_data(zones_data: list) -> dict:
    """Generates crowd routing and congestion predictions asynchronously."""
    fallback = {
        "global_status": "Normal",
        "insights": ["Crowd flow is normal across most zones."],
        "routing_advice": "Proceed to designated gates."
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = CROWD_PROMPT.format(data=json.dumps(zones_data))
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini crowd analysis failed: %s", str(e))
        return fallback

async def assign_volunteer_task(location: str) -> dict:
    """Generates an optimal task for a volunteer based on their location asynchronously."""
    fallback = {
        "task": "Monitor designated area",
        "priority": "Medium",
        "description": "Keep an eye on the crowd flow and report any issues."
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = VOLUNTEER_PROMPT.format(location=location)
    
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini volunteer assignment failed: %s", str(e))
        return fallback

async def optimize_sustainability(metrics: dict) -> dict:
    """Provides AI recommendations for reducing energy/water usage asynchronously."""
    fallback = {
        "status": "Optimization Failed",
        "recommendations": ["Dim stadium lights in empty zones to save power."]
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = SUSTAINABILITY_PROMPT.format(metrics=json.dumps(metrics))
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini sustainability failed: %s", str(e))
        return fallback

async def ask_assistant(query: str, context: dict) -> str:
    """Answers a natural language query about the stadium asynchronously."""
    if not _init_gemini():
        return "I am currently offline. Please try again later."
        
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = ASSISTANT_PROMPT.format(context=json.dumps(context), query=query)
    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error("Gemini assistant failed: %s", str(e))
        return "I'm having trouble processing that right now."
