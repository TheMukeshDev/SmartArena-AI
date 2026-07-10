"""
SmartArena AI — Pydantic Request Schemas
==========================================

Validates incoming request payloads for all AI operation endpoints.
Enforces min_length constraints to prevent empty or trivially short inputs.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class IncidentRequest(BaseModel):
    """Schema for incident classification requests."""

    description: str = Field(
        ..., min_length=10, description="Description of the incident."
    )


class CrowdAnalyzeRequest(BaseModel):
    """Schema for crowd analysis requests."""

    zones: List[Dict[str, Any]] = Field(
        default_factory=list, description="Real-time zone data."
    )


class VolunteerAssignRequest(BaseModel):
    """Schema for volunteer task assignment requests."""

    location: str = Field(
        ..., min_length=2, description="Current location of the volunteer."
    )


class SustainabilityOptimizeRequest(BaseModel):
    """Schema for sustainability optimization requests."""

    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Current usage metrics."
    )


class ChatRequest(BaseModel):
    """Schema for AI assistant chat requests."""

    query: str = Field(..., min_length=2, description="User query for ArenaBot.")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Real-time stadium context."
    )
    preferred_language: str = Field(
        default="en",
        description="Preferred response language (en/hi/es/fr/ar).",
    )
    previous_interaction_id: Optional[str] = Field(
        default=None, description="ID of the previous interaction for multi-turn chat."
    )


class TransportSuggestRequest(BaseModel):
    """Schema for transport suggestion requests."""

    gate: str = Field(..., min_length=1, description="Current gate location.")
    arrival_time: str = Field(..., min_length=1, description="Desired arrival time.")
