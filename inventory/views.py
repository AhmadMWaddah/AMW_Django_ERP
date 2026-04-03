"""
-- AMW Django ERP - Inventory Views --

Phase 7: Product list, ledger, and HTMX stock adjustment.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from inventory.models import Product, StockTransaction
from inventory.operations.stock import stock_in, stock_out


@login_required
def product_list(request):
    """Product catalog list view with search."""
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").order_by("sku")

    if query:
        products = products.filter(
            Q(sku__icontains=query)
            | Q(name__icontains=query)
            | Q(category__name__icontains=query)
        )

    return render(
        request,
        "inventory/pages/product_list.html",
        {"products": products, "query": query},
    )


@login_required
def product_detail(request, product_id):
    """Product detail with stock movement ledger."""
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=product_id,
    )
    transactions = (
        StockTransaction.objects.filter(product=product)
        .select_related("created_by")
        .order_by("-created_at")[:50]
    )

    return render(
        request,
        "inventory/pages/product_detail.html",
        {"product": product, "transactions": transactions},
    )


@login_required
def stock_ledger(request, product_id):
    """Stock movement history page (ledger only)."""
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    transactions = (
        StockTransaction.objects.filter(product=product)
        .select_related("created_by")
        .order_by("-created_at")
    )

    return render(
        request,
        "inventory/pages/stock_ledger.html",
        {"product": product, "transactions": transactions},
    )


@require_POST
@login_required
def adjust_stock_htmx(request, product_id):
    """HTMX endpoint for stock adjustment."""
    product = get_object_or_404(Product, pk=product_id)
    action = request.POST.get("action")  # "in" or "out"
    quantity_str = request.POST.get("quantity", "0")
    location_note = request.POST.get("location_note", "")

    try:
        from decimal import Decimal, InvalidOperation

        quantity = Decimal(quantity_str)
    except (ValueError, InvalidOperation):
        return JsonResponse(
            {"error": "Invalid quantity"},
            status=400,
            headers={"HX-Trigger": '{"showToast": {"message": "Invalid quantity entered.", "type": "error"}}'},
        )

    if quantity <= 0:
        return JsonResponse(
            {"error": "Quantity must be positive"},
            status=400,
            headers={"HX-Trigger": '{"showToast": {"message": "Quantity must be positive.", "type": "error"}}'},
        )

    try:
        if action == "in":
            stock_in(
                product=product,
                quantity=quantity,
                unit_cost=product.wac_price or Decimal("0"),
                employee=request.user,
                location_note=location_note or None,
                notes="HTMX stock adjustment (add)",
            )
            message = f"Added {quantity} to {product.sku}. New stock: {product.current_stock}"
        elif action == "out":
            stock_out(
                product=product,
                quantity=quantity,
                employee=request.user,
                location_note=location_note or None,
                notes="HTMX stock adjustment (reduce)",
            )
            message = f"Removed {quantity} from {product.sku}. New stock: {product.current_stock}"
        else:
            return JsonResponse(
                {"error": "Invalid action"},
                status=400,
                headers={"HX-Trigger": '{"showToast": {"message": "Invalid action.", "type": "error"}}'},
            )

        # Return updated product detail fragment
        product.refresh_from_db()
        return JsonResponse(
            {"message": message, "current_stock": str(product.current_stock), "wac_price": str(product.wac_price)},
            headers={
                "HX-Trigger": f'{{"showToast": {{"message": "{message}", "type": "success"}}}}',
            },
        )
    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
            headers={"HX-Trigger": f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'},
        )
