"""
-- AMW Django ERP - Purchasing Views --

Phase 7: Supplier list, PO tracking, HTMX receive stock.
Phase 7.5: Pagination added to all list views.
"""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from core.utils import paginate_queryset
from purchasing.models import PurchaseOrder, Supplier, SupplierCategory
from purchasing.operations.orders import receive_items


@login_required
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


@login_required
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


@login_required
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


@login_required
def order_detail(request, order_id):
    """PO detail with line items and receiving status."""
    order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "created_by").prefetch_related("items", "items__product"),
        pk=order_id,
    )

    return render(
        request,
        "purchasing/pages/order_detail.html",
        {"order": order},
    )


@require_POST
@login_required
def receive_stock_htmx(request, order_id):
    """HTMX endpoint to receive stock against a PO."""
    order = get_object_or_404(PurchaseOrder, pk=order_id)

    # Parse items from POST data
    # Expected: items_json = [{"item_id": 1, "quantity": "10"}, ...]
    import json

    items_json = request.POST.get("items", "[]")
    try:
        items_data = json.loads(items_json)
        items_to_receive = [
            {"item_id": item["item_id"], "quantity": Decimal(str(item["quantity"]))} for item in items_data
        ]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return JsonResponse(
            {"error": f"Invalid items data: {e}"},
            status=400,
            headers={
                "HX-Trigger": '{"showToast": {"message": "Invalid receive data.", "type": "error"}}',
            },
        )

    if not items_to_receive:
        return JsonResponse(
            {"error": "No items to receive"},
            status=400,
            headers={
                "HX-Trigger": '{"showToast": {"message": "No items to receive.", "type": "error"}}',
            },
        )

    try:
        result = receive_items(order, items_to_receive, request.user)
        message = f"Stock received for {order.po_number}. Status: {result.status}"
        return JsonResponse(
            {"status": result.status, "message": message},
            headers={
                "HX-Trigger": f'{{"showToast": {{"message": "{message}", "type": "success"}}}}',
                "HX-Refresh": "true",
            },
        )
    except ValueError as e:
        return JsonResponse(
            {"error": str(e)},
            status=400,
            headers={"HX-Trigger": f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'},
        )
