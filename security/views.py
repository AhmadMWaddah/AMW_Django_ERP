"""
-- AMW Django ERP - Security Views --
Phase 7: Departments, Roles, Policies list pages.
Phase 7.5: Detail views and pagination.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, render

from core.utils import paginate_queryset
from security.models import Department, Policy, Role


@login_required
def department_list(request):
    """Department list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    departments = Department.objects.annotate(
        employee_count=Count("employees"),
        role_count=Count("roles"),
    ).order_by("name")

    if query:
        departments = departments.filter(Q(name__icontains=query) | Q(slug__icontains=query))

    pagination_data = paginate_queryset(departments, request)

    context = {
        "query": query,
        "departments": pagination_data["page_obj"].object_list,
        "title": "Departments",
        "row_template": "security/components/department_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "security/pages/department_list.html", context)


@login_required
def department_detail(request, slug):
    """Department detail view with children and employees."""
    department = get_object_or_404(
        Department.objects.prefetch_related(
            Prefetch(
                "children",
                queryset=Department.objects.annotate(
                    employee_count=Count("employees"),
                    role_count=Count("roles"),
                ),
            ),
            Prefetch(
                "roles",
                queryset=Role.objects.annotate(
                    policy_count=Count("policies"),
                    employee_count=Count("employees"),
                ).select_related("department"),
            ),
            "employees",
        ),
        slug=slug,
    )

    context = {
        "department": department,
    }

    return render(request, "security/pages/department_detail.html", context)


@login_required
def role_list(request):
    """Role list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    dept_filter = request.GET.get("department", "").strip()

    roles = (
        Role.objects.select_related("department")
        .annotate(
            policy_count=Count("policies"),
            employee_count=Count("employees"),
        )
        .order_by("department__name", "name")
    )

    if query:
        roles = roles.filter(Q(name__icontains=query) | Q(department__name__icontains=query))

    if dept_filter:
        roles = roles.filter(department__slug=dept_filter)

    pagination_data = paginate_queryset(roles, request)

    context = {
        "query": query,
        "dept_filter": dept_filter,
        "roles": pagination_data["page_obj"].object_list,
        "title": "Roles",
        "row_template": "security/components/role_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "security/pages/role_list.html", context)


@login_required
def role_detail(request, slug):
    """Role detail view with policies and employees."""
    role = get_object_or_404(
        Role.objects.select_related("department")
        .prefetch_related("policies", "employees")
        .annotate(
            policy_count=Count("policies"),
            employee_count=Count("employees"),
        ),
        slug=slug,
    )

    context = {
        "role": role,
    }

    return render(request, "security/pages/role_detail.html", context)


@login_required
def policy_list(request):
    """Policy list view with search and pagination."""
    query = request.GET.get("q", "").strip()
    effect_filter = request.GET.get("effect", "").strip()

    policies = Policy.objects.annotate(
        roles_count=Count("roles"),
    ).order_by("name")

    if query:
        policies = policies.filter(Q(name__icontains=query) | Q(slug__icontains=query) | Q(resource__icontains=query))

    if effect_filter:
        policies = policies.filter(effect=effect_filter)

    pagination_data = paginate_queryset(policies, request)

    context = {
        "query": query,
        "effect_filter": effect_filter,
        "policies": pagination_data["page_obj"].object_list,
        "title": "Policies",
        "row_template": "security/components/policy_table.html",
        **pagination_data,
    }

    if getattr(request, "htmx", None):
        return render(request, "components/table_content_only.html", context)

    return render(request, "security/pages/policy_list.html", context)


@login_required
def policy_detail(request, slug):
    """Policy detail view with usage information."""
    policy = get_object_or_404(
        Policy.objects.prefetch_related(
            Prefetch(
                "roles",
                queryset=Role.objects.annotate(
                    employee_count=Count("employees"),
                )
                .select_related("department")
                .prefetch_related("employees"),
            ),
        ),
        slug=slug,
    )

    context = {
        "policy": policy,
    }

    return render(request, "security/pages/policy_detail.html", context)
