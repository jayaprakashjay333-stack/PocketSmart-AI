from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

from database import init_db
from auth import get_optional_user
from routes.auth_routes import router as auth_router
from routes.home_routes import router as home_router
from routes.party_routes import router as party_router
from routes.jewelry_routes import router as jewelry_router
from routes.history_routes import router as history_router

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="PocketSmart AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(auth_router)
app.include_router(home_router)
app.include_router(party_router)
app.include_router(jewelry_router)
app.include_router(history_router)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = await get_optional_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
