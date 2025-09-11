from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# SCHEMAS 

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


# SCHEMAS DE AUTENTICACIÓN

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Mínimo 6 caracteres")
    avatar: Optional[str] = "icon1"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    avatar: str
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None

class UserProfileComplete(BaseModel):
    user: UserResponse
    families: List[Dict[str, Any]]
    total_points: int
    total_families: int


class FamilyCreateAuth(BaseModel):
    """Schema para crear familia cuando el usuario está autenticado"""
    name: str
    preferred_language: str = "es"
    members: List[FamilyMemberCreate]

class ChatMessageAuth(BaseModel):
    """Schema para chat cuando el usuario está autenticado"""
    message: str
    family_id: int  # Se validará que pertenezca al usuario
    location: Optional[Dict[str, float]] = None
    speaker_name: Optional[str] = None

class FamilyResponseAuth(BaseModel):
    """Respuesta de familia con información del propietario"""
    id: int
    user_id: int
    name: str
    preferred_language: str
    created_at: datetime
    members: List[Dict[str, Any]]
    total_points: Optional[int] = 0