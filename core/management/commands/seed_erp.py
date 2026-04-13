"""
AMW Django ERP - Seed ERP Data Command

Generates idempotent, persona-based dummy data aligned with architecture.

Usage:
    python manage.py seed_erp              # Safe mode (aborts if DEBUG=False)
    python manage.py seed_erp --force      # Force mode (runs even in production)

Constitution Compliance:
- Double quotes for all Python strings (Section 11.5)
- Idempotent operations (safe for repeated execution)
- Safety check for production environments

Departments: Executive, Logistics, Commercial, Finance
Roles: Owner (all roles), Warehouse Lead, Sales Manager, Auditor
Policies: inventory.*, purchasing.*, sales.*, customer.*, audit.*, inventory:audit
"""

from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from security.models import Department, Policy, Role

Employee = get_user_model()


class Command(BaseCommand):
    """
    Management command to seed ERP system with dummy data.

    Creates:
    - 4 Departments (Executive, Logistics, Commercial, Finance)
    - 4 Employee personas (Owner with ALL roles, Warehouse Lead, Sales Manager, Auditor)
    - Policies scoped to built modules only (no HR/Accounting)
    - Roles with proper policy assignments
    - Product catalog, initial stock, customers, sales orders
    - Supplier catalog, purchase orders
    """

    help = "Seed ERP system with dummy data for development and testing"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force execution even if DEBUG=False (production mode)",
        )

    def handle(self, *args, **options):
        """Main command entry point."""
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "Cannot seed data in production mode (DEBUG=False). " "Use --force to override (NOT RECOMMENDED)."
            )

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("AMW Django ERP - Seed Data Command"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write()

        if options["force"]:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: Running in production mode! " "This will create test data in your production database."
                )
            )
            self.stdout.write()

        with transaction.atomic():
            # Phase 3: IAM Hierarchy
            self._seed_departments()
            self._seed_policies()
            self._seed_roles()
            self._seed_employees()

            # Phase 4: Product Catalog Foundation
            self._seed_categories()
            self._seed_products()
            self._seed_initial_stock()

            # Phase 5: Sales & CRM
            self._seed_customer_categories()
            self._seed_customers()
            self._seed_sales_orders()

            # Phase 8: Purchasing
            self._seed_supplier_categories()
            self._seed_suppliers()
            self._seed_purchase_orders()

        self.stdout.write()
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Seed complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write()
        self.stdout.write(self.style.SUCCESS("See CREDENTIALS.md file for login credentials and test data."))
        self.stdout.write()

    # -- IAM Hierarchy ---------------------------------------------------

    def _seed_departments(self):
        """Create exactly four departments."""
        self.stdout.write("Seeding Departments...")

        departments_data = [
            {"name": "Executive", "description": "Executive management and ownership"},
            {"name": "Logistics", "description": "Warehouse, inventory, and shipping"},
            {"name": "Commercial", "description": "Sales and customer relations"},
            {"name": "Finance", "description": "Financial oversight and auditing"},
        ]

        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data["name"],
                defaults=dept_data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created: {dept.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  Exists: {dept.name}"))

        self.stdout.write()

    def _seed_policies(self):
        """Create policies scoped to built modules only."""
        self.stdout.write("Seeding Policies...")

        policies_data = [
            # Inventory policies
            {
                "name": "Inventory: View",
                "resource": "inventory.*",
                "action": "view",
                "effect": "allow",
                "description": "View inventory items and stock levels",
            },
            {
                "name": "Inventory: Adjust",
                "resource": "inventory.*",
                "action": "adjust",
                "effect": "allow",
                "description": "Adjust stock quantities",
            },
            {
                "name": "Inventory: Audit",
                "resource": "inventory.*",
                "action": "audit",
                "effect": "allow",
                "description": "Perform inventory audits and reconciliations",
            },
            # Purchasing policies
            {
                "name": "Purchasing: View",
                "resource": "purchasing.*",
                "action": "view",
                "effect": "allow",
                "description": "View purchasing data",
            },
            {
                "name": "Purchasing: Manage",
                "resource": "purchasing.*",
                "action": "manage",
                "effect": "allow",
                "description": "Create and manage purchase orders",
            },
            {
                "name": "Purchasing: Create",
                "resource": "purchasing.order",
                "action": "create",
                "effect": "allow",
                "description": "Create draft purchase orders",
            },
            {
                "name": "Purchasing: Issue",
                "resource": "purchasing.order",
                "action": "issue",
                "effect": "allow",
                "description": "Issue purchase orders to suppliers",
            },
            {
                "name": "Purchasing: Receive",
                "resource": "purchasing.order",
                "action": "receive",
                "effect": "allow",
                "description": "Receive stock against purchase orders",
            },
            {
                "name": "Purchasing: Cancel",
                "resource": "purchasing.order",
                "action": "cancel",
                "effect": "allow",
                "description": "Cancel purchase orders",
            },
            # Sales policies
            {
                "name": "Sales: View",
                "resource": "sales.*",
                "action": "view",
                "effect": "allow",
                "description": "View sales orders and customer data",
            },
            {
                "name": "Sales: Manage",
                "resource": "sales.*",
                "action": "manage",
                "effect": "allow",
                "description": "Create and manage sales orders",
            },
            {
                "name": "Sales: Create",
                "resource": "sales.order",
                "action": "create",
                "effect": "allow",
                "description": "Create draft sales orders",
            },
            {
                "name": "Sales: Confirm",
                "resource": "sales.order",
                "action": "confirm",
                "effect": "allow",
                "description": "Confirm draft sales orders",
            },
            {
                "name": "Sales: Void",
                "resource": "sales.order",
                "action": "void",
                "effect": "allow",
                "description": "Void confirmed sales orders",
            },
            {
                "name": "Sales: Add Item",
                "resource": "sales.order",
                "action": "add_item",
                "effect": "allow",
                "description": "Add line items to draft orders",
            },
            # Customer policies
            {
                "name": "Customer: View",
                "resource": "customer.*",
                "action": "view",
                "effect": "allow",
                "description": "View customer records",
            },
            {
                "name": "Customer: Manage",
                "resource": "customer.*",
                "action": "manage",
                "effect": "allow",
                "description": "Create and manage customer records",
            },
            # Audit policies
            {
                "name": "Audit: View",
                "resource": "audit.*",
                "action": "view",
                "effect": "allow",
                "description": "View audit logs",
            },
            {
                "name": "Audit: Manage",
                "resource": "audit.*",
                "action": "manage",
                "effect": "allow",
                "description": "Manage audit records",
            },
            # Executive wildcard (full access)
            {
                "name": "Executive: Full Access",
                "resource": "*",
                "action": "*",
                "effect": "allow",
                "description": "Full access to all resources and actions",
            },
        ]

        for policy_data in policies_data:
            policy, created = Policy.objects.get_or_create(
                name=policy_data["name"],
                defaults={
                    "resource": policy_data["resource"],
                    "action": policy_data["action"],
                    "effect": policy_data["effect"],
                    "description": policy_data["description"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created: {policy.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  Exists: {policy.name}"))

        self.stdout.write()

    def _seed_roles(self):
        """Create roles with proper policy assignments."""
        self.stdout.write("Seeding Roles...")

        # Departments
        executive_dept = Department.objects.get(name="Executive")
        logistics_dept = Department.objects.get(name="Logistics")
        commercial_dept = Department.objects.get(name="Commercial")
        finance_dept = Department.objects.get(name="Finance")

        # Policies
        inv_view = Policy.objects.get(name="Inventory: View")
        inv_adjust = Policy.objects.get(name="Inventory: Adjust")
        inv_audit = Policy.objects.get(name="Inventory: Audit")
        pur_view = Policy.objects.get(name="Purchasing: View")
        pur_manage = Policy.objects.get(name="Purchasing: Manage")
        pur_create = Policy.objects.get(name="Purchasing: Create")
        pur_issue = Policy.objects.get(name="Purchasing: Issue")
        pur_receive = Policy.objects.get(name="Purchasing: Receive")
        pur_cancel = Policy.objects.get(name="Purchasing: Cancel")
        sales_view = Policy.objects.get(name="Sales: View")
        sales_manage = Policy.objects.get(name="Sales: Manage")
        sales_create = Policy.objects.get(name="Sales: Create")
        sales_confirm = Policy.objects.get(name="Sales: Confirm")
        sales_void = Policy.objects.get(name="Sales: Void")
        sales_add_item = Policy.objects.get(name="Sales: Add Item")
        cust_view = Policy.objects.get(name="Customer: View")
        cust_manage = Policy.objects.get(name="Customer: Manage")
        audit_view = Policy.objects.get(name="Audit: View")
        audit_manage = Policy.objects.get(name="Audit: Manage")
        exec_full = Policy.objects.get(name="Executive: Full Access")

        roles_data = [
            # Owner gets ALL roles (assigned separately in _seed_employees)
            {
                "name": "Owner",
                "department": executive_dept,
                "policies": [exec_full],
                "description": "Full system access",
            },
            # Warehouse Lead: inventory.* + purchasing.*
            {
                "name": "Warehouse Lead",
                "department": logistics_dept,
                "policies": [
                    inv_view, inv_adjust, inv_audit,
                    pur_view, pur_manage, pur_create, pur_issue, pur_receive, pur_cancel,
                ],
                "description": "Full inventory and purchasing access",
            },
            # Sales Manager: sales.* + customer.*
            {
                "name": "Sales Manager",
                "department": commercial_dept,
                "policies": [
                    sales_view, sales_manage, sales_create, sales_confirm, sales_void, sales_add_item,
                    cust_view, cust_manage,
                ],
                "description": "Sales and customer management",
            },
            # Auditor: audit.* + inventory:audit
            {
                "name": "Auditor",
                "department": finance_dept,
                "policies": [audit_view, audit_manage, inv_audit],
                "description": "Audit oversight and inventory reconciliation",
            },
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data["name"],
                department=role_data["department"],
                defaults={"description": role_data["description"]},
            )
            if created:
                role.policies.set(role_data["policies"])
                self.stdout.write(self.style.SUCCESS(f"  Created: {role.name} ({role.department.name})"))
            else:
                role.policies.set(role_data["policies"])
                self.stdout.write(self.style.WARNING(f"  Exists: {role.name} ({role.department.name})"))

        self.stdout.write()

    def _seed_employees(self):
        """Create employee personas. Owner gets ALL roles."""
        self.stdout.write("Seeding Employees...")

        # All roles
        owner_role = Role.objects.get(name="Owner", department__name="Executive")
        warehouse_role = Role.objects.get(name="Warehouse Lead", department__name="Logistics")
        sales_role = Role.objects.get(name="Sales Manager", department__name="Commercial")
        auditor_role = Role.objects.get(name="Auditor", department__name="Finance")

        # Owner gets ALL roles
        owner_all_roles = [owner_role, warehouse_role, sales_role, auditor_role]

        employees_data = [
            {
                "email": "amw@amw.io",
                "first_name": "Ahmad",
                "last_name": "Waddah",
                "is_staff": True,
                "is_superuser": True,
                "roles": owner_all_roles,
                "password": "12",
            },
            {
                "email": "warehouse.lead@amw.io",
                "first_name": "Warehouse",
                "last_name": "Lead",
                "is_staff": False,
                "is_superuser": False,
                "roles": [warehouse_role],
                "password": "password123",
            },
            {
                "email": "sales.manager@amw.io",
                "first_name": "Sales",
                "last_name": "Manager",
                "is_staff": False,
                "is_superuser": False,
                "roles": [sales_role],
                "password": "password123",
            },
            {
                "email": "auditor@amw.io",
                "first_name": "Finance",
                "last_name": "Auditor",
                "is_staff": False,
                "is_superuser": False,
                "roles": [auditor_role],
                "password": "password123",
            },
        ]

        for emp_data in employees_data:
            employee, created = Employee.objects.get_or_create(
                email=emp_data["email"],
                defaults={
                    "first_name": emp_data["first_name"],
                    "last_name": emp_data["last_name"],
                    "is_staff": emp_data["is_staff"],
                    "is_superuser": emp_data["is_superuser"],
                },
            )
            employee.roles.set(emp_data["roles"])
            employee.set_password(emp_data["password"])
            employee.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created: {employee.get_full_name()} ({employee.email})"))
            else:
                self.stdout.write(self.style.WARNING(f"  Updated: {employee.get_full_name()} ({employee.email})"))

        self.stdout.write()

    # -- Product Catalog -------------------------------------------------

    def _seed_categories(self):
        """Seed product categories."""
        self.stdout.write("Seeding Categories...")

        try:
            from inventory.models import Category

            categories_data = [
                {"name": "Major Appliances", "description": "Large household appliances"},
                {"name": "Small Appliances", "description": "Portable household appliances"},
                {"name": "Kitchenware", "description": "Kitchen tools and equipment"},
                {"name": "Cleaning & Home", "description": "Cleaning supplies and home care"},
                {"name": "Electronics", "description": "Consumer electronics and accessories"},
            ]

            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data["name"],
                    defaults={"description": cat_data["description"]},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created: {category.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Exists: {category.name}"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Inventory app not found - skipping categories"))

        self.stdout.write()

    def _seed_products(self):
        """Seed sample products for WAC engine testing."""
        self.stdout.write("Seeding Products...")

        try:
            from inventory.models import Category, Product

            maj = Category.objects.get(name="Major Appliances")
            sml = Category.objects.get(name="Small Appliances")
            kit = Category.objects.get(name="Kitchenware")
            cln = Category.objects.get(name="Cleaning & Home")
            elc = Category.objects.get(name="Electronics")

            products_data = [
                {
                    "sku": "MAJ-FR-500",
                    "name": "Frost-Free Refrigerator 500L",
                    "category": maj,
                    "unit_of_measure": "pcs",
                    "description": "Energy-efficient frost-free refrigerator 500L",
                    "location_note": "Warehouse A, Shelf 1-3",
                },
                {
                    "sku": "MAJ-WM-CR159",
                    "name": "Washing Machine Crazy 159",
                    "category": maj,
                    "unit_of_measure": "pcs",
                    "description": "Front-load washing machine 159 programs",
                    "location_note": "Warehouse A, Shelf 4-6",
                },
                {
                    "sku": "MAJ-OV-ELC",
                    "name": "Electric Convection Oven",
                    "category": maj,
                    "unit_of_measure": "pcs",
                    "description": "Countertop electric convection oven",
                    "location_note": "Warehouse A, Shelf 7-9",
                },
                {
                    "sku": "MAJ-AC-12",
                    "name": "Split AC 12000 BTU",
                    "category": maj,
                    "unit_of_measure": "pcs",
                    "description": "Energy-efficient split AC 12000 BTU",
                    "location_note": "Warehouse A, Shelf 10-12",
                },
                {
                    "sku": "SML-IR-STM",
                    "name": "Steam Iron Pro",
                    "category": sml,
                    "unit_of_measure": "pcs",
                    "description": "Professional steam iron ceramic soleplate",
                    "location_note": "Warehouse B, Shelf A2",
                },
                {
                    "sku": "SML-VL-18",
                    "name": "Vacuum Cleaner 1800W",
                    "category": sml,
                    "unit_of_measure": "pcs",
                    "description": "Bagless vacuum 1800W HEPA filter",
                    "location_note": "Warehouse B, Shelf A3",
                },
                {
                    "sku": "SML-HD-22",
                    "name": "Hair Dryer 2200W",
                    "category": sml,
                    "unit_of_measure": "pcs",
                    "description": "Professional hair dryer 2200W ionic",
                    "location_note": "Warehouse B, Shelf A4",
                },
                {
                    "sku": "KIT-BL-HSP",
                    "name": "High-Speed Blender",
                    "category": kit,
                    "unit_of_measure": "pcs",
                    "description": "Professional high-speed blender",
                    "location_note": "Warehouse B, Shelf B1",
                },
                {
                    "sku": "KIT-TS-4S",
                    "name": "4-Slice Toaster",
                    "category": kit,
                    "unit_of_measure": "pcs",
                    "description": "Stainless steel 4-slice toaster bagel mode",
                    "location_note": "Warehouse B, Shelf B2",
                },
                {
                    "sku": "KIT-MX-5L",
                    "name": "Stand Mixer 5L",
                    "category": kit,
                    "unit_of_measure": "pcs",
                    "description": "5-liter stand mixer dough hook whisk",
                    "location_note": "Warehouse B, Shelf B3",
                },
                {
                    "sku": "CLN-AF-2L",
                    "name": "Air Freshener 2L",
                    "category": cln,
                    "unit_of_measure": "pcs",
                    "description": "Automatic air freshener 2L lavender",
                    "location_note": "Warehouse C, Shelf A1",
                },
                {
                    "sku": "CLN-VC-3L",
                    "name": "Floor Cleaner 3L",
                    "category": cln,
                    "unit_of_measure": "pcs",
                    "description": "Multi-surface floor cleaner 3L",
                    "location_note": "Warehouse C, Shelf A2",
                },
                {
                    "sku": "ELC-LED-55",
                    "name": "LED TV 55 inch 4K",
                    "category": elc,
                    "unit_of_measure": "pcs",
                    "description": "55-inch 4K Smart LED TV HDR",
                    "location_note": "Warehouse D, Shelf A1",
                },
                {
                    "sku": "ELC-SB-21",
                    "name": "Soundbar 2.1 Channel",
                    "category": elc,
                    "unit_of_measure": "pcs",
                    "description": "2.1 channel soundbar wireless subwoofer",
                    "location_note": "Warehouse D, Shelf A2",
                },
            ]

            for prod_data in products_data:
                product, created = Product.objects.get_or_create(
                    sku=prod_data["sku"],
                    defaults={
                        "name": prod_data["name"],
                        "category": prod_data["category"],
                        "unit_of_measure": prod_data["unit_of_measure"],
                        "description": prod_data["description"],
                        "location_note": prod_data["location_note"],
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created: {product.name} ({product.sku})"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Exists: {product.name} ({product.sku})"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Inventory app not found - skipping products"))

        self.stdout.write()

    def _seed_initial_stock(self):
        """Seed initial stock levels using stock_in operations."""
        self.stdout.write("Seeding Initial Stock Levels...")

        try:
            from inventory.models import Product
            from inventory.operations.stock import StockChangeType, stock_in

            owner = Employee.objects.get(email="amw@amw.io")

            stock_data = [
                {"sku": "MAJ-FR-500", "quantity": Decimal("50.0000"), "unit_cost": Decimal("450.0000")},
                {"sku": "MAJ-WM-CR159", "quantity": Decimal("30.0000"), "unit_cost": Decimal("380.0000")},
                {"sku": "SML-IR-STM", "quantity": Decimal("100.0000"), "unit_cost": Decimal("25.5000")},
                {"sku": "MAJ-OV-ELC", "quantity": Decimal("40.0000"), "unit_cost": Decimal("120.0000")},
                {"sku": "KIT-BL-HSP", "quantity": Decimal("75.0000"), "unit_cost": Decimal("45.0000")},
                {"sku": "MAJ-AC-12", "quantity": Decimal("25.0000"), "unit_cost": Decimal("550.0000")},
                {"sku": "SML-VL-18", "quantity": Decimal("60.0000"), "unit_cost": Decimal("85.0000")},
                {"sku": "SML-HD-22", "quantity": Decimal("90.0000"), "unit_cost": Decimal("35.0000")},
                {"sku": "KIT-TS-4S", "quantity": Decimal("55.0000"), "unit_cost": Decimal("55.0000")},
                {"sku": "KIT-MX-5L", "quantity": Decimal("35.0000"), "unit_cost": Decimal("150.0000")},
                {"sku": "CLN-AF-2L", "quantity": Decimal("200.0000"), "unit_cost": Decimal("8.0000")},
                {"sku": "CLN-VC-3L", "quantity": Decimal("150.0000"), "unit_cost": Decimal("12.0000")},
                {"sku": "ELC-LED-55", "quantity": Decimal("20.0000"), "unit_cost": Decimal("350.0000")},
                {"sku": "ELC-SB-21", "quantity": Decimal("40.0000"), "unit_cost": Decimal("95.0000")},
            ]

            for stock_item in stock_data:
                try:
                    product = Product.objects.get(sku=stock_item["sku"])
                    stock_in(
                        product=product,
                        quantity=stock_item["quantity"],
                        unit_cost=stock_item["unit_cost"],
                        employee=owner,
                        change_type=StockChangeType.INTAKE,
                        notes="Initial stock seeding",
                    )
                    product.refresh_from_db()
                    self.stdout.write(
                        self.style.SUCCESS(f"  {product.sku}: {product.current_stock} units @ WAC {product.wac_price}")
                    )
                except Product.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  Product {stock_item['sku']} not found - skipping"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Inventory app not found - skipping stock levels"))

        self.stdout.write()

    # -- Sales & CRM -----------------------------------------------------

    def _seed_customer_categories(self):
        """Seed customer categories."""
        self.stdout.write("Seeding Customer Categories...")

        try:
            from sales.models import CustomerCategory

            categories_data = [
                {"name": "Retail", "description": "Individual retail customers"},
                {"name": "Corporate", "description": "Corporate and business customers"},
                {"name": "VIP", "description": "VIP and premium customers"},
                {"name": "Wholesale", "description": "Wholesale and bulk buyers"},
            ]

            for cat_data in categories_data:
                category, created = CustomerCategory.objects.get_or_create(
                    name=cat_data["name"],
                    defaults={"description": cat_data["description"]},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created: {category.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Exists: {category.name}"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Sales app not found - skipping customer categories"))

        self.stdout.write()

    def _seed_customers(self):
        """Seed customer records."""
        self.stdout.write("Seeding Customers...")

        try:
            from sales.models import Customer, CustomerCategory

            retail = CustomerCategory.objects.get(name="Retail")
            corporate = CustomerCategory.objects.get(name="Corporate")
            vip = CustomerCategory.objects.get(name="VIP")
            wholesale = CustomerCategory.objects.get(name="Wholesale")

            customers_data = [
                {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+20 123 456 7890",
                    "category": retail,
                    "shipping_address": "123 Tahrir St, Cairo, Egypt",
                },
                {
                    "name": "ABC Corporation",
                    "email": "purchasing@abc-corp.com",
                    "phone": "+20 2 3456 7890",
                    "category": corporate,
                    "shipping_address": "456 Business Park, New Cairo, Egypt",
                },
                {
                    "name": "Ahmed Mohamed",
                    "email": "ahmed.vip@example.com",
                    "phone": "+20 100 999 8888",
                    "category": vip,
                    "shipping_address": "789 Nile Corniche, Zamalek, Cairo, Egypt",
                },
                {
                    "name": "Sara Ali",
                    "email": "sara.ali@example.com",
                    "phone": "+20 111 222 3333",
                    "category": retail,
                    "shipping_address": "10 Heliopolis Ave, Cairo, Egypt",
                },
                {
                    "name": "Delta Hotels Group",
                    "email": "orders@deltahotels.com",
                    "phone": "+20 2 7654 3210",
                    "category": wholesale,
                    "shipping_address": "Delta Hotels Warehouse, 6th October City, Egypt",
                },
                {
                    "name": "Omar Hassan",
                    "email": "omar.h@example.com",
                    "phone": "+20 122 333 4444",
                    "category": vip,
                    "shipping_address": "Maadi Riverside, Cairo, Egypt",
                },
            ]

            for cust_data in customers_data:
                customer, created = Customer.objects.get_or_create(
                    name=cust_data["name"],
                    defaults={
                        "email": cust_data["email"],
                        "phone": cust_data["phone"],
                        "category": cust_data["category"],
                        "shipping_address": cust_data["shipping_address"],
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created: {customer.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Exists: {customer.name}"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Sales app not found - skipping customers"))

        self.stdout.write()

    def _seed_sales_orders(self):
        """Seed sales orders in various states."""
        self.stdout.write("Seeding Sales Orders...")

        try:
            from sales.logic.pricing import calculate_order_totals
            from sales.models import (
                Customer,
                OrderStatus,
                PaymentMethod,
                PaymentStatus,
                SalesOrder,
                SalesOrderItem,
            )
            from sales.operations.orders import confirm_order, generate_order_number, void_order

            sales_mgr = Employee.objects.get(email="sales.manager@amw.io")

            john = Customer.objects.get(name="John Doe")
            abc_corp = Customer.objects.get(name="ABC Corporation")
            ahmed = Customer.objects.get(name="Ahmed Mohamed")
            sara = Customer.objects.get(name="Sara Ali")

            from inventory.models import Product

            refrigerator = Product.objects.get(sku="MAJ-FR-500")
            washing_machine = Product.objects.get(sku="MAJ-WM-CR159")
            iron = Product.objects.get(sku="SML-IR-STM")
            oven = Product.objects.get(sku="MAJ-OV-ELC")
            blender = Product.objects.get(sku="KIT-BL-HSP")
            hair_dryer = Product.objects.get(sku="SML-HD-22")

            # Order 1: Draft
            order1 = SalesOrder.objects.create(
                order_number=generate_order_number(),
                customer=abc_corp,
                created_by=sales_mgr,
                shipping_address_snapshot=abc_corp.shipping_address,
                status=OrderStatus.DRAFT,
                payment_status=PaymentStatus.PENDING,
                notes="Draft order - awaiting customer confirmation",
            )
            SalesOrderItem.objects.create(
                order=order1, product=refrigerator, quantity=Decimal("2.0000"), snapshot_unit_price=Decimal("450.0000")
            )
            SalesOrderItem.objects.create(
                order=order1,
                product=washing_machine,
                quantity=Decimal("1.0000"),
                snapshot_unit_price=Decimal("380.0000"),
            )
            subtotal, tax, total = calculate_order_totals(order1)
            order1.subtotal, order1.tax_amount, order1.total_amount = subtotal, tax, total
            order1.save()
            self.stdout.write(self.style.SUCCESS(f"  Created Draft: {order1.order_number} ({order1.total_amount})"))

            # Order 2: Confirmed + Partially Paid
            order2 = SalesOrder.objects.create(
                order_number=generate_order_number(),
                customer=john,
                created_by=sales_mgr,
                shipping_address_snapshot=john.shipping_address,
                status=OrderStatus.DRAFT,
                payment_status=PaymentStatus.PENDING,
            )
            SalesOrderItem.objects.create(
                order=order2, product=iron, quantity=Decimal("3.0000"), snapshot_unit_price=Decimal("25.5000")
            )
            SalesOrderItem.objects.create(
                order=order2, product=blender, quantity=Decimal("1.0000"), snapshot_unit_price=Decimal("45.0000")
            )
            subtotal, tax, total = calculate_order_totals(order2)
            order2.subtotal, order2.tax_amount, order2.total_amount = subtotal, tax, total
            order2.save()
            confirm_order(order2, sales_mgr)
            order2.amount_paid = Decimal("50.0000")
            order2.payment_status = PaymentStatus.PARTIALLY_PAID
            order2.payment_method = PaymentMethod.COD
            order2.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Created Confirmed: {order2.order_number} ({order2.total_amount}, Partially Paid)"
                )
            )

            # Order 3: Shipped + Paid
            order3 = SalesOrder.objects.create(
                order_number=generate_order_number(),
                customer=ahmed,
                created_by=sales_mgr,
                shipping_address_snapshot=ahmed.shipping_address,
                status=OrderStatus.DRAFT,
                payment_status=PaymentStatus.PENDING,
            )
            SalesOrderItem.objects.create(
                order=order3, product=oven, quantity=Decimal("1.0000"), snapshot_unit_price=Decimal("120.0000")
            )
            SalesOrderItem.objects.create(
                order=order3, product=refrigerator, quantity=Decimal("1.0000"), snapshot_unit_price=Decimal("450.0000")
            )
            subtotal, tax, total = calculate_order_totals(order3)
            order3.subtotal, order3.tax_amount, order3.total_amount = subtotal, tax, total
            order3.save()
            confirm_order(order3, sales_mgr)
            order3.status = OrderStatus.SHIPPED
            order3.payment_status = PaymentStatus.PAID
            order3.payment_method = PaymentMethod.CREDIT_CARD
            order3.amount_paid = total
            order3.save()
            self.stdout.write(
                self.style.SUCCESS(f"  Created Shipped: {order3.order_number} ({order3.total_amount}, Paid)")
            )

            # Order 4: Voided
            order4 = SalesOrder.objects.create(
                order_number=generate_order_number(),
                customer=sara,
                created_by=sales_mgr,
                shipping_address_snapshot=sara.shipping_address,
                status=OrderStatus.DRAFT,
                payment_status=PaymentStatus.PENDING,
                notes="Customer requested cancellation",
            )
            SalesOrderItem.objects.create(
                order=order4, product=hair_dryer, quantity=Decimal("2.0000"), snapshot_unit_price=Decimal("35.0000")
            )
            subtotal, tax, total = calculate_order_totals(order4)
            order4.subtotal, order4.tax_amount, order4.total_amount = subtotal, tax, total
            order4.save()
            void_order(order4, sales_mgr, reason="Customer cancelled order")
            self.stdout.write(self.style.WARNING(f"  Created Voided: {order4.order_number} ({order4.total_amount})"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Sales app not found - skipping sales orders"))

        self.stdout.write()

    # -- Purchasing ------------------------------------------------------

    def _seed_supplier_categories(self):
        """Seed supplier categories."""
        self.stdout.write("Seeding Supplier Categories...")

        try:
            from purchasing.models import SupplierCategory

            categories_data = [
                {"name": "Raw Materials", "description": "Raw material suppliers"},
                {"name": "Electronics", "description": "Electronic component suppliers"},
                {"name": "Packaging", "description": "Packaging material suppliers"},
                {"name": "Logistics", "description": "Shipping and logistics providers"},
            ]

            for cat_data in categories_data:
                category, created = SupplierCategory.objects.get_or_create(
                    name=cat_data["name"],
                    defaults={"description": cat_data["description"]},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created: {category.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Exists: {category.name}"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Purchasing app not found - skipping supplier categories"))

        self.stdout.write()

    def _seed_suppliers(self):
        """Seed supplier records."""
        self.stdout.write("Seeding Suppliers...")

        try:
            from purchasing.models import Supplier, SupplierCategory

            raw_mat = SupplierCategory.objects.get(name="Raw Materials")
            electronics = SupplierCategory.objects.get(name="Electronics")
            packaging = SupplierCategory.objects.get(name="Packaging")
            logistics = SupplierCategory.objects.get(name="Logistics")

            suppliers_data = [
                {
                    "name": "Cairo Steel Co.",
                    "email": "sales@cairosteel.com",
                    "phone": "+20 2 1234 5678",
                    "category": raw_mat,
                    "address": "Industrial Zone, 10th of Ramadan, Egypt",
                    "contact_person": "Mahmoud Ibrahim",
                    "notes": "Primary steel supplier, net-30 terms",
                },
                {
                    "name": "Alex Plastics",
                    "email": "orders@alexplastics.com",
                    "phone": "+20 3 9876 5432",
                    "category": raw_mat,
                    "address": "Borg El Arab, Alexandria, Egypt",
                    "contact_person": "Fatma Nasser",
                    "notes": "Plastic raw materials, COD",
                },
                {
                    "name": "TechParts Egypt",
                    "email": "info@techparts.eg",
                    "phone": "+20 2 5555 1234",
                    "category": electronics,
                    "address": "Smart Village, 6th October City, Egypt",
                    "contact_person": "Karim Adel",
                    "notes": "Electronic components and circuit boards",
                },
                {
                    "name": "PackRight Solutions",
                    "email": "sales@packright.com",
                    "phone": "+20 2 4444 5678",
                    "category": packaging,
                    "address": "Obour City, Cairo, Egypt",
                    "contact_person": "Nadia Hassan",
                    "notes": "Cardboard boxes and packaging materials",
                },
                {
                    "name": "FastShip Logistics",
                    "email": "dispatch@fastship.eg",
                    "phone": "+20 2 3333 9999",
                    "category": logistics,
                    "address": "Cairo International Airport Cargo, Egypt",
                    "contact_person": "Omar Tarek",
                    "notes": "Express shipping and freight forwarding",
                },
            ]

            for sup_data in suppliers_data:
                supplier, created = Supplier.objects.get_or_create(
                    name=sup_data["name"],
                    defaults={
                        "email": sup_data["email"],
                        "phone": sup_data["phone"],
                        "category": sup_data["category"],
                        "address": sup_data["address"],
                        "contact_person": sup_data["contact_person"],
                        "notes": sup_data["notes"],
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  Created: {supplier.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Exists: {supplier.name}"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  Purchasing app not found - skipping suppliers"))

        self.stdout.write()

    def _seed_purchase_orders(self):
        """Seed purchase orders in various states."""
        self.stdout.write("Seeding Purchase Orders...")

        try:
            from decimal import Decimal as D

            from purchasing.models import POStatus, PurchaseOrder, PurchaseOrderItem, Supplier
            from purchasing.operations.orders import generate_po_number, issue_order, receive_items

            if PurchaseOrder.objects.exists():
                self.stdout.write(self.style.WARNING("  Purchase orders already exist - skipping"))
                return

            cairo_steel = Supplier.objects.get(name="Cairo Steel Co.")
            tech_parts = Supplier.objects.get(name="TechParts Egypt")
            packright = Supplier.objects.get(name="PackRight Solutions")

            owner = Employee.objects.get(email="amw@amw.io")

            from inventory.models import Product

            fridge = Product.objects.get(sku="MAJ-FR-500")
            oven = Product.objects.get(sku="MAJ-OV-ELC")
            blender = Product.objects.get(sku="KIT-BL-HSP")
            ac_unit = Product.objects.get(sku="MAJ-AC-12")

            # PO 1: Draft
            po1 = PurchaseOrder.objects.create(
                po_number=generate_po_number(),
                supplier=cairo_steel,
                created_by=owner,
                status=POStatus.DRAFT,
                notes="Draft PO - pending approval",
            )
            PurchaseOrderItem.objects.create(order=po1, product=fridge, quantity=D("20.0000"), unit_cost=D("400.0000"))
            PurchaseOrderItem.objects.create(order=po1, product=ac_unit, quantity=D("15.0000"), unit_cost=D("500.0000"))
            po1.total_cost = sum(item.total_cost for item in po1.items.all())
            po1.save()
            self.stdout.write(self.style.SUCCESS(f"  Created Draft PO: {po1.po_number} ({po1.total_cost})"))

            # PO 2: Issued
            po2 = PurchaseOrder.objects.create(
                po_number=generate_po_number(),
                supplier=tech_parts,
                created_by=owner,
                status=POStatus.DRAFT,
                notes="Electronic components order",
            )
            PurchaseOrderItem.objects.create(order=po2, product=blender, quantity=D("50.0000"), unit_cost=D("35.0000"))
            po2.total_cost = sum(item.total_cost for item in po2.items.all())
            po2.save()
            issue_order(po2, owner)
            self.stdout.write(self.style.SUCCESS(f"  Created Issued PO: {po2.po_number} ({po2.total_cost})"))

            # PO 3: In-Progress (partially received)
            po3 = PurchaseOrder.objects.create(
                po_number=generate_po_number(),
                supplier=packright,
                created_by=owner,
                status=POStatus.DRAFT,
                notes="Packaging materials restock",
            )
            po3_item = PurchaseOrderItem.objects.create(
                order=po3, product=oven, quantity=D("30.0000"), unit_cost=D("95.0000")
            )
            po3.total_cost = sum(item.total_cost for item in po3.items.all())
            po3.save()
            issue_order(po3, owner)
            receive_items(po3, [{"item_id": po3_item.id, "quantity": D("10.0000")}], owner, "Warehouse A")
            self.stdout.write(self.style.SUCCESS(f"  Created In-Progress PO: {po3.po_number} ({po3.total_cost})"))

            # PO 4: Completed (fully received)
            po4 = PurchaseOrder.objects.create(
                po_number=generate_po_number(),
                supplier=cairo_steel,
                created_by=owner,
                status=POStatus.DRAFT,
                notes="Completed steel order",
            )
            po4_item = PurchaseOrderItem.objects.create(
                order=po4, product=fridge, quantity=D("10.0000"), unit_cost=D("420.0000")
            )
            po4.total_cost = sum(item.total_cost for item in po4.items.all())
            po4.save()
            issue_order(po4, owner)
            receive_items(po4, [{"item_id": po4_item.id, "quantity": D("10.0000")}], owner, "Warehouse A")
            self.stdout.write(self.style.SUCCESS(f"  Created Completed PO: {po4.po_number} ({po4.total_cost})"))

        except ImportError:
            self.stdout.write(self.style.WARNING("  Purchasing app not found - skipping purchase orders"))

        self.stdout.write()
