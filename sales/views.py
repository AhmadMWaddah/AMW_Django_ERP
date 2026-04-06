"""
-- AMW Django ERP - Sales Views --

Phase 7: Customer list, order dashboard, HTMX confirm order with Toast.
Phase 7.5: Pagination added to all list views.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from core.utils import paginate_queryset
from sales.models import Customer, SalesOrder
from sales.operations.orders import confirm_order, void_order


@login_required
def customer_list(request):
    """Customer registry with search and pagination."""
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "").strip()

    customers = Customer.objects.select_related("category").order_by("name")

    if query:
        customers = customers.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(slug__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_filter:
        customers = customers.filter(category__slug=category_filter)

    from sales.models import CustomerCategory

    categories = CustomerCategory.objects.all().order_by("name")
    pagination_data = paginate_queryset(customers, request)

    context = {
        "query": query,
        "category_filter": category_filter,
        "categories": categories,
        "customers": pagination_data["page_obj"].object_list,
        "title": "Customers",
        "row_template": "sales/components/customer_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(
        request,
        "sales/pages/customer_list.html",
        context,
    )


@login_required
def customer_detail(request, slug):
    """Customer detail with order history."""
    customer = get_object_or_404(
        Customer.objects.select_related("category"),
        slug=slug,
    )
    orders = (
        SalesOrder.objects.filter(customer=customer).prefetch_related("items", "items__product").order_by("-created_at")
    )

    return render(
        request,
        "sales/pages/customer_detail.html",
        {"customer": customer, "orders": orders},
    )


@login_required
def order_list(request):
    """Sales order dashboard with search and pagination."""
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    orders = (
        SalesOrder.objects.select_related("customer", "created_by")
        .prefetch_related("items", "items__product")
        .order_by("-created_at")
    )

    if query:
        orders = orders.filter(Q(order_number__icontains=query) | Q(customer__name__icontains=query))

    if status_filter:
        orders = orders.filter(status=status_filter)

    pagination_data = paginate_queryset(orders, request)

    context = {
        "query": query,
        "status_filter": status_filter,
        "orders": pagination_data["page_obj"].object_list,
        "title": "Orders",
        "row_template": "sales/components/order_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(
        request,
        "sales/pages/order_list.html",
        context,
    )


@login_required
def order_detail(request, order_id):
    """Order detail with line items and pricing snapshots."""
    order = get_object_or_404(
        SalesOrder.objects.select_related("customer", "created_by").prefetch_related("items", "items__product"),
        pk=order_id,
    )

    return render(
        request,
        "sales/pages/order_detail.html",
        {"order": order},
    )


@require_POST
@login_required
def confirm_order_htmx(request, order_id):
    """HTMX endpoint to confirm a sales order with Toast feedback."""
    order = get_object_or_404(SalesOrder, pk=order_id)

    try:
        confirm_order(order, request.user)
        message = f"Order {order.order_number} confirmed successfully."
        return JsonResponse(
            {"status": "confirmed", "message": message},
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


@require_POST
@login_required
def void_order_htmx(request, order_id):
    """HTMX endpoint to void a sales order with Toast feedback."""
    order = get_object_or_404(SalesOrder, pk=order_id)
    reason = request.POST.get("reason", "Voided via HTMX")

    try:
        void_order(order, request.user, reason=reason)
        message = f"Order {order.order_number} voided. Stock restored."
        return JsonResponse(
            {"status": "voided", "message": message},
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
