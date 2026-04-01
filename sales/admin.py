"""
-- AMW Django ERP - Sales Admin --

Registers sales models in Django admin for CRM and order management.
"""

from django.contrib import admin
from django.utils.html import format_html

from sales.models import (
    Customer,
    CustomerCategory,
    SalesOrder,
    SalesOrderItem,
    OrderStatus,
    PaymentStatus,
)


@admin.register(CustomerCategory)
class CustomerCategoryAdmin(admin.ModelAdmin):
    """Admin interface for CustomerCategory model."""

    list_display = ["name", "code", "parent", "deleted_at_display"]
    list_filter = ["parent"]
    search_fields = ["name", "code", "description"]
    ordering = ["name"]
    readonly_fields = ["created_at", "modified_at", "deleted_at"]

    fieldsets = (
        ("Category Details", {"fields": ("name", "code", "parent", "description")}),
        ("Status", {"fields": ("deleted_at", "created_at", "modified_at")}),
    )

    def deleted_at_display(self, obj):
        return "Yes" if obj.deleted_at else "No"
    deleted_at_display.short_description = "Deleted"


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer model."""

    list_display = ["name", "email", "phone", "category", "deleted_at_display"]
    list_filter = ["category"]
    search_fields = ["name", "email", "phone"]
    ordering = ["name"]
    readonly_fields = ["created_at", "modified_at", "deleted_at"]

    fieldsets = (
        ("Customer Details", {"fields": ("name", "email", "phone", "category")}),
        ("Addresses", {"fields": ("shipping_address", "billing_address")}),
        ("Notes", {"fields": ("notes",)}),
        ("Status", {"fields": ("deleted_at", "created_at", "modified_at")}),
    )

    def deleted_at_display(self, obj):
        return "Yes" if obj.deleted_at else "No"
    deleted_at_display.short_description = "Deleted"


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    """Admin interface for SalesOrder model."""

    list_display = [
        "order_number",
        "customer",
        "status_badge",
        "payment_status_badge",
        "total_amount",
        "amount_paid",
        "created_at",
    ]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["order_number", "customer__name"]
    ordering = ["-created_at"]
    readonly_fields = [
        "order_number",
        "customer",
        "shipping_address_snapshot",
        "status",
        "payment_status",
        "payment_method",
        "amount_paid",
        "subtotal",
        "tax_amount",
        "total_amount",
        "created_by",
        "created_at",
        "confirmed_by",
        "confirmed_at",
        "shipped_by",
        "shipped_at",
        "voided_by",
        "voided_at",
        "deleted_at",
    ]

    fieldsets = (
        ("Order Information", {"fields": ("order_number", "customer", "created_at")}),
        ("Snapshot", {"fields": ("shipping_address_snapshot",)}),
        ("Status & Payment", {
            "fields": (
                "status",
                "payment_status",
                "payment_method",
                "amount_paid",
            )
        }),
        ("Financials", {
            "fields": ("subtotal", "tax_amount", "total_amount"),
            "description": "All amounts use Decimal 19,4 precision",
        }),
        ("Workflow", {
            "fields": (
                "created_by", "created_at",
                "confirmed_by", "confirmed_at",
                "shipped_by", "shipped_at",
                "voided_by", "voided_at",
            )
        }),
        ("Notes", {"fields": ("notes",)}),
    )

    inlines = []  # Will add SalesOrderItemInline below

    actions = ["confirm_selected_orders", "void_selected_orders"]

    def status_badge(self, obj):
        colors = {
            OrderStatus.DRAFT: "gray",
            OrderStatus.CONFIRMED: "blue",
            OrderStatus.SHIPPED: "green",
            OrderStatus.VOIDED: "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def payment_status_badge(self, obj):
        colors = {
            PaymentStatus.PENDING: "gray",
            PaymentStatus.PARTIALLY_PAID: "orange",
            PaymentStatus.PAID: "green",
        }
        color = colors.get(obj.payment_status, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = "Payment"

    def confirm_selected_orders(self, request, queryset):
        """Bulk confirm selected draft orders."""
        from sales.operations.orders import confirm_order

        confirmed_count = 0
        for order in queryset.filter(status=OrderStatus.DRAFT):
            try:
                confirm_order(order, request.user)
                confirmed_count += 1
            except Exception as e:
                self.message_user(request, f"Failed to confirm {order.order_number}: {str(e)}")
        self.message_user(request, f"Confirmed {confirmed_count} orders")

    confirm_selected_orders.short_description = "Confirm selected draft orders"

    def void_selected_orders(self, request, queryset):
        """Bulk void selected orders."""
        from sales.operations.orders import void_order

        voided_count = 0
        for order in queryset.filter(status__in=[OrderStatus.DRAFT, OrderStatus.CONFIRMED]):
            try:
                void_order(order, request.user, reason="Bulk void via admin")
                voided_count += 1
            except Exception as e:
                self.message_user(request, f"Failed to void {order.order_number}: {str(e)}")
        self.message_user(request, f"Voided {voided_count} orders")

    void_selected_orders.short_description = "Void selected orders (Draft/Confirmed only)"


class SalesOrderItemInline(admin.TabularInline):
    """Inline admin for SalesOrderItem."""

    model = SalesOrderItem
    extra = 0
    readonly_fields = [
        "snapshot_unit_price",
        "total_price",
    ]
    fields = [
        "product",
        "quantity",
        "snapshot_unit_price",
        "total_price",
    ]

    def has_add_permission(self, request, obj=None):
        # Only allow adding items to draft orders
        if obj and obj.status != "DRAFT":
            return False
        return True

    def has_change_permission(self, request, obj=None):
        # Only allow editing draft orders
        if obj and obj.status != "DRAFT":
            return False
        return True


# Register inline with SalesOrderAdmin
SalesOrderAdmin.inlines = [SalesOrderItemInline]


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for SalesOrderItem model."""

    list_display = ["order", "product", "quantity", "snapshot_unit_price", "total_price"]
    list_filter = ["order__status"]
    search_fields = ["order__order_number", "product__name"]
    ordering = ["order", "id"]
    readonly_fields = ["snapshot_unit_price", "total_price", "deleted_at"]

    fieldsets = (
        ("Order Link", {"fields": ("order", "product")}),
        ("Pricing (Constitution 9.5: Decimal 19,4)", {
            "fields": ("quantity", "snapshot_unit_price", "total_price"),
            "description": "Unit price is frozen at order time and never changes",
        }),
        ("Notes", {"fields": ("notes",)}),
    )
