"""
Amar Krishi - AI Assistant Service
Wraps the Google Gemini free API (https://aistudio.google.com/app/apikey).

Kept as a plain REST call via `requests` (no SDK dependency) so it stays
lightweight and easy to swap for another free provider (Hugging Face,
Cloudflare AI, etc.) later — see `ask_gemini` as the single integration point.
"""

import requests
from flask import current_app

SYSTEM_PROMPT = (
    "You are the Amar Krishi AI Assistant, a helpful farming advisor for "
    "farmers in Bangladesh. Answer questions about crops, soil, irrigation, "
    "fertilizers, plant diseases, pests, weather-related farming decisions, "
    "and market prices. Keep answers practical, concise, and easy to "
    "understand for a smallholder farmer. Respond in the same language "
    "(Bengali or English) the user writes in. If a question is unrelated to "
    "agriculture, politely redirect the conversation back to farming topics."
)

MAX_HISTORY_TURNS = 8  # last N exchanges kept for context


def _build_contents(message, history):
    """Build Gemini `contents` payload from session chat history + new message."""
    contents = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = "user" if turn.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": turn.get("text", "")}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    return contents


def ask_gemini(message, history=None):
    """
    Send a message (+ optional prior turns) to Gemini.
    Returns (success: bool, reply_or_error_message: str).
    """
    history = history or []
    api_key = current_app.config.get("GEMINI_API_KEY")

    if not api_key:
        return False, "ai_not_configured"

    url = current_app.config["GEMINI_API_URL"]
    payload = {
        "contents": _build_contents(message, history),
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 512,
        },
    }

    try:
        resp = requests.post(
            url,
            params={"key": api_key},
            json=payload,
            timeout=20,
        )
        if resp.status_code != 200:
            current_app.logger.error("Gemini API error %s: %s", resp.status_code, resp.text[:500])
            return False, "ai_unavailable"

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return False, "ai_no_response"

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        if not text:
            return False, "ai_no_response"

        return True, text

    except requests.exceptions.RequestException as exc:
        current_app.logger.error("Gemini request failed: %s", exc)
        return False, "ai_unavailable"
