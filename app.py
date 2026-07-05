"""
Amar Krishi - Digital Farming Assistance Platform
Main Flask Application Entry Point

Production notes:
- The module-level `app` object is what Gunicorn imports (`gunicorn app:app`).
- No debug code or hardcoded secrets live here; everything comes from config.py,
  which in turn reads environment variables set in Render's dashboard.
"""

import os
import logging
from flask import Flask, session, request
from config import get_config
from models.models import db, User
from translations import get_text
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # --- Logging (stdout, so Render's log stream picks it up) ---
    logging.basicConfig(
        level=getattr(logging, app.config.get("LOG_LEVEL", "INFO")),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))

    # Ensure upload folder exists (created automatically if missing).
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # --- Language context: makes t('key') available in every template ---
    @app.context_processor
    def inject_translation_helper():
        lang = session.get("lang", app.config.get("DEFAULT_LANGUAGE", "bn"))

        def t(key):
            return get_text(key, lang)

        return dict(t=t, current_lang=lang)

    # --- Inject logged-in user + unread notification count into all templates ---
    @app.context_processor
    def inject_user_globals():
        from models.models import Notification
        user = None
        unread_count = 0
        if "user_id" in session:
            user = User.query.get(session["user_id"])
            if user:
                unread_count = Notification.query.filter_by(user_id=user.user_id, status="Unread").count()
        return dict(nav_user=user, unread_count=unread_count)

    # --- Basic health check endpoint for Render / uptime monitors ---
    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app


app = create_app()


if __name__ == "__main__":
    # Local development only. In production, Gunicorn runs `app:app` directly
    # (see Procfile) and this block never executes.
    with app.app_context():
        db.create_all()  # convenience for local dev; schema.sql is the canonical source
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
