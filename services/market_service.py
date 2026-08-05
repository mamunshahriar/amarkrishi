"""
Amar Krishi - Market Price Service
Modular by design: if MARKET_API_URL is configured, prices are fetched from
that external API. If it's unset, unreachable, or returns bad data, the app
automatically falls back to the local `market_prices` table so the page
never breaks.

There is currently no free, reliable, official Bangladesh government market
API. This module is written so that whenever one becomes available (e.g. DAM
- Department of Agricultural Marketing), it's a matter of setting
MARKET_API_URL / MARKET_API_KEY and adjusting `_parse_external_response()`
to match that API's JSON shape — nothing else in the app needs to change.
"""

from datetime import datetime, timezone

import requests
from flask import current_app

from models.models import MarketPrice, Crop


def _parse_external_response(payload):
    """
    Normalize an external API's JSON into the same shape the templates use.
    Adjust this to match whatever API you plug in via MARKET_API_URL.
    Expected item shape: {crop_name, price_per_kg, previous_price, market_name, district}
    """
    items = payload.get("data", payload) if isinstance(payload, dict) else payload
    normalized = []
    for item in items:
        normalized.append({
            "crop_name": item.get("crop_name") or item.get("commodity"),
            "price_per_kg": item.get("price_per_kg") or item.get("price"),
            "previous_price": item.get("previous_price"),
            "market_name": item.get("market_name") or item.get("market", "N/A"),
            "district": item.get("district", ""),
        })
    return normalized


def fetch_external_prices():
    """Returns a normalized list of price dicts, or None if unavailable."""
    api_url = current_app.config.get("MARKET_API_URL")
    if not api_url:
        return None

    headers = {}
    api_key = current_app.config.get("MARKET_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = requests.get(api_url, headers=headers, timeout=8)
        resp.raise_for_status()
        return _parse_external_response(resp.json())
    except (requests.exceptions.RequestException, ValueError) as exc:
        current_app.logger.warning("Market API unavailable, using local data: %s", exc)
        return None


def get_market_prices():
    """
    Returns (prices, meta) where `prices` is either the external list or the
    local DB rows (SQLAlchemy MarketPrice objects joined with Crop), and
    `meta` describes the source + last-updated time for the UI badge.
    """
    external = fetch_external_prices()
    if external:
        return external, {
            "source": "external_api",
            "label": "Live market data",
            "last_updated": datetime.now(timezone.utc),
        }

    local_prices = MarketPrice.query.join(Crop).all()
    latest = max((p.update_date for p in local_prices), default=None)
    return local_prices, {
        "source": "local_fallback",
        "label": "Local reference data",
        "last_updated": latest,
    }
