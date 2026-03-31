"""
AMW Django ERP - Seed ERP Data Command

Generates idempotent, persona-based dummy data for Phases 1-4.

Usage:
    python manage.py seed_erp              # Safe mode (aborts if DEBUG=False)
    python manage.py seed_erp --force      # Force mode (runs even in production)

Constitution Compliance:
- Double quotes for all Python strings (Section 11.5)
- Idempotent operations (safe for repeated execution)
- Safety check for production environments
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
    - Employee personas (Owner, Inventory Manager, Inventory Clerk, Sales Rep)
    - Department hierarchy (Executive, Logistics, Commercial)
    - Policies (inventory:*, sales:*)
    - Roles (Inventory Lead, Clerk, Sales)
    - Product catalog foundation (Phase 4 preparation)
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
        # Safety check: abort if not in DEBUG mode unless --force is provided
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
                    "⚠️  WARNING: Running in production mode! "
                    "This will create test data in your production database."
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

            # Phase 4: Initial Stock Levels
            self._seed_initial_stock()

        self.stdout.write()
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("✅ Seed complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write()
        self.stdout.write(self.style.SUCCESS("See CREDENTIALS.md file for login credentials and test data."))
        self.stdout.write()

    def _seed_departments(self):
        """Create department hierarchy."""
        self.stdout.write("📁 Seeding Departments...")

        departments_data = [
            {"name": "Executive", "description": "Executive management and ownership"},
            {"name": "Logistics", "description": "Warehouse, inventory, and shipping"},
            {"name": "Commercial", "description": "Sales and customer relations"},
        ]

        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data["name"],
                defaults=dept_data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {dept.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Exists: {dept.name}"))

        self.stdout.write()

    def _seed_policies(self):
        """Create policies for all modules."""
        self.stdout.write("🔐 Seeding Policies...")

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
            # Sales policies
            {
                "name": "Sales: View",
                "resource": "sales.*",
                "action": "view",
                "effect": "allow",
                "description": "View sales orders and customer data",
            },
            {
                "name": "Sales: Create",
                "resource": "sales.*",
                "action": "create",
                "effect": "allow",
                "description": "Create new sales orders",
            },
            # Executive policies (full access)
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
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {policy.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Exists: {policy.name}"))

        self.stdout.write()

    def _seed_roles(self):
        """Create roles and assign policies."""
        self.stdout.write("🎭 Seeding Roles...")

        # Get departments
        executive_dept = Department.objects.get(name="Executive")
        logistics_dept = Department.objects.get(name="Logistics")
        commercial_dept = Department.objects.get(name="Commercial")

        # Get policies
        inventory_view = Policy.objects.get(name="Inventory: View")
        inventory_adjust = Policy.objects.get(name="Inventory: Adjust")
        inventory_audit = Policy.objects.get(name="Inventory: Audit")
        sales_view = Policy.objects.get(name="Sales: View")
        sales_create = Policy.objects.get(name="Sales: Create")
        executive_full = Policy.objects.get(name="Executive: Full Access")

        roles_data = [
            {
                "name": "Owner",
                "department": executive_dept,
                "policies": [executive_full],
                "description": "Full system access",
            },
            {
                "name": "Inventory Lead",
                "department": logistics_dept,
                "policies": [inventory_view, inventory_adjust, inventory_audit],
                "description": "Full inventory management access",
            },
            {
                "name": "Clerk",
                "department": logistics_dept,
                "policies": [inventory_view, inventory_adjust],
                "description": "View and adjust stock (no audit)",
            },
            {
                "name": "Sales",
                "department": commercial_dept,
                "policies": [sales_view, sales_create],
                "description": "View and create sales orders",
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
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {role.name} ({role.department.name})"))
            else:
                role.policies.set(role_data["policies"])
                self.stdout.write(self.style.WARNING(f"  ⚠️  Exists: {role.name} ({role.department.name})"))

        self.stdout.write()

    def _seed_employees(self):
        """Create employee personas with roles."""
        self.stdout.write("👥 Seeding Employees...")

        # Get roles
        owner_role = Role.objects.get(name="Owner", department__name="Executive")
        inventory_lead_role = Role.objects.get(name="Inventory Lead", department__name="Logistics")
        clerk_role = Role.objects.get(name="Clerk", department__name="Logistics")
        sales_role = Role.objects.get(name="Sales", department__name="Commercial")

        employees_data = [
            {
                "email": "amw@amw.io",
                "first_name": "Ahmad",
                "last_name": "Manager",
                "is_staff": True,
                "is_superuser": True,
                "roles": [owner_role],
                "description": "The Owner - Superuser with full access",
            },
            {
                "email": "stock.manager@amw.io",
                "first_name": "Stock",
                "last_name": "Manager",
                "is_staff": False,
                "is_superuser": False,
                "roles": [inventory_lead_role],
                "description": "Inventory Manager - Full inventory access",
            },
            {
                "email": "stock.clerk@amw.io",
                "first_name": "Stock",
                "last_name": "Clerk",
                "is_staff": False,
                "is_superuser": False,
                "roles": [clerk_role],
                "description": "Inventory Clerk - View and adjust only",
            },
            {
                "email": "sales.rep@amw.io",
                "first_name": "Sales",
                "last_name": "Representative",
                "is_staff": False,
                "is_superuser": False,
                "roles": [sales_role],
                "description": "Sales Representative - Sales access",
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
            if created:
                employee.roles.set(emp_data["roles"])
                # Set password: "12" for Owner, "password123" for others
                if emp_data["email"] == "amw@amw.io":
                    employee.set_password("12")
                else:
                    employee.set_password("password123")
                employee.save()
                self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {employee.get_full_name()} ({employee.email})"))
            else:
                # Update roles even if exists
                employee.roles.set(emp_data["roles"])
                # Set password: "12" for Owner, "password123" for others
                if emp_data["email"] == "amw@amw.io":
                    employee.set_password("12")
                else:
                    employee.set_password("password123")
                employee.save()
                self.stdout.write(self.style.WARNING(f"  ⚠️  Exists: {employee.get_full_name()} ({employee.email})"))

        self.stdout.write()

    def _seed_categories(self):
        """
        Seed product categories for Phase 4.

        Creates hierarchical category structure for inventory.
        """
        self.stdout.write("📦 Seeding Categories (Phase 4)...")

        try:
            from inventory.models import Category

            categories_data = [
                {"name": "Major Appliances", "code": "MAJ", "description": "Large household appliances"},
                {"name": "Small Appliances", "code": "SML", "description": "Portable household appliances"},
                {"name": "Kitchenware", "code": "KIT", "description": "Kitchen tools and equipment"},
            ]

            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data["name"],
                    defaults={
                        "code": cat_data["code"],
                        "description": cat_data["description"],
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {category.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Exists: {category.name}"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  ⚠️  Inventory app not found - skipping categories"))

        self.stdout.write()

    def _seed_products(self):
        """
        Seed sample products for Phase 4 WAC engine testing.

        Creates products with SKU pattern: CATEGORY-SUBCATEGORY-MODEL
        """
        self.stdout.write("🏷️  Seeding Products (Phase 4)...")

        try:
            from inventory.models import Category, Product

            # Get categories
            maj_category = Category.objects.get(name="Major Appliances")
            sml_category = Category.objects.get(name="Small Appliances")
            kit_category = Category.objects.get(name="Kitchenware")

            products_data = [
                {
                    "sku": "MAJ-FR-500",
                    "name": "Frost-Free Refrigerator 500L",
                    "category": maj_category,
                    "unit_of_measure": "pcs",
                    "description": "Energy-efficient frost-free refrigerator with 500L capacity",
                    "location_note": "Warehouse A, Shelf 1-3",
                },
                {
                    "sku": "MAJ-WM-CR159",
                    "name": "Washing Machine Crazy 159",
                    "category": maj_category,
                    "unit_of_measure": "pcs",
                    "description": "Front-load washing machine with 159 programs",
                    "location_note": "Warehouse A, Shelf 4-6",
                },
                {
                    "sku": "SML-IR-STM",
                    "name": "Steam Iron Pro",
                    "category": sml_category,
                    "unit_of_measure": "pcs",
                    "description": "Professional steam iron with ceramic soleplate",
                    "location_note": "Warehouse B, Shelf A2",
                },
                {
                    "sku": "MAJ-OV-ELC",
                    "name": "Electric Convection Oven",
                    "category": maj_category,
                    "unit_of_measure": "pcs",
                    "description": "Countertop electric convection oven with digital controls",
                    "location_note": "Warehouse A, Shelf 7-9",
                },
                {
                    "sku": "KIT-BL-HSP",
                    "name": "High-Speed Blender",
                    "category": kit_category,
                    "unit_of_measure": "pcs",
                    "description": "Professional high-speed blender for smoothies",
                    "location_note": "Warehouse B, Shelf B1",
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
                    self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {product.name} ({product.sku})"))
                else:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Exists: {product.name} ({product.sku})"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  ⚠️  Inventory app not found - skipping products"))

        self.stdout.write()

    def _seed_initial_stock(self):
        """
        Seed initial stock levels for Phase 4 products.

        Uses stock_in operations to create proper transaction ledger entries
        and set initial WAC prices.
        """
        self.stdout.write("📊 Seeding Initial Stock Levels (Phase 4)...")

        try:
            from inventory.models import Product
            from inventory.operations.stock import stock_in, StockChangeType

            # Get the Owner employee for stock operations
            owner = Employee.objects.get(email="amw@amw.io")

            # Initial stock data: SKU, quantity, unit_cost
            stock_data = [
                {"sku": "MAJ-FR-500", "quantity": Decimal("50.0000"), "unit_cost": Decimal("450.0000")},
                {"sku": "MAJ-WM-CR159", "quantity": Decimal("30.0000"), "unit_cost": Decimal("380.0000")},
                {"sku": "SML-IR-STM", "quantity": Decimal("100.0000"), "unit_cost": Decimal("25.5000")},
                {"sku": "MAJ-OV-ELC", "quantity": Decimal("40.0000"), "unit_cost": Decimal("120.0000")},
                {"sku": "KIT-BL-HSP", "quantity": Decimal("75.0000"), "unit_cost": Decimal("45.0000")},
            ]

            for stock_item in stock_data:
                try:
                    product = Product.objects.get(sku=stock_item["sku"])

                    # Perform stock-in operation
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
                        self.style.SUCCESS(
                            f"  ✅ {product.sku}: {product.current_stock} units @ WAC {product.wac_price}"
                        )
                    )
                except Product.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Product {stock_item['sku']} not found - skipping"))
        except ImportError:
            self.stdout.write(self.style.WARNING("  ⚠️  Inventory app not found - skipping stock levels"))

        self.stdout.write()
