"""
Amar Krishi - AI Assistant Service
Wraps Groq's free, OpenAI-compatible chat API (https://console.groq.com).

v3: Gemini's API key rollout (mid-2026) turned out to be unreliable in
practice — the new "Auth key" format (`AQ.Ab...`) frequently fails with
raw REST calls and even the official SDK for some accounts, and the
2.0-era free-tier models were deprecated, causing 429s. Groq is a much
simpler, more predictable free option: plain `Authorization: Bearer`
auth with a stable `gsk_...` key format, no SDK required, generous free
daily quota, and no credit card needed.
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


def _build_messages(message, history):
    """Build an OpenAI-style `messages` array from session history + the new message."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = "user" if turn.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": turn.get("text", "")})
    messages.append({"role": "user", "content": message})
    return messages


def ask_ai_assistant(message, history=None):
    """
    Send a message (+ optional prior turns) to Groq.
    Returns (success: bool, reply_or_error_message: str).
    """
    history = history or []
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        return False, "ai_not_configured"

    url = current_app.config["GROQ_API_URL"]
    model = current_app.config.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": _build_messages(message, history),
                "temperature": 0.6,
                "max_tokens": 512,
            },
            timeout=20,
        )
        if resp.status_code != 200:
            current_app.logger.error("Groq API error %s: %s", resp.status_code, resp.text[:500])
            return False, "ai_unavailable"

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            return False, "ai_no_response"

        text = (choices[0].get("message", {}).get("content") or "").strip()
        if not text:
            return False, "ai_no_response"
        return True, text
    except requests.exceptions.RequestException as exc:
        current_app.logger.error("Groq request failed: %s", exc)
        return False, "ai_unavailable"


# Backwards-compatible alias — routes/main_routes.py can import either name.
ask_gemini = ask_ai_assistant
