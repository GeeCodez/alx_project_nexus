from accounts.throttles import OTPThrottle
from rest_framework import generics, permissions
from rest_framework.response import Response
from accounts.services.otp_services import AuthOTPService
from accounts.serializers.otp_serializers import(
    VerifyOTPSerializer,
    ResendOTPSerializer
)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        success, message = AuthOTPService.verify_registration_otp(email,code)

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

        allowed, data = AuthOTPService.resend_registration_otp(email)

        if not allowed:
            return Response(
                data,
                status=429
            )

        return Response(data)
