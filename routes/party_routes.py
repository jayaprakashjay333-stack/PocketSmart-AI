import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth import get_current_user
from database import SessionLocal
from models import RecommendationHistory
from services.gemini_service import generate_party_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/party-planner", response_class=HTMLResponse)
async def party_planner_page(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("party_planner.html", {"request": request, "user": user})

@router.post("/generate-party")
async def generate_party(
    request: Request,
    total_budget: float = Form(...),
    event_type: str = Form(...),
    number_of_guests: int = Form(...),
    venue_type: str = Form(...),
    event_location: str = Form(...),
    food_preference: str = Form(...),
    decoration_preference: str = Form(...),
    entertainment_preference: str = Form(...),
    accommodation_required: str = Form(...),
    additional_requirements: str = Form(""),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if total_budget <= 0:
        return templates.TemplateResponse("party_planner.html", {"request": request, "user": user, "error": "Budget must be greater than zero."})
    if number_of_guests <= 0:
        return templates.TemplateResponse("party_planner.html", {"request": request, "user": user, "error": "Number of guests must be at least 1."})
    payload = {
        "total_budget": total_budget,
        "event_type": event_type,
        "number_of_guests": number_of_guests,
        "venue_type": venue_type,
        "event_location": event_location,
        "food_preference": food_preference,
        "decoration_preference": decoration_preference,
        "entertainment_preference": entertainment_preference,
        "accommodation_required": accommodation_required,
        "additional_requirements": additional_requirements,
    }
    result = generate_party_recommendations(payload)
    history = RecommendationHistory(
        user_id=user.id,
        planner_type="party",
        budget=str(total_budget),
        input_data=json.dumps(payload, ensure_ascii=False),
        result_data=json.dumps(result, ensure_ascii=False),
    )
    db.add(history)
    db.commit()
    return templates.TemplateResponse("party_results.html", {"request": request, "user": user, "result": result, "budget": total_budget})
