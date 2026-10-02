import json
import math
import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


def extract_json_from_text(text: str):
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            fragment = cleaned[start : end + 1]
            try:
                return json.loads(fragment)
            except json.JSONDecodeError:
                return None
    return None

def call_gemini(prompt: str, model: str | None = None) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")
    primary_model = model or os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    models = [primary_model]
    if model is None:
        models.extend(
            candidate
            for candidate in ("gemini-3.8-flash", "gemini-3.5-flash")
            if candidate != primary_model
        )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }
    retryable_statuses = {429, 500, 502, 503, 504}
    last_error = None
    for model_index, selected_model in enumerate(models):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
        for attempt in range(2):
            try:
                response = httpx.post(url, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except httpx.HTTPStatusError as exc:
                last_error = exc
                should_try_another_model = exc.response.status_code in retryable_statuses | {404}
                if not should_try_another_model:
                    raise
                if exc.response.status_code not in retryable_statuses or attempt == 1:
                    break
                time.sleep(0.5 * (attempt + 1))
            except (httpx.RequestError, KeyError, IndexError, TypeError) as exc:
                last_error = exc
                break
        if model_index < len(models) - 1:
            continue
    if last_error is not None:
        raise last_error
    raise httpx.HTTPError("Gemini request could not be completed.")

def parse_and_validate_gemini_response(raw: Any, planner_type: str, budget: float):
    payload = raw if isinstance(raw, dict) else extract_json_from_text(str(raw))
    if not payload or not isinstance(payload, dict):
        raise ValueError("Gemini response was not valid JSON.")

    categories = payload.get("categories") or []
    recommendations = payload.get("recommendations") or []
    money_saving_tips = payload.get("money_saving_tips") or []
    if not isinstance(categories, list) or not isinstance(recommendations, list) or not isinstance(money_saving_tips, list):
        raise ValueError("Gemini response contains invalid recommendation lists.")

    try:
        estimated_total = float(payload["estimated_total"])
        category_total = sum(float(category["allocation"]) for category in categories)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Gemini response contains incomplete or invalid cost data.") from exc

    if not math.isfinite(estimated_total) or estimated_total < 0 or estimated_total > budget:
        raise ValueError("Gemini recommendation total is outside the requested budget.")
    if not math.isfinite(category_total) or category_total < 0 or category_total > budget:
        raise ValueError("Gemini category allocations are outside the requested budget.")
    if abs(category_total - estimated_total) > 0.02:
        raise ValueError("Gemini category allocations do not add up to the estimated total.")

    for category in categories:
        if not isinstance(category, dict) or not all(key in category for key in ("category", "allocation", "suggestion")):
            raise ValueError("Gemini response contains an incomplete category.")
    for recommendation in recommendations:
        if not isinstance(recommendation, dict) or not all(
            key in recommendation
            for key in ("name", "category", "estimated_price", "platform", "reason", "search_link")
        ):
            raise ValueError("Gemini response contains an incomplete recommendation.")
        try:
            price = float(recommendation["estimated_price"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Gemini response contains an invalid estimated price.") from exc
        if not math.isfinite(price) or price < 0 or price > budget:
            raise ValueError("Gemini recommendation price is outside the requested budget.")

    if not all(isinstance(tip, str) for tip in money_saving_tips):
        raise ValueError("Gemini response contains invalid money-saving tips.")

    payload["planner_type"] = planner_type
    payload["budget"] = float(budget)
    payload["estimated_total"] = estimated_total
    payload["remaining_budget"] = round(float(budget) - estimated_total, 2)
    payload["categories"] = categories
    payload["recommendations"] = recommendations
    payload["money_saving_tips"] = money_saving_tips
    return payload
