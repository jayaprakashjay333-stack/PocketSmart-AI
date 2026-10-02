import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth import get_current_user
from database import SessionLocal
from models import RecommendationHistory
from services.gemini_service import generate_jewelry_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner_page(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": user})

@router.post("/generate-jewelry")
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    jewelry_type: str = Form(...),
    style: str = Form(...),
    material: str = Form(...),
    outfit_color: str = Form(...),
    outfit_description: str = Form(...),
    additional_requirements: str = Form(""),
    image: UploadFile = File(default=None),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if budget <= 0:
        return templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": user, "error": "Budget must be greater than zero."})
    payload = {
        "budget": budget,
        "occasion": occasion,
        "jewelry_type": jewelry_type,
        "style": style,
        "material": material,
        "outfit_color": outfit_color,
        "outfit_description": outfit_description,
        "additional_requirements": additional_requirements,
    }
    stored_image = None
    if image and image.filename:
        allowed = {"image/jpeg", "image/png", "image/webp"}
        if image.content_type not in allowed:
            return templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": user, "error": "Invalid image type. Use PNG, JPG, or WEBP."})
        file_bytes = await image.read()
        if len(file_bytes) > 2 * 1024 * 1024:
            return templates.TemplateResponse("jewelry_planner.html", {"request": request, "user": user, "error": "Image size must be under 2MB."})
        safe_name = image.filename.replace(" ", "_")
        upload_path = UPLOAD_DIR / safe_name
        with open(upload_path, "wb") as f:
            f.write(file_bytes)
        stored_image = str(upload_path.relative_to(Path(__file__).resolve().parents[1])).replace('\\', '/')
    if stored_image:
        payload["image_path"] = stored_image
    result = generate_jewelry_recommendations(payload)
    history = RecommendationHistory(
        user_id=user.id,
        planner_type="jewelry",
        budget=str(budget),
        input_data=json.dumps(payload, ensure_ascii=False),
        result_data=json.dumps(result, ensure_ascii=False),
    )
    db.add(history)
    db.commit()
    return templates.TemplateResponse("jewelry_results.html", {"request": request, "user": user, "result": result, "budget": budget, "image_path": stored_image})
