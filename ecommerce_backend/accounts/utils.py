from django.conf import settings
import random
from django.contrib.auth.hashers import make_password, check_password
from accounts.models.otp_models import OTP
from datetime import timedelta
from django.utils import timezone
from accounts.infrastructure.email_service import EmailService

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 3
OTP_RESEND_COOLDOWN = 60  # seconds

def generate_otp():
    return str(random.randint(100000,999999))

def create_and_send_otp(email=None, purpose="registration"):
    OTP.objects.filter(email=email, purpose=purpose, is_used=False).update(is_used=True)

    code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp = OTP.objects.create(
        email=email,
        otp=make_password(str(code)),
        purpose=purpose,
        expires_at=expires_at,
    )
    try:
        EmailService.send_otp_email(email, code, purpose) # type: ignore
    except Exception as e:
        return f"Failed to send OTP email to {email}: {e}"
    return otp
    


def verify_otp(email, code, purpose="registration"):
    otp = OTP.objects.filter(
        email=email,
        purpose=purpose,
        is_used=False
    ).order_by("-created_at").first()

    if not otp:
        return False, "Invalid OTP"

    if otp.is_expired():
        return False, "OTP expired"

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        return False, "Too many attempts"

    if not check_password(str(code), otp.otp):
        otp.attempts += 1
        otp.save()
        return False, "Invalid OTP"

    updated = OTP.objects.filter(
        id=otp.id, #type:ignore
        is_used=False
    ).update(is_used=True)

    if not updated:
        return False, "OTP already used"
    otp.save()

    return True, "OTP verified"


def check_otp_cooldown(email, purpose="registration"):
    last_otp = OTP.objects.filter(
        email=email,
        purpose=purpose
    ).order_by("-created_at").first()

    if not last_otp:
        return True, 0

    elapsed = (timezone.now() - last_otp.created_at).total_seconds()

    if elapsed < OTP_RESEND_COOLDOWN:
        retry_after = int(OTP_RESEND_COOLDOWN - elapsed)
        return False, retry_after

    return True, 0
