"""
-- AMW Django ERP - Core Context Processors --
"""


def ui_context(request):
    """
    Provides global UI context for navigation and app identification.
    Returns empty nav_hierarchy for unauthenticated users.
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
    Every item has default 'icon' (str) and 'children' (list) to prevent template errors.
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
                    "icon": "",
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
                    "icon": "",
                    "url": "Security:DepartmentList",
                    "app": "security",
                    "children": [],
                },
                {
                    "title": "Roles",
                    "icon": "",
                    "url": "Security:RoleList",
                    "app": "security",
                    "children": [],
                },
                {
                    "title": "Policies",
                    "icon": "",
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
                    "icon": "",
                    "url": "Inventory:ProductList",
                    "app": "inventory",
                    "children": [],
                },
                {
                    "title": "Categories",
                    "icon": "",
                    "url": "Inventory:CategoryList",
                    "app": "inventory",
                    "children": [],
                },
                {
                    "title": "Stock Adjustments",
                    "icon": "",
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
                    "icon": "",
                    "url": "Sales:CustomerList",
                    "app": "sales",
                    "children": [],
                },
                {
                    "title": "Sales Orders",
                    "icon": "",
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
                    "icon": "",
                    "url": "Purchasing:SupplierList",
                    "app": "purchasing",
                    "children": [],
                },
                {
                    "title": "Purchase Orders",
                    "icon": "",
                    "url": "Purchasing:OrderList",
                    "app": "purchasing",
                    "children": [],
                },
            ],
        },
    ]
