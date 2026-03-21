from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework.views import APIView
class APIRootSerializer(serializers.Serializer):
    name=serializers.CharField()
class APIRootView(APIView):
    permission_classes = [AllowAny]
    serializer_class = APIRootSerializer 

    def get(self, request, *args, **kwargs):
        return Response({
            "admin":request.build_absolute_uri("/admin/"),
            "products": request.build_absolute_uri("/api/products/"),
            "orders": request.build_absolute_uri("/api/orders/"),
            "payments": request.build_absolute_uri("/api/payments/"),
            "accounts": request.build_absolute_uri("/api/accounts/"),
        })