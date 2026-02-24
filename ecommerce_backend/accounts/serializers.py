from sys import exception
from rest_framework import serializers
from .models import User
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import create_and_send_otp, verify_otp


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password")

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        phone = attrs.get("phone_number")

        if not username:
            raise serializers.ValidationError({"username": "Username is required."})

        if not (email or phone):
            raise serializers.ValidationError(
                {"contact": "Provide either email or phone number."}
            )

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already in use."})

        if phone and User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError({"phone_number": "Phone already in use."})

        return attrs
    
    def validate_password(self,value):
        if len(value)<8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if not identifier or not password:
            raise AuthenticationFailed("Identifier and password required")

        user = User.objects.filter(
            Q(username=identifier)
            | Q(email=identifier)
            | Q(phone_number=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("Account not verified")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "date_joined")


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()