import random
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from accounts.models.otp_models import OTP
from accounts.infrastructure.email_service import EmailService

User = get_user_model()

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 3

def generate_otp():
    return str(random.randint(100000, 999999))

@transaction.atomic
def request_password_reset(email):
    user = User.objects.filter(email=email).first()

    if not user:
        return True, "If this email exists, an OTP has been sent."

    OTP.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    raw_otp = generate_otp()
    purpose="Password reset"
    otp_obj = OTP.objects.create(
        user=user,
        otp=make_password(raw_otp),
        expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )

    try:
        EmailService.send_otp_email(email, raw_otp, purpose) #type:ignore
    except Exception:
        otp_obj.lock()
        return False, "Failed to send OTP."

    return True, "If this email exists, an OTP has been sent."

@transaction.atomic
def verify_password_reset_otp(email, code, purpose='password_reset'):
    user = User.objects.filter(email=email).first()
    if not user:
        return False, "Invalid OTP."

    otp_obj = (
        OTP.objects
        .filter(user=user, is_used=False)
        .order_by("-created_at")
        .first()
    )

    if not otp_obj:
        return False, "Invalid OTP."

    if otp_obj.is_expired():
        otp_obj.lock()
        return False, "OTP expired."

    if otp_obj.attempts >= OTP_MAX_ATTEMPTS:
        otp_obj.lock()
        return False, "Too many attempts."

    if not check_password(code, otp_obj.otp):
        otp_obj.increment_attempts()
        return False, "Invalid OTP."

    updated = OTP.objects.filter(
        id=otp_obj.id, #type: ignore
        is_used=False
    ).update(is_used=True)

    if not updated:
        return False, "OTP already used."

    return True, "OTP verified."

@transaction.atomic
def reset_password(email, new_password):
    user = User.objects.filter(email=email).first()
    if not user:
        return False, "Invalid request."

    user.set_password(new_password)
    user.save(update_fields=["password"])

    # Invalidate all remaining reset OTPs
    OTP.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)

    return True, "Password reset successful."