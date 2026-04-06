"""
-- AMW Django ERP - Inventory Views --
Phase 7: Product list, ledger, categories, stock adjustments, and HTMX stock adjustment.
Phase 7.5: Pagination added to all list views.
"""

from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from core.utils import paginate_queryset
from inventory.models import Category, Product, StockAdjustment, StockTransaction
from inventory.operations.stock import stock_in, stock_out


@login_required
def product_list(request):
    """Product catalog list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    products = Product.objects.select_related("category").order_by("sku")

    if query:
        products = products.filter(
            Q(sku__icontains=query) | Q(name__icontains=query) | Q(category__name__icontains=query)
        )

    if category_filter:
        products = products.filter(category__slug=category_filter)

    pagination_data = paginate_queryset(products, request)

    categories = Category.objects.all().order_by("name")

    context = {
        "query": query,
        "category_filter": category_filter,
        "categories": categories,
        "products": pagination_data["page_obj"].object_list,
        "title": "Products",
        "row_template": "inventory/components/product_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "inventory/pages/product_list.html", context)


@login_required
def product_detail(request, slug):
    """Product detail with stock movement ledger."""
    from security.logic.enforcement import PolicyEngine

    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    transactions = (
        StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")[:50]
    )

    engine = PolicyEngine(request.user)
    can_adjust_stock = engine.has_permission("inventory.stock", "adjust")

    return render(
        request,
        "inventory/pages/product_detail.html",
        {
            "product": product,
            "transactions": transactions,
            "can_adjust_stock": can_adjust_stock,
        },
    )


@login_required
def stock_ledger(request, slug):
    """Stock movement history page (ledger only) with pagination."""
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    transactions = StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")

    pagination_data = paginate_queryset(transactions, request)

    context = {
        "product": product,
        "transactions": pagination_data["page_obj"].object_list,
        **pagination_data,
    }

    return render(request, "inventory/pages/stock_ledger.html", context)


@login_required
def category_list(request):
    """Category list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    categories = Category.objects.all().order_by("name")

    if query:
        categories = categories.filter(Q(name__icontains=query) | Q(slug__icontains=query))

    pagination_data = paginate_queryset(categories, request)

    context = {
        "query": query,
        "categories": pagination_data["page_obj"].object_list,
        "title": "Categories",
        "row_template": "inventory/components/category_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "inventory/pages/category_list.html", context)


@login_required
def adjustment_list(request):
    """Stock adjustment list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    adjustments = StockAdjustment.objects.select_related("product", "requested_by", "approved_by").order_by(
        "-requested_at"
    )

    if query:
        adjustments = adjustments.filter(
            Q(product__name__icontains=query) | Q(product__sku__icontains=query) | Q(reason__icontains=query)
        )

    if status_filter:
        adjustments = adjustments.filter(status=status_filter)

    pagination_data = paginate_queryset(adjustments, request)

    context = {
        "query": query,
        "status_filter": status_filter,
        "adjustments": pagination_data["page_obj"].object_list,
        "title": "Stock Adjustments",
        "row_template": "inventory/components/adjustment_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "inventory/pages/adjustment_list.html", context)


@require_POST
@login_required
def adjust_stock_htmx(request, slug):
    """HTMX endpoint for stock adjustment by slug.

    Policy: Requires 'inventory.stock' -> 'adjust' permission.
    """
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

    product = get_object_or_404(Product, slug=slug)
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
