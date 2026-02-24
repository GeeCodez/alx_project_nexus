import django
from django.core.mail import send_mail
import africastalking
from django.conf import settings
import random
from django.contrib.auth.hashers import make_password, check_password
from accounts.models import OTP
from datetime import timedelta
from django.utils import timezone
from .models import OTP

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 3
OTP_RESEND_COOLDOWN = 60  # seconds

def generate_otp():
    return str(random.randint(100000,999999))
    
def send_otp_email(email, code):
    subject = "Your Verification Code"
    message = f"Your OTP code is {code}. It expires in 5 minutes."

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def create_and_send_otp(email=None, purpose="registration"):
    # invalidate old OTPs
    OTP.objects.filter(email=email, purpose=purpose, is_used=False).update(is_used=True)

    code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp = OTP.objects.create(
        email=email,
        code=make_password(str(code)),
        purpose=purpose,
        expires_at=expires_at,
    )
    try:
        send_otp_email(email, code)
    except Exception as e:
        print(f"Failed to send OTP email to {email}: {e}")
        # logger.error(f"Failed to send OTP email to {email}: {e}")
    return otp
    #to be assigned to celery later

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

    if not check_password(str(code), otp.code):
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

# africastalking.initialize(
#     username=settings.AFRICASTALKING_USERNAME,
#     api_key=settings.AFRICASTALKING_API_KEY,
# )

# sms = africastalking.SMS


# def send_otp_sms(phone_number, code):
#     message = f"Your OTP code is {code}. It expires in 5 minutes."

#     try:
#         response = sms.send( # type: ignore
#             message,
#             [str(phone_number)],
#             enqueue=True   # important fix
#         ) #type: ignore
#         print(response)
#         return response
#     except Exception as e:
#         print("SMS sending failed:", e)
#         return None