"""
-- AMW Django ERP - Accounts Views --

Authentication views: login, logout
Employee views: list, detail

Security:
- CSRF protection enabled on all forms
- POST-only logout to prevent CSRF attacks
- Open redirect protection using Django's built-in validator
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from accounts.models import Employee
from core.utils import paginate_queryset


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Employee login view.

    GET: Display login form
    POST: Authenticate and log in

    Security:
    - Validates 'next' parameter using Django's url_has_allowed_host_and_scheme
    - Uses CSRF protection
    - Generic error messages to prevent user enumeration
    """
    if request.user.is_authenticated:
        return redirect("Accounts:Dashboard")

    error_message = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next", request.GET.get("next", ""))

        # Normalize email to lowercase for case-insensitive authentication
        if email:
            email = email.lower()

        # Validate next URL using Django's built-in validator
        # This prevents open redirect attacks
        if next_url and not url_has_allowed_host_and_scheme(
            url=next_url, allowed_hosts={request.get_host()}, require_https=False
        ):
            next_url = ""

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Safe redirect after login
                redirect_to = next_url if next_url else "Accounts:Dashboard"
                return redirect(redirect_to)
            else:
                # Generic error message (doesn't reveal if user exists)
                error_message = "Invalid email or password"
        else:
            error_message = "Please provide both email and password"

    # Preserve next parameter for GET requests
    next_url = request.GET.get("next", "")

    return render(request, "accounts/pages/login.html", {"error_message": error_message, "next": next_url})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """
    Employee logout view.

    POST: Log out and redirect to login page

    Security:
    - POST-only to prevent CSRF attacks
    - Uses namespaced URL for login redirect
    """
    logout(request)
    return redirect("Accounts:Login")


@login_required
def dashboard_view(request):
    """
    Simple dashboard view - requires authentication.
    """
    return render(request, "accounts/pages/dashboard.html")


@login_required
def employee_list(request):
    """Employee list view with search and pagination."""
    from security.models import Department

    query = request.GET.get("q", "").strip()
    dept_filter = request.GET.get("department", "").strip()

    employees = Employee.objects.select_related("department").prefetch_related("roles").all().order_by("email")

    if query:
        employees = employees.filter(
            Q(email__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    if dept_filter:
        employees = employees.filter(department__slug=dept_filter)

    departments = Department.objects.all().order_by("name")
    pagination_data = paginate_queryset(employees, request)

    context = {
        "query": query,
        "dept_filter": dept_filter,
        "departments": departments,
        "employees": pagination_data["page_obj"].object_list,
        "title": "Employees",
        "row_template": "accounts/components/employee_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "accounts/pages/employee_list.html", context)


@login_required
def employee_detail(request, slug):
    """Employee detail/profile view (read-only)."""
    employee = get_object_or_404(Employee.objects.select_related("department").prefetch_related("roles"), slug=slug)

    context = {
        "employee": employee,
    }

    return render(request, "accounts/pages/employee_detail.html", context)
