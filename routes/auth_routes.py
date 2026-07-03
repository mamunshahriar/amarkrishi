"""
Amar Krishi - Authentication Routes
Handles registration, login, logout, and forgot-password UI.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember_me")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.user_id
            session["user_name"] = user.name
            session.permanent = bool(remember)
            flash("success", "login_success")
            return redirect(url_for("main.dashboard"))

        flash("error", "invalid_credentials")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        phone = request.form.get("phone", "").strip()
        district = request.form.get("district", "")

        if password != confirm:
            flash("error", "password_mismatch")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("error", "email_exists")
            return redirect(url_for("auth.register"))

        new_user = User(name=name, email=email, phone=phone, district=district)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("success", "registration_success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        # Demo only: in production, send a real reset-token email here.
        flash("success", "reset_link_sent")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
