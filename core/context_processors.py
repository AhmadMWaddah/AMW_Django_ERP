"""
-- AMW Django ERP - Core Context Processors --
"""


def ui_context(request):
    """
    Provides global UI context for navigation and app identification.
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
    Admin-only links (admin:*) are excluded.
    All other links point to custom UI pages.
    """
    return [
        {
            "title": "Dashboard",
            "icon": "layout-dashboard",
            "url": "Accounts:Dashboard",
            "app": "accounts",
        },
        {
            "title": "Identity",
            "icon": "users",
            "children": [
                {"title": "Employees", "url": "Accounts:EmployeeList", "app": "accounts"},
            ],
        },
        {
            "title": "IAM",
            "icon": "shield-check",
            "children": [
                {"title": "Departments", "url": "Security:DepartmentList", "app": "security"},
                {"title": "Roles", "url": "Security:RoleList", "app": "security"},
                {"title": "Policies", "url": "Security:PolicyList", "app": "security"},
            ],
        },
        {
            "title": "Inventory",
            "icon": "package",
            "children": [
                {"title": "Products", "url": "Inventory:ProductList", "app": "inventory"},
                {"title": "Categories", "url": "Inventory:CategoryList", "app": "inventory"},
                {"title": "Stock Adjustments", "url": "Inventory:AdjustmentList", "app": "inventory"},
            ],
        },
        {
            "title": "Sales & CRM",
            "icon": "shopping-cart",
            "children": [
                {"title": "Customers", "url": "Sales:CustomerList", "app": "sales"},
                {"title": "Sales Orders", "url": "Sales:OrderList", "app": "sales"},
            ],
        },
        {
            "title": "Purchasing",
            "icon": "truck",
            "children": [
                {"title": "Suppliers", "url": "Purchasing:SupplierList", "app": "purchasing"},
                {"title": "Purchase Orders", "url": "Purchasing:OrderList", "app": "purchasing"},
            ],
        },
    ]
