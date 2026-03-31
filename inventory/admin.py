"""
-- AMW Django ERP - Inventory Admin --

Registers inventory models in Django admin for manual testing and management.
"""

from django.contrib import admin

from inventory.models import Category, Product, StockAdjustment, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""

    list_display = ["name", "code", "parent", "created_at"]
    list_filter = ["parent"]
    search_fields = ["name", "code", "description"]
    ordering = ["name"]
    readonly_fields = ["created_at", "modified_at", "deleted_at"]

    fieldsets = (
        ("Category Details", {"fields": ("name", "code", "parent", "description")}),
        ("Status", {"fields": ("deleted_at", "created_at", "modified_at")}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""

    list_display = [
        "sku",
        "name",
        "category",
        "current_stock",
        "wac_price",
        "unit_of_measure",
    ]
    list_filter = ["category", "unit_of_measure"]
    search_fields = ["sku", "name", "description"]
    ordering = ["sku"]
    readonly_fields = ["current_stock", "wac_price", "created_at", "modified_at", "deleted_at"]

    fieldsets = (
        (
            "Product Details",
            {
                "fields": (
                    "sku",
                    "name",
                    "category",
                    "description",
                    "unit_of_measure",
                    "location_note",
                )
            },
        ),
        (
            "Stock Information (Controlled)",
            {
                "fields": ("current_stock", "wac_price"),
                "description": "These fields are controlled by operations layer. Do not edit manually.",
            },
        ),
        (
            "Status",
            {"fields": ("deleted_at", "created_at", "modified_at")},
        ),
    )


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    """Admin interface for StockTransaction model."""

    list_display = [
        "product",
        "change_type",
        "quantity",
        "balance_after",
        "wac_after",
        "created_by",
        "created_at",
    ]
    list_filter = ["change_type", "product", "created_at"]
    search_fields = ["product__sku", "product__name", "reference_id"]
    ordering = ["-created_at"]
    readonly_fields = [
        "product",
        "change_type",
        "quantity",
        "unit_cost",
        "balance_before",
        "balance_after",
        "wac_before",
        "wac_after",
        "reference_type",
        "reference_id",
        "location_note",
        "created_by",
        "created_at",
        "notes",
    ]

    fieldsets = (
        (
            "Transaction Details",
            {
                "fields": (
                    "product",
                    "change_type",
                    "quantity",
                    "unit_cost",
                )
            },
        ),
        (
            "Stock State",
            {
                "fields": (
                    "balance_before",
                    "balance_after",
                    "wac_before",
                    "wac_after",
                ),
                "description": "Stock and WAC values before and after this transaction",
            },
        ),
        (
            "Reference",
            {
                "fields": (
                    "reference_type",
                    "reference_id",
                    "location_note",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "notes",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        # Prevent manual creation - use operations layer
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent modification - immutable ledger
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion - immutable ledger
        return False


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    """Admin interface for StockAdjustment model."""

    list_display = [
        "product",
        "old_quantity",
        "new_quantity",
        "get_quantity_change",
        "reason",
        "status",
        "requested_by",
        "requested_at",
    ]
    list_filter = ["status", "reason", "requested_at"]
    search_fields = ["product__sku", "product__name", "notes"]
    ordering = ["-requested_at"]
    readonly_fields = [
        "product",
        "old_quantity",
        "new_quantity",
        "reason",
        "status",
        "requested_by",
        "requested_at",
        "approved_by",
        "approved_at",
        "executed_at",
        "rejection_comment",
        "notes",
        "location_note",
        "deleted_at",
    ]

    fieldsets = (
        (
            "Adjustment Details",
            {
                "fields": (
                    "product",
                    "old_quantity",
                    "new_quantity",
                    "reason",
                    "location_note",
                )
            },
        ),
        (
            "Status",
            {"fields": ("status",)},
        ),
        (
            "Workflow",
            {
                "fields": (
                    "requested_by",
                    "requested_at",
                    "approved_by",
                    "approved_at",
                    "executed_at",
                    "rejection_comment",
                )
            },
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
    )

    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):
        """Bulk approve selected pending adjustments."""
        from inventory.operations.stock import approve_adjustment

        approved_count = 0
        for adjustment in queryset.filter(status="PENDING"):
            approve_adjustment(adjustment, request.user)
            approved_count += 1
        self.message_user(request, f"Approved {approved_count} adjustments")

    approve_selected.short_description = "Approve selected pending adjustments"

    def reject_selected(self, request, queryset):
        """Bulk reject selected pending adjustments."""
        rejected_count = 0
        for adjustment in queryset.filter(status="PENDING"):
            adjustment.reject(request.user, comment="Bulk rejected via admin action")
            rejected_count += 1
        self.message_user(request, f"Rejected {rejected_count} adjustments")

    reject_selected.short_description = "Reject selected pending adjustments"

    def get_quantity_change(self, obj):
        """Display quantity change."""
        change = obj.get_quantity_change()
        prefix = "+" if change >= 0 else ""
        return f"{prefix}{change}"

    get_quantity_change.short_description = "Change"
