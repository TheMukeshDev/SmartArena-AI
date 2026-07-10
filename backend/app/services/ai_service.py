"""AI service layer for SmartArena.

Provides high-level wrappers around Gemini-based AI capabilities for incident
classification, crowd analysis, volunteer assignment, sustainability
optimisation, chat interaction, and transport suggestions. Results are
optionally persisted to Firestore and served through a local SQLite cache.
"""

import datetime
import hashlib
import json
import logging
import os
import threading
from typing import Any

from app.ai.gemini import (
    ask_assistant,
    analyze_crowd_data,
    assign_volunteer_task,
    classify_incident,
    optimize_sustainability,
    suggest_transport,
)
from app.config.firebase import get_firestore_client
from app.services.cache import SQLiteCache
from app.services.weather import fetch_weather

logger = logging.getLogger(__name__)

_cache = SQLiteCache(
    db_path=os.getenv("CACHE_DB_PATH", "cache.db"),
    ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
)

CROWD_HISTORY_MAX = 6
_crowd_history: list[dict[str, Any]] = []
_crowd_history_lock = threading.Lock()


def _cache_key(query: str, context: dict[str, Any], language: str = "en") -> str:
    """Return a deterministic cache key derived from *query*, *context* and *language*."""
    context_hash = hashlib.sha256(
        json.dumps(context, sort_keys=True, default=str).encode()
    ).hexdigest()
    return f"chat:{query.strip().lower()}_{language}_{context_hash}"


class AIService:
    """Stateless facade that delegates AI work to specialised Gemini helpers."""

    @staticmethod
    async def process_incident(description: str, uid: str) -> dict[str, Any]:
        """Classify an incident report and persist it to Firestore.

        Args:
            description: Free-text description of the incident.
            uid: UID of the user reporting the incident.

        Returns:
            Classification dict produced by :func:`classify_incident`.
        """
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
    async def process_crowd_analysis(
        zones: list[dict[str, Any]], uid: str
    ) -> dict[str, Any]:
        """Analyse crowd density across *zones* with historical context.

        Maintains a ring buffer of recent snapshots (up to
        :data:`CROWD_HISTORY_MAX`) protected by a threading lock so that
        concurrent requests remain consistent.

        Args:
            zones: List of zone descriptors to analyse.
            uid: UID of the user requesting the analysis.

        Returns:
            Crowd analysis dict produced by :func:`analyze_crowd_data`.
        """
        history_snapshot: dict[str, Any] = {
            "zones": zones,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        with _crowd_history_lock:
            _crowd_history.append(history_snapshot)
            if len(_crowd_history) > CROWD_HISTORY_MAX:
                _crowd_history.pop(0)
            history_copy = list(_crowd_history)

        weather = await fetch_weather()
        weather_str: str = weather.summary if weather else "Unknown"
        analysis = await analyze_crowd_data(
            zones, history=history_copy, weather=weather_str
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
    async def process_volunteer_assignment(location: str, uid: str) -> dict[str, Any]:
        """Assign a volunteer task at *location* and record it in Firestore.

        Args:
            location: Current location of the volunteer.
            uid: UID of the volunteer.

        Returns:
            Assignment dict produced by :func:`assign_volunteer_task`.
        """
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
    async def process_sustainability(
        metrics: dict[str, Any], uid: str
    ) -> dict[str, Any]:
        """Compute sustainability optimisation recommendations.

        Args:
            metrics: Current sustainability metrics.
            uid: UID of the requesting user.

        Returns:
            Optimisation dict produced by :func:`optimize_sustainability`.
        """
        weather = await fetch_weather()
        weather_str: str = weather.summary if weather else "Unknown"
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
        context: dict[str, Any],
        language: str = "en",
        previous_interaction_id: str | None = None,
    ) -> tuple[str | None, str | None]:
        """Send a chat query to the assistant, using cache when possible.

        Caching is only applied for brand-new interactions (i.e. when
        *previous_interaction_id* is ``None``).

        Args:
            query: The user's chat message.
            context: Conversation context / metadata.
            language: ISO-639-1 language code (default ``"en"``).
            previous_interaction_id: Optional ID of a prior interaction to
                continue.

        Returns:
            A ``(reply, interaction_id)`` tuple.
        """
        lang_name: str = {
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
    async def process_transport_suggestion(
        gate: str, arrival_time: str
    ) -> dict[str, Any]:
        """Suggest transport options for a given gate and arrival time.

        Args:
            gate: Gate identifier at the venue.
            arrival_time: Planned arrival time string.

        Returns:
            Transport suggestion dict produced by :func:`suggest_transport`.
        """
        weather = await fetch_weather()
        weather_str: str = weather.summary if weather else "Unknown"
        return await suggest_transport(gate, arrival_time, weather=weather_str)
