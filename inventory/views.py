"""
-- AMW Django ERP - Inventory Views --
Phase 7: Product list, ledger, categories, stock adjustments, and HTMX stock adjustment.
Phase 7.5: Pagination added to all list views.
Phase 7.6: Refactored to return empty responses with HTMX headers (no JsonResponse).
"""

from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from core.utils import paginate_queryset
from inventory.models import Category, Product, StockAdjustment, StockTransaction
from inventory.operations.stock import stock_in, stock_out
from security.logic.enforcement import require_permission


@require_permission("inventory.*", "view")
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
        products = products.filter(category__name__iexact=category_filter)

    categories = Category.objects.all().order_by("name")
    pagination_data = paginate_queryset(products, request, page_size=20)

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


@require_permission("inventory.*", "view")
def product_detail(request, slug):
    """Product detail view with stock ledger."""
    product = get_object_or_404(Product, slug=slug)
    transactions = StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")
    paginated = paginate_queryset(transactions, request, page_size=20)

    context = {
        "product": product,
        "transactions": paginated["page_obj"].object_list,
        **paginated,
    }
    return render(request, "inventory/pages/product_detail.html", context)


@require_permission("inventory.*", "view")
def stock_ledger(request, slug):
    """Full stock ledger view for a specific product."""
    product = get_object_or_404(Product, slug=slug)
    transactions = StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")
    pagination_data = paginate_queryset(transactions, request, page_size=50)

    context = {
        "product": product,
        "transactions": pagination_data["page_obj"].object_list,
        "title": f"Stock Ledger - {product.sku}",
        **pagination_data,
    }
    return render(request, "inventory/pages/stock_ledger.html", context)


@require_permission("inventory.*", "view")
def category_list(request):
    """Category list view with search and pagination."""
    query = request.GET.get("q", "").strip()

    categories = Category.objects.all().order_by("name")
    if query:
        categories = categories.filter(name__icontains=query)

    pagination_data = paginate_queryset(categories, request, page_size=20)
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


@require_permission("inventory.*", "view")
def category_detail(request, slug):
    """Category detail view showing products in category."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).order_by("sku")
    paginated = paginate_queryset(products, request, page_size=20)

    context = {
        "category": category,
        "products": paginated,
    }
    return render(request, "inventory/pages/category_detail.html", context)


@require_permission("inventory.*", "view")
def adjustment_list(request):
    """Stock adjustment list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    adjustments = StockAdjustment.objects.all().order_by("-created_at")
    if query:
        adjustments = adjustments.filter(Q(product__name__icontains=query) | Q(product__sku__icontains=query))
    if status_filter:
        adjustments = adjustments.filter(status=status_filter)

    pagination_data = paginate_queryset(adjustments, request, page_size=20)
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


def adjustment_detail(request, pk):
    """Stock adjustment detail view."""
    adjustment = get_object_or_404(StockAdjustment, pk=pk)
    context = {"adjustment": adjustment}
    return render(request, "inventory/pages/adjustment_detail.html", context)


@require_POST
@require_permission("inventory.stock", "adjust")
def adjust_stock_htmx(request, slug):
    """HTMX endpoint for stock adjustment by slug.

    Policy: Requires 'inventory.stock' -> 'adjust' permission.
    Returns partial HTML for targeted swap + toast trigger.
    """
    product = get_object_or_404(Product, slug=slug)
    action = request.POST.get("action")
    quantity_str = request.POST.get("quantity", "0")
    location_note = request.POST.get("location_note", "")

    try:
        quantity = Decimal(quantity_str)
    except (ValueError, InvalidOperation):
        response = HttpResponse(status=400)
        response["HX-Trigger"] = '{"showToast": {"message": "Invalid quantity entered.", "type": "error"}}'
        return response

    if quantity <= 0:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = '{"showToast": {"message": "Quantity must be positive.", "type": "error"}}'
        return response

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
            response = HttpResponse(status=400)
            response["HX-Trigger"] = '{"showToast": {"message": "Invalid action.", "type": "error"}}'
            return response

        product.refresh_from_db()

        transactions = (
            StockTransaction.objects.filter(product=product).select_related("created_by").order_by("-created_at")[:20]
        )
        ledger_rows = render_to_string("inventory/components/ledger_rows.html", {"transactions": transactions})

        response = HttpResponse(f'<template id="ledger-template">{ledger_rows}</template>')
        response["HX-Trigger"] = (
            f'{{"showToast": {{"message": "{message}", "type": "success"}}, "refreshLedger": true, "newStock": "{product.current_stock}", "newValue": "{product.get_stock_value}"}}'
        )
        return response
    except ValueError as e:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'
        return response
