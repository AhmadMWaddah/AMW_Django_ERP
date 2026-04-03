"""
-- AMW Django ERP - Purchasing Models --

Constitution Alignment:
- Section 8.4: Soft Delete Rule (all models use SoftDeleteMixin)
- Section 8.5: Stock Valuation Rule (WAC recalculation on receipt)
- Section 8.6: Atomic Safety (operations use transaction.atomic)
- Section 8.7: Audit Rule (all state changes logged)
- Section 9.5: Financial Precision (Decimal 19,4 for all currency fields)

Models:
- SupplierCategory: Hierarchical supplier categorization
- Supplier: Supplier records with contact info
- PurchaseOrder: Purchase order header with supplier snapshot
- PurchaseOrderItem: Order line items with unit cost
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from core.models import SoftDeleteModel


class SupplierCategory(SoftDeleteModel):
    """
    Hierarchical supplier categorization.

    Supports parent-child relationships for supplier segments.
    Example: Raw Materials -> Metals, Electronics
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Raw Materials', 'Electronics')",
    )
    code = models.SlugField(
        unique=True,
        blank=True,
        help_text="Auto-generated slug code",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent category (for hierarchical structure)",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Category description",
    )

    class Meta:
        db_table = "purchasing_supplier_categories"
        verbose_name = "Supplier Category"
        verbose_name_plural = "Supplier Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        if self.parent and self.parent.pk == self.pk:
            raise ValidationError("Category cannot be its own parent")

    def get_full_path(self):
        """Return full category path including ancestors."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " / ".join(path)


class Supplier(SoftDeleteModel):
    """
    Supplier model for procurement workflows.

    Constitution Section 8.4: Uses SoftDeleteMixin for historical visibility.
    """

    # -- Identity Fields --
    name = models.CharField(
        max_length=200,
        help_text="Supplier name (individual or company)",
    )
    email = models.EmailField(
        blank=True,
        help_text="Supplier email address",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Supplier phone number",
    )

    # -- Categorization --
    category = models.ForeignKey(
        SupplierCategory,
        on_delete=models.PROTECT,
        related_name="suppliers",
        help_text="Supplier category",
    )

    # -- Address Information --
    address = models.TextField(
        blank=True,
        help_text="Supplier physical address",
    )
    contact_person = models.CharField(
        max_length=200,
        blank=True,
        help_text="Primary contact person name",
    )

    # -- Metadata --
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this supplier",
    )

    class Meta:
        db_table = "purchasing_suppliers"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["category", "name"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name.strip():
            raise ValidationError("Supplier name is required")


class POStatus(models.TextChoices):
    """
    Purchase order status state machine.

    Flow: Draft -> Issued -> In-Progress -> Completed
    Cancelled: From Draft, Issued, or In-Progress
    """

    DRAFT = "DRAFT", "Draft"
    ISSUED = "ISSUED", "Issued"
    IN_PROGRESS = "IN_PROGRESS", "In-Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class PurchaseOrder(SoftDeleteModel):
    """
    Purchase order header with supplier snapshot and tracking.

    Constitution Section 9.2:
    - supplier_info_snapshot: Copied from Supplier at order confirmation

    Constitution Section 9.5:
    - All currency fields use DecimalField(19,4)
    - Order numbering is atomic and unique (PO-00001 format)
    """

    # -- Order Identification --
    po_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Atomic unique PO number (format: PO-00001)",
        editable=False,
    )

    # -- Supplier Link --
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        help_text="Supplier for this purchase order",
    )

    # -- Snapshot Fields (Constitution 9.2) --
    supplier_info_snapshot = models.JSONField(
        blank=True,
        null=True,
        help_text="Supplier info copied at order confirmation",
    )

    # -- Status --
    status = models.CharField(
        max_length=20,
        choices=POStatus.choices,
        default=POStatus.DRAFT,
        help_text="PO status (Draft -> Issued -> In-Progress -> Completed -> Cancelled)",
    )

    # -- Financial Fields (Constitution 9.5: Decimal 19,4) --
    total_cost = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Total cost of all line items",
        editable=False,
    )

    # -- Actor & Timestamps --
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="purchase_orders_created",
        help_text="Employee who created this PO",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_orders_issued",
        help_text="Employee who issued this PO",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_orders_completed",
        help_text="Employee who completed this PO",
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_orders_cancelled",
        help_text="Employee who cancelled this PO",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="PO creation timestamp",
    )
    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="PO issued timestamp",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="PO completed timestamp",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="PO cancelled timestamp",
    )

    # -- Notes --
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes about this PO",
    )

    class Meta:
        db_table = "purchasing_orders"
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["po_number"]),
            models.Index(fields=["supplier", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"

    def clean(self):
        if self.pk:
            old_instance = PurchaseOrder.objects.get(pk=self.pk)
            self._validate_status_transition(old_instance.status, self.status)

    def _validate_status_transition(self, old_status, new_status):
        """Validate PO status transitions."""
        valid_transitions = {
            POStatus.DRAFT: [POStatus.ISSUED, POStatus.CANCELLED],
            POStatus.ISSUED: [POStatus.IN_PROGRESS, POStatus.CANCELLED],
            POStatus.IN_PROGRESS: [POStatus.COMPLETED, POStatus.CANCELLED],
            POStatus.COMPLETED: [],  # Terminal state
            POStatus.CANCELLED: [],  # Terminal state
        }
        if new_status not in valid_transitions.get(old_status, []):
            raise ValidationError(f"Invalid status transition from {old_status} to {new_status}")

    def is_fully_received(self):
        """Check if all items have been fully received."""
        return all(item.is_fully_received() for item in self.items.all())

    def get_received_total(self):
        """Calculate total cost of received items."""
        return sum(item.received_quantity * item.unit_cost for item in self.items.all())


class PurchaseOrderItem(SoftDeleteModel):
    """
    Purchase order line item with unit cost.

    Constitution Section 9.5:
    - unit_cost: DecimalField(19,4) precision
    """

    # -- Order Link --
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Parent purchase order",
    )

    # -- Product Link --
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="purchase_order_items",
        help_text="Product being ordered",
    )

    # -- Quantity & Pricing (Constitution 9.5: Decimal 19,4) --
    quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Quantity ordered",
    )
    received_quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Quantity received so far (for partial receiving)",
    )
    unit_cost = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Unit cost from supplier (19,4 precision)",
    )
    total_cost = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Line total (quantity * unit_cost)",
        editable=False,
    )

    class Meta:
        db_table = "purchasing_order_items"
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self):
        return f"{self.order.po_number} - {self.product.sku} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def clean(self):
        if self.quantity <= Decimal("0"):
            raise ValidationError("Quantity must be positive")
        if self.unit_cost < Decimal("0"):
            raise ValidationError("Unit cost cannot be negative")
        if self.received_quantity > self.quantity:
            raise ValidationError(
                f"Received quantity ({self.received_quantity}) " f"cannot exceed ordered quantity ({self.quantity})"
            )

    def is_fully_received(self):
        """Check if this line item has been fully received."""
        return self.received_quantity >= self.quantity

    def get_remaining_quantity(self):
        """Calculate remaining quantity to receive."""
        return max(Decimal("0"), self.quantity - self.received_quantity)
