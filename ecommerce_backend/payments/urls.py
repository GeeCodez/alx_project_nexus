from django.urls import path
from .views import (
    InitializePaymentAPIView,
    PaystackWebhookAPIView,
    RootView
)

urlpatterns = [
    path("",RootView.as_view(),name='payment-root'),
    path("initialize/", InitializePaymentAPIView.as_view(), name="payment-initialize"),
    path("webhook/paystack/", PaystackWebhookAPIView.as_view(), name="paystack-webhook"),
]