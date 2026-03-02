import random,secrets
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from accounts.utils import verify_otp,create_and_send_otp
from accounts.models.otp_models import OTP
from accounts.infrastructure.email_service import EmailService

User = get_user_model()
purpose="password_reset"
OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 3

def generate_otp():
    return str(random.randint(100000, 999999))

def request_password_reset(email):
    user = User.objects.filter(email=email).first()

    if not user:
        return True, "If this email exists, an OTP has been sent."

    return create_and_send_otp(email,purpose)

@transaction.atomic
def verify_password_reset_otp(email, code, purpose='password_reset'):
    user = User.objects.filter(email=email).first()
    if not user:
        return False, "Invalid OTP."

    success, message = verify_otp(email, code, purpose)

    if not success:
        return False, message

    # Generate reset token
    raw_token = secrets.token_urlsafe(32)

    otp_instance = OTP.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False
    ).latest("created_at")

    otp_instance.reset_token = make_password(raw_token)
    otp_instance.reset_token_expires_at = timezone.now() + timezone.timedelta(minutes=OTP_EXPIRY_MINUTES)
    otp_instance.save(update_fields=["reset_token"])

    return True, raw_token
   

@transaction.atomic
def reset_password(email, new_password, reset_token):
    user = User.objects.filter(email=email).first()
    if not user:
        return False, "Invalid request."

    otp_instance = OTP.objects.filter(
        user=user,
        purpose="password_reset",
        is_used=False
    ).latest("created_at")

    if not otp_instance.reset_token:
        return False, "Unauthorized."
    
    if otp_instance.is_reset_token_expired():
        return False, "Reset token has expired."

    if not check_password(reset_token, otp_instance.reset_token):
        return False, "Invalid token."

    user.set_password(new_password)
    user.save(update_fields=["password"])

    otp_instance.is_used = True
    otp_instance.save(update_fields=["is_used"])

    return True, "Password reset successful."