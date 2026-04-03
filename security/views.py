"""
-- AMW Django ERP - Security Views --
Phase 7: Departments, Roles, Policies list pages.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from security.models import Department, Policy, Role


@login_required
def department_list(request):
    """Department list view with search."""
    query = request.GET.get("q", "").strip()
    departments = Department.objects.all().order_by("name")
    if query:
        departments = departments.filter(Q(name__icontains=query) | Q(slug__icontains=query))
    return render(request, "security/pages/department_list.html", {"departments": departments, "query": query})


@login_required
def role_list(request):
    """Role list view with search."""
    query = request.GET.get("q", "").strip()
    roles = Role.objects.select_related("department").all().order_by("department__name", "name")
    if query:
        roles = roles.filter(Q(name__icontains=query) | Q(department__name__icontains=query))
    return render(request, "security/pages/role_list.html", {"roles": roles, "query": query})


@login_required
def policy_list(request):
    """Policy list view with search."""
    query = request.GET.get("q", "").strip()
    policies = Policy.objects.all().order_by("name")
    if query:
        policies = policies.filter(Q(name__icontains=query) | Q(slug__icontains=query) | Q(resource__icontains=query))
    return render(request, "security/pages/policy_list.html", {"policies": policies, "query": query})
