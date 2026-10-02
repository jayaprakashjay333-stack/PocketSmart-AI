import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/pocketsmart.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models import RecommendationHistory, User
    Base.metadata.create_all(bind=engine)
    create_demo_user()

def create_demo_user():
    from sqlalchemy.orm import Session
    from auth import hash_password
    from models import User

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "demo@pocketsmart.ai").first():
            demo_user = User(
                name="Demo User",
                email="demo@pocketsmart.ai",
                hashed_password=hash_password("demo12345"),
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()
