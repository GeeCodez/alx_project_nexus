from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "total_price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "currency", "payment_reference", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("id", "user__email", "payment_reference")
    readonly_fields = ("created_at", "total_amount", "currency", "payment_reference")
    inlines = [OrderItemInline]
    ordering = ("-created_at",)
    date_hierarchy = "created_at"