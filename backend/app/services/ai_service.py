import os
import hashlib
import json
import datetime
import logging

from app.config.firebase import get_firestore_client
from app.services.cache import SQLiteCache
from app.services.weather import fetch_weather
from app.ai.gemini import (
    classify_incident,
    analyze_crowd_data,
    assign_volunteer_task,
    optimize_sustainability,
    ask_assistant,
    suggest_transport,
)

logger = logging.getLogger(__name__)

_cache = SQLiteCache(
    db_path=os.getenv("CACHE_DB_PATH", "cache.db"),
    ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
)

CROWD_HISTORY_MAX = 6
_crowd_history: list[dict] = []


def _cache_key(query: str, context: dict, language: str = "en") -> str:
    context_hash = hashlib.sha256(
        json.dumps(context, sort_keys=True, default=str).encode()
    ).hexdigest()
    return f"chat:{query.strip().lower()}_{language}_{context_hash}"


class AIService:
    @staticmethod
    async def process_incident(description: str, uid: str) -> dict:
        classification = await classify_incident(description)
        db = get_firestore_client()
        if db:
            doc_ref = db.collection("incidents").add(
                {
                    "description": description,
                    "classification": classification,
                    "reporter_uid": uid,
                    "timestamp": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                }
            )
            try:
                from app.routes.events import push_incident

                push_incident(
                    {
                        "description": description,
                        "classification": classification,
                        "reporter_uid": uid,
                        "doc_id": (
                            doc_ref[1].id if hasattr(doc_ref, "__len__") else None
                        ),
                    }
                )
            except Exception:
                logger.warning("Failed to push SSE incident", exc_info=True)
        return classification

    @staticmethod
    async def process_crowd_analysis(zones: list, uid: str) -> dict:
        history_snapshot = {
            "zones": zones,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        _crowd_history.append(history_snapshot)
        if len(_crowd_history) > CROWD_HISTORY_MAX:
            _crowd_history.pop(0)

        weather = await fetch_weather()
        weather_str = weather.summary if weather else "Unknown"
        analysis = await analyze_crowd_data(
            zones, history=list(_crowd_history), weather=weather_str
        )
        db = get_firestore_client()
        if db:
            db.collection("crowd_data").add(
                {
                    "zones": zones,
                    "analysis": analysis,
                    "requested_by": uid,
                    "timestamp": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                }
            )
        return analysis

    @staticmethod
    async def process_volunteer_assignment(location: str, uid: str) -> dict:
        assignment = await assign_volunteer_task(location)
        db = get_firestore_client()
        if db:
            db.collection("volunteers").document(uid).set(
                {
                    "current_location": location,
                    "current_task": assignment,
                    "updated_at": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                },
                merge=True,
            )
        return assignment

    @staticmethod
    async def process_sustainability(metrics: dict, uid: str) -> dict:
        weather = await fetch_weather()
        weather_str = weather.summary if weather else "Unknown"
        optimization = await optimize_sustainability(metrics, weather=weather_str)
        db = get_firestore_client()
        if db:
            db.collection("sustainability").add(
                {
                    "metrics": metrics,
                    "optimization": optimization,
                    "requested_by": uid,
                    "timestamp": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                }
            )
        return optimization

    @staticmethod
    async def process_chat(
        query: str,
        context: dict,
        language: str = "en",
        previous_interaction_id: str = None,
    ) -> tuple:
        lang_name = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "ar": "Arabic",
        }.get(language, "English")
        key = _cache_key(query, context, language)
        cached = _cache.get(key)
        if (
            cached is not None and not previous_interaction_id
        ):  # Only use cache for new interactions
            return cached, None

        reply, interaction_id = await ask_assistant(
            query,
            context,
            language=lang_name,
            previous_interaction_id=previous_interaction_id,
        )
        if not previous_interaction_id:
            _cache.set(key, reply)
        return reply, interaction_id

    @staticmethod
    async def process_transport_suggestion(gate: str, arrival_time: str) -> dict:
        weather = await fetch_weather()
        weather_str = weather.summary if weather else "Unknown"
        return await suggest_transport(gate, arrival_time, weather=weather_str)
