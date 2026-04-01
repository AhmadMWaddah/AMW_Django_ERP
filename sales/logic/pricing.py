"""
-- AMW Django ERP - Sales Pricing Logic --

Constitution Section 9.5: Financial Precision
- All currency calculations use Decimal class (not float)
- Rounding uses ROUND_HALF_UP for consistency
- Precision: 19,4 decimal places
"""

from decimal import Decimal, ROUND_HALF_UP


def calculate_order_totals(order):
    """
    Calculate order subtotal, tax, and total.

    Constitution Section 9.5: Uses Decimal 19,4 precision with ROUND_HALF_UP.

    Args:
        order: SalesOrder instance

    Returns:
        tuple: (subtotal, tax_amount, total_amount) as Decimal(19,4)
    """
    # Calculate subtotal from line items
    subtotal = Decimal("0.0000")
    for item in order.items.all():
        line_total = item.quantity * item.snapshot_unit_price
        subtotal += line_total

    # Calculate tax (flat 14% for Egypt - configurable)
    tax_rate = get_tax_rate()
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    # Calculate total
    total_amount = (subtotal + tax_amount).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    return subtotal, tax_amount, total_amount


def get_tax_rate():
    """
    Get tax rate from settings.

    Default: 14% (Egypt VAT)
    Configure via: SALES_TAX_RATE = Decimal("0.14")

    Returns:
        Decimal: Tax rate (e.g., 0.14 for 14%)
    """
    from django.conf import settings

    return getattr(settings, "SALES_TAX_RATE", Decimal("0.14"))


def calculate_line_total(quantity, unit_price):
    """
    Calculate line item total with proper rounding.

    Args:
        quantity: Quantity (Decimal)
        unit_price: Unit price (Decimal)

    Returns:
        Decimal: Line total (19,4 precision)
    """
    total = quantity * unit_price
    return total.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def format_currency(amount):
    """
    Format currency for display (2 decimal places).

    Args:
        amount: Decimal amount

    Returns:
        str: Formatted string (e.g., "1,234.56")
    """
    from django.utils.formats import number_format

    return number_format(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
