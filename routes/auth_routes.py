"""
Amar Krishi - Authentication Routes
Handles registration, login, logout, email verification (OTP), and
OTP-based password reset.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.models import db, User
from services.mail_service import create_otp, send_otp_email, verify_otp

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember_me")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if current_app.config.get("REQUIRE_EMAIL_VERIFICATION") and not user.is_verified:
                session["pending_verification_user_id"] = user.user_id
                flash("error", "verify_email_first")
                return redirect(url_for("auth.verify_email"))

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

        if current_app.config.get("REQUIRE_EMAIL_VERIFICATION"):
            otp = create_otp(new_user, "verify_email")
            send_otp_email(new_user, otp, "verify_email")
            session["pending_verification_user_id"] = new_user.user_id
            flash("success", "verification_code_sent")
            return redirect(url_for("auth.verify_email"))

        flash("success", "registration_success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    user_id = session.get("pending_verification_user_id")
    user = User.query.get(user_id) if user_id else None

    if not user:
        flash("error", "session_expired")
        return redirect(url_for("auth.login"))

    if user.is_verified:
        session.pop("pending_verification_user_id", None)
        flash("success", "already_verified")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        is_valid, reason = verify_otp(user, code, "verify_email")

        if is_valid:
            user.is_verified = True
            db.session.commit()
            session.pop("pending_verification_user_id", None)
            flash("success", "email_verified")
            return redirect(url_for("auth.login"))

        flash("error", f"otp_{reason}")
        return redirect(url_for("auth.verify_email"))

    return render_template("verify_email.html", email=user.email)


@auth_bp.route("/verify-email/resend")
def resend_verification():
    user_id = session.get("pending_verification_user_id")
    user = User.query.get(user_id) if user_id else None
    if user and not user.is_verified:
        otp = create_otp(user, "verify_email")
        send_otp_email(user, otp, "verify_email")
        flash("success", "verification_code_sent")
    return redirect(url_for("auth.verify_email"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        # Always show the same success message whether or not the email
        # exists, so the form can't be used to enumerate registered accounts.
        if user:
            otp = create_otp(user, "reset_password")
            send_otp_email(user, otp, "reset_password")
            session["pending_reset_user_id"] = user.user_id

        flash("success", "reset_code_sent")
        return redirect(url_for("auth.reset_password"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    user_id = session.get("pending_reset_user_id")
    user = User.query.get(user_id) if user_id else None

    if not user:
        flash("error", "session_expired")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        new_password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if new_password != confirm:
            flash("error", "password_mismatch")
            return redirect(url_for("auth.reset_password"))

        is_valid, reason = verify_otp(user, code, "reset_password")
        if not is_valid:
            flash("error", f"otp_{reason}")
            return redirect(url_for("auth.reset_password"))

        user.set_password(new_password)
        db.session.commit()
        session.pop("pending_reset_user_id", None)
        flash("success", "password_reset_success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", email=user.email)


@auth_bp.route("/reset-password/resend")
def resend_reset_code():
    user_id = session.get("pending_reset_user_id")
    user = User.query.get(user_id) if user_id else None
    if user:
        otp = create_otp(user, "reset_password")
        send_otp_email(user, otp, "reset_password")
        flash("success", "reset_code_sent")
    return redirect(url_for("auth.reset_password"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
