"""
Amar Krishi - Configuration
All sensitive/environment-dependent values are read from environment variables.
No secrets or debug output are hardcoded here — safe to commit to GitHub.
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Security ---
    # SECRET_KEY MUST be set via environment variable in production (Render dashboard).
    # The fallback below is ONLY for local development convenience.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Session cookie hardening (safe defaults; SECURE is auto-enabled in production
    # via ProductionConfig below so local HTTP development still works).
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # --- MySQL Database (Render / any host) ---
    # These map directly to the environment variables you set in Render's dashboard:
    # MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "amar_krishi")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

    # Allow a full DATABASE_URL to override the pieces above if provided
    # (handy for Render's managed MySQL / third-party DB add-ons).
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Keep MySQL connections healthy across Render's proxy/idle-timeout behavior.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # discard dead connections before using them
        "pool_recycle": 280,     # recycle connections before typical cloud DB idle timeouts
    }

    # --- Optional MongoDB (AI prediction logs) ---
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/amar_krishi_logs")

    # --- File Uploads ---
    # NOTE: Render's filesystem is ephemeral on the free/standard web service plan —
    # anything written to UPLOAD_FOLDER is lost on redeploy or restart unless you
    # attach a Render Persistent Disk or switch to S3/Cloudinary-style storage.
    UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # --- Weather ---
    # Primary source is Open-Meteo (https://open-meteo.com) which is free and
    # requires NO API key at all, so weather works out of the box on Render.
    # If WEATHER_API_KEY is set, OpenWeatherMap is used instead/as a secondary source.
    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
    WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    # --- Market Prices ---
    # Optional external market-price API. If unset (or the request fails),
    # the app automatically falls back to the local MarketPrice table so the
    # page never breaks. See services/market_service.py.
    MARKET_API_URL = os.environ.get("MARKET_API_URL", "")
    MARKET_API_KEY = os.environ.get("MARKET_API_KEY", "")

    # --- AI Assistant (Google Gemini free tier) ---
    # Create a free key at https://aistudio.google.com/app/apikey
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_API_URL = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )

    # --- Email (Flask-Mail) for verification codes & password reset OTPs ---
    # Works with Gmail (use an App Password), SendGrid SMTP, Mailtrap, etc.
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    # If no MAIL_USERNAME/PASSWORD is configured, the app logs OTP codes to the
    # server log instead of failing, so local/dev testing never gets blocked.
    MAIL_CONFIGURED = bool(MAIL_USERNAME and MAIL_PASSWORD)

    OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 10))
    # Set to "False" to allow login before the email is verified (kept optional
    # per the spec — verification is enforced by default).
    REQUIRE_EMAIL_VERIFICATION = os.environ.get("REQUIRE_EMAIL_VERIFICATION", "True").lower() == "true"

    # --- Default language ---
    DEFAULT_LANGUAGE = "bn"

    # --- Logging ---
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class ProductionConfig(Config):
    """Used automatically on Render when FLASK_ENV=production is set."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # only send cookies over HTTPS (Render serves HTTPS by default)


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


def get_config():
    """Select config class based on FLASK_ENV (defaults to production-safe)."""
    env = os.environ.get("FLASK_ENV", "production").lower()
    return DevelopmentConfig if env == "development" else ProductionConfig