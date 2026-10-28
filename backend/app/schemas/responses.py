from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    preferred_language: str
    created_at: datetime

class MessageOut(BaseModel):
    role: str
    content: str
    sources: Optional[List[Any]] = None
    confidence: Optional[float] = None
    timestamp: datetime

class ConversationOut(BaseModel):
    session_id: str
    title: Optional[str]
    messages: List[MessageOut]
    created_at: datetime

class CollegeOut(BaseModel):
    id: str
    name: str
    short_name: Optional[str]
    college_type: str
    location: dict
    website: Optional[str]
    fees: dict
    placements: dict
    branches: List[dict]
    ranking: dict
