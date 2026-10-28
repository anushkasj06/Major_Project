from pydantic import BaseModel, Field
from typing import Optional, List

class CollegeCreate(BaseModel):
    name: str = Field(..., min_length=3)
    short_name: Optional[str] = None
    college_type: str = "engineering"
    location: dict = {}
    website: Optional[str] = None
    established_year: Optional[int] = None
    affiliation: Optional[str] = None
    branches: List[dict] = []
    fees: dict = {}
    placements: dict = {}
    cutoffs: dict = {}
    hostels: dict = {}
    scholarships: List[str] = []
    ranking: dict = {}
    contact: dict = {}

class CollegeUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    website: Optional[str] = None
    fees: Optional[dict] = None
    placements: Optional[dict] = None
    cutoffs: Optional[dict] = None
