"""
-- AMW Django ERP - Core Context Processors --
Version: 1.6 (Single PolicyEngine Per Request)
"""

import fnmatch

from security.logic.enforcement import PolicyEngine


def ui_context(request):
    """
    Provides global UI context for navigation, app identification, and policy checks.
    Ensures nav_hierarchy is empty for unauthenticated users.
    Filters nav_hierarchy based on user's PolicyEngine permissions.

    Performance: Creates a SINGLE PolicyEngine instance per request and reuses it
    across all permission checks, eliminating N+1 database queries.
    """
    if not request.user.is_authenticated:
        return {
            "app_name": "AMW ERP",
            "active_app": "dashboard",
            "nav_hierarchy": [],
        }

    path = request.path
    active_app = _resolve_active_app(path)

    # Create ONE engine for the entire request lifecycle
    engine = PolicyEngine(request.user)

    # Build and filter navigation hierarchy based on permissions
    nav_hierarchy = _build_nav_hierarchy(engine)

    return {
        "app_name": "AMW ERP",
        "active_app": active_app,
        "nav_hierarchy": nav_hierarchy,
        "can_adjust_stock": _has_inventory_adjust_policy(engine),
        # Dashboard card visibility — requires view-level access, not just any permission
        "has_inventory_access": _check_nav_permission(engine, "inventory.*", "view"),
        "has_sales_access": _check_nav_permission(engine, "sales.*", "view")
        or _check_nav_permission(engine, "customer.*", "view"),
        "has_purchasing_access": _check_nav_permission(engine, "purchasing.*", "view"),
        "has_security_access": _check_nav_permission(engine, "security.department", "view")
        or _check_nav_permission(engine, "security.role", "view")
        or _check_nav_permission(engine, "security.policy", "view"),
        "has_accounts_access": _has_module_access(engine, "accounts")
        or _check_nav_permission(engine, "accounts.employee", "view"),
        "has_audit_access": _check_nav_permission(engine, "audit.*", "view"),
    }


def _resolve_active_app(path):
    """Resolve the active app from the request path."""
    path_parts = [p for p in path.strip("/").split("/") if p]
    if not path_parts:
        return "dashboard"
    return path_parts[0]


def _has_inventory_adjust_policy(engine):
    """Check if the user has 'Inventory: Adjust' policy."""
    try:
        return engine.has_permission("inventory.stock", "adjust")
    except Exception:
        return False


def _check_nav_permission(engine, resource, action):
    """Check if user has permission for a nav item."""
    try:
        return engine.has_permission(resource, action)
    except Exception:
        return False


def _has_module_access(engine, module_prefix):
    """
    Check if user has ANY permission within a module namespace.

    This is truly inclusive: it checks all the user's policies and returns True
    if ANY of them have a resource pattern that matches the module prefix.

    For example, a user with sales.order:confirm will see the Sales module,
    because 'sales.order' matches the 'sales.*' pattern via fnmatch.

    Args:
        engine: PolicyEngine instance (already cached)
        module_prefix: Module prefix (e.g., 'inventory', 'sales', 'purchasing')

    Returns:
        bool: True if user has any permission in this module
    """
    try:
        permissions = engine.get_all_permissions()

        # Pattern for this module's wildcard (e.g., 'sales.*')
        module_wildcard = f"{module_prefix}.*"

        for resource in permissions:
            # Check if this resource matches the module wildcard pattern
            # e.g., 'sales.order' matches 'sales.*', 'sales.*' matches 'sales.*'
            if fnmatch.fnmatch(resource, module_wildcard):
                return True
            # Also check if the module prefix is a prefix of the resource
            # e.g., resource='sales.order' starts with 'sales.'
            if resource.startswith(f"{module_prefix}."):
                return True

        # Check for executive wildcard (*:*)
        return engine.has_permission("*", "*")
    except Exception:
        return False


def _build_nav_hierarchy(engine):
    """
    Build the sidebar navigation structure filtered by user permissions.
    Every single dictionary GUARANTEES 'icon' and 'children' keys exist.
    Only includes sections the user has permission to access.
    Uses module-level wildcard patterns to align with seeded policies.

    Accepts a pre-initialized PolicyEngine to avoid N+1 queries.
    """
    nav = []

    # Dashboard - always visible for authenticated users
    nav.append(
        {
            "title": "Dashboard",
            "icon": "layout-dashboard",
            "url": "Accounts:Dashboard",
            "app": "accounts",
            "children": [],
        }
    )

    # Identity section - visible if user has any accounts module access or executive wildcard
    # Note: No accounts.* policies are seeded by default, so this checks for ad-hoc policies
    if _has_module_access(engine, "accounts") or _check_nav_permission(engine, "accounts.employee", "view"):
        identity_section = {
            "title": "Identity",
            "icon": "users",
            "url": "",
            "app": "accounts",
            "children": [
                {
                    "title": "Employees",
                    "icon": "users",
                    "url": "Accounts:EmployeeList",
                    "app": "accounts",
                    "children": [],
                },
            ],
        }
        nav.append(identity_section)

    # IAM section - visible if user has any security module access
    # Note: No security.* policies are seeded by default
    if (
        _has_module_access(engine, "security")
        or _check_nav_permission(engine, "security.department", "view")
        or _check_nav_permission(engine, "security.role", "view")
        or _check_nav_permission(engine, "security.policy", "view")
    ):
        iam_children = []
        # Check each IAM resource individually
        if _check_nav_permission(engine, "security.department", "view") or _has_module_access(engine, "security"):
            iam_children.append(
                {
                    "title": "Departments",
                    "icon": "building-2",
                    "url": "Security:DepartmentList",
                    "app": "security",
                    "children": [],
                }
            )
        if _check_nav_permission(engine, "security.role", "view") or _has_module_access(engine, "security"):
            iam_children.append(
                {
                    "title": "Roles",
                    "icon": "briefcase",
                    "url": "Security:RoleList",
                    "app": "security",
                    "children": [],
                }
            )
        if _check_nav_permission(engine, "security.policy", "view") or _has_module_access(engine, "security"):
            iam_children.append(
                {
                    "title": "Policies",
                    "icon": "key-round",
                    "url": "Security:PolicyList",
                    "app": "security",
                    "children": [],
                }
            )

        if iam_children:
            nav.append(
                {
                    "title": "IAM",
                    "icon": "shield-check",
                    "url": "",
                    "app": "security",
                    "children": iam_children,
                }
            )

    # Inventory section — requires view permission, not just any inventory permission
    if _check_nav_permission(engine, "inventory.*", "view"):
        inventory_children = []
        # All children visible if user has inventory.* view
        inventory_children.append(
            {
                "title": "Products",
                "icon": "boxes",
                "url": "Inventory:ProductList",
                "app": "inventory",
                "children": [],
            }
        )
        inventory_children.append(
            {
                "title": "Categories",
                "icon": "tags",
                "url": "Inventory:CategoryList",
                "app": "inventory",
                "children": [],
            }
        )
        inventory_children.append(
            {
                "title": "Stock Adjustments",
                "icon": "arrow-left-right",
                "url": "Inventory:AdjustmentList",
                "app": "inventory",
                "children": [],
            }
        )

        nav.append(
            {
                "title": "Inventory",
                "icon": "package",
                "url": "",
                "app": "inventory",
                "children": inventory_children,
            }
        )

    # Sales section — requires view permission
    if _check_nav_permission(engine, "sales.*", "view") or _check_nav_permission(
        engine, "customer.*", "view"
    ):
        sales_children = []
        sales_children.append(
            {
                "title": "Customers",
                "icon": "users",
                "url": "Sales:CustomerList",
                "app": "sales",
                "children": [],
            }
        )
        sales_children.append(
            {
                "title": "Sales Orders",
                "icon": "clipboard-list",
                "url": "Sales:OrderList",
                "app": "sales",
                "children": [],
            }
        )

        nav.append(
            {
                "title": "Sales & CRM",
                "icon": "shopping-cart",
                "url": "",
                "app": "sales",
                "children": sales_children,
            }
        )

    # Purchasing section — requires view permission
    if _check_nav_permission(engine, "purchasing.*", "view"):
        purchasing_children = []
        purchasing_children.append(
            {
                "title": "Suppliers",
                "icon": "user-cog",
                "url": "Purchasing:SupplierList",
                "app": "purchasing",
                "children": [],
            }
        )
        purchasing_children.append(
            {
                "title": "Purchase Orders",
                "icon": "clipboard-list",
                "url": "Purchasing:OrderList",
                "app": "purchasing",
                "children": [],
            }
        )

        nav.append(
            {
                "title": "Purchasing",
                "icon": "truck",
                "url": "",
                "app": "purchasing",
                "children": purchasing_children,
            }
        )

    # Audit section - standalone section with its own header
    if _has_module_access(engine, "audit"):
        audit_section = {
            "title": "Audit",
            "icon": "file-text",
            "url": "",
            "app": "audit",
            "children": [
                {
                    "title": "Audit Log",
                    "icon": "file-text",
                    "url": "audit:AuditLogList",
                    "app": "audit",
                    "children": [],
                },
            ],
        }
        nav.append(audit_section)

    return nav
