"""
Amar Krishi - Mail Service
Generates and sends one-time codes for email verification and password reset.

If MAIL_USERNAME / MAIL_PASSWORD are not configured (e.g. local dev without
SMTP credentials), the code is written to the server log instead of emailed,
so development is never blocked on having a mailbox set up.
"""

import random
from datetime import datetime, timedelta

from flask import current_app
from flask_mail import Mail, Message

from models.models import db, EmailOTP

mail = Mail()


def _generate_code():
    return f"{random.randint(0, 999999):06d}"


def create_otp(user, purpose):
    """Create (and persist) a fresh OTP for the given user/purpose, invalidating older ones."""
    EmailOTP.query.filter_by(user_id=user.user_id, purpose=purpose, used=False).update({"used": True})

    expiry_minutes = current_app.config.get("OTP_EXPIRY_MINUTES", 10)
    otp = EmailOTP(
        user_id=user.user_id,
        code=_generate_code(),
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
    )
    db.session.add(otp)
    db.session.commit()
    return otp


def send_otp_email(user, otp, purpose):
    """Send the OTP by email. Falls back to logging it if SMTP isn't configured."""
    subject_map = {
        "verify_email": "Verify your Amar Krishi account",
        "reset_password": "Reset your Amar Krishi password",
    }
    body_map = {
        "verify_email": (
            f"Hi {user.name},\n\nYour Amar Krishi email verification code is: {otp.code}\n"
            f"This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.\n\n"
            "If you did not create this account, you can ignore this email."
        ),
        "reset_password": (
            f"Hi {user.name},\n\nYour Amar Krishi password reset code is: {otp.code}\n"
            f"This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.\n\n"
            "If you did not request a password reset, you can ignore this email."
        ),
    }

    if not current_app.config.get("MAIL_CONFIGURED"):
        # Dev-friendly fallback: no SMTP creds set, so log instead of failing.
        current_app.logger.warning(
            "MAIL not configured — %s OTP for %s is: %s", purpose, user.email, otp.code
        )
        return True, "logged"

    try:
        msg = Message(
            subject=subject_map.get(purpose, "Amar Krishi Verification Code"),
            recipients=[user.email],
            body=body_map.get(purpose, f"Your code is {otp.code}"),
        )
        mail.send(msg)
        return True, "sent"
    except Exception as exc:  # noqa: BLE001 - we want a friendly message either way
        current_app.logger.error("Failed to send OTP email to %s: %s", user.email, exc)
        return False, "failed"


def verify_otp(user, code, purpose):
    """Validate a submitted code. Returns (is_valid, reason)."""
    otp = (
        EmailOTP.query.filter_by(user_id=user.user_id, purpose=purpose, used=False)
        .order_by(EmailOTP.created_at.desc())
        .first()
    )
    if not otp:
        return False, "no_code"
    if otp.is_expired():
        return False, "expired"
    otp.attempts = (otp.attempts or 0) + 1
    if otp.attempts > 5:
        otp.used = True
        db.session.commit()
        return False, "too_many_attempts"
    if otp.code != code.strip():
        db.session.commit()
        return False, "invalid"

    otp.used = True
    db.session.commit()
    return True, "ok"