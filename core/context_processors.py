"""
-- AMW Django ERP - Core Context Processors --
Version: 1.1 (Hardened for Template Safety)
"""


def ui_context(request):
    """
    Provides global UI context for navigation and app identification.
    Ensures nav_hierarchy is empty for unauthenticated users.
    """
    if not request.user.is_authenticated:
        return {
            "app_name": "AMW ERP",
            "active_app": "dashboard",
            "nav_hierarchy": [],
        }

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
    Every single dictionary GUARANTEES 'icon' and 'children' keys exist.
    """
    return [
        {
            "title": "Dashboard",
            "icon": "layout-dashboard",
            "url": "Accounts:Dashboard",
            "app": "accounts",
            "children": [],
        },
        {
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
        },
        {
            "title": "IAM",
            "icon": "shield-check",
            "url": "",
            "app": "security",
            "children": [
                {
                    "title": "Departments",
                    "icon": "building-2",
                    "url": "Security:DepartmentList",
                    "app": "security",
                    "children": [],
                },
                {
                    "title": "Roles",
                    "icon": "briefcase",
                    "url": "Security:RoleList",
                    "app": "security",
                    "children": [],
                },
                {
                    "title": "Policies",
                    "icon": "key-round",
                    "url": "Security:PolicyList",
                    "app": "security",
                    "children": [],
                },
            ],
        },
        {
            "title": "Inventory",
            "icon": "package",
            "url": "",
            "app": "inventory",
            "children": [
                {
                    "title": "Products",
                    "icon": "boxes",
                    "url": "Inventory:ProductList",
                    "app": "inventory",
                    "children": [],
                },
                {
                    "title": "Categories",
                    "icon": "tags",
                    "url": "Inventory:CategoryList",
                    "app": "inventory",
                    "children": [],
                },
                {
                    "title": "Stock Adjustments",
                    "icon": "arrow-left-right",
                    "url": "Inventory:AdjustmentList",
                    "app": "inventory",
                    "children": [],
                },
            ],
        },
        {
            "title": "Sales & CRM",
            "icon": "shopping-cart",
            "url": "",
            "app": "sales",
            "children": [
                {
                    "title": "Customers",
                    "icon": "users",
                    "url": "Sales:CustomerList",
                    "app": "sales",
                    "children": [],
                },
                {
                    "title": "Sales Orders",
                    "icon": "clipboard-list",
                    "url": "Sales:OrderList",
                    "app": "sales",
                    "children": [],
                },
            ],
        },
        {
            "title": "Purchasing",
            "icon": "truck",
            "url": "",
            "app": "purchasing",
            "children": [
                {
                    "title": "Suppliers",
                    "icon": "user-cog",
                    "url": "Purchasing:SupplierList",
                    "app": "purchasing",
                    "children": [],
                },
                {
                    "title": "Purchase Orders",
                    "icon": "clipboard-list",
                    "url": "Purchasing:OrderList",
                    "app": "purchasing",
                    "children": [],
                },
            ],
        },
    ]
