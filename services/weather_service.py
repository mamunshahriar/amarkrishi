"""
Amar Krishi - Real-Time Weather Service
Primary source: Open-Meteo (https://open-meteo.com) — free, no API key needed.
Secondary source: OpenWeatherMap — used only if WEATHER_API_KEY is set and
Open-Meteo fails for some reason.
"""

from datetime import datetime, timezone

import requests
from flask import current_app

# WMO weather codes -> short condition text (used by Open-Meteo)
WMO_CONDITIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}

# Fallback coordinates for major Bangladeshi districts (used when geocoding fails)
DISTRICT_COORDS = {
    "Dhaka": (23.8103, 90.4125), "Rajshahi": (24.3745, 88.6042),
    "Khulna": (22.8456, 89.5403), "Rangpur": (25.7439, 89.2752),
    "Barisal": (22.7010, 90.3535), "Sylhet": (24.8949, 91.8687),
    "Chattogram": (22.3569, 91.7832), "Mymensingh": (24.7471, 90.4203),
}


def _geocode(place_name):
    try:
        resp = requests.get(
            current_app.config["OPEN_METEO_GEOCODE_URL"],
            params={"name": place_name, "count": 1, "language": "en"},
            timeout=8,
        )
        resp.raise_for_status()
        results = resp.json().get("results")
        if results:
            return results[0]["latitude"], results[0]["longitude"], results[0].get("name", place_name)
    except requests.exceptions.RequestException:
        pass

    if place_name in DISTRICT_COORDS:
        lat, lon = DISTRICT_COORDS[place_name]
        return lat, lon, place_name

    return None


def _fetch_open_meteo(lat, lon):
    resp = requests.get(
        current_app.config["OPEN_METEO_URL"],
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,precipitation_probability",
            "hourly": "precipitation_probability",
            "timezone": "Asia/Dhaka",
        },
        timeout=8,
    )
    resp.raise_for_status()
    data = resp.json()
    current = data.get("current", {})

    code = current.get("weather_code", 0)
    rain_prob = current.get("precipitation_probability")
    if rain_prob is None:
        hourly_probs = data.get("hourly", {}).get("precipitation_probability", [])
        rain_prob = hourly_probs[0] if hourly_probs else 0

    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
        "rain_probability": rain_prob,
        "condition": WMO_CONDITIONS.get(code, "Unknown"),
        "source": "Open-Meteo (live)",
    }


def _fetch_openweathermap(lat, lon):
    api_key = current_app.config.get("WEATHER_API_KEY")
    if not api_key:
        return None
    resp = requests.get(
        current_app.config["WEATHER_API_URL"],
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
        timeout=8,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "temperature": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "wind_speed": data.get("wind", {}).get("speed"),
        "rain_probability": data.get("clouds", {}).get("all", 0),
        "condition": (data.get("weather") or [{}])[0].get("description", "Unknown").title(),
        "source": "OpenWeatherMap (live)",
    }


def get_live_weather(place_name):
    """
    Returns a dict with live weather for a district/city name, or None if
    both providers fail (caller should fall back to cached DB data).
    """
    location = _geocode(place_name)
    if not location:
        return None
    lat, lon, resolved_name = location

    try:
        result = _fetch_open_meteo(lat, lon)
    except requests.exceptions.RequestException:
        current_app.logger.warning("Open-Meteo failed for %s, trying OpenWeatherMap", place_name)
        try:
            result = _fetch_openweathermap(lat, lon)
        except requests.exceptions.RequestException:
            result = None

    if not result:
        return None

    result["district"] = resolved_name
    result["fetched_at"] = datetime.now(timezone.utc)
    return result


def weather_alert_from(condition_text, rain_probability):
    """Very simple alert derivation for the UI badge, based on live data."""
    text = (condition_text or "").lower()
    if "thunderstorm" in text or "severe" in text:
        return "Storm", "High"
    if rain_probability and rain_probability >= 70:
        return "Heavy Rain", "Medium"
    if "fog" in text:
        return "Fog", "Low"
    return "None", "Low"