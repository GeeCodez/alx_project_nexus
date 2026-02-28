from django.contrib import admin
from .models import Order, OrderItem
from .services import update_order_status


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
    readonly_fields = ("user", "total_amount", "currency", "payment_reference", "created_at")
    inlines = (OrderItemInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self,request,obj,form,change):
        if change:
            old_obj=Order.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                update_order_status(obj, obj.status)
                return
        super().save_model(request,obj,form,change)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            obj_id = request.resolver_match.kwargs.get("object_id") #type: ignore
            if obj_id:
                order = Order.objects.get(pk=obj_id)
                allowed = Order.STATUS_TRANSITIONS.get(order.status, []) #type: ignore
                kwargs["choices"] = [
                    (choice, label)
                    for choice, label in db_field.choices #type: ignore
                    if choice == order.status or choice in allowed
                ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "unit_price", "total_price")
    readonly_fields = ("order", "product", "product_name", "quantity", "unit_price", "total_price")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
