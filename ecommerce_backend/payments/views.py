import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import json

from orders.models import Order
from .serializers import InitializePaymentSerializer
from .services import initialize_paystack_payment, verify_paystack_payment
from .services import verify_paystack_signature, process_paystack_webhook
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class RootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return Response({
            "Root view for payments"
        })

class InitializePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InitializePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"] # type: ignore

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        #if order has already been paid for or cancelled, return error
        if order.status != "pending":
            return Response(
                {"detail": "Order cannot be paid for"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment, authorization_url = initialize_paystack_payment(
            order=order,
            user=request.user,
            email=request.user.email,
        )

        return Response(
            {
                "payment_id": payment.id,
                "reference": payment.reference,
                "authorization_url": authorization_url,
            },
            status=status.HTTP_201_CREATED
        )
    
@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        signature = request.headers.get("x-paystack-signature")

        if not signature:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not verify_paystack_signature(request.body, signature):
            return Response(status=status.HTTP_403_FORBIDDEN)

        event = json.loads(request.body)

        process_paystack_webhook(event)

        return Response(status=status.HTTP_200_OK)