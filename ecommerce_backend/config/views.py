# core/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class APIRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "products": request.build_absolute_uri("/api/products/"),
            "orders": request.build_absolute_uri("/api/orders/"),
            "payments": request.build_absolute_uri("/api/payments/"),
            "accounts": request.build_absolute_uri("/api/accounts/"),
            "categories": request.build_absolute_uri("/api/categories/"),
            # "docs": request.build_absolute_uri("/docs/"),
        })