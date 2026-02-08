from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference",
        "user",
        "order",
        "amount",
        "status",
        "provider",
        "created_at",
    )
    list_filter = ("status", "provider", "created_at")
    search_fields = ("reference", "user__email")