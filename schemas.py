from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class TokenData(BaseModel):
    email: Optional[str] = None

class HomePlannerInput(BaseModel):
    total_budget: float = Field(..., gt=0)
    room_type: str
    style: str
    items_required: str
    quantity: str
    preferred_platform: str
    additional_requirements: Optional[str] = ""

class PartyPlannerInput(BaseModel):
    total_budget: float = Field(..., gt=0)
    event_type: str
    number_of_guests: int = Field(..., gt=0)
    venue_type: str
    event_location: str
    food_preference: str
    decoration_preference: str
    entertainment_preference: str
    accommodation_required: str
    additional_requirements: Optional[str] = ""

class JewelryPlannerInput(BaseModel):
    budget: float = Field(..., gt=0)
    occasion: str
    jewelry_type: str
    style: str
    material: str
    outfit_color: str
    outfit_description: str
    additional_requirements: Optional[str] = ""

class RecommendationResponse(BaseModel):
    planner_type: str
    budget: float
    estimated_total: float
    remaining_budget: float
    categories: list[Dict[str, Any]]
    recommendations: list[Dict[str, Any]]
    money_saving_tips: list[str]
    warning: Optional[str] = None
