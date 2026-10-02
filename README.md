# PocketSmart AI

PocketSmart AI is a smart budgeting and recommendation web app built for college projects. It helps users plan home interiors, party budgets, and jewelry shopping within a chosen budget using AI-powered recommendations with fallback mock data if Gemini is not available.

Gemini Flash is connected for live recommendations. The app validates the model's JSON response and budget totals, retries transient API/model failures, and uses estimated fallback recommendations if Gemini is unavailable or returns invalid data. Prices are estimates; no live shopping, booking, or availability APIs are connected.

## Features
- Smart home interior planner
- Budget-based party organizer
- Jewelry recommendation assistant
- User registration and login
- JWT-based session handling
- SQLite database with SQLAlchemy
- Recommendation history and detail view
- Responsive design with light and dark mode

## Technology Stack
- Python 3.13+
- FastAPI
- Jinja2
- SQLAlchemy
- SQLite
- JWT
- Gemini API integration

## Folder Structure
```text
PocketSmart-AI/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── gemini_utils.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── routes/
├── services/
├── templates/
├── static/
└── data/
```

## Installation
```bash
cd PocketSmart-AI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Setup
Copy `.env.example` to `.env` and update values:
```bash
copy .env.example .env
```

Example:
```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-flash-lite-latest
SECRET_KEY=pocketsmart-demo-secret-key
DATABASE_URL=sqlite:///./data/pocketsmart.db
```

`GEMINI_MODEL` is optional. If omitted, the app uses `gemini-flash-lite-latest` and tries other supported Flash models when that model is temporarily unavailable.

## Database Setup
The database is created automatically on startup.

## How to Run
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/`

## Getting a Gemini API Key
1. Go to Google AI Studio.
2. Create a new API key.
3. Add it to your `.env` file as `GEMINI_API_KEY`.
4. Restart the server after changing `.env`.

## Demo Login
- Email: demo@pocketsmart.ai
- Password: demo12345

## API Endpoints
- GET /
- GET /login
- GET /register
- POST /register
- POST /login
- GET /logout
- POST /generate-home
- POST /generate-party
- POST /generate-jewelry
- GET /dashboard
- GET /history
- GET /recommendations-details/{id}
- GET /session-info
- GET /session-data

## Testing
- Import check: ensure dependencies install
- Run the app and open the homepage
- Register a user
- Login and create plan recommendations
- Verify history records appear
- Test fallback by leaving the Gemini API key empty

## Screenshots
Placeholder for screenshots.

## Future Enhancements
- Real product price APIs
- User profile and settings
- Advanced charts and comparison views
- Multi-user sharing and collaboration
