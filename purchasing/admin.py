"""
-- AMW Django ERP - Purchasing Admin --

Registers all purchasing models with appropriate admin integration.
"""

from django.contrib import admin

from core.admin import SoftDeleteAdminMixin
from purchasing.models import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierCategory


@admin.register(SupplierCategory)
class SupplierCategoryAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ["name", "slug", "parent", "deleted_display"]
    list_filter = ["parent"]
    search_fields = ["name", "slug"]
    ordering = ["name"]


@admin.register(Supplier)
class SupplierAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = ["name", "email", "phone", "category", "deleted_display"]
    list_filter = ["category"]
    search_fields = ["name", "email", "phone"]
    ordering = ["name"]


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    readonly_fields = ["total_cost"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = [
        "po_number",
        "supplier",
        "status",
        "total_cost",
        "created_by",
        "created_at",
        "deleted_display",
    ]
    list_filter = ["status", "supplier"]
    search_fields = ["po_number", "supplier__name"]
    readonly_fields = [
        "po_number",
        "supplier_info_snapshot",
        "total_cost",
        "created_by",
        "created_at",
        "issued_by",
        "issued_at",
        "completed_by",
        "completed_at",
        "cancelled_by",
        "cancelled_at",
    ]
    ordering = ["-created_at"]
    inlines = [PurchaseOrderItemInline]

    def save_model(self, request, obj, form, change):
        """Auto-set created_by to the current user on creation."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status in ("COMPLETED",):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(SoftDeleteAdminMixin, admin.ModelAdmin):
    list_display = [
        "order",
        "product",
        "quantity",
        "received_quantity",
        "unit_cost",
        "total_cost",
        "is_fully_received",
        "deleted_display",
    ]
    list_filter = ["order__status"]
    search_fields = ["order__po_number", "product__sku", "product__name"]
    readonly_fields = ["total_cost"]
    ordering = ["order", "id"]
