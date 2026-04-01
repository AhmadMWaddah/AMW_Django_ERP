"""
-- AMW Django ERP - Sales Order Operations --

Constitution Alignment:
- Section 8.1: Operations-First Business Logic (all order logic lives here)
- Section 8.6: Atomic Safety Rule (transaction.atomic + select_for_update)
- Section 8.7: Audit Rule (all state changes logged)
- Section 9.5: Financial Precision (Decimal 19,4, ROUND_HALF_UP)

Operations:
- confirm_order(): Atomic stock deduction via inventory.operations
- void_order(): Atomic inventory rollback
- calculate_order_totals(): Decimal precision calculations
- generate_order_number(): Atomic unique order numbering
"""

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from audit.logic.logging import log_audit
from inventory.operations.stock import stock_in, stock_out
from sales.logic.pricing import calculate_order_totals
from sales.models import OrderStatus, SalesOrder


def generate_order_number():
    """
    Generate atomic unique order number.

    Format: #Eg-00001 (configurable via ORDER_PREFIX setting)
    Uses database locking to ensure uniqueness.

    Constitution Section 9.5: Order numbering must be atomic and unique.

    Returns:
        str: New order number (e.g., "#Eg-00001")
    """
    from sales.models import SalesOrder

    # Get prefix from settings (default: "Eg")
    prefix = getattr(settings, "ORDER_PREFIX", "Eg")

    # Get the highest existing order number atomically
    last_order = (
        SalesOrder.objects.all_with_deleted()
        .filter(order_number__startswith=f"#{prefix}-")
        .order_by("-order_number")
        .first()
    )

    if last_order:
        # Extract the numeric part and increment
        try:
            last_num = int(last_order.order_number.split("-")[1])
            new_num = last_num + 1
        except (IndexError, ValueError):
            new_num = 1
    else:
        new_num = 1

    # Format with zero padding (5 digits)
    return f"#{prefix}-{new_num:05d}"


@transaction.atomic
def confirm_order(order, employee):
    """
    Confirm a sales order (Draft → Confirmed).

    Atomic operation that:
    1. Validates order can be confirmed
    2. Deducts stock for each order item via inventory.operations.stock.stock_out()
    3. Updates order status to CONFIRMED
    4. Logs audit trail

    Constitution Section 8.6: Uses select_for_update() for concurrency safety.
    Constitution Section 8.1: All logic in operations layer, not views.

    Args:
        order: SalesOrder instance to confirm
        employee: Employee confirming the order

    Returns:
        SalesOrder: Confirmed order

    Raises:
        ValueError: If order cannot be confirmed (wrong status, insufficient stock, etc.)
    """
    # Lock order for update (prevent concurrent modifications)
    order = SalesOrder.objects.select_for_update().get(pk=order.pk)

    # Validate status
    if order.status != OrderStatus.DRAFT:
        raise ValueError(f"Only DRAFT orders can be confirmed (current: {order.status})")

    # Validate order has items
    if not order.items.exists():
        raise ValueError("Cannot confirm order without items")

    # Capture state BEFORE
    old_status = order.status
    items_data = []

    # Process each order item - deduct stock
    for item in order.items.all():
        try:
            # Call inventory stock_out operation (atomic, with select_for_update)
            stock_out(
                product=item.product,
                quantity=item.quantity,
                employee=employee,
                change_type="SALE",
                reference_type="SalesOrder",
                reference_id=str(order.id),
                notes=f"Order {order.order_number} confirmed",
            )
            items_data.append({
                "product": str(item.product),
                "quantity": str(item.quantity),
            })
        except ValueError as e:
            # Rollback entire order if any item fails
            raise ValueError(f"Failed to deduct stock for {item.product.sku}: {str(e)}")

    # Update order status
    order.status = OrderStatus.CONFIRMED
    order.confirmed_by = employee
    order.confirmed_at = now()
    order.save(update_fields=["status", "confirmed_by", "confirmed_at"])

    # Audit log (Constitution 8.7)
    log_audit(
        actor=employee,
        action_code="sales.order.confirm",
        action="confirm",
        target=order,
        before={"status": old_status.value},
        after={"status": OrderStatus.CONFIRMED.value},
        extra_data={
            "order_number": order.order_number,
            "items": items_data,
            "total_amount": str(order.total_amount),
        },
    )

    return order


@transaction.atomic
def void_order(order, employee, reason=None):
    """
    Void a sales order (reverse stock deduction).

    Atomic operation that:
    1. Validates order can be voided (only Draft or Confirmed, not Shipped)
    2. Adds stock back for each order item via inventory.operations.stock.stock_in()
    3. Updates order status to VOIDED
    4. Logs audit trail

    Constitution Section 8.6: Uses select_for_update() for concurrency safety.
    Constitution Section 8.1: All logic in operations layer, not views.

    Args:
        order: SalesOrder instance to void
        employee: Employee voiding the order
        reason: Optional reason for voiding

    Returns:
        SalesOrder: Voided order

    Raises:
        ValueError: If order cannot be voided (already Shipped or Voided)
    """
    # Lock order for update
    order = SalesOrder.objects.select_for_update().get(pk=order.pk)

    # Validate status (can only void Draft or Confirmed)
    if order.status not in [OrderStatus.DRAFT, OrderStatus.CONFIRMED]:
        raise ValueError(
            f"Cannot void order with status {order.status}. "
            "Only Draft or Confirmed orders can be voided. "
            "Shipped orders require a return process."
        )

    # Capture state BEFORE
    old_status = order.status
    items_data = []

    # Process each order item - add stock back
    for item in order.items.all():
        try:
            # Call inventory stock_in operation (atomic, with select_for_update)
            stock_in(
                product=item.product,
                quantity=item.quantity,
                unit_cost=item.product.wac_price,  # Use current WAC for valuation
                employee=employee,
                change_type="SALE",  # Using SALE as reverse type
                reference_type="SalesOrder.Void",
                reference_id=str(order.id),
                notes=f"Order {order.order_number} voided: {reason or 'No reason provided'}",
            )
            items_data.append({
                "product": str(item.product),
                "quantity": str(item.quantity),
            })
        except Exception as e:
            # Rollback entire void if any item fails
            raise ValueError(f"Failed to restore stock for {item.product.sku}: {str(e)}")

    # Update order status
    order.status = OrderStatus.VOIDED
    order.voided_by = employee
    order.voided_at = now()
    order.save(update_fields=["status", "voided_by", "voided_at"])

    # Audit log (Constitution 8.7)
    log_audit(
        actor=employee,
        action_code="sales.order.void",
        action="void",
        target=order,
        before={"status": old_status.value},
        after={"status": OrderStatus.VOIDED.value},
        extra_data={
            "order_number": order.order_number,
            "reason": reason or "No reason provided",
            "items": items_data,
        },
    )

    return order


@transaction.atomic
def calculate_and_update_totals(order):
    """
    Calculate and update order totals.

    Constitution Section 9.5: Uses Decimal 19,4 precision with ROUND_HALF_UP.

    Args:
        order: SalesOrder instance to update

    Returns:
        SalesOrder: Order with updated totals
    """
    # Lock order for update
    order = SalesOrder.objects.select_for_update().get(pk=order.pk)

    # Calculate totals using pricing logic
    subtotal, tax_amount, total_amount = calculate_order_totals(order)

    # Update order
    order.subtotal = subtotal
    order.tax_amount = tax_amount
    order.total_amount = total_amount
    order.save(update_fields=["subtotal", "tax_amount", "total_amount"])

    return order


@transaction.atomic
def update_payment(order, amount, employee, notes=None):
    """
    Record a payment against an order.

    Updates amount_paid and payment_status automatically.

    Args:
        order: SalesOrder instance
        amount: Payment amount (Decimal)
        employee: Employee recording the payment
        notes: Optional payment notes

    Returns:
        SalesOrder: Order with updated payment tracking

    Raises:
        ValueError: If amount is invalid or exceeds total
    """
    # Lock order for update
    order = SalesOrder.objects.select_for_update().get(pk=order.pk)

    # Validate amount
    if amount <= Decimal("0"):
        raise ValueError("Payment amount must be positive")

    new_amount_paid = order.amount_paid + amount
    if new_amount_paid > order.total_amount:
        raise ValueError(
            f"Payment would exceed total. Current paid: {order.amount_paid}, "
            f"Total: {order.total_amount}, Attempted: {amount}"
        )

    # Capture state BEFORE
    old_payment_status = order.payment_status
    old_amount_paid = order.amount_paid

    # Update payment tracking
    order.amount_paid = new_amount_paid
    order.update_payment_status()
    order.save(update_fields=["amount_paid", "payment_status"])

    # Audit log
    log_audit(
        actor=employee,
        action_code="sales.order.payment",
        action="payment",
        target=order,
        before={
            "amount_paid": str(old_amount_paid),
            "payment_status": old_payment_status.value,
        },
        after={
            "amount_paid": str(order.amount_paid),
            "payment_status": order.payment_status.value,
        },
        extra_data={
            "order_number": order.order_number,
            "payment_amount": str(amount),
            "notes": notes or "",
        },
    )

    return order
