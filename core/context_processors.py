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
            "title": "Inventory",
            "icon": "package",
            "children": [
                {"title": "Products", "url": "Inventory:ProductList", "app": "inventory"},
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
        {
            "title": "Administration",
            "icon": "settings",
            "children": [
                {"title": "Admin Panel", "url": "admin:index", "app": "admin"},
            ],
        },
    ]
