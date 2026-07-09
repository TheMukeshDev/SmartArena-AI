import json
import logging
import google.generativeai as genai
from flask import current_app

logger = logging.getLogger(__name__)

def _init_gemini():
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set.")
        return False
    genai.configure(api_key=api_key)
    return True

def classify_incident(description: str) -> dict:
    """Classifies an incident using Gemini."""
    fallback = {
        "category": "General",
        "priority": "Medium",
        "action": "Dispatch staff to investigate.",
        "announcement": ""
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are an AI Incident Manager for a smart stadium.
    Analyze the following incident report and respond ONLY with a raw JSON object containing these keys:
    - "category": (Choose one: Medical, Security, Maintenance, Crowd Control, General)
    - "priority": (Choose one: Low, Medium, High, Critical)
    - "action": (A brief 1-sentence action plan for volunteers/staff)
    - "announcement": (A brief public announcement text if necessary, or an empty string)
    
    Incident: "{description}"
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini incident classification failed: %s", str(e))
        return fallback

def analyze_crowd_data(zones_data: list) -> dict:
    """Generates crowd routing and congestion predictions."""
    fallback = {
        "global_status": "Normal",
        "insights": ["Crowd flow is normal across most zones."],
        "routing_advice": "Proceed to designated gates."
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are the AI Crowd Intelligence system for a smart stadium.
    Analyze the following real-time zone data and respond ONLY with a raw JSON object containing:
    - "global_status": (Choose one: Optimal, Moderate, Congested, Critical)
    - "insights": (A list of 2 short insights about bottlenecks or anomalies)
    - "routing_advice": (1 short sentence of advice on which gates to route incoming fans to)
    
    Data: {json.dumps(zones_data)}
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini crowd analysis failed: %s", str(e))
        return fallback

def assign_volunteer_task(location: str) -> dict:
    """Generates an optimal task for a volunteer based on their location."""
    fallback = {
        "task": "Monitor designated area",
        "priority": "Medium",
        "description": "Keep an eye on the crowd flow and report any issues."
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are an AI Volunteer Coordinator for a smart stadium.
    A volunteer is currently located at: "{location}".
    Assign them a highly specific, realistic task based on potential needs in that area (e.g. crowd control, ticketing, directing, spills, VIP escort).
    Respond ONLY with a raw JSON object containing:
    - "task": (A short title of the task)
    - "priority": (Low, Medium, High, Critical)
    - "description": (1 sentence explaining what they need to do)
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini volunteer assignment failed: %s", str(e))
        return fallback

def optimize_sustainability(metrics: dict) -> dict:
    """Provides AI recommendations for reducing energy/water usage."""
    fallback = {
        "status": "Optimization Failed",
        "recommendations": ["Dim stadium lights in empty zones to save power."]
    }
    
    if not _init_gemini():
        return fallback

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are an AI Sustainability Engine for a smart stadium.
    Analyze the current usage metrics: {json.dumps(metrics)}
    Respond ONLY with a raw JSON object containing:
    - "status": (A brief summary of current efficiency, e.g. "Energy Spike Detected")
    - "recommendations": (A list of 2 actionable steps to reduce carbon footprint right now)
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error("Gemini sustainability failed: %s", str(e))
        return fallback

def ask_assistant(query: str, context: dict) -> str:
    """Answers a natural language query about the stadium."""
    if not _init_gemini():
        return "I am currently offline. Please try again later."
        
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are 'ArenaBot', the highly intelligent AI assistant for SmartArena AI.
    Answer the user's question concisely based on the following real-time stadium context (if relevant). If the context doesn't have the answer, use your best judgement or ask for clarification. Keep answers under 3 sentences.
    
    Context: {json.dumps(context)}
    
    User Query: "{query}"
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error("Gemini assistant failed: %s", str(e))
        return "I'm having trouble processing that right now."
