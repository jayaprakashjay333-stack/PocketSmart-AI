import logging
from typing import Any

import httpx

from gemini_utils import call_gemini, parse_and_validate_gemini_response
from services.recommendation_service import build_fallback_home, build_fallback_party, build_fallback_jewelry

logger = logging.getLogger(__name__)


def _generate_valid_recommendations(prompt: str, planner_type: str, budget: float) -> dict:
    for attempt in range(2):
        try:
            raw = call_gemini(prompt)
            return parse_and_validate_gemini_response(raw, planner_type, budget)
        except ValueError:
            if attempt == 1:
                raise
            prompt += (
                "\nCorrection: the previous output failed validation. Return corrected JSON. "
                "Category allocations must sum exactly to estimated_total, which must be "
                "between zero and the budget."
            )
    raise ValueError("Gemini did not return a valid recommendation.")


def generate_home_recommendations(payload: dict[str, Any]) -> dict:
    budget = float(payload.get("total_budget") or payload.get("budget") or 0)
    prompt = f"""
    You are an expert home interior budgeting assistant for India.
    Return exactly one valid JSON object, with no markdown or text outside the JSON.
    Requirements:
    - Budget: INR {budget}
    - Room type: {payload.get('room_type')}
    - Style: {payload.get('style')}
    - Items required: {payload.get('items_required')}
    - Quantity: {payload.get('quantity')}
    - Preferred platform: {payload.get('preferred_platform')}
    - Additional requirements: {payload.get('additional_requirements')}
    Respect the budget strictly. All amounts are INR estimates, not live quotes.
    Set estimated_total to the sum of all category allocation values and keep it <= budget.
    Set remaining_budget to budget minus estimated_total.
    Return JSON with keys:
    planner_type, budget, estimated_total, remaining_budget, categories, recommendations, money_saving_tips.
    Each category object must include category, allocation, suggestion.
    The sum of category allocation values must equal estimated_total exactly to two decimals.
    Each recommendation object must include name, category, estimated_price, platform, reason, search_link.
    Include a few relevant product ideas; each item's estimated_price must be <= budget.
    Use search links rather than product-detail URLs when an exact verified product is not known.
    Never claim live prices, availability, discounts, or API access to shopping platforms.
    Include practical, concise money-saving tips.
    """
    try:
        return _generate_valid_recommendations(prompt, "home", budget)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        logger.warning("Gemini home recommendations unavailable; using estimates (%s).", type(exc).__name__)
        return build_fallback_home(budget)

def generate_party_recommendations(payload: dict[str, Any]) -> dict:
    budget = float(payload.get("total_budget") or payload.get("budget") or 0)
    prompt = f"""
    You are a party planning budgeting assistant for India.
    Return exactly one valid JSON object, with no markdown or text outside the JSON.
    Requirements:
    - Budget: INR {budget}
    - Event type: {payload.get('event_type')}
    - Number of guests: {payload.get('number_of_guests')}
    - Venue type: {payload.get('venue_type')}
    - Event location: {payload.get('event_location')}
    - Food preference: {payload.get('food_preference')}
    - Decoration preference: {payload.get('decoration_preference')}
    - Entertainment preference: {payload.get('entertainment_preference')}
    - Accommodation required: {payload.get('accommodation_required')}
    - Additional requirements: {payload.get('additional_requirements')}
    Respect the budget strictly. All amounts are INR estimates, not live quotes.
    Set estimated_total to the sum of all category allocation values and keep it <= budget.
    Set remaining_budget to budget minus estimated_total.
    Return JSON with keys:
    planner_type, budget, estimated_total, remaining_budget, categories, recommendations, money_saving_tips.
    categories MUST be a JSON array (never an object/map) with one object per category.
    Include Food, Decoration, Venue, Entertainment, Accommodation, Miscellaneous.
    Set Accommodation allocation to 0 when accommodation is not required.
    Every category object must contain category (string), allocation (number), suggestion (string).
    The sum of category allocation values must equal estimated_total exactly to two decimals.
    recommendations MUST be a JSON array of objects with name, category, estimated_price, platform, reason, search_link.
    Include relevant suggestions for the guest count and location; each item's estimated_price must be <= budget.
    Use search links rather than claiming a live booking or listing.
    Mention Swiggy, Zomato, or OYO only as examples, never as live platform access.
    Never claim real-time prices, availability, discounts, or platform API access.
    money_saving_tips MUST be an array of strings containing practical, concise cost-saving tips.
    """
    try:
        return _generate_valid_recommendations(prompt, "party", budget)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        logger.warning("Gemini party recommendations unavailable; using estimates (%s).", type(exc).__name__)
        return build_fallback_party(budget)

def generate_jewelry_recommendations(payload: dict[str, Any]) -> dict:
    budget = float(payload.get("budget") or 0)
    prompt = f"""
    You are an expert jewelry budgeting assistant for India.
    Return exactly one valid JSON object, with no markdown or text outside the JSON.
    Requirements:
    - Budget: INR {budget}
    - Occasion: {payload.get('occasion')}
    - Jewelry type: {payload.get('jewelry_type')}
    - Style: {payload.get('style')}
    - Material: {payload.get('material')}
    - Outfit color: {payload.get('outfit_color')}
    - Outfit description: {payload.get('outfit_description')}
    - Additional requirements: {payload.get('additional_requirements')}
    Respect the budget strictly. All amounts are INR estimates, not live quotes.
    Set estimated_total to the sum of all category allocation values and keep it <= budget.
    Set remaining_budget to budget minus estimated_total.
    Return JSON with keys:
    planner_type, budget, estimated_total, remaining_budget, categories, recommendations, money_saving_tips.
    The sum of category allocation values must equal estimated_total exactly to two decimals.
    Each category object must include category, allocation, suggestion.
    Recommendations should include name, category, estimated_price, platform, reason, search_link.
    Include the selected jewelry type, style, color, and material suggestion, and a distinct alternative.
    Each item's estimated_price must be <= budget; explain that precious-metal costs vary when relevant.
    Use search links rather than product-detail URLs when an exact verified product is not known.
    Never claim live prices, stock, purity verification, discounts, or platform API access.
    Include practical, concise money-saving tips.
    """
    try:
        return _generate_valid_recommendations(prompt, "jewelry", budget)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        logger.warning("Gemini jewelry recommendations unavailable; using estimates (%s).", type(exc).__name__)
        return build_fallback_jewelry(budget)
