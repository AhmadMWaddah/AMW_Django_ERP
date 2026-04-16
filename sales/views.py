"""
-- AMW Django ERP - Sales Views --

Phase 7: Customer list, order dashboard, HTMX confirm order with Toast.
Phase 7.5: Pagination added to all list views.
Phase 7.6: Refactored to return empty responses with HTMX headers (no JsonResponse).
"""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate_queryset
from core.views import require_post_with_405
from sales.models import Customer, SalesOrder
from sales.operations.orders import add_order_item, confirm_order, create_order, void_order
from security.logic.enforcement import PolicyEngine, require_permission


@require_permission("customer.*", "view")
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


@require_permission("customer.*", "view")
def customer_detail(request, slug):
    """Customer detail with order history."""
    customer = get_object_or_404(
        Customer.objects.select_related("category"),
        slug=slug,
    )
    orders = (
        SalesOrder.objects.filter(customer=customer).prefetch_related("items", "items__product").order_by("-created_at")
    )

    engine = PolicyEngine(request.user)
    can_create_order = engine.has_permission("sales.order", "create")

    return render(
        request,
        "sales/pages/customer_detail.html",
        {
            "customer": customer,
            "orders": orders,
            "can_create_order": can_create_order,
        },
    )


@login_required
@require_post_with_405
def order_create(request, customer_slug):
    """Create a new draft sales order for a customer.

    Server-side authorization: requires sales.order:create permission.
    """
    if not PolicyEngine(request.user).has_permission("sales.order", "create"):
        raise PermissionDenied("You do not have permission to create sales orders.")

    customer = get_object_or_404(
        Customer.objects.select_related("category"),
        slug=customer_slug,
    )
    order = create_order(customer, request.user)
    return redirect("Sales:OrderDetail", order_id=order.pk)


@require_permission("sales.*", "view")
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

    engine = PolicyEngine(request.user)
    can_confirm = engine.has_permission("sales.order", "confirm")

    pagination_data = paginate_queryset(orders, request)

    context = {
        "query": query,
        "status_filter": status_filter,
        "orders": pagination_data["page_obj"].object_list,
        "title": "Orders",
        "row_template": "sales/components/order_table.html",
        "can_confirm": can_confirm,
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(
        request,
        "sales/pages/order_list.html",
        context,
    )


@require_permission("sales.*", "view")
def order_detail(request, order_id):
    """Order detail with line items and pricing snapshots."""
    order = get_object_or_404(
        SalesOrder.objects.select_related("customer", "created_by").prefetch_related("items", "items__product"),
        pk=order_id,
    )

    engine = PolicyEngine(request.user)
    can_confirm_order = engine.has_permission("sales.order", "confirm")
    can_void_order = engine.has_permission("sales.order", "void")
    can_create_order = engine.has_permission("sales.order", "create")

    # Get products for the add item modal (only needed for DRAFT orders)
    # Gated by create permission, not confirm permission
    products = []
    if order.status == "DRAFT" and can_create_order:
        from inventory.models import Product

        products = Product.objects.filter(deleted_at__isnull=True).order_by("sku")

    return render(
        request,
        "sales/pages/order_detail.html",
        {
            "order": order,
            "can_confirm_order": can_confirm_order,
            "can_void_order": can_void_order,
            "can_create_order": can_create_order,
            "products": products,
        },
    )


@login_required
@require_post_with_405
def confirm_order_htmx(request, order_id):
    """HTMX endpoint to confirm a sales order with Toast feedback.

    Server-side authorization: requires sales.order:confirm permission.
    Returns empty response with HX-Trigger/HX-Refresh headers for HTMX lifecycle.
    """
    if not PolicyEngine(request.user).has_permission("sales.order", "confirm"):
        response = HttpResponse(status=403)
        response["HX-Trigger"] = (
            '{"showToast": {"message": "Permission denied: you cannot confirm orders.", "type": "error"}}'
        )
        return response

    order = get_object_or_404(SalesOrder, pk=order_id)

    try:
        confirm_order(order, request.user)
        message = f"Order {order.order_number} confirmed successfully."
        response = HttpResponse(status=200)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{message}", "type": "success"}}}}'
        response["HX-Refresh"] = "true"
        return response
    except ValueError as e:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'
        return response


@login_required
@require_post_with_405
def void_order_htmx(request, order_id):
    """HTMX endpoint to void a sales order with Toast feedback.

    Server-side authorization: requires sales.order:void permission.
    Returns empty response with HX-Trigger/HX-Refresh headers for HTMX lifecycle.
    """
    if not PolicyEngine(request.user).has_permission("sales.order", "void"):
        response = HttpResponse(status=403)
        response["HX-Trigger"] = (
            '{"showToast": {"message": "Permission denied: you cannot void orders.", "type": "error"}}'
        )
        return response

    order = get_object_or_404(SalesOrder, pk=order_id)
    reason = request.POST.get("reason", "Voided via HTMX")

    try:
        void_order(order, request.user, reason=reason)
        message = f"Order {order.order_number} voided. Stock restored."
        response = HttpResponse(status=200)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{message}", "type": "success"}}}}'
        response["HX-Refresh"] = "true"
        return response
    except ValueError as e:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'
        return response


@login_required
@require_post_with_405
def add_line_item(request, order_id):
    """HTMX endpoint to add a line item to a DRAFT sales order.

    Server-side authorization: requires sales.order:create permission.
    Returns empty response with HX-Trigger/HX-Refresh headers for HTMX lifecycle.
    """
    from decimal import Decimal

    from inventory.models import Product

    if not PolicyEngine(request.user).has_permission("sales.order", "create"):
        response = HttpResponse(status=403)
        response["HX-Trigger"] = (
            '{"showToast": {"message": "Permission denied: you cannot add line items.", "type": "error"}}'
        )
        return response

    order = get_object_or_404(SalesOrder, pk=order_id)

    # Get form data
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity")
    unit_price = request.POST.get("unit_price")
    notes = request.POST.get("notes", "")

    # Validate inputs
    if not product_id or not quantity or not unit_price:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = (
            '{"showToast": {"message": "Product, quantity, and unit price are required.", "type": "error"}}'
        )
        return response

    try:
        quantity = Decimal(quantity)
        unit_price = Decimal(unit_price)
    except Exception:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = '{"showToast": {"message": "Invalid quantity or unit price format.", "type": "error"}}'
        return response

    # Get product
    product = get_object_or_404(Product, pk=product_id)

    try:
        add_order_item(order, product, quantity, unit_price, request.user, notes)
        message = f"Added {product.sku} to order {order.order_number}."
        response = HttpResponse(status=200)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{message}", "type": "success"}}}}'
        response["HX-Refresh"] = "true"
        return response
    except ValueError as e:
        response = HttpResponse(status=400)
        response["HX-Trigger"] = f'{{"showToast": {{"message": "{e}", "type": "error"}}}}'
        return response
