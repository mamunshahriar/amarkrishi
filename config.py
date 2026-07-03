"""
Amar Krishi - Configuration
Reads sensitive values from environment variables. Defaults are provided
for local development only — change SECRET_KEY and DB credentials in production.
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Security ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    WTF_CSRF_ENABLED = True

    # --- MySQL Database ---
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB = os.environ.get("MYSQL_DB")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )
SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Optional MongoDB (AI prediction logs) ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/amar_krishi_logs")

    # --- File Uploads ---
UPLOAD_FOLDER = os.path.join(basedir, "static", "uploads")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # --- Weather (placeholder, plug a real API key when available) ---
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

    # --- Default language ---
DEFAULT_LANGUAGE = "bn"
