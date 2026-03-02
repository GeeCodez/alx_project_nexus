from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction, IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from accounts.services.otp_services import AuthOTPService
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthService:

    @staticmethod
    @transaction.atomic
    def register_user(validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        phone = validated_data.get("phone_number")
        password = validated_data.pop("password")

        try:
            user = User.objects.filter(username=username).first()

            if user and user.is_active:
                raise ValidationError(
                    "Unable to register with provided credentials."
                )
            
            if user:
                user.email = email
                user.phone_number = phone # type: ignore
                user.set_password(password)
                user.save()
                return user

            user = User(username=username,email=email,phone_number=phone,is_active=False)
            user.set_password(password)
            user.save()
            if email:
                AuthOTPService.send_registration_otp(email)
            return user

        except IntegrityError:
            raise ValidationError(
                "Unable to register with provided credentials."
            )

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