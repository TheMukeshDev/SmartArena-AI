import datetime
import logging
from app.config.firebase import get_firestore_client
from app.ai.gemini import (
    classify_incident,
    analyze_crowd_data,
    assign_volunteer_task,
    optimize_sustainability,
    ask_assistant
)

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def process_incident(description: str, uid: str) -> dict:
        classification = classify_incident(description)
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
    def process_crowd_analysis(zones: list, uid: str) -> dict:
        analysis = analyze_crowd_data(zones)
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
    def process_volunteer_assignment(location: str, uid: str) -> dict:
        assignment = assign_volunteer_task(location)
        db = get_firestore_client()
        if db:
            db.collection("volunteers").document(uid).set({
                "current_location": location,
                "current_task": assignment,
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }, merge=True)
        return assignment

    @staticmethod
    def process_sustainability(metrics: dict, uid: str) -> dict:
        optimization = optimize_sustainability(metrics)
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
    def process_chat(query: str, context: dict) -> str:
        # Chat responses typically aren't persisted unless we want chat history
        return ask_assistant(query, context)
