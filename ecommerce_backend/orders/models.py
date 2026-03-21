from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from products.models import Product
from phonenumber_field.modelfields import PhoneNumberField



class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    STATUS_TRANSITIONS = {
        Status.PENDING: [Status.PAID, Status.CANCELLED],
        Status.PAID: [Status.PROCESSING, Status.CANCELLED],
        Status.PROCESSING: [Status.SHIPPED],
        Status.SHIPPED: [Status.DELIVERED],
        Status.DELIVERED: [],
        Status.CANCELLED: []
    }

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    # phone_number=PhoneNumberField(max_length=20,null=True, blank=True) # for unauthenticated users
    # person_name=models.CharField(max_length=50,null=True,blank=True) # for unauthenticated users
    # pick_up_point=models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="GHS")
    payment_reference = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"]), models.Index(fields=["created_at"])]

    def clean(self):
        if self.pk:
            old = Order.objects.get(pk=self.pk)
            if old.status != self.status:
                allowed = self.STATUS_TRANSITIONS.get(old.status, []) #type: ignore
                if self.status not in allowed:
                    raise ValidationError(f"Invalid status transition from {old.status} to {self.status}")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def cancel(self):
        if self.Status.CANCELLED not in self.STATUS_TRANSITIONS.get(self.status, []): #type: ignore
            raise ValidationError("Cannot cancel this order at its current stage")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def __str__(self):
        return f"Order {self.id} - {self.user}"


class OrderItem(models.Model):

    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        indexes = [models.Index(fields=["order"]), models.Index(fields=["product"])]

    def save(self, *args, **kwargs):
        if self.quantity is not None and self.unit_price is not None:
            self.total_price = Decimal(self.quantity) * self.unit_price
        else:
            self.total_price = Decimal("0.00")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
