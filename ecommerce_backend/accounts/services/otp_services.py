from django.contrib.auth import get_user_model
from accounts.utils import create_and_send_otp, verify_otp, check_otp_cooldown


User = get_user_model()

class OTPService:
    @staticmethod
    def send_registration_otp(email):
        return create_and_send_otp(email)
    
    @staticmethod
    def verify_registration_otp(email, code):
        """
        Verify OTP and activate user
        """
        success, message = verify_otp(email, code)

        if not success:
            return False, message

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return False, "User not found"

        user.is_active = True
        user.save(update_fields=["is_active"])

        return True, "Account verified successfully"

    @staticmethod
    def resend_registration_otp(email):
        """
        Resend OTP with cooldown check
        """
        allowed, retry_after = check_otp_cooldown(email)

        if not allowed:
            return False, {
                "error": "OTP recently sent",
                "retry_after": retry_after
            }

        create_and_send_otp(email=email)
        return True, {"message": "OTP resent successfully"}