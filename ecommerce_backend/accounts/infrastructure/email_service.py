from django.core.mail import send_mail
from django.conf import settings

class EmailService:
    
    @staticmethod
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