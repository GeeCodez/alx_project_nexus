from rest_framework import serializers
from accounts.models import User

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
                {"contact": "Either email or phone number is required"}
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
    
    def create(self, validated_data):
        if not validated_data.get("phone_number"):
            validated_data["phone_number"]=None
        if not validated_data.get("email"):
            validated_data["email"]=None
            
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

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
