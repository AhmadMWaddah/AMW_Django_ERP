"""
-- AMW Django ERP - Core Context Processors --

Injects global app state into every template context:
- app_name: Current application name
- nav_hierarchy: Navigation structure for sidebar rendering
- active_app: Currently active app/module for highlighting
"""


def ui_context(request):
    """
    Provides global UI context for navigation and app identification.

    Returns:
        dict: app_name, nav_hierarchy, active_app
    """
    path = request.path
    active_app = _resolve_active_app(path)

    return {
        "app_name": "AMW ERP",
        "active_app": active_app,
        "nav_hierarchy": _build_nav_hierarchy(),
    }


def _resolve_active_app(path):
    """Resolve the active app from the request path."""
    path_parts = [p for p in path.strip("/").split("/") if p]
    if not path_parts:
        return "dashboard"
    return path_parts[0]


def _build_nav_hierarchy():
    """
    Build the sidebar navigation structure.

    Returns a list of dicts with keys:
    - title: Display name
    - icon: Lucide icon name
    - url: URL name (namespaced)
    - app: App identifier (matches _resolve_active_app output)
    - children: Optional sub-items
    """
    return [
        {
            "title": "Dashboard",
            "icon": "layout-dashboard",
            "url": "Accounts:Dashboard",
            "app": "accounts",
        },
        {
            "title": "Core",
            "icon": "settings",
            "children": [
                {"title": "Admin", "url": "admin:index", "app": "admin"},
            ],
        },
        {
            "title": "Identity",
            "icon": "users",
            "children": [
                {"title": "Employees", "url": "admin:accounts_employee_changelist", "app": "accounts"},
            ],
        },
        {
            "title": "IAM",
            "icon": "shield-check",
            "children": [
                {"title": "Departments", "url": "admin:security_department_changelist", "app": "security"},
                {"title": "Roles", "url": "admin:security_role_changelist", "app": "security"},
                {"title": "Policies", "url": "admin:security_policy_changelist", "app": "security"},
            ],
        },
        {
            "title": "Inventory",
            "icon": "package",
            "children": [
                {"title": "Products", "url": "inventory:product_list", "app": "inventory"},
                {"title": "Stock Adjustments", "url": "admin:inventory_stockadjustment_changelist", "app": "inventory"},
                {"title": "Categories", "url": "admin:inventory_category_changelist", "app": "inventory"},
            ],
        },
        {
            "title": "Sales & CRM",
            "icon": "shopping-cart",
            "children": [
                {"title": "Customers", "url": "sales:customer_list", "app": "sales"},
                {"title": "Sales Orders", "url": "sales:order_list", "app": "sales"},
                {"title": "Admin: Customers", "url": "admin:sales_customer_changelist", "app": "sales"},
                {"title": "Admin: Orders", "url": "admin:sales_salesorder_changelist", "app": "sales"},
            ],
        },
        {
            "title": "Purchasing",
            "icon": "truck",
            "children": [
                {"title": "Suppliers", "url": "purchasing:supplier_list", "app": "purchasing"},
                {"title": "Purchase Orders", "url": "purchasing:order_list", "app": "purchasing"},
                {"title": "Admin: Suppliers", "url": "admin:purchasing_supplier_changelist", "app": "purchasing"},
                {"title": "Admin: POs", "url": "admin:purchasing_purchaseorder_changelist", "app": "purchasing"},
            ],
        },
    ]
