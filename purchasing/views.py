"""
-- AMW Django ERP - Purchasing Views --

Phase 7: Supplier list, PO tracking, HTMX receive stock.
Phase 7.5: Pagination added to all list views.
Phase 7.6: Refactored to return empty responses with HTMX headers (no JsonResponse).
"""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from core.utils import paginate_queryset
from core.views import require_post_with_405
from purchasing.models import PurchaseOrder, Supplier, SupplierCategory
from purchasing.operations.orders import receive_items
from security.logic.enforcement import PolicyEngine, require_permission


@require_permission("purchasing.*", "view")
def supplier_list(request):
    """Supplier registry with search and pagination."""
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    suppliers = Supplier.objects.select_related("category").order_by("name")

    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(slug__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_filter:
        suppliers = suppliers.filter(category__slug=category_filter)

    categories = SupplierCategory.objects.all().order_by("name")
    pagination_data = paginate_queryset(suppliers, request)

    context = {
        "query": query,
        "category_filter": category_filter,
        "categories": categories,
        "suppliers": pagination_data["page_obj"].object_list,
        "title": "Suppliers",
        "row_template": "purchasing/components/supplier_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(
        request,
        "purchasing/pages/supplier_list.html",
        context,
    )


@require_permission("purchasing.*", "view")
def supplier_detail(request, slug):
    """Supplier detail with PO history."""
    supplier = get_object_or_404(
        Supplier.objects.select_related("category"),
        slug=slug,
    )
    orders = (
        PurchaseOrder.objects.filter(supplier=supplier)
        .select_related("created_by")
        .prefetch_related("items", "items__product")
        .order_by("-created_at")
    )

    return render(
        request,
        "purchasing/pages/supplier_detail.html",
        {"supplier": supplier, "orders": orders},
    )


@require_permission("purchasing.*", "view")
def order_list(request):
    """Purchase order dashboard with search and pagination."""
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    orders = (
        PurchaseOrder.objects.select_related("supplier", "created_by")
        .prefetch_related("items", "items__product")
        .order_by("-created_at")
    )

    if query:
        orders = orders.filter(Q(po_number__icontains=query) | Q(supplier__name__icontains=query))

    if status_filter:
        orders = orders.filter(status=status_filter)

    pagination_data = paginate_queryset(orders, request)

    context = {
        "query": query,
        "status_filter": status_filter,
        "orders": pagination_data["page_obj"].object_list,
        "title": "Purchase Orders",
        "row_template": "purchasing/components/order_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(
        request,
        "purchasing/pages/order_list.html",
        context,
    )


@require_permission("purchasing.*", "view")
def order_detail(request, order_id):
    """PO detail with line items and receiving status."""
    order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "created_by").prefetch_related("items", "items__product"),
        pk=order_id,
    )

    engine = PolicyEngine(request.user)
    can_receive_items = engine.has_permission("purchasing.order", "receive")

    return render(
        request,
        "purchasing/pages/order_detail.html",
        {
            "order": order,
            "can_receive_items": can_receive_items,
        },
    )


@login_required
@require_post_with_405
def receive_stock_htmx(request, order_id):
    """HTMX endpoint to receive stock against a PO.

    Server-side authorization: requires purchasing.order:receive permission.
    Returns empty response with HX-Trigger/HX-Refresh headers for HTMX lifecycle.
    """
    if not PolicyEngine(request.user).has_permission("purchasing.order", "receive"):
        response = HttpResponse(status=403)
        response["HX-Trigger"] = (
            '{"showToast": {"message": "Permission denied: you cannot receive stock.", "type": "error"}}'
        )
        return response

    order = get_object_or_404(PurchaseOrder, pk=order_id)

    items_to_receive = []

    for key, value in request.POST.items():
        if key.startswith("qty_") and value:
            try:
                item_id = int(key.replace("qty_", ""))
                qty = Decimal(value)
                if qty > 0:
                    items_to_receive.append({"item_id": item_id, "quantity": qty})
            except (ValueError, IndexError):
                continue

    if not items_to_receive:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = '{"showToast": {"message": "No items to receive.", "type": "error"}}'
        return response

    try:
        result = receive_items(order, items_to_receive, request.user)
        message = f"Stock received for {order.po_number}. Status: {result.status}"
        response = HttpResponse(status=200)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{message}", "type": "success"}}}}'
        response["HX-Refresh"] = "true"
        return response
    except ValueError as e:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'
        return response
