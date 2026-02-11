from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "quantity", "unit_price", "total_price")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "currency", "payment_reference", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("id", "user__email", "payment_reference")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("user", "status", "total_amount", "currency", "payment_reference", "created_at")
    inlines = (OrderItemInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "unit_price", "total_price")
    readonly_fields = ("order", "product", "product_name", "quantity", "unit_price", "total_price")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False