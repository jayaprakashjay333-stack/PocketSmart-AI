import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth import get_current_user
from database import SessionLocal
from models import RecommendationHistory

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    entries = db.query(RecommendationHistory).filter(RecommendationHistory.user_id == user.id).order_by(RecommendationHistory.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "recent_history": entries[:5], "total_history": len(entries), "recent_count": min(len(entries), 5)})

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    entries = db.query(RecommendationHistory).filter(RecommendationHistory.user_id == user.id).order_by(RecommendationHistory.created_at.desc()).all()
    return templates.TemplateResponse("history.html", {"request": request, "user": user, "entries": entries})

@router.post("/history/{history_id}/delete")
async def delete_history_item(request: Request, history_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    item = db.query(RecommendationHistory).filter(RecommendationHistory.id == history_id, RecommendationHistory.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History item not found.")
    db.delete(item)
    db.commit()
    return await history_page(request, db)

@router.get("/recommendations-details/{history_id}", response_class=HTMLResponse)
async def recommendation_details(request: Request, history_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    item = db.query(RecommendationHistory).filter(RecommendationHistory.id == history_id, RecommendationHistory.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")
    result = json.loads(item.result_data)
    return templates.TemplateResponse("recommendation_detail.html", {"request": request, "user": user, "result": result, "item": item})
