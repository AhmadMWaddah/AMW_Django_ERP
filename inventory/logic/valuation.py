"""
-- AMW Django ERP - WAC Valuation Logic --

Constitution Section 6.5: Stock Valuation Rule
- Inventory valuation uses Weighted Average Cost (WAC)
- WAC must be recalculated automatically on stock-in flows
- Stock updates must not allow silent corruption of quantity, cost, or audit history

WAC Formula:
    New WAC = (Old Qty × Old WAC + New Qty × New Cost) / (Old Qty + New Qty)

Trigger Points:
- ✅ Recalculate on: INTAKE, PURCHASE, ADJUST_ADD (stock-in at cost)
- ❌ Do NOT recalculate on: SALE, ADJUST_REDUCE, TRANSFER, RETURN (stock-out)
"""

from decimal import ROUND_HALF_UP, Decimal


def calculate_wac(old_quantity, old_wac, new_quantity, new_cost):
    """
    Calculate new Weighted Average Cost after stock intake.

    Formula:
        New WAC = (Old Qty × Old WAC + New Qty × New Cost) / (Old Qty + New Qty)

    Args:
        old_quantity: Current stock quantity before intake
        old_wac: Current WAC price before intake
        new_quantity: Quantity being added
        new_cost: Unit cost of the new stock

    Returns:
        Decimal: New WAC price (19,4 precision)

    Example:
        >>> calculate_wac(Decimal('10'), Decimal('100.0000'), Decimal('5'), Decimal('120.0000'))
        Decimal('106.6667')
    """
    # Handle edge case: no old stock
    if old_quantity == Decimal("0"):
        return new_cost.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    # Handle edge case: no new stock
    if new_quantity == Decimal("0"):
        return old_wac

    # Calculate total value before and after
    old_value = old_quantity * old_wac
    new_value = new_quantity * new_cost
    total_value = old_value + new_value

    # Calculate total quantity
    total_quantity = old_quantity + new_quantity

    # Calculate new WAC with 19,4 precision
    new_wac = total_value / total_quantity
    return new_wac.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def should_recalculate_wac(change_type):
    """
    Determine if WAC should be recalculated for a given change type.

    Constitution Section 6.5: WAC recalculated only on stock-in flows.

    Args:
        change_type: StockChangeType value

    Returns:
        bool: True if WAC should be recalculated

    Trigger Points:
        - INTAKE: Yes (stock purchase/intake)
        - PURCHASE: Yes (purchase order receipt)
        - ADJUST_ADD: Yes (manual stock addition at cost)
        - SALE: No (stock-out)
        - ADJUST_REDUCE: No (stock reduction)
        - TRANSFER: No (location change only)
        - RETURN: No (customer return - may have separate logic)
        - DAMAGE: No (write-off)
    """
    from inventory.models import StockChangeType

    wac_trigger_types = [
        StockChangeType.INTAKE,
        StockChangeType.PURCHASE,
        StockChangeType.ADJUST_ADD,
    ]

    return change_type in wac_trigger_types


def calculate_stock_value(quantity, wac_price):
    """
    Calculate total stock value.

    Args:
        quantity: Stock quantity
        wac_price: Weighted Average Cost price

    Returns:
        Decimal: Total value (quantity × WAC)
    """
    return (quantity * wac_price).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def format_wac_for_display(wac_value):
    """
    Format WAC value for display (2 decimal places for UI).

    Args:
        wac_value: Decimal WAC price

    Returns:
        str: Formatted string (e.g., "106.67")
    """
    return str(wac_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
