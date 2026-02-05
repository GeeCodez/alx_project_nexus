from rest_framework import serializers
from .models import User
from django.db.models import Q
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password")

    def validate(self, attrs):
        if not attrs.get("username"):
            raise serializers.ValidationError("Username is required.")

        if not (attrs.get("email") or attrs.get("phone_number")):
            raise serializers.ValidationError(
                "Provide either email or phone number."
            )
        return attrs
    
    def validate_password(self,value):
        if len(value)<8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = User.objects.filter(
            Q(username=identifier)
            | Q(email=identifier)
            | Q(phone_number=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "date_joined")