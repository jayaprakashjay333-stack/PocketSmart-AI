from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth import create_access_token, get_optional_user, get_user_by_email, hash_password, verify_password
from database import SessionLocal
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login")
async def login_page(request: Request):
    user = await get_optional_user(request)
    return templates.TemplateResponse("login.html", {"request": request, "user": user})

@router.get("/register")
async def register_page(request: Request):
    user = await get_optional_user(request)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

@router.post("/register")
async def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()
    email = email.strip().lower()
    if not name or len(name) < 2:
        return templates.TemplateResponse("register.html", {"request": request, "user": None, "error": "Name must be at least 2 characters long."})
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "user": None, "error": "Passwords do not match."})
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {"request": request, "user": None, "error": "Password must be at least 6 characters."})
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {"request": request, "user": None, "error": "Email already registered."})
    user = User(name=name, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "user": None, "error": "Invalid email or password."})
    token = create_access_token({"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.post("/token")
async def issue_token(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "name": user.name, "email": user.email}}

@router.get("/session-info")
async def session_info(request: Request):
    user = await get_optional_user(request)
    return {"authenticated": user is not None, "user": {"id": user.id, "name": user.name, "email": user.email} if user else None}

@router.get("/session-data")
async def session_data(request: Request):
    user = await get_optional_user(request)
    return {"session": {"user_id": user.id if user else None, "name": user.name if user else None, "email": user.email if user else None}}
