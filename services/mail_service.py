"""
Amar Krishi - Mail Service
Generates and sends one-time codes for email verification and password reset.
"""

import random
import traceback
from datetime import datetime, timedelta

from flask import current_app
from flask_mail import Mail, Message

from models.models import db, EmailOTP

mail = Mail()


def _generate_code():
    return f"{random.randint(0, 999999):06d}"


def create_otp(user, purpose):
    """Create and store a fresh OTP."""
    EmailOTP.query.filter_by(
        user_id=user.user_id,
        purpose=purpose,
        used=False
    ).update({"used": True})

    expiry_minutes = current_app.config.get("OTP_EXPIRY_MINUTES", 10)

    otp = EmailOTP(
        user_id=user.user_id,
        code=f"{random.randint(0,999999):06d}",
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes),
    )

    db.session.add(otp)
    db.session.commit()

    return otp


def send_otp_email(user, otp, purpose):
    """Send OTP email."""

    subject_map = {
        "verify_email": "Verify your Amar Krishi Account",
        "reset_password": "Reset Your Amar Krishi Password",
    }

    body_map = {
        "verify_email": (
            f"Hi {user.name},\n\n"
            f"Your Amar Krishi verification code is:\n\n"
            f"{otp.code}\n\n"
            f"This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES',10)} minutes.\n\n"
            f"Thank you."
        ),

        "reset_password": (
            f"Hi {user.name},\n\n"
            f"Your password reset code is:\n\n"
            f"{otp.code}\n\n"
            f"This code expires in {current_app.config.get('OTP_EXPIRY_MINUTES',10)} minutes.\n\n"
            f"Thank you."
        )
    }

    if not current_app.config.get("MAIL_CONFIGURED"):
        current_app.logger.warning(
            "MAIL NOT CONFIGURED -> OTP for %s (%s): %s",
            user.email,
            purpose,
            otp.code
        )
        return True, "logged"

    try:
        current_app.logger.info("========== SMTP DEBUG ==========")
        current_app.logger.info(f"MAIL_SERVER={current_app.config.get('MAIL_SERVER')}")
        current_app.logger.info(f"MAIL_PORT={current_app.config.get('MAIL_PORT')}")
        current_app.logger.info(f"MAIL_USERNAME={current_app.config.get('MAIL_USERNAME')}")
        current_app.logger.info(f"MAIL_USE_TLS={current_app.config.get('MAIL_USE_TLS')}")
        current_app.logger.info(f"MAIL_USE_SSL={current_app.config.get('MAIL_USE_SSL')}")
        current_app.logger.info(f"Sending mail to {user.email}")

        msg = Message(
            subject=subject_map.get(purpose, "Amar Krishi OTP"),
            sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
            recipients=[user.email],
            body=body_map.get(purpose, f"Your OTP is {otp.code}")
        )

        mail.send(msg)

        current_app.logger.info("EMAIL SENT SUCCESSFULLY")
        current_app.logger.info("===============================")

        return True, "sent"

    except Exception as e:
        current_app.logger.error("========== SMTP ERROR ==========")
        current_app.logger.error(str(e))
        current_app.logger.error(traceback.format_exc())
        current_app.logger.error("===============================")

        return False, str(e)


def verify_otp(user, code, purpose):
    """Verify submitted OTP."""

    otp = (
        EmailOTP.query.filter_by(
            user_id=user.user_id,
            purpose=purpose,
            used=False
        )
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
