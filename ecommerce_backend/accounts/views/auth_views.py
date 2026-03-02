from rest_framework.throttling import AnonRateThrottle
from rest_framework import generics, permissions
from rest_framework.response import Response
from accounts.services.auth_services import AuthService
from rest_framework.views import APIView
from rest_framework import status
from accounts.serializers.auth_serializers import(
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        AuthService.register_user(serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"message": "Registration successful. Please check your email for the OTP to verify your account."},
            status=201
        )

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