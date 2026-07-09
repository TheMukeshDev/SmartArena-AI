import os
import datetime
import logging
import redis
from app.config.firebase import get_firestore_client
from app.ai.gemini import (
    classify_incident,
    analyze_crowd_data,
    assign_volunteer_task,
    optimize_sustainability,
    ask_assistant
)

logger = logging.getLogger(__name__)

# Initialize Redis for semantic caching
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url) if redis_url else None
_in_memory_cache = {}

class AIService:
    @staticmethod
    async def process_incident(description: str, uid: str) -> dict:
        classification = await classify_incident(description)
        db = get_firestore_client()
        if db:
            db.collection("incidents").add({
                "description": description,
                "classification": classification,
                "reporter_uid": uid,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
        return classification

    @staticmethod
    async def process_crowd_analysis(zones: list, uid: str) -> dict:
        analysis = await analyze_crowd_data(zones)
        db = get_firestore_client()
        if db:
            db.collection("crowd_data").add({
                "zones": zones,
                "analysis": analysis,
                "requested_by": uid,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
        return analysis

    @staticmethod
    async def process_volunteer_assignment(location: str, uid: str) -> dict:
        assignment = await assign_volunteer_task(location)
        db = get_firestore_client()
        if db:
            db.collection("volunteers").document(uid).set({
                "current_location": location,
                "current_task": assignment,
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }, merge=True)
        return assignment

    @staticmethod
    async def process_sustainability(metrics: dict, uid: str) -> dict:
        optimization = await optimize_sustainability(metrics)
        db = get_firestore_client()
        if db:
            db.collection("sustainability").add({
                "metrics": metrics,
                "optimization": optimization,
                "requested_by": uid,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
        return optimization
        
    @staticmethod
    async def process_chat(query: str, context: dict) -> str:
        cache_key = f"chat:{query.strip().lower()}_{hash(frozenset(context.items()))}"
        
        # Try Redis first
        if redis_client:
            try:
                cached = redis_client.get(cache_key)
                if cached:
                    return cached.decode('utf-8')
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        # Fallback to in-memory
        elif cache_key in _in_memory_cache:
            return _in_memory_cache[cache_key]
            
        reply = await ask_assistant(query, context)
        
        if redis_client:
            try:
                redis_client.setex(cache_key, 3600, reply) # Cache for 1 hour
            except Exception as e:
                logger.warning(f"Redis cache set error: {e}")
        else:
            _in_memory_cache[cache_key] = reply
            
        return reply
