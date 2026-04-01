"""
-- AMW Django ERP - Sales Models --

Constitution Alignment:
- Section 8.4: Soft Delete Rule (all models use SoftDeleteMixin)
- Section 9.2: Sales Snapshots (pricing and shipping address preserved)
- Section 9.5: Financial Precision (Decimal 19,4 for all currency fields)
- Section 8.6: Atomic Safety (operations use transaction.atomic)
- Section 8.7: Audit Rule (all state changes logged)

Models:
- CustomerCategory: Hierarchical customer categorization
- Customer: Customer records with shipping address
- SalesOrder: Order header with snapshot and payment tracking
- SalesOrderItem: Order line items with frozen pricing
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from core.models import SoftDeleteModel


class CustomerCategory(SoftDeleteModel):
    """
    Hierarchical customer categorization.

    Supports parent-child relationships for customer segments.
    Example: Corporate -> Enterprise, Corporate -> SMB
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Corporate', 'Retail')",
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
        db_table = "sales_customer_categories"
        verbose_name = "Customer Category"
        verbose_name_plural = "Customer Categories"
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


class Customer(SoftDeleteModel):
    """
    Customer model for CRM and sales orders.

    Constitution Section 9.2: Shipping address is snapshotted to SalesOrder at order time.
    """

    # -- Identity Fields --
    name = models.CharField(
        max_length=200,
        help_text="Customer name (individual or company)",
    )
    email = models.EmailField(
        blank=True,
        help_text="Customer email address",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Customer phone number",
    )

    # -- Categorization --
    category = models.ForeignKey(
        CustomerCategory,
        on_delete=models.PROTECT,
        related_name="customers",
        help_text="Customer category/segment",
    )

    # -- Address Information (snapshotted to orders) --
    shipping_address = models.TextField(
        blank=True,
        help_text="Default shipping address (snapshotted to SalesOrder at order time)",
    )
    billing_address = models.TextField(
        blank=True,
        help_text="Billing address (if different from shipping)",
    )

    # -- Metadata --
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this customer",
    )

    class Meta:
        db_table = "sales_customers"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
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
            raise ValidationError("Customer name is required")


class OrderStatus(models.TextChoices):
    """
    Order status state machine.

    Flow: Draft -> Confirmed -> Shipped
    Voided: Only for un-shipped orders (Draft or Confirmed)
    """

    DRAFT = "DRAFT", "Draft"
    CONFIRMED = "CONFIRMED", "Confirmed"
    SHIPPED = "SHIPPED", "Shipped"
    VOIDED = "VOIDED", "Voided"


class PaymentStatus(models.TextChoices):
    """Payment status for order tracking."""

    PENDING = "PENDING", "Pending"
    PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
    PAID = "PAID", "Paid"


class PaymentMethod(models.TextChoices):
    """Payment method choices."""

    COD = "COD", "Cash on Delivery"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    CREDIT_CARD = "CREDIT_CARD", "Credit Card"


class SalesOrder(SoftDeleteModel):
    """
    Sales order header with snapshot fields and payment tracking.

    Constitution Section 9.2:
    - shipping_address_snapshot: Copied from Customer at order time
    - snapshot pricing preserved on SalesOrderItem

    Constitution Section 9.5:
    - All currency fields use DecimalField(19,4)
    - Order numbering is atomic and unique (#Eg-00001 format)
    """

    # -- Order Identification --
    order_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Atomic unique order number (format: #Eg-00001)",
        editable=False,
    )

    # -- Customer Link --
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
        help_text="Customer who placed this order",
    )

    # -- Snapshot Fields (Constitution 9.2) --
    shipping_address_snapshot = models.TextField(
        blank=True,
        help_text="Shipping address copied from Customer at order time",
    )

    # -- Status & Payment --
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT,
        help_text="Order status (Draft → Confirmed → Shipped → Voided)",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Payment status (Pending, Partially Paid, Paid)",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        blank=True,
        help_text="Payment method (COD, Bank Transfer, Credit Card)",
    )
    amount_paid = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Amount paid so far (for partial payment tracking)",
    )

    # -- Financial Fields (Constitution 9.5: Decimal 19,4) --
    subtotal = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Order subtotal (sum of line item totals)",
        editable=False,
    )
    tax_amount = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Tax amount",
        editable=False,
    )
    total_amount = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        default=Decimal("0.0000"),
        help_text="Order total (subtotal + tax)",
        editable=False,
    )

    # -- Actor & Timestamps --
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales_orders_created",
        help_text="Employee who created this order",
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sales_orders_confirmed",
        help_text="Employee who confirmed this order",
    )
    shipped_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sales_orders_shipped",
        help_text="Employee who marked this order as shipped",
    )
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sales_orders_voided",
        help_text="Employee who voided this order",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Order creation timestamp",
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Order confirmation timestamp",
    )
    shipped_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Order shipped timestamp",
    )
    voided_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Order voided timestamp",
    )

    # -- Notes --
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes about this order",
    )

    class Meta:
        db_table = "sales_orders"
        verbose_name = "Sales Order"
        verbose_name_plural = "Sales Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["customer", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["payment_status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"

    def clean(self):
        # Validate payment amount
        if self.amount_paid > self.total_amount:
            raise ValidationError("Amount paid cannot exceed total amount")

        # Validate status transitions
        if self.pk:
            old_instance = SalesOrder.objects.get(pk=self.pk)
            self._validate_status_transition(old_instance.status, self.status)

    def _validate_status_transition(self, old_status, new_status):
        """Validate order status transitions."""
        valid_transitions = {
            OrderStatus.DRAFT: [OrderStatus.CONFIRMED, OrderStatus.VOIDED],
            OrderStatus.CONFIRMED: [OrderStatus.SHIPPED, OrderStatus.VOIDED],
            OrderStatus.SHIPPED: [],  # Terminal state
            OrderStatus.VOIDED: [],  # Terminal state
        }
        if new_status not in valid_transitions.get(old_status, []):
            raise ValidationError(
                f"Invalid status transition from {old_status} to {new_status}"
            )

    def get_amount_due(self):
        """Calculate remaining amount due."""
        return self.total_amount - self.amount_paid

    def update_payment_status(self):
        """Update payment_status based on amount_paid."""
        if self.amount_paid >= self.total_amount:
            self.payment_status = PaymentStatus.PAID
        elif self.amount_paid > Decimal("0"):
            self.payment_status = PaymentStatus.PARTIALLY_PAID
        else:
            self.payment_status = PaymentStatus.PENDING


class SalesOrderItem(SoftDeleteModel):
    """
    Sales order line item with frozen pricing.

    Constitution Section 9.2:
    - snapshot_unit_price: Frozen at order time (19,4 precision)
    - Does not change if Product price changes later
    """

    # -- Order Link --
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Parent sales order",
    )

    # -- Product Link --
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="sales_order_items",
        help_text="Product being ordered",
    )

    # -- Quantity & Pricing (Constitution 9.5: Decimal 19,4) --
    quantity = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Quantity ordered",
    )
    snapshot_unit_price = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Unit price frozen at order time (19,4 precision)",
    )
    total_price = models.DecimalField(
        max_digits=19,
        decimal_places=4,
        help_text="Line total (quantity × snapshot_unit_price)",
        editable=False,
    )

    # -- Notes --
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Line item notes",
    )

    class Meta:
        db_table = "sales_order_items"
        verbose_name = "Sales Order Item"
        verbose_name_plural = "Sales Order Items"
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.product.sku} × {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculate total_price before saving
        self.total_price = self.quantity * self.snapshot_unit_price
        super().save(*args, **kwargs)

    def clean(self):
        if self.quantity <= Decimal("0"):
            raise ValidationError("Quantity must be positive")
        if self.snapshot_unit_price < Decimal("0"):
            raise ValidationError("Unit price cannot be negative")
