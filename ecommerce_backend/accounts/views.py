import email
from .models import User
from rest_framework.throttling import AnonRateThrottle
from .throttles import OTPThrottle
# from .permissions import AnonymousOnly
from rest_framework import generics, permissions
from rest_framework.response import Response
from .utils import create_and_send_otp, verify_otp, check_otp_cooldown
from .serializers import(
    RegisterSerializer,
    LoginSerializer,
    VerifyOTPSerializer,
    UserSerializer,
    ResendOTPSerializer
)


class APIRootView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "register": request.build_absolute_uri("/api/accounts/register/"),
            "login": request.build_absolute_uri("/api/accounts/login/"),
            "me": request.build_absolute_uri("/api/accounts/me/"),
        })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        create_and_send_otp(email=user.email, purpose="registration")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Registration successful. Please check your email for the OTP to verify your account."})

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        success, message = verify_otp(email, code, "registration")

        if not success:
            return Response({"error": message}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({"message": "Account verified successfully"})

class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        allowed, retry_after = check_otp_cooldown(email, "registration")

        if not allowed:
            return Response(
                {
                    "error": "OTP recently sent",
                    "retry_after": retry_after
                },
                status=429
            )

        create_and_send_otp(email=email, purpose="registration")

        return Response({"message": "OTP resent successfully"})