from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Prefetch

from .models import Order, OrderItem
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["get", "post", "patch"]  # restrict attack surface

    # 🔥 Query Optimization (Very Important)
    def get_queryset(self):

        queryset = (
            Order.objects
            .filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("product")
                )
            )
        )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Order updates not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # ✅ Cancel Order Endpoint
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):

        order = self.get_object()

        if order.status in ["shipped", "delivered"]:
            return Response(
                {"detail": "Cannot cancel shipped or delivered order"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == "cancelled":
            return Response(
                {"detail": "Order already cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = "cancelled"
        order.save(update_fields=["status"])

        return Response(
            {"detail": "Order cancelled successfully"},
            status=status.HTTP_200_OK
        )