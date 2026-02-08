from django.urls import path
from .views import (
    InitializePaymentAPIView,
    PaystackWebhookAPIView,
)

urlpatterns = [
    path("initialize/", InitializePaymentAPIView.as_view(), name="payment-initialize"),
    path("webhook/paystack/", PaystackWebhookAPIView.as_view(), name="paystack-webhook"),
]