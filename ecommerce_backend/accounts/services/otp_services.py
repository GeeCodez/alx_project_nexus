from django.contrib.auth import get_user_model
from accounts.utils import create_and_send_otp, verify_otp, resend_otp


User = get_user_model()
purpose="registration"
class AuthOTPService:
    @staticmethod
    def send_registration_otp(email):
        return create_and_send_otp(email,purpose)
    
    @staticmethod
    def verify_registration_otp(email, code):
        """
        Verify OTP and activate user
        """
        success, message = verify_otp(email, code, purpose)

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
        #function defined in utils
        resend_otp(email,purpose)