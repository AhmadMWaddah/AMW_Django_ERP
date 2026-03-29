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

from django.contrib.auth import get_user_model
from django.db.models import Q

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
        Get all roles assigned to the employee.
        
        Returns:
            QuerySet of Role instances
        """
        # Get roles from employee's department
        if hasattr(self.employee, 'department') and self.employee.department:
            return Role.objects.filter(
                department=self.employee.department,
                is_active=True
            )
        
        # If no department, check for roles directly assigned
        if hasattr(self.employee, 'roles'):
            return self.employee.roles.filter(is_active=True)
        
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
        policies = Policy.objects.filter(
            roles__in=roles,
            is_active=True
        ).distinct()
        
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
            if policy.effect == 'deny' and policy.matches(resource, action):
                return False
        
        # Check for allow
        for policy in policies:
            if policy.effect == 'allow' and policy.matches(resource, action):
                return True
        
        # Default: deny
        return False
    
    def can_access(self, resource_path, action='read'):
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
            if policy.effect == 'allow':
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
    
    Usage:
        @require_permission('inventory.stock', 'adjust')
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
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Authentication required")
            
            if not check_permission(request.user, resource, action):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(
                    f"Permission denied: {action} on {resource}"
                )
            
            return func(request, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator
