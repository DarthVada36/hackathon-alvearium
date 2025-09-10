from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FamilyMemberCreate(BaseModel):
    name: str
    age: int
    member_type: str = Field(..., pattern="^(adult|child)$")

class FamilyCreate(BaseModel):
    name: str
    preferred_language: str = "es"
    members: List[FamilyMemberCreate]

class FamilyResponse(BaseModel):
    id: int
    name: str
    preferred_language: str
    created_at: datetime
    members: List[Dict[str, Any]]

class ChatMessage(BaseModel):
    message: str
    family_id: int
    location: Optional[Dict[str, float]] = None
    speaker_name: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    points_earned: int = 0
    total_points: int = 0
    # Hacemos 'situation' opcional para evitar errores cuando el agente no lo incluya
    situation: Optional[str] = None
    achievements: List[str] = []
    error: Optional[str] = None

class LocationUpdate(BaseModel):
    family_id: int
    latitude: float
    longitude: float

class RouteProgress(BaseModel):
    family_id: int
    current_poi_index: int
    points_earned: int
    current_location: Optional[Dict[str, float]] = None

class HealthCheck(BaseModel):
    status: str
    database: str
    services: Dict[str, str]
