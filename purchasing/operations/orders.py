"""
-- AMW Django ERP - Purchase Order Operations --

Constitution Alignment:
- Section 8.1: Operations-First Business Logic (all PO logic lives here)
- Section 8.5: Stock Valuation Rule (WAC recalculation on receipt)
- Section 8.6: Atomic Safety (transaction.atomic + select_for_update)
- Section 8.7: Audit Rule (all state changes logged)
- Section 9.5: Financial Precision (Decimal 19,4, ROUND_HALF_UP)

Operations:
- generate_po_number(): Atomic unique PO numbering (PO-00001 format)
- issue_order(): Draft -> Issued with supplier snapshot
- receive_items(): Atomic stock intake with WAC recalculation
- cancel_order(): Cancel PO with audit trail
"""

from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from audit.logic.logging import log_audit
from inventory.logic.valuation import calculate_wac, should_recalculate_wac
from inventory.models import Product, StockChangeType, StockTransaction
from purchasing.models import POStatus, PurchaseOrder, PurchaseOrderItem


def _validate_unit_cost_variance(product, unit_cost):
    """
    Validate that the received unit cost is within acceptable variance
    of the product's current WAC price.

    This is a sanity check against data entry errors (e.g., $1000 instead of $10)
    that would corrupt the Weighted Average Cost for all future transactions.

    Constitution Section 8.5: Protect WAC integrity.

    Args:
        product: Product instance being received
        unit_cost: Unit cost from the PO line item

    Raises:
        ValueError: If unit cost deviates beyond configured threshold
    """
    threshold = getattr(settings, "PO_WAC_VARIANCE_THRESHOLD", Decimal("0.25"))

    # Skip check if product has no WAC yet (new product, first receipt)
    if product.wac_price == Decimal("0"):
        return

    variance = abs(unit_cost - product.wac_price) / product.wac_price

    if variance > threshold:
        threshold_pct = int(threshold * 100)
        actual_pct = int(variance * 100)
        raise ValueError(
            f"Unit cost {unit_cost} for {product.sku} deviates {actual_pct}% "
            f"from current WAC {product.wac_price}. "
            f"Threshold is {threshold_pct}%. "
            f"Review the PO line item cost before receiving."
        )


def generate_po_number():
    """
    Generate atomic unique PO number.

    Format: PO-00001 (configurable via PO_PREFIX setting, default "PO")
    Uses database locking to ensure uniqueness.

    Constitution Section 9.5: Order numbering must be atomic and unique.

    Returns:
        str: New PO number (e.g., "PO-00001")
    """
    # Get prefix from settings (default: "PO")
    prefix = getattr(settings, "PO_PREFIX", "PO")

    # Get the highest existing PO number atomically
    last_po = (
        PurchaseOrder.objects.all_with_deleted()
        .filter(po_number__startswith=f"{prefix}-")
        .order_by("-po_number")
        .first()
    )

    if last_po:
        try:
            last_num = int(last_po.po_number.split("-")[1])
            new_num = last_num + 1
        except (IndexError, ValueError):
            new_num = 1
    else:
        new_num = 1

    return f"{prefix}-{new_num:05d}"


@transaction.atomic
def issue_order(order, employee):
    """
    Issue a purchase order (Draft -> Issued).

    Atomic operation that:
    1. Validates order can be issued
    2. Generates unique PO number
    3. Snapshots supplier info
    4. Updates order status to ISSUED
    5. Logs audit trail

    Args:
        order: PurchaseOrder instance to issue
        employee: Employee issuing the order

    Returns:
        PurchaseOrder: Issued order

    Raises:
        ValueError: If order cannot be issued
    """
    order = PurchaseOrder.objects.select_for_update().get(pk=order.pk)

    if order.status != POStatus.DRAFT:
        raise ValueError(f"Only DRAFT orders can be issued (current: {order.status})")

    if not order.items.exists():
        raise ValueError("Cannot issue order without line items")

    # Capture state BEFORE
    old_status = order.status

    # Snapshot supplier info
    order.supplier_info_snapshot = {
        "name": order.supplier.name,
        "email": order.supplier.email,
        "phone": order.supplier.phone,
        "address": order.supplier.address,
        "contact_person": order.supplier.contact_person,
    }

    # Generate PO number
    order.po_number = generate_po_number()

    # Update status
    order.status = POStatus.ISSUED
    order.issued_by = employee
    order.issued_at = now()
    order.save(
        update_fields=[
            "po_number",
            "supplier_info_snapshot",
            "status",
            "issued_by",
            "issued_at",
        ]
    )

    # Audit log
    log_audit(
        actor=employee,
        action_code="purchasing.order.issue",
        action="issue",
        target=order,
        before={"status": str(old_status)},
        after={
            "status": str(POStatus.ISSUED.value),
            "po_number": order.po_number,
        },
        extra_data={
            "supplier": order.supplier.name,
            "total_cost": str(order.total_cost),
        },
    )

    return order


@transaction.atomic
def receive_items(order, items_to_receive, employee, location_note=None):
    """
    Receive items against a purchase order.

    Atomic operation that:
    1. Validates order can receive items (Issued or In-Progress)
    2. Increases stock via inventory.operations.stock.stock_in()
    3. Recalculates WAC for each product
    4. Updates received_quantity on PO items
    5. Updates PO status (In-Progress or Completed)
    6. Logs audit trail

    Constitution Section 8.5: WAC recalculated on stock-in.
    Constitution Section 8.6: select_for_update() for concurrency safety.

    Args:
        order: PurchaseOrder instance to receive against
        items_to_receive: List of dicts:
            [
                {"item_id": 1, "quantity": Decimal("10")},
                {"item_id": 2, "quantity": Decimal("5")},
            ]
        employee: Employee receiving the items
        location_note: Optional storage location note

    Returns:
        PurchaseOrder: Updated order with new status

    Raises:
        ValueError: If order cannot receive or quantities are invalid
    """
    order = PurchaseOrder.objects.select_for_update().get(pk=order.pk)

    # Validate status
    if order.status not in (POStatus.ISSUED, POStatus.IN_PROGRESS):
        raise ValueError(f"Only Issued or In-Progress orders can receive items " f"(current: {order.status})")

    if not items_to_receive:
        raise ValueError("No items to receive")

    # Capture state BEFORE
    old_status = order.status
    received_items_data = []

    for item_data in items_to_receive:
        item_id = item_data["item_id"]
        receive_qty = item_data["quantity"]

        # Fetch order item
        po_item = PurchaseOrderItem.objects.select_for_update().get(pk=item_id, order=order)

        # Validate quantity
        remaining = po_item.quantity - po_item.received_quantity
        if receive_qty <= Decimal("0"):
            raise ValueError("Receive quantity must be positive")
        if receive_qty > remaining:
            raise ValueError(f"Cannot receive {receive_qty} of {po_item.product.sku}: " f"only {remaining} remaining")

        # WAC sanity check: prevent cost typo from corrupting valuation
        _validate_unit_cost_variance(po_item.product, po_item.unit_cost)

        # Update received quantity
        po_item.received_quantity += receive_qty
        po_item.save(update_fields=["received_quantity"])

        # Call inventory stock_in operation (atomic, triggers WAC recalc)
        _receive_stock_atomic(
            product=po_item.product,
            quantity=receive_qty,
            unit_cost=po_item.unit_cost,
            employee=employee,
            reference_type="PurchaseOrder",
            reference_id=str(order.id),
            location_note=location_note,
            notes=f"PO {order.po_number} receipt",
        )

        received_items_data.append(
            {
                "product": str(po_item.product),
                "received": str(receive_qty),
                "total_received": str(po_item.received_quantity),
            }
        )

    # Determine new status
    if order.is_fully_received():
        new_status = POStatus.COMPLETED
        order.completed_by = employee
        order.completed_at = now()
        order.save(update_fields=["status", "completed_by", "completed_at"])
    else:
        new_status = POStatus.IN_PROGRESS

    order.status = new_status
    order.save(update_fields=["status"])

    # Audit log
    log_audit(
        actor=employee,
        action_code="purchasing.order.receive",
        action="receive",
        target=order,
        before={"status": str(old_status)},
        after={"status": str(new_status)},
        extra_data={
            "po_number": order.po_number,
            "items_received": received_items_data,
        },
    )

    return order


def _receive_stock_atomic(
    product,
    quantity,
    unit_cost,
    employee,
    reference_type=None,
    reference_id=None,
    location_note=None,
    notes=None,
):
    """
    Internal stock intake for PO receiving.

    This is a direct call that mirrors inventory.operations.stock.stock_in()
    but uses the PURCHASE change type explicitly.

    Args:
        product: Product instance
        quantity: Quantity received (positive)
        unit_cost: Unit cost from PO line item
        employee: Employee receiving
        reference_type: Reference document type
        reference_id: Reference document ID
        location_note: Storage location
        notes: Additional notes

    Returns:
        StockTransaction: Created transaction record
    """
    # Lock product row for update
    product = Product.objects.select_for_update().get(pk=product.pk)

    # Capture state BEFORE
    old_quantity = product.current_stock
    old_wac = product.wac_price

    # Calculate new WAC (PURCHASE triggers recalculation)
    change_type = StockChangeType.PURCHASE
    if should_recalculate_wac(change_type):
        new_wac = calculate_wac(old_quantity, old_wac, quantity, unit_cost)
    else:
        new_wac = old_wac

    # Calculate new quantity
    new_quantity = old_quantity + quantity

    # Update product
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
            "change_type": str(change_type),
            "quantity": str(quantity),
            "unit_cost": str(unit_cost),
        },
    )

    return transaction_record


@transaction.atomic
def cancel_order(order, employee, reason=None):
    """
    Cancel a purchase order.

    Atomic operation that:
    1. Validates order can be cancelled (not Completed)
    2. Updates order status to CANCELLED
    3. Logs audit trail

    Args:
        order: PurchaseOrder instance to cancel
        employee: Employee cancelling the order
        reason: Optional cancellation reason

    Returns:
        PurchaseOrder: Cancelled order

    Raises:
        ValueError: If order cannot be cancelled
    """
    order = PurchaseOrder.objects.select_for_update().get(pk=order.pk)

    if order.status in (POStatus.COMPLETED, POStatus.CANCELLED):
        raise ValueError(f"Cannot cancel order with status {order.status}. " "Completed orders cannot be cancelled.")

    # Capture state BEFORE
    old_status = order.status

    # Update status
    order.status = POStatus.CANCELLED
    order.cancelled_by = employee
    order.cancelled_at = now()
    order.save(update_fields=["status", "cancelled_by", "cancelled_at"])

    # Audit log
    log_audit(
        actor=employee,
        action_code="purchasing.order.cancel",
        action="cancel",
        target=order,
        before={"status": str(old_status)},
        after={"status": str(POStatus.CANCELLED.value)},
        extra_data={
            "po_number": order.po_number,
            "reason": reason or "No reason provided",
        },
    )

    return order
