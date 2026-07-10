"""
SmartArena AI — Admin Routes
==============================

Admin-only endpoints for gate management, announcements,
security logs, and user management.
"""

import datetime
import logging

from flask import Blueprint, request, g
from pydantic import BaseModel, Field
from typing import Optional

from app.middleware.auth import require_auth, require_role
from app.utils.response import success_response, error_response
from app.config.firebase import get_firestore_client
from app.services.navigation import ZONE_ADJACENCY

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


class GateUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Gate name.")
    status: str = Field(
        default="open",
        description="Gate status: open, closed, maintenance.",
    )
    capacity: Optional[int] = Field(
        default=None, ge=0, description="Gate capacity limit."
    )


class AnnouncementRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    priority: str = Field(default="normal", description="normal or urgent")
    target_zones: list[str] = Field(
        default_factory=list, description="Zones to target, empty = all."
    )


def _get_db():
    return get_firestore_client()


# ── Gate Management ──────────────────────────────────────────────────────────


@admin_bp.route("/gates", methods=["GET"])
@require_auth
@require_role(["admin"])
def list_gates():
    db = _get_db()
    gates = []

    gate_zones = [z for z in ZONE_ADJACENCY if z.startswith("Gate")]

    if db:
        docs = db.collection("gates").stream()
        stored = {doc.id: doc.to_dict() for doc in docs}
        for gz in gate_zones:
            data = stored.get(gz, {})
            gates.append(
                {
                    "name": gz,
                    "status": data.get("status", "open"),
                    "capacity": data.get("capacity", 5000),
                    "current_count": data.get("current_count", 0),
                }
            )
    else:
        for gz in gate_zones:
            gates.append(
                {
                    "name": gz,
                    "status": "open",
                    "capacity": 5000,
                    "current_count": 0,
                }
            )

    return success_response({"gates": gates}, "Gates retrieved.")


@admin_bp.route("/gates", methods=["POST"])
@require_auth
@require_role(["admin"])
def update_gate():
    try:
        data = GateUpdateRequest(**request.get_json())
    except Exception as e:
        return error_response(str(e), status_code=400)

    db = _get_db()
    if not db:
        return error_response("Database unavailable", status_code=503)

    gate_ref = db.collection("gates").document(data.name)
    gate_ref.set(
        {
            "name": data.name,
            "status": data.status,
            "capacity": data.capacity,
            "updated_at": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        },
        merge=True,
    )

    _log_security_event(
        "gate_update",
        f"Gate '{data.name}' status changed to '{data.status}'",
        g.user["uid"],
    )

    return success_response(
        {"name": data.name, "status": data.status},
        f"Gate '{data.name}' updated.",
    )


# ── Announcements ────────────────────────────────────────────────────────────


@admin_bp.route("/announcements", methods=["GET"])
@require_auth
@require_role(["admin"])
def list_announcements():
    db = _get_db()
    announcements = []

    if db:
        docs = (
            db.collection("announcements")
            .order_by("created_at", direction="DESCENDING")
            .limit(50)
            .stream()
        )
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            announcements.append(data)

    return success_response(
        {"announcements": announcements}, "Announcements retrieved."
    )


@admin_bp.route("/announcements", methods=["POST"])
@require_auth
@require_role(["admin"])
def create_announcement():
    try:
        data = AnnouncementRequest(**request.get_json())
    except Exception as e:
        return error_response(str(e), status_code=400)

    db = _get_db()
    if not db:
        return error_response("Database unavailable", status_code=503)

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_ref = db.collection("announcements").document()
    doc_ref.set(
        {
            "title": data.title,
            "message": data.message,
            "priority": data.priority,
            "target_zones": data.target_zones,
            "created_by": g.user["uid"],
            "created_at": now,
            "active": True,
        }
    )

    _log_security_event(
        "announcement_created",
        f"Announcement '{data.title}' broadcast ({data.priority})",
        g.user["uid"],
    )

    return success_response(
        {"id": doc_ref.id, "title": data.title},
        "Announcement broadcast.",
        status_code=201,
    )


@admin_bp.route("/announcements/<announcement_id>", methods=["DELETE"])
@require_auth
@require_role(["admin"])
def delete_announcement(announcement_id: str):
    db = _get_db()
    if not db:
        return error_response("Database unavailable", status_code=503)

    doc_ref = db.collection("announcements").document(announcement_id)
    if not doc_ref.get().exists:
        return error_response("Announcement not found", status_code=404)

    doc_ref.delete()

    _log_security_event(
        "announcement_deleted",
        f"Announcement '{announcement_id}' deleted",
        g.user["uid"],
    )

    return success_response(message="Announcement deleted.")


# ── Security Logs ────────────────────────────────────────────────────────────


@admin_bp.route("/security/logs", methods=["GET"])
@require_auth
@require_role(["admin"])
def list_security_logs():
    db = _get_db()
    logs = []

    if db:
        limit = min(int(request.args.get("limit", 100)), 500)
        docs = (
            db.collection("security_logs")
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            logs.append(data)

    return success_response({"logs": logs}, "Security logs retrieved.")


# ── User Management ──────────────────────────────────────────────────────────


@admin_bp.route("/users", methods=["GET"])
@require_auth
@require_role(["admin"])
def list_users():
    db = _get_db()
    users = []

    if db:
        docs = db.collection("users").stream()
        for doc in docs:
            data = doc.to_dict()
            data["uid"] = doc.id
            users.append(data)

    return success_response({"users": users}, "Users retrieved.")


# ── Helper ───────────────────────────────────────────────────────────────────


def _log_security_event(event_type: str, description: str, admin_uid: str):
    db = _get_db()
    if not db:
        return
    try:
        db.collection("security_logs").add(
            {
                "event_type": event_type,
                "description": description,
                "admin_uid": admin_uid,
                "timestamp": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
            }
        )
    except Exception as e:
        logger.error("Failed to log security event: %s", str(e))
