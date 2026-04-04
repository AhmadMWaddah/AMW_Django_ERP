"""
-- AMW Django ERP - Inventory Views --
Phase 7: Product list, ledger, categories, stock adjustments, and HTMX stock adjustment.
"""

from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from inventory.models import Category, Product, StockAdjustment, StockTransaction
from inventory.operations.stock import stock_in, stock_out


@login_required
def product_list(request):
    """Product catalog list view with search."""
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").order_by("sku")
    if query:
        products = products.filter(
            Q(sku__icontains=query) | Q(name__icontains=query) | Q(category__name__icontains=query)
        )
    return render(request, "inventory/pages/product_list.html", {"products": products, "query": query})


@login_required
def product_detail(request, product_id):
    """Product detail with stock movement ledger."""
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    transactions = (
        StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")[:50]
    )
    return render(request, "inventory/pages/product_detail.html", {"product": product, "transactions": transactions})


@login_required
def stock_ledger(request, product_id):
    """Stock movement history page (ledger only)."""
    product = get_object_or_404(Product.objects.select_related("category"), pk=product_id)
    transactions = StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")
    return render(request, "inventory/pages/stock_ledger.html", {"product": product, "transactions": transactions})


@login_required
def category_list(request):
    """Category list view with search."""
    query = request.GET.get("q", "").strip()
    categories = Category.objects.all().order_by("name")
    if query:
        categories = categories.filter(Q(name__icontains=query) | Q(code__icontains=query))
    return render(request, "inventory/pages/category_list.html", {"categories": categories, "query": query})


@login_required
def adjustment_list(request):
    """Stock adjustment list view."""
    status_filter = request.GET.get("status", "").strip()
    adjustments = StockAdjustment.objects.select_related("product", "requested_by", "approved_by").order_by(
        "-requested_at"
    )
    if status_filter:
        adjustments = adjustments.filter(status=status_filter)
    return render(
        request, "inventory/pages/adjustment_list.html", {"adjustments": adjustments, "status_filter": status_filter}
    )


@require_POST
@login_required
def adjust_stock_htmx(request, product_id):
    """HTMX endpoint for stock adjustment by product ID."""
    return _adjust_stock_common(request, product_id=None)


@require_POST
@login_required
def adjust_stock_by_sku_htmx(request):
    """HTMX endpoint for stock adjustment by SKU (used from product list modal)."""
    sku = request.POST.get("sku", "").strip()
    if not sku:
        return JsonResponse(
            {"error": "SKU is required"},
            status=400,
            headers={"HX-Trigger": '{"showToast": {"message": "SKU is required.", "type": "error"}}'},
        )
    try:
        product = Product.objects.get(sku=sku)
    except Product.DoesNotExist:
        return JsonResponse(
            {"error": f"Product with SKU '{sku}' not found"},
            status=404,
            headers={"HX-Trigger": '{"showToast": {"message": f"Product \'{sku}\' not found.", "type": "error"}}'},
        )
    return _adjust_stock_common(request, product)


def _adjust_stock_common(request, product_id=None, product=None):
    """Shared stock adjustment logic. Policy: Requires 'inventory.stock' -> 'adjust' permission."""
    from security.logic.enforcement import PolicyEngine

    engine = PolicyEngine(request.user)
    if not engine.has_permission("inventory.stock", "adjust"):
        return JsonResponse(
            {"error": "Permission denied"},
            status=403,
            headers={
                "HX-Trigger": '{"showToast": {"message": "You do not have permission to adjust stock.", "type": "error"}}'
            },
        )

    if product is None:
        product = get_object_or_404(Product, pk=product_id)

    action = request.POST.get("action")
    quantity_str = request.POST.get("quantity", "0")
    location_note = request.POST.get("location_note", "")

    try:
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

        product.refresh_from_db()
        return JsonResponse(
            {"message": message, "current_stock": str(product.current_stock), "wac_price": str(product.wac_price)},
            headers={"HX-Trigger": f'{{"showToast": {{"message": "{message}", "type": "success"}}}}'},
        )
    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
            headers={"HX-Trigger": f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'},
        )
