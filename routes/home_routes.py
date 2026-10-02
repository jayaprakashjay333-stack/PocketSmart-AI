import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth import get_current_user
from database import SessionLocal
from models import RecommendationHistory
from services.gemini_service import generate_home_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/home-planner", response_class=HTMLResponse)
async def home_planner_page(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("home_planner.html", {"request": request, "user": user})

@router.post("/generate-home")
async def generate_home(
    request: Request,
    total_budget: float = Form(...),
    room_type: str = Form(...),
    style: str = Form(...),
    items_required: str = Form(...),
    quantity: str = Form(...),
    preferred_platform: str = Form(...),
    additional_requirements: str = Form(""),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if total_budget <= 0:
        return templates.TemplateResponse("home_planner.html", {"request": request, "user": user, "error": "Budget must be greater than zero."})
    payload = {
        "total_budget": total_budget,
        "room_type": room_type,
        "style": style,
        "items_required": items_required,
        "quantity": quantity,
        "preferred_platform": preferred_platform,
        "additional_requirements": additional_requirements,
    }
    result = generate_home_recommendations(payload)
    history = RecommendationHistory(
        user_id=user.id,
        planner_type="home",
        budget=str(total_budget),
        input_data=json.dumps(payload, ensure_ascii=False),
        result_data=json.dumps(result, ensure_ascii=False),
    )
    db.add(history)
    db.commit()
    return templates.TemplateResponse("home_results.html", {"request": request, "user": user, "result": result, "budget": total_budget})
