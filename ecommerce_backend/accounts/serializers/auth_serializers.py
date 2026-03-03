from rest_framework import serializers
from accounts.models import User
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password")

    def validate(self, attrs):
        # Normalize first
        attrs["email"] = attrs.get("email") or None
        attrs["phone_number"] = attrs.get("phone_number") or None

        username = attrs.get("username")
        email = attrs.get("email")
        phone = attrs.get("phone_number")

        if not username:
            raise serializers.ValidationError(
                {"username": "Username is required."}
            )

        if not (email or phone):
            raise serializers.ValidationError(
                {"contact": "Either email or phone number is required"}
            )

        return attrs
    
    def validate_password(self,value):
        if len(value)<8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if not attrs.get("identifier") or not attrs.get("password"):
            raise serializers.ValidationError("Identifier and password required")
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "date_joined")
