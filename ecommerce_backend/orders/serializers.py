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
        fields = ["id", "product", "product_name",
                  "quantity", "unit_price", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True, write_only=True)
    order_items = OrderItemReadSerializer(source="items", many=True, read_only=True)

    person_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    pick_up_point = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    tracking_token = serializers.UUIDField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "status", "currency", "total_amount", "payment_reference", 
            "created_at", "items", "order_items", "person_name", 
            "phone_number", "pick_up_point","tracking_token"
        ]
        read_only_fields = ["id", "status", "total_amount", "payment_reference", "created_at","tracking_token"]

    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data.pop("items")

        if not items_data:
            raise serializers.ValidationError({"items": "Order must contain at least one item."})

        if request.user.is_authenticated:
            user = request.user
            person_name = None
            phone_number = None
            pick_up_point = None
        else:
            user = None
            person_name = validated_data.get("person_name")
            phone_number = validated_data.get("phone_number")
            pick_up_point = validated_data.get("pick_up_point")

            if not person_name or not phone_number:
                raise serializers.ValisdationError({"detail": "Guest users must provide name and phone number."})

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                person_name=person_name,
                phone_number=phone_number,
                pick_up_point=pick_up_point,
                currency="GHS",
                total_amount=Decimal("0.00"),
            )

            total_order_amount = Decimal("0.00")
            order_items = []

            product_ids = [item["product_id"] for item in items_data]
            products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

            for item in items_data:
                product = products.get(item["product_id"])

                if not product:
                    raise serializers.ValidationError({"items": f"Invalid product ID {item['product_id']}"})

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
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.user is None:
            data["message"] = (
                "Please save your tracking token securely. "
                "You will need it to check your order status."
            )

        return data