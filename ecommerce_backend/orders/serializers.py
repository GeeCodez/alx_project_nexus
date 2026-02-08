from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from .models import Order, OrderItem
from products.models import Product

class OrderItemWriteSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive product")
        return value

class OrderItemReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
        )


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemWriteSerializer(many=True, write_only=True) #for write operitions
    order_items = OrderItemReadSerializer(
        source="items",
        many=True,
        read_only=True
    ) # for read operations

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "currency",
            "total_amount",
            "payment_reference",
            "created_at",
            "items",
            "order_items",
        )
        read_only_fields = (
            "id",
            "status",
            "total_amount",
            "payment_reference",
            "created_at",
        )

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        if not items_data:
            raise serializers.ValidationError(
                {"items": "Order must contain at least one item."}
            )

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                currency="GHS",
                total_amount=Decimal("0.00"),
            )

            total_order_amount = Decimal("0.00")
            order_items = []

            products = {
                p.id: p # type: ignore
                for p in Product.objects.filter(
                    id__in=[item["product_id"] for item in items_data]
                )
            }

            for item in items_data:
                product = products.get(item["product_id"])
                if not product:
                    raise serializers.ValidationError(
                        {"items": f"Invalid product ID {item['product_id']}"}
                    )

                quantity = item["quantity"]
                unit_price = product.price
                total_price = unit_price * quantity

                total_order_amount += total_price

                order_items.append(
                    OrderItem(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            order.total_amount = total_order_amount
            order.save(update_fields=["total_amount"])

        return order
