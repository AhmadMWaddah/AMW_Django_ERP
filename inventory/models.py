"""
-- AMW Django ERP - Inventory Models --

Constitution Alignment:
- Section 6.4: Soft Delete Rule (Category, Product use SoftDeleteModel)
- Section 6.5: Stock Valuation Rule (WAC on stock-in)
- Section 6.6: Atomic Safety Rule (operations use transaction.atomic)
- Section 6.7: Audit Rule (all stock movements logged)

Models:
- Category: Hierarchical product categorization
- Product: SKU-based product catalog with controlled stock
- StockTransaction: Immutable ledger for all stock movements
- StockAdjustment: Managed stock corrections with approval workflow
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now

from core.models import SoftDeleteModel


class Category(SoftDeleteModel):
    """
    Hierarchical category model for product organization.

    Supports parent-child relationships for category trees.
    Example: Appliances -> Major Appliances -> Refrigerators

    Constitution Section 6.4: Uses soft delete for historical visibility.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Major Appliances')",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text="URL-friendly slug (e.g., 'major-appliances')",
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
        db_table = "inventory_categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness by appending random suffix if needed
            base_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def clean(self):
        # Prevent circular references
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


class Product(SoftDeleteModel):
    """
    Product model with SKU-based identification and controlled stock.

    Constitution Section 9.1:
    - current_stock is controlled field (not directly edited)
    - Stock movement represented by transaction ledger
    - WAC price tracked for valuation

    SKU Pattern: CATEGORY-SUBCATEGORY-MODEL (e.g., WM-CR-159)
    """

    # -- Identity Fields --
    sku = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique SKU code (e.g., 'WM-CR-159' for Washing Machine Crazy 159)",
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text="URL-friendly slug (e.g., 'wm-cr-159')",
    )
    name = models.CharField(
        max_length=200,
        help_text="Product name",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        help_text="Product category",
    )

    # -- Unit of Measure --
    UNIT_OF_MEASURE_CHOICES = [
        ("pcs", "Pieces"),
        ("kg", "Kilograms"),
        ("g", "Grams"),
        ("l", "Liters"),
        ("ml", "Milliliters"),
        ("m", "Meters"),
        ("cm", "Centimeters"),
        ("box", "Boxes"),
        ("pack", "Packs"),
    ]
    unit_of_measure = models.CharField(
        max_length=10,
        choices=UNIT_OF_MEASURE_CHOICES,
        default="pcs",
        help_text="Unit of measure for this product",
    )

    # -- Controlled Stock Fields (Constitution 9.1) --
    current_stock = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Current stock quantity (controlled by operations layer)",
        editable=False,
    )
    wac_price = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Weighted Average Cost price (19,4 precision)",
        editable=False,
    )

    # -- Metadata --
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Product description",
    )
    location_note = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Storage location note (e.g., 'Warehouse A, Shelf 5')",
    )

    class Meta:
        db_table = "inventory_products"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["sku"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["category", "sku"]),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def save(self, *args, **kwargs):
        # Auto-generate slug from SKU if not provided
        if not self.slug:
            self.slug = slugify(self.sku)
            # Ensure uniqueness by appending random suffix if needed
            base_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def clean(self):
        # Validate SKU format (should contain at least one hyphen)
        if "-" not in self.sku:
            raise ValidationError("SKU should follow pattern CATEGORY-SUBCATEGORY-MODEL (e.g., 'WM-CR-159')")

    def get_stock_value(self):
        """Calculate total stock value (quantity × WAC price)."""
        return self.current_stock * self.wac_price


class StockChangeType(models.TextChoices):
    """
    Enumeration of stock change types for StockTransaction.

    These types determine whether WAC should be recalculated:
    - INTAKE, ADJUST_ADD: Recalculate WAC (stock-in at cost)
    - Others: Do NOT recalculate WAC (stock-out or non-cost movements)
    """

    INTAKE = "INTAKE", "Stock Intake (Purchase)"
    ADJUST_ADD = "ADJUST_ADD", "Manual Add (Correction)"
    ADJUST_REDUCE = "ADJUST_REDUCE", "Manual Reduce (Correction)"
    SALE = "SALE", "Sale Order Deduction"
    PURCHASE = "PURCHASE", "Purchase Order Receipt"
    TRANSFER = "TRANSFER", "Warehouse Transfer"
    RETURN = "RETURN", "Customer Return"
    DAMAGE = "DAMAGE", "Damage/Loss Write-off"


class StockTransaction(models.Model):
    """
    Immutable ledger for all stock movements.

    Constitution Section 6.6: Every stock change must be recorded atomically.
    Constitution Section 6.7: All movements are auditable.

    This model is IMMUTABLE - once created, it cannot be modified.
    Use StockAdjustment for corrections.
    """

    # -- Transaction Details --
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        help_text="Product affected by this transaction",
    )
    change_type = models.CharField(
        max_length=20,
        choices=StockChangeType.choices,
        help_text="Type of stock change",
    )
    quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Quantity changed (positive for in, negative for out)",
    )
    unit_cost = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Unit cost for this transaction (for WAC calculation)",
    )

    # -- State After Transaction --
    balance_before = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Stock balance before this transaction",
    )
    balance_after = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Stock balance after this transaction",
    )
    wac_before = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="WAC price before this transaction",
    )
    wac_after = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="WAC price after this transaction",
    )

    # -- Reference Information --
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type of reference document (e.g., 'PurchaseOrder', 'SalesOrder')",
    )
    reference_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="ID of reference document",
    )
    location_note = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Storage location (if different from product default)",
    )

    # -- Actor and Timestamp --
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_transactions",
        help_text="Employee who created this transaction",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Transaction timestamp",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this transaction",
    )

    class Meta:
        db_table = "inventory_stock_transactions"
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["change_type", "-created_at"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]

    def __str__(self):
        return f"{self.product.sku} - {self.get_change_type_display()} - {self.quantity} @ {self.created_at}"

    def save(self, *args, **kwargs):
        # Enforce immutability
        if self.pk:
            raise ValidationError("StockTransaction is immutable and cannot be modified")
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        # Prevent deletion - use StockAdjustment for corrections
        raise ValidationError("StockTransaction is immutable. Use StockAdjustment for corrections.")


class StockAdjustmentStatus(models.TextChoices):
    """Status workflow for stock adjustments."""

    PENDING = "PENDING", "Pending Approval"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    EXECUTED = "EXECUTED", "Executed"


class StockAdjustment(SoftDeleteModel):
    """
    Stock adjustment workflow model.

    Used for manual stock corrections that require approval.
    Separates the adjustment REQUEST from the actual TRANSACTION.

    Workflow:
    1. Create adjustment (status: PENDING)
    2. Approve adjustment (status: APPROVED)
    3. Execute adjustment (status: EXECUTED, creates StockTransaction)
    """

    # -- Adjustment Details --
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="adjustments",
        help_text="Product to adjust",
    )
    old_quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Current stock quantity before adjustment",
    )
    new_quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Target stock quantity after adjustment",
    )
    reason = models.CharField(
        max_length=50,
        choices=[
            ("DAMAGE", "Damage/Loss"),
            ("FOUND", "Stock Found"),
            ("CORRECTION", "Inventory Correction"),
            ("EXPIRY", "Expiry Write-off"),
            ("OTHER", "Other"),
        ],
        help_text="Reason for adjustment",
    )

    # -- Status Workflow --
    status = models.CharField(
        max_length=20,
        choices=StockAdjustmentStatus.choices,
        default=StockAdjustmentStatus.PENDING,
        help_text="Adjustment status",
    )

    # -- Approval Information --
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="adjustment_requests",
        help_text="Employee who requested the adjustment",
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Request timestamp",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_adjustments",
        help_text="Employee who approved the adjustment",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Approval timestamp",
    )
    executed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Execution timestamp (when transaction was created)",
    )
    rejection_comment = models.TextField(
        blank=True,
        null=True,
        help_text="Required comment when rejecting adjustment (explains why)",
    )

    # -- Notes and Reference --
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the adjustment",
    )
    location_note = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Storage location note",
    )

    class Meta:
        db_table = "inventory_stock_adjustments"
        verbose_name = "Stock Adjustment"
        verbose_name_plural = "Stock Adjustments"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status", "-requested_at"]),
            models.Index(fields=["product", "status"]),
        ]

    def __str__(self):
        return f"Adjustment {self.product.sku}: {self.old_quantity} → {self.new_quantity} ({self.status})"

    def clean(self):
        # Validate quantity change
        if self.new_quantity < 0:
            raise ValidationError("New quantity cannot be negative")

    def get_quantity_change(self):
        """Calculate the quantity change (positive or negative)."""
        return self.new_quantity - self.old_quantity

    def approve(self, approver):
        """Approve the adjustment (does not execute it)."""
        if self.status != StockAdjustmentStatus.PENDING:
            raise ValidationError("Only pending adjustments can be approved")
        self.status = StockAdjustmentStatus.APPROVED
        self.approved_by = approver
        self.approved_at = now()
        self.save(update_fields=["status", "approved_by", "approved_at"])

    def reject(self, approver, comment=None):
        """
        Reject the adjustment.

        Args:
            approver: Employee rejecting the adjustment
            comment: Required comment explaining the rejection reason

        Raises:
            ValidationError: If adjustment is not PENDING or comment is not provided
        """
        if self.status != StockAdjustmentStatus.PENDING:
            raise ValidationError("Only pending adjustments can be rejected")
        if not comment:
            raise ValidationError("Rejection requires a comment explaining the reason")
        self.status = StockAdjustmentStatus.REJECTED
        self.approved_by = approver
        self.approved_at = now()
        self.rejection_comment = comment
        self.save(update_fields=["status", "approved_by", "approved_at", "rejection_comment"])

    def mark_executed(self):
        """Mark adjustment as executed (called after transaction creation)."""
        if self.status != StockAdjustmentStatus.APPROVED:
            raise ValidationError("Only approved adjustments can be executed")
        self.status = StockAdjustmentStatus.EXECUTED
        self.executed_at = now()
        self.save(update_fields=["status", "executed_at"])
