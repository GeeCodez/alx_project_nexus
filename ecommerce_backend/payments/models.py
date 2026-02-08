import uuid
from django.conf import settings
from django.db import models

class Payment(models.Model):
    class Status(models.TextChoices):
        INITIALIZED = "initialized", "Initialized"
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        ABANDONED = "abandoned", "Abandoned"
        REFUNDED = "refunded", "Refunded"

    class Provider(models.TextChoices):
        PAYSTACK = "paystack", "Paystack"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="GHS")
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.PAYSTACK)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIALIZED, db_index=True)
    reference = models.CharField(max_length=150, unique=True, db_index=True)
    provider_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} - {self.reference} - {self.status}"