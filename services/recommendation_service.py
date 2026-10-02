from typing import Any

def clamp_budget_total(budget: float, estimated_total: float) -> float:
    return min(float(estimated_total), float(budget))

def build_fallback_home(budget: float) -> dict:
    base = clamp_budget_total(budget, budget * 0.9)
    return {
        "planner_type": "home",
        "budget": float(budget),
        "estimated_total": round(base, 2),
        "remaining_budget": round(float(budget) - base, 2),
        "categories": [
            {"category": "Lighting", "allocation": round(base * 0.25, 2), "suggestion": "Modern LED downlights for a balanced, elegant finish."},
            {"category": "Furniture", "allocation": round(base * 0.35, 2), "suggestion": "Space-smart furniture with added storage."},
            {"category": "Decor", "allocation": round(base * 0.2, 2), "suggestion": "Add textured cushions and wall accents."},
            {"category": "Utility", "allocation": round(base - round(base * 0.8, 2), 2), "suggestion": "Use practical organizers and multi-use pieces."},
        ],
        "recommendations": [
            {"name": "Modern LED Ceiling Light", "category": "Lighting", "estimated_price": 1499, "platform": "Estimated Price", "reason": "Best value for a modern room upgrade.", "search_link": "https://www.amazon.in/"},
            {"name": "Compact Accent Chair", "category": "Furniture", "estimated_price": 2999, "platform": "Estimated Price", "reason": "Adds comfort without crowding the space.", "search_link": "https://www.flipkart.com/"},
            {"name": "Printed Cushion Set", "category": "Decor", "estimated_price": 999, "platform": "Estimated Price", "reason": "Brings style without overspending.", "search_link": "https://www.amazon.in/"},
        ],
        "money_saving_tips": [
            "Prioritize lighting and statement pieces before buying extras.",
            "Choose neutral tones and add accents later for flexibility.",
            "Buy multipurpose furniture to reduce room clutter and cost."
        ],
        "warning": "Gemini was unavailable, so these are estimate-based recommendations."
    }

def build_fallback_party(budget: float) -> dict:
    total = clamp_budget_total(budget, budget * 0.92)
    return {
        "planner_type": "party",
        "budget": float(budget),
        "estimated_total": round(total, 2),
        "remaining_budget": round(float(budget) - total, 2),
        "categories": [
            {"category": "Food", "allocation": round(total * 0.3, 2), "suggestion": "Buffet-style menu with a few signature dishes."},
            {"category": "Decoration", "allocation": round(total * 0.2, 2), "suggestion": "Use DIY lighting and themed florals."},
            {"category": "Venue", "allocation": round(total * 0.2, 2), "suggestion": "Book a compact venue with an aesthetic backdrop."},
            {"category": "Entertainment", "allocation": round(total * 0.15, 2), "suggestion": "Use a playlist, speaker system, or minimal DJ setup."},
            {"category": "Accommodation", "allocation": round(total * 0.1, 2), "suggestion": "Book shared or off-peak stays when needed."},
            {"category": "Miscellaneous", "allocation": round(total - round(total * 0.95, 2), 2), "suggestion": "Keep a reserve for printing and last-minute essentials."},
        ],
        "recommendations": [
            {"name": "Combo Buffet Package", "category": "Food", "estimated_price": 4800, "platform": "Estimated Price", "reason": "Balanced menu for a mid-sized event.", "search_link": "https://www.swiggy.com/"},
            {"name": "Backdrop + Lighting Setup", "category": "Decoration", "estimated_price": 3200, "platform": "Estimated Price", "reason": "High visual impact with low cost.", "search_link": "https://www.zomato.com/"},
            {"name": "Community Hall Booking", "category": "Venue", "estimated_price": 5500, "platform": "Estimated Price", "reason": "Practical and budget-friendly venue option.", "search_link": "https://www.oyo.com/"},
        ],
        "money_saving_tips": [
            "Use a single theme across food and decor for a premium look at lower cost.",
            "Avoid last-minute purchases by planning a month in advance.",
            "Choose a venue with in-house decor for lower overhead costs."
        ],
        "warning": "Gemini was unavailable, so these are estimate-based party planning recommendations."
    }

def build_fallback_jewelry(budget: float) -> dict:
    total = clamp_budget_total(budget, budget * 0.85)
    return {
        "planner_type": "jewelry",
        "budget": float(budget),
        "estimated_total": round(total, 2),
        "remaining_budget": round(float(budget) - total, 2),
        "categories": [
            {"category": "Main Statement Piece", "allocation": round(total * 0.5, 2), "suggestion": "Choose one standout piece and keep the rest minimal."},
            {"category": "Accent Pair", "allocation": round(total * 0.25, 2), "suggestion": "Add a matching complement to the outfit."},
            {"category": "Accessories", "allocation": round(total * 0.15, 2), "suggestion": "Use small metal accessories to elevate the look."},
            {"category": "Reserve", "allocation": round(total - round(total * 0.9, 2), 2), "suggestion": "Keep some budget aside for tailoring or finishing touches."},
        ],
        "recommendations": [
            {"name": "Gold Tone Statement Necklace", "category": "Jewelry", "estimated_price": 3500, "platform": "Estimated Price", "reason": "Ideal for festive and wedding outfits.", "search_link": "https://www.amazon.in/"},
            {"name": "Minimal Pearl Earrings", "category": "Jewelry", "estimated_price": 2200, "platform": "Estimated Price", "reason": "Elegant and versatile for multiple occasions.", "search_link": "https://www.flipkart.com/"},
        ],
        "money_saving_tips": [
            "Choose a statement piece that complements the outfit rather than buying a full set.",
            "Artificial or plated options can provide a premium look at a lower price.",
            "Match the jewelry color to your outfit so the look feels intentional without excess spending."
        ],
        "warning": "Gemini was unavailable, so these are estimate-based jewelry suggestions."
    }
