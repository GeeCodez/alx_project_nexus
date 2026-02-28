from rest_framework.throttling import AnonRateThrottle
from .throttles import OTPThrottle
from rest_framework import generics, permissions
from rest_framework.response import Response
from accounts.services.auth_services import AuthService
from rest_framework.views import APIView
from rest_framework import status
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
        user = AuthService.register_user(serializer)

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
        token=AuthService.login(**serializer.validated_data)
        return Response(token)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token=request.data["refresh"]
        
        success, message=AuthService.logout_user(refresh_token)

        if not success:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": message}, status.HTTP_205_RESET_CONTENT)

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

        success, message = AuthService.verify_registration_otp(email,code)

        if not success:
            return Response({"error": message}, status=400)

        return Response({"message": message})

class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        allowed, data = AuthService.resend_registration_otp(email)

        if not allowed:
            return Response(
                data,
                status=429
            )

        return Response(data)