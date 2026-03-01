from accounts.services.password_reset_service import request_password_reset,verify_password_reset_otp, reset_password
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accounts.serializers.password_reset_serializers import (
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
    PasswordResetConfirmSerializer,
)


class PasswordResetRequestView(APIView):

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"] # type: ignore

        success, message = request_password_reset(email)

        # Always return 200 to prevent enumeration
        return Response(
            {"message": message},
            status=status.HTTP_200_OK
        )

class PasswordResetVerifyView(APIView):

    def post(self, request):
        serializer = PasswordResetVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"] #type:ignore
        otp = serializer.validated_data["otp"] #type:ignore

        success, message = verify_password_reset_otp(email, otp)

        if not success:
            return Response(
                {"message": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": message},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"] #type:ignore
        new_password = serializer.validated_data["new_password"] #type:ignore

        success, message = reset_password(email, new_password)

        if not success:
            return Response(
                {"message": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": message},
            status=status.HTTP_200_OK
        )