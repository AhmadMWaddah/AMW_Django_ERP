"""
-- AMW Django ERP - Stock Operations --

Constitution Alignment:
- Section 6.1: Operations-First Business Logic (all stock changes go through here)
- Section 6.6: Atomic Safety Rule (transaction.atomic + select_for_update)
- Section 6.7: Audit Rule (all movements logged with before/after snapshots)

Usage:
    from inventory.operations.stock import stock_in, stock_out, adjust_stock

    # Stock intake (triggers WAC recalculation)
    stock_in(product, quantity, unit_cost, employee, change_type=StockChangeType.PURCHASE)

    # Stock reduction (no WAC recalculation)
    stock_out(product, quantity, employee, change_type=StockChangeType.SALE)

    # Manual adjustment (with approval workflow)
    adjust_stock(employee, product, new_quantity, reason="CORRECTION")
"""

from decimal import Decimal

from django.db import transaction
from django.utils.timezone import now

from audit.logic.logging import log_audit
from inventory.logic.valuation import calculate_wac, should_recalculate_wac
from inventory.models import Product, StockAdjustment, StockChangeType, StockTransaction


@transaction.atomic
def stock_in(
    product,
    quantity,
    unit_cost,
    employee,
    change_type=StockChangeType.PURCHASE,
    reference_type=None,
    reference_id=None,
    location_note=None,
    notes=None,
):
    """
    Add stock to inventory (triggers WAC recalculation).

    Constitution Section 6.6: Uses select_for_update() for concurrency safety.
    Constitution Section 6.5: Recalculates WAC on stock-in.

    Args:
        product: Product instance (will be locked for update)
        quantity: Quantity to add (must be positive)
        unit_cost: Cost per unit (for WAC calculation)
        employee: Employee performing the operation
        change_type: Type of stock-in (PURCHASE, INTAKE, ADJUST_ADD)
        reference_type: Reference document type (e.g., "PurchaseOrder")
        reference_id: Reference document ID
        location_note: Storage location (if different from product default)
        notes: Additional notes

    Returns:
        StockTransaction: Created transaction record

    Raises:
        ValueError: If quantity is not positive
    """
    if quantity <= Decimal("0"):
        raise ValueError("Quantity must be positive for stock-in")

    # Lock product row for update (prevent race conditions)
    product = Product.objects.select_for_update().get(pk=product.pk)

    # Capture state BEFORE
    old_quantity = product.current_stock
    old_wac = product.wac_price

    # Calculate new WAC if this is a WAC-triggering change type
    if should_recalculate_wac(change_type):
        new_wac = calculate_wac(old_quantity, old_wac, quantity, unit_cost)
    else:
        new_wac = old_wac

    # Calculate new quantity
    new_quantity = old_quantity + quantity

    # Update product (atomic)
    product.current_stock = new_quantity
    product.wac_price = new_wac
    product.save(update_fields=["current_stock", "wac_price"])

    # Create immutable transaction record
    transaction_record = StockTransaction.objects.create(
        product=product,
        change_type=change_type,
        quantity=quantity,
        unit_cost=unit_cost,
        balance_before=old_quantity,
        balance_after=new_quantity,
        wac_before=old_wac,
        wac_after=new_wac,
        reference_type=reference_type,
        reference_id=reference_id,
        location_note=location_note or product.location_note,
        created_by=employee,
        notes=notes,
    )

    # Audit log (Constitution 6.7)
    log_audit(
        actor=employee,
        action_code=f"inventory.stock.{change_type.value.lower()}",
        action="adjust",
        target=product,
        before={
            "current_stock": str(old_quantity),
            "wac_price": str(old_wac),
        },
        after={
            "current_stock": str(new_quantity),
            "wac_price": str(new_wac),
        },
        extra_data={
            "transaction_id": transaction_record.id,
            "change_type": change_type,
            "quantity": str(quantity),
            "unit_cost": str(unit_cost),
        },
    )

    return transaction_record


@transaction.atomic
def stock_out(
    product,
    quantity,
    employee,
    change_type=StockChangeType.SALE,
    reference_type=None,
    reference_id=None,
    location_note=None,
    notes=None,
):
    """
    Remove stock from inventory (does NOT trigger WAC recalculation).

    Constitution Section 6.6: Uses select_for_update() for concurrency safety.

    Args:
        product: Product instance (will be locked for update)
        quantity: Quantity to remove (must be positive)
        employee: Employee performing the operation
        change_type: Type of stock-out (SALE, ADJUST_REDUCE, DAMAGE, etc.)
        reference_type: Reference document type
        reference_id: Reference document ID
        location_note: Storage location
        notes: Additional notes

    Returns:
        StockTransaction: Created transaction record

    Raises:
        ValueError: If quantity is not positive or would result in negative stock
    """
    if quantity <= Decimal("0"):
        raise ValueError("Quantity must be positive for stock-out")

    # Lock product row for update
    product = Product.objects.select_for_update().get(pk=product.pk)

    # Validate sufficient stock
    if product.current_stock < quantity:
        raise ValueError(
            f"Insufficient stock: available={product.current_stock}, requested={quantity}"
        )

    # Capture state BEFORE
    old_quantity = product.current_stock
    old_wac = product.wac_price

    # Calculate new quantity (WAC remains unchanged for stock-out)
    new_quantity = old_quantity - quantity
    new_wac = old_wac

    # Update product (atomic)
    product.current_stock = new_quantity
    product.wac_price = new_wac
    product.save(update_fields=["current_stock", "wac_price"])

    # Create immutable transaction record
    # Note: quantity is stored as negative for stock-out
    transaction_record = StockTransaction.objects.create(
        product=product,
        change_type=change_type,
        quantity=-quantity,  # Negative for stock-out
        unit_cost=old_wac,  # Use current WAC as cost basis
        balance_before=old_quantity,
        balance_after=new_quantity,
        wac_before=old_wac,
        wac_after=new_wac,
        reference_type=reference_type,
        reference_id=reference_id,
        location_note=location_note or product.location_note,
        created_by=employee,
        notes=notes,
    )

    # Audit log
    log_audit(
        actor=employee,
        action_code=f"inventory.stock.{change_type.value.lower()}",
        action="adjust",
        target=product,
        before={
            "current_stock": str(old_quantity),
            "wac_price": str(old_wac),
        },
        after={
            "current_stock": str(new_quantity),
            "wac_price": str(new_wac),
        },
        extra_data={
            "transaction_id": transaction_record.id,
            "change_type": change_type,
            "quantity": str(-quantity),
        },
    )

    return transaction_record


@transaction.atomic
def adjust_stock(
    employee,
    product,
    new_quantity,
    reason="CORRECTION",
    notes=None,
    location_note=None,
):
    """
    Create a stock adjustment request (requires approval workflow).

    This creates a StockAdjustment record in PENDING status.
    Use approve_adjustment() to execute the adjustment.

    Args:
        employee: Employee requesting the adjustment
        product: Product to adjust
        new_quantity: Target quantity after adjustment
        reason: Reason code (DAMAGE, FOUND, CORRECTION, EXPIRY, OTHER)
        notes: Additional notes
        location_note: Storage location note

    Returns:
        StockAdjustment: Created adjustment record (PENDING status)
    """
    # Capture current state
    old_quantity = product.current_stock

    # Create adjustment request
    adjustment = StockAdjustment.objects.create(
        product=product,
        old_quantity=old_quantity,
        new_quantity=new_quantity,
        reason=reason,
        requested_by=employee,
        notes=notes,
        location_note=location_note or product.location_note,
    )

    # Audit log for adjustment request
    log_audit(
        actor=employee,
        action_code="inventory.adjustment.request",
        action="create",
        target=adjustment,
        before=None,
        after={
            "old_quantity": str(old_quantity),
            "new_quantity": str(new_quantity),
            "reason": reason,
            "status": "PENDING",
        },
    )

    return adjustment


@transaction.atomic
def approve_adjustment(adjustment, approver):
    """
    Approve and execute a stock adjustment.

    Workflow:
    1. Validate adjustment is in PENDING or APPROVED status
    2. Calculate quantity change
    3. Execute stock movement (stock_in or stock_out)
    4. Mark adjustment as EXECUTED

    Args:
        adjustment: StockAdjustment instance to approve
        approver: Employee approving the adjustment

    Returns:
        StockTransaction: Created transaction record

    Raises:
        ValueError: If adjustment is not in valid status
    """
    from inventory.models import StockAdjustmentStatus

    # Validate status
    if adjustment.status not in [
        StockAdjustmentStatus.PENDING,
        StockAdjustmentStatus.APPROVED,
    ]:
        raise ValueError(
            f"Adjustment must be PENDING or APPROVED, got {adjustment.status}"
        )

    # Approve if still pending
    if adjustment.status == StockAdjustmentStatus.PENDING:
        adjustment.approve(approver)

    # Calculate quantity change
    quantity_change = adjustment.new_quantity - adjustment.old_quantity

    # Execute stock movement
    if quantity_change > Decimal("0"):
        # Stock increase - use ADJUST_ADD (triggers WAC recalc)
        # Note: For corrections, we don't have a cost basis, so use current WAC
        product = adjustment.product
        transaction_record = stock_in(
            product=product,
            quantity=abs(quantity_change),
            unit_cost=product.wac_price,  # Use current WAC as cost basis
            employee=approver,
            change_type=StockChangeType.ADJUST_ADD,
            reference_type="StockAdjustment",
            reference_id=str(adjustment.id),
            location_note=adjustment.location_note,
            notes=f"Adjustment approved: {adjustment.notes}",
        )
    elif quantity_change < Decimal("0"):
        # Stock decrease - use ADJUST_REDUCE (no WAC recalc)
        transaction_record = stock_out(
            product=adjustment.product,
            quantity=abs(quantity_change),
            employee=approver,
            change_type=StockChangeType.ADJUST_REDUCE,
            reference_type="StockAdjustment",
            reference_id=str(adjustment.id),
            location_note=adjustment.location_note,
            notes=f"Adjustment approved: {adjustment.notes}",
        )
    else:
        # No quantity change - just mark as executed
        transaction_record = None

    # Mark adjustment as executed
    adjustment.mark_executed()

    # Audit log for approval
    log_audit(
        actor=approver,
        action_code="inventory.adjustment.approve",
        action="approve",
        target=adjustment,
        before={"status": adjustment.status},
        after={"status": "EXECUTED"},
        extra_data={
            "transaction_id": transaction_record.id if transaction_record else None,
            "quantity_change": str(quantity_change),
        },
    )

    return transaction_record


@transaction.atomic
def transfer_stock(
    product,
    quantity,
    employee,
    from_location,
    to_location,
    reference_type=None,
    reference_id=None,
    notes=None,
):
    """
    Transfer stock between locations (does not change total quantity).

    Note: This is a placeholder for future multi-location support.
    Currently creates a transaction record for tracking.

    Args:
        product: Product to transfer
        quantity: Quantity to transfer
        employee: Employee performing the transfer
        from_location: Source location
        to_location: Destination location
        reference_type: Reference document type
        reference_id: Reference document ID
        notes: Additional notes

    Returns:
        StockTransaction: Created transaction record
    """
    # Lock product row
    product = Product.objects.select_for_update().get(pk=product.pk)

    # Capture state
    old_quantity = product.current_stock
    old_wac = product.wac_price

    # Create transaction record (quantity = 0 for transfer, but we track the movement)
    transaction_record = StockTransaction.objects.create(
        product=product,
        change_type=StockChangeType.TRANSFER,
        quantity=Decimal("0"),  # No net change
        unit_cost=old_wac,
        balance_before=old_quantity,
        balance_after=old_quantity,
        wac_before=old_wac,
        wac_after=old_wac,
        reference_type=reference_type,
        reference_id=reference_id,
        location_note=f"{from_location} → {to_location}",
        created_by=employee,
        notes=notes,
    )

    # Audit log
    log_audit(
        actor=employee,
        action_code="inventory.stock.transfer",
        action="transfer",
        target=product,
        before={"location": from_location},
        after={"location": to_location},
        extra_data={
            "transaction_id": transaction_record.id,
            "quantity_transferred": str(quantity),
            "from_location": from_location,
            "to_location": to_location,
        },
    )

    return transaction_record
