"""
SmartArena AI — Admin Routes
==============================

Admin-only endpoints for gate management, announcements,
security logs, and user management.
"""

import datetime
import logging

from flask import Blueprint, request, g
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Literal

from app.middleware.auth import require_auth, require_role
from app.utils.response import success_response, error_response
from app.config.firebase import get_firestore_client
from app.services.navigation import ZONE_ADJACENCY

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


class GateUpdateRequest(BaseModel):
    """Schema for gate update requests."""

    name: str = Field(..., min_length=1, description="Gate name.")
    status: Literal["open", "closed", "maintenance"] = Field(
        default="open",
        description="Gate status: open, closed, or maintenance.",
    )
    capacity: Optional[int] = Field(
        default=None, ge=0, description="Gate capacity limit."
    )


class AnnouncementRequest(BaseModel):
    """Schema for announcement creation requests."""

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    priority: Literal["normal", "urgent"] = Field(
        default="normal", description="Announcement priority: normal or urgent."
    )
    target_zones: list[str] = Field(
        default_factory=list, description="Zones to target, empty = all."
    )


def _get_db():
    """Get Firestore client instance.

    Returns:
        Firestore client or None if unavailable.
    """
    return get_firestore_client()


# ── Gate Management ──────────────────────────────────────────────────────────


@admin_bp.route("/gates", methods=["GET"])
@require_auth
@require_role(["admin"])
def list_gates():
    """List all stadium gates with current status and occupancy.

    Returns:
        JSON response containing gates array with name, status,
        capacity, and current_count fields.
    """
    db = _get_db()
    gates = []

    gate_zones = [z for z in ZONE_ADJACENCY if z.startswith("Gate")]

    if db:
        docs = db.collection("gates").stream()
        stored = {doc.id: doc.to_dict() for doc in docs}
        for gate_zone in gate_zones:
            data = stored.get(gate_zone, {})
            gates.append(
                {
                    "name": gate_zone,
                    "status": data.get("status", "open"),
                    "capacity": data.get("capacity", 5000),
                    "current_count": data.get("current_count", 0),
                }
            )
    else:
        for gate_zone in gate_zones:
            gates.append(
                {
                    "name": gate_zone,
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
    """Update a gate's status and/or capacity.

    Expects JSON body with name, status, and optional capacity.

    Returns:
        JSON response confirming the gate update.
    """
    try:
        data = GateUpdateRequest(**request.get_json())
    except ValidationError:
        return error_response(
            "Invalid gate data. Check status and capacity values.",
            status_code=400,
        )

    db = _get_db()
    if not db:
        return error_response("Database unavailable", status_code=503)

    gate_ref = db.collection("gates").document(data.name)
    gate_ref.set(
        {
            "name": data.name,
            "status": data.status,
            "capacity": data.capacity,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
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
    """List recent announcements, newest first.

    Returns:
        JSON response containing announcements array.
    """
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
    """Create and broadcast a new stadium announcement.

    Expects JSON body with title, message, priority, and target_zones.

    Returns:
        JSON response with the new announcement ID and title.
    """
    try:
        data = AnnouncementRequest(**request.get_json())
    except ValidationError:
        return error_response(
            "Invalid announcement data. Check title and message lengths.",
            status_code=400,
        )

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
    """Delete an announcement by ID.

    Args:
        announcement_id: Firestore document ID of the announcement.

    Returns:
        JSON response confirming deletion.
    """
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
    """List recent security audit logs.

    Query Parameters:
        limit: Maximum number of logs to return (default 100, max 500).

    Returns:
        JSON response containing security log entries.
    """
    db = _get_db()
    logs = []

    if db:
        try:
            limit = min(int(request.args.get("limit", 100)), 500)
        except (ValueError, TypeError):
            limit = 100
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
    """List all registered users.

    Returns:
        JSON response containing users array with uid, email,
        name, and role fields.
    """
    db = _get_db()
    users = []

    if db:
        docs = db.collection("users").limit(500).stream()
        for doc in docs:
            data = doc.to_dict()
            data["uid"] = doc.id
            users.append(data)

    return success_response({"users": users}, "Users retrieved.")


# ── Helper ───────────────────────────────────────────────────────────────────


def _log_security_event(event_type: str, description: str, admin_uid: str) -> None:
    """Log a security-relevant event to Firestore.

    Args:
        event_type: Classification of the event (e.g. 'gate_update').
        description: Human-readable description of what happened.
        admin_uid: UID of the admin who performed the action.
    """
    db = _get_db()
    if not db:
        return
    try:
        db.collection("security_logs").add(
            {
                "event_type": event_type,
                "description": description,
                "admin_uid": admin_uid,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )
    except Exception as e:
        logger.error("Failed to log security event: %s", str(e))
