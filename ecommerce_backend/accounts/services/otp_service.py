from accounts.utils import create_and_send_otp, verify_otp, check_otp_cooldown

class OTPService:
    @staticmethod
    def send_registration_otp(email):
        return create_and_send_otp(email)

    @staticmethod
    def verify_registration_otp(email,code):
        return verify_otp(email,code,"registration")

    @staticmethod
    def check_registration_cooldown(email):
        return check_otp_cooldown(email)