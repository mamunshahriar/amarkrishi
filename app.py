"""
Amar Krishi - Digital Farming Assistance Platform
Main Flask Application Entry Point
"""

import os
from flask import Flask, session, request
from config import Config
from models.models import db, User, Crop
from translations import get_text
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
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

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates tables if they don't exist (schema.sql is the canonical source)
    app.run(debug=True, host="0.0.0.0", port=5000)
