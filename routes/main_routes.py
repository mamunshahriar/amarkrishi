"""
Amar Krishi - Main Application Routes
Dashboard and all core farming modules.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from werkzeug.utils import secure_filename
import os, random

from models.models import (
    db, User, Crop, Disease, DiseaseReport, CropRecommendation,
    MarketPrice, Weather, Transaction, Notification
)

main_bp = Blueprint("main", __name__)

DISTRICTS = ["Dhaka", "Rajshahi", "Khulna", "Rangpur", "Barisal", "Sylhet", "Chattogram", "Mymensingh"]


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------
@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    weather = Weather.query.filter_by(district=user.district).first() or Weather.query.first()
    market = MarketPrice.query.limit(5).all()
    notifications = Notification.query.filter_by(user_id=user.user_id).order_by(Notification.created_at.desc()).limit(5).all()

    income = sum(float(t.amount) for t in Transaction.query.filter_by(user_id=user.user_id, type="Income").all())
    expense = sum(float(t.amount) for t in Transaction.query.filter_by(user_id=user.user_id, type="Expense").all())

    return render_template(
        "dashboard.html",
        user=user,
        weather=weather,
        market=market,
        notifications=notifications,
        income=income,
        expense=expense,
        profit=income - expense,
    )


# ---------------------------------------------------------
# Crop Advisory / Recommendation
# ---------------------------------------------------------
@main_bp.route("/crop-advisory", methods=["GET", "POST"])
@login_required
def crop_advisory():
    results = []
    if request.method == "POST":
        soil_type = request.form.get("soil_type")
        season = request.form.get("season")

        query = Crop.query
        if season:
            query = query.filter((Crop.season == season) | (Crop.season == "All Season"))
        if soil_type:
            query = query.filter(Crop.soil_type.ilike(f"%{soil_type}%"))
        results = query.all()

        if not results:
            results = Crop.query.limit(4).all()

    return render_template("crop.html", crops=results, districts=DISTRICTS)


# ---------------------------------------------------------
# AI Disease Detection
# ---------------------------------------------------------
@main_bp.route("/disease-detection", methods=["GET", "POST"])
@login_required
def disease_detection():
    result = None
    if request.method == "POST":
        file = request.files.get("leaf_image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)

                # Placeholder AI prediction (replace with real TensorFlow/Teachable Machine model)
                disease = Disease.query.order_by(db.func.rand()).first()
                confidence = round(random.uniform(82, 98), 2)

                report = DiseaseReport(
                    user_id=session["user_id"],
                    disease_id=disease.disease_id if disease else None,
                    image_path=f"uploads/{filename}",
                    result=disease.disease_name if disease else "Unknown",
                    confidence=confidence,
                )
                db.session.add(report)
                db.session.commit()
                result = {"disease": disease, "confidence": confidence, "image": filename}
            else:
                flash("error", "invalid_image")

    history = DiseaseReport.query.filter_by(user_id=session["user_id"]).order_by(DiseaseReport.detection_date.desc()).limit(5).all()
    return render_template("disease.html", result=result, history=history)


# ---------------------------------------------------------
# Market Prices
# ---------------------------------------------------------
@main_bp.route("/market-prices")
@login_required
def market_prices():
    prices = MarketPrice.query.join(Crop).all()
    return render_template("market.html", prices=prices)


@main_bp.route("/api/market-trend/<int:crop_id>")
@login_required
def market_trend_api(crop_id):
    # Demo 7-day trend data for Chart.js (replace with real historical query)
    base = float(MarketPrice.query.filter_by(crop_id=crop_id).first().price_per_kg) if MarketPrice.query.filter_by(crop_id=crop_id).first() else 20
    trend = [round(base + random.uniform(-2, 2), 2) for _ in range(7)]
    return jsonify({"labels": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Today"], "prices": trend})


# ---------------------------------------------------------
# Weather & Alerts
# ---------------------------------------------------------
@main_bp.route("/weather")
@login_required
def weather():
    user = current_user()
    records = Weather.query.all()
    selected = Weather.query.filter_by(district=user.district).first() or (records[0] if records else None)
    return render_template("weather.html", records=records, selected=selected, districts=DISTRICTS)


# ---------------------------------------------------------
# Profile
# ---------------------------------------------------------
@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        user.name = request.form.get("name", user.name)
        user.phone = request.form.get("phone", user.phone)
        user.address = request.form.get("address", user.address)
        user.district = request.form.get("district", user.district)
        user.land_size = request.form.get("land_size", user.land_size) or 0
        user.preferred_crops = request.form.get("preferred_crops", user.preferred_crops)
        db.session.commit()
        flash("success", "profile_updated")
        return redirect(url_for("main.profile"))

    return render_template("profile.html", user=user, districts=DISTRICTS)


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------
@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = current_user()
    if request.method == "POST":
        lang = request.form.get("language")
        if lang in ("en", "bn"):
            user.language_pref = lang
            session["lang"] = lang
            db.session.commit()
            flash("success", "settings_updated")
        return redirect(url_for("main.settings"))
    return render_template("settings.html", user=user)


# ---------------------------------------------------------
# Expense Tracker
# ---------------------------------------------------------
@main_bp.route("/expense-tracker", methods=["GET", "POST"])
@login_required
def expense_tracker():
    if request.method == "POST":
        t = Transaction(
            user_id=session["user_id"],
            type=request.form.get("type"),
            category=request.form.get("category"),
            amount=request.form.get("amount") or 0,
            note=request.form.get("note"),
        )
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("main.expense_tracker"))

    transactions = Transaction.query.filter_by(user_id=session["user_id"]).order_by(Transaction.transaction_date.desc()).all()
    income = sum(float(t.amount) for t in transactions if t.type == "Income")
    expense = sum(float(t.amount) for t in transactions if t.type == "Expense")
    return render_template("expense.html", transactions=transactions, income=income, expense=expense)


# ---------------------------------------------------------
# Simple feature pages (demo UI placeholders for extra modules)
# ---------------------------------------------------------
@main_bp.route("/fertilizer-suggestion")
@login_required
def fertilizer_suggestion():
    return render_template("feature_placeholder.html", page_key="nav_fertilizer", icon="fa-flask")


@main_bp.route("/irrigation-management")
@login_required
def irrigation_management():
    return render_template("feature_placeholder.html", page_key="nav_irrigation", icon="fa-faucet-drip")


@main_bp.route("/pest-prediction")
@login_required
def pest_prediction():
    return render_template("feature_placeholder.html", page_key="nav_pest", icon="fa-bug")


@main_bp.route("/yield-prediction")
@login_required
def yield_prediction():
    return render_template("feature_placeholder.html", page_key="nav_yield", icon="fa-chart-line")


@main_bp.route("/subsidy-loans")
@login_required
def subsidy_loans():
    return render_template("feature_placeholder.html", page_key="nav_subsidy", icon="fa-hand-holding-dollar")


@main_bp.route("/ai-assistant")
@login_required
def ai_assistant():
    return render_template("feature_placeholder.html", page_key="nav_assistant", icon="fa-robot")


@main_bp.route("/community-forum")
@login_required
def community_forum():
    return render_template("feature_placeholder.html", page_key="nav_forum", icon="fa-comments")


@main_bp.route("/expert-consultation")
@login_required
def expert_consultation():
    return render_template("feature_placeholder.html", page_key="nav_consultation", icon="fa-user-doctor")


# ---------------------------------------------------------
# Language switch (works on any page)
# ---------------------------------------------------------
@main_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in ("en", "bn"):
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.dashboard"))
