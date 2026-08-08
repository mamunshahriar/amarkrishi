"""
Amar Krishi - AI Assistant Service
Wraps Google's official `google-genai` SDK (https://aistudio.google.com/app/apikey).

v2: Google migrated Gemini API keys from the old "Standard" format
(`AIzaSy...`, plain `?key=` REST auth) to the new "Auth key" format
(`AQ.Ab...`) starting mid-2026. Auth keys are not reliably usable with
hand-rolled REST calls (`?key=` query param or `Authorization: Bearer`
both fail for many accounts) — Google's own docs now recommend the
official SDK instead, which is what this version does. Standard keys
(`AIzaSy...`) still work fine here too, since the SDK accepts both.
"""
from flask import current_app
from google import genai
from google.genai import types

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

_clients = {}  # api_key -> genai.Client, so we don't rebuild a client per request


def _get_client():
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        return None
    if api_key not in _clients:
        _clients[api_key] = genai.Client(api_key=api_key)
    return _clients[api_key]


def _build_contents(message, history):
    """Build SDK `Content` objects from session chat history + new message."""
    contents = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = "user" if turn.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=turn.get("text", ""))]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
    return contents


def ask_gemini(message, history=None):
    """
    Send a message (+ optional prior turns) to Gemini.
    Returns (success: bool, reply_or_error_message: str).
    """
    history = history or []
    client = _get_client()
    if client is None:
        return False, "ai_not_configured"

    model = current_app.config.get("GEMINI_MODEL", "gemini-2.0-flash")

    try:
        response = client.models.generate_content(
            model=model,
            contents=_build_contents(message, history),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.6,
                max_output_tokens=512,
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        if not text:
            return False, "ai_no_response"
        return True, text
    except Exception as exc:
        current_app.logger.error("Gemini API error: %s", exc)
        return False, "ai_unavailable"
