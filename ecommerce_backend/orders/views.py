from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import Order, OrderItem
from .serializers import OrderSerializer

class OrderViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.CreateModelMixin,GenericViewSet,):
    serializer_class = OrderSerializer
    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        order_items_qs = OrderItem.objects.select_related("product")

        return (
                Order.objects
                .filter(user=user)
                .select_related("user")
                .prefetch_related(Prefetch("items", queryset=order_items_qs))
            )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        try:
            order.cancel()
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": "Order cancelled successfully"},
            status=status.HTTP_200_OK
        )
    
class GuestOrderTrackingViewSet(mixins.RetrieveModelMixin,GenericViewSet,):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    lookup_field = "tracking_token"

    def get_queryset(self):
        order_items_qs = OrderItem.objects.select_related("product")

        return (
            Order.objects
            .select_related("user")
            .prefetch_related(Prefetch("items", queryset=order_items_qs))
        )