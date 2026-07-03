"""
Amar Krishi - Database Models (SQLAlchemy ORM)
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    district = db.Column(db.String(100))
    land_size = db.Column(db.Numeric(6, 2), default=0)
    preferred_crops = db.Column(db.String(255))
    profile_image = db.Column(db.String(255), default="default-farmer.png")
    language_pref = db.Column(db.String(2), default="bn")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    disease_reports = db.relationship("DiseaseReport", backref="user", lazy=True, cascade="all, delete-orphan")
    recommendations = db.relationship("CropRecommendation", backref="user", lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="user", lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class Crop(db.Model):
    __tablename__ = "crops"

    crop_id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    crop_name_bn = db.Column(db.String(100))
    season = db.Column(db.String(20), nullable=False)
    soil_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    expected_yield = db.Column(db.String(100))
    growing_time_days = db.Column(db.Integer)
    profit_level = db.Column(db.String(10), default="Medium")
    market_demand = db.Column(db.String(10), default="Medium")
    water_requirement = db.Column(db.String(10), default="Medium")
    image = db.Column(db.String(255))


class Disease(db.Model):
    __tablename__ = "diseases"

    disease_id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(150), nullable=False)
    disease_name_bn = db.Column(db.String(150))
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.crop_id"))
    symptoms = db.Column(db.Text)
    possible_cause = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prevention = db.Column(db.Text)
    medicine = db.Column(db.String(255))


class DiseaseReport(db.Model):
    __tablename__ = "disease_reports"

    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey("diseases.disease_id"))
    image_path = db.Column(db.String(255), nullable=False)
    result = db.Column(db.String(150))
    confidence = db.Column(db.Numeric(5, 2))
    detection_date = db.Column(db.DateTime, default=datetime.utcnow)


class CropRecommendation(db.Model):
    __tablename__ = "crop_recommendations"

    recommendation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.crop_id"), nullable=False)
    district = db.Column(db.String(100))
    soil_type = db.Column(db.String(100))
    water_availability = db.Column(db.String(50))
    season = db.Column(db.String(50))
    recommendation_date = db.Column(db.DateTime, default=datetime.utcnow)


class MarketPrice(db.Model):
    __tablename__ = "market_prices"

    price_id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey("crops.crop_id"), nullable=False)
    market_name = db.Column(db.String(150), nullable=False)
    district = db.Column(db.String(100))
    price_per_kg = db.Column(db.Numeric(8, 2), nullable=False)
    previous_price = db.Column(db.Numeric(8, 2))
    update_date = db.Column(db.Date, default=datetime.utcnow)

    crop = db.relationship("Crop")


class Weather(db.Model):
    __tablename__ = "weather"

    weather_id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Numeric(4, 1))
    humidity = db.Column(db.Integer)
    wind_speed = db.Column(db.Numeric(4, 1))
    rain_probability = db.Column(db.Integer)
    alert_type = db.Column(db.String(20), default="None")
    alert_severity = db.Column(db.String(10), default="Low")
    best_irrigation_time = db.Column(db.String(100))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # Income / Expense
    category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    note = db.Column(db.String(255))
    transaction_date = db.Column(db.Date, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(10), default="Unread")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
