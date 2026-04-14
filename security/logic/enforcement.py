"""
-- AMW Django ERP - Security/IAM Policy Enforcement Engine --

Constitution Section 6.3: Policy checks must be reusable from Python code.

This module provides the policy enforcement engine for checking permissions.
Usage:
    from security.logic.enforcement import PolicyEngine

    engine = PolicyEngine(employee)
    if engine.has_permission('inventory.stock', 'adjust'):
        # Allow operation
        pass
"""

from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import resolve_url

from ..models import Policy, Role

Employee = get_user_model()


class PolicyEngine:
    """
    Policy enforcement engine for checking employee permissions.

    Implements the IAM hierarchy: Employee -> Department -> Role -> Policies

    Usage:
        engine = PolicyEngine(employee)
        allowed = engine.has_permission('inventory.stock', 'adjust')
    """

    def __init__(self, employee):
        """
        Initialize policy engine for an employee.

        Args:
            employee: Employee instance to check permissions for
        """
        self.employee = employee
        self._policy_cache = None

    def _get_employee_roles(self):
        """
        Get all roles ASSIGNED to the employee (not all department roles).

        Constitution Section 6.3: IAM follows Employee -> Department -> Role -> Policies
        Roles must be explicitly assigned to employees, not inherited from department.

        Returns:
            QuerySet of Role instances assigned to this employee
        """
        # Primary: Get roles directly assigned to employee through M2M relationship
        if hasattr(self.employee, "roles"):
            return self.employee.roles.filter(is_active=True)

        # Fallback: If employee has a department but no roles assigned, return none
        # Roles are NOT automatically inherited from department
        # This prevents over-granting permissions
        return Role.objects.none()

    def _get_all_policies(self):
        """
        Get all policies from employee's roles.

        Returns:
            List of Policy instances
        """
        if self._policy_cache is not None:
            return self._policy_cache

        roles = self._get_employee_roles()
        policies = Policy.objects.filter(roles__in=roles, is_active=True).distinct()

        self._policy_cache = list(policies)
        return self._policy_cache

    def has_permission(self, resource, action):
        """
        Check if employee has permission for a specific resource and action.

        Args:
            resource: Resource identifier (e.g., 'inventory.stock')
            action: Action identifier (e.g., 'adjust', 'create', 'delete')

        Returns:
            bool: True if allowed, False if denied
        """
        policies = self._get_all_policies()

        # Check for explicit deny first
        for policy in policies:
            if policy.effect == "deny" and policy.matches(resource, action):
                return False

        # Check for allow
        for policy in policies:
            if policy.effect == "allow" and policy.matches(resource, action):
                return True

        # Default: deny
        return False

    def can_access(self, resource_path, action="read"):
        """
        Alias for has_permission with more intuitive naming.

        Args:
            resource_path: Full resource path (e.g., 'inventory.stock.adjust')
            action: Action (default: 'read')

        Returns:
            bool: True if access granted
        """
        return self.has_permission(resource_path, action)

    def get_all_permissions(self):
        """
        Get all permissions for this employee.

        Returns:
            dict: {resource: [actions]}
        """
        policies = self._get_all_policies()
        permissions = {}

        for policy in policies:
            if policy.effect == "allow":
                if policy.resource not in permissions:
                    permissions[policy.resource] = []
                permissions[policy.resource].append(policy.action)

        return permissions


def check_permission(employee, resource, action):
    """
    Convenience function for checking permissions.

    Usage:
        from security.logic.enforcement import check_permission

        if check_permission(employee, 'inventory.stock', 'adjust'):
            # Allow operation
            pass

    Args:
        employee: Employee instance
        resource: Resource identifier
        action: Action identifier

    Returns:
        bool: True if allowed
    """
    engine = PolicyEngine(employee)
    return engine.has_permission(resource, action)


def require_permission(resource, action):
    """
    Decorator for requiring permission on a view or operation.

    For standard GET requests: renders the styled 403 error page.
    For HTMX POST requests: returns 403 JSON with toast notification.

    Usage:
        @require_permission("inventory.stock", "adjust")
        def adjust_stock(request, product_id):
            # Only employees with permission can access
            pass

    Args:
        resource: Resource identifier
        action: Action identifier

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, "user") or not request.user.is_authenticated:
                login_url = resolve_url("Accounts:Login")
                if getattr(request, "htmx", None):
                    return JsonResponse(
                        {"error": "Authentication required"},
                        status=401,
                        headers={"HX-Redirect": login_url},
                    )
                return redirect_to_login(request.get_full_path(), login_url)

            if not check_permission(request.user, resource, action):
                # HTMX requests get JSON toast; normal requests get styled 403 page
                if getattr(request, "htmx", None):
                    return JsonResponse(
                        {"error": f"Permission denied: {action} on {resource}"},
                        status=403,
                        headers={
                            "HX-Trigger": '{"showToast": {"message": "Permission denied. You do not have access to this resource.", "type": "error"}}'
                        },
                    )
                raise PermissionDenied(f"You do not have permission to {action} {resource}.")

            return func(request, *args, **kwargs)
        return wrapper

    return decorator
