from pydantic import BaseModel, Field
from typing import List, Dict, Any

class IncidentRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Description of the incident.")

class CrowdAnalyzeRequest(BaseModel):
    zones: List[Dict[str, Any]] = Field(default_factory=list, description="Real-time zone data.")

class VolunteerAssignRequest(BaseModel):
    location: str = Field(..., min_length=2, description="Current location of the volunteer.")

class SustainabilityOptimizeRequest(BaseModel):
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Current usage metrics.")

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2, description="User query for ArenaBot.")
    context: Dict[str, Any] = Field(default_factory=dict, description="Real-time stadium context.")
