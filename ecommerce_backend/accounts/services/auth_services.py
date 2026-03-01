from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from accounts.services.otp_services import OTPService
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthService:

    @staticmethod
    @transaction.atomic
    def register_user(serializer):
        """
        Register and send otp to user
        """
        user = serializer.save(is_active=False)
        OTPService.send_registration_otp(user.email)
        return user

    @staticmethod
    def logout_user(refresh_token):
        if not refresh_token:
            raise ValueError("Token must be provided")
        try:
            token= RefreshToken(refresh_token)
            token.blacklist()
            return True,"Logout successful"
        except Exception as e:
            return False, "Invalid token or token expired"
    
    @staticmethod
    def login(identifier,password):
        user=User.objects.filter(
            Q(username=identifier)
            | Q(email=identifier)
            | Q(phone_number=identifier)
        ).first()
        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")
        
        if not user.is_active:
            raise AuthenticationFailed("Account not active. Please verify your email.")
            
        refresh=RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }