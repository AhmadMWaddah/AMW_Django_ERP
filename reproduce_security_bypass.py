"""
Focused IAM regression script for Phase 7.5 closure.

Run with the project virtualenv active:
    python reproduce_security_bypass.py

The script exercises the main bypass paths discussed in the IAM audit and
prints PASS/FAIL lines for each gate. It exits non-zero on the first failure.
"""

import logging
import os
import sys
import uuid
from decimal import Decimal

import django

# Django setup must happen before any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()
logging.getLogger("django").setLevel(logging.ERROR)

from django.db import transaction  # noqa: E402
from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

from accounts.models import Employee  # noqa: E402
from inventory.models import Category as InventoryCategory  # noqa: E402
from inventory.models import Product  # noqa: E402
from purchasing.models import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierCategory  # noqa: E402
from purchasing.operations.orders import issue_order  # noqa: E402
from sales.models import Customer, CustomerCategory  # noqa: E402
from security.models import Department, Policy, Role  # noqa: E402


def check(condition, label, detail=""):
    if condition:
        print(f"PASS: {label}")
        return

    if detail:
        print(f"FAIL: {label} ({detail})")
    else:
        print(f"FAIL: {label}")
    sys.exit(1)


def main():
    token = uuid.uuid4().hex[:8]

    with transaction.atomic():
        purchasing_dept = Department.objects.create(name=f"Purchasing Audit {token}")
        sales_dept = Department.objects.create(name=f"Sales Audit {token}")
        inventory_dept = Department.objects.create(name=f"Inventory Audit {token}")

        purchasing_view_role = Role.objects.create(name=f"Purchasing Viewer {token}", department=purchasing_dept)
        purchasing_receive_role = Role.objects.create(name=f"Purchasing Receiver {token}", department=purchasing_dept)
        sales_create_role = Role.objects.create(name=f"Sales Creator {token}", department=sales_dept)
        inventory_adjust_role = Role.objects.create(name=f"Inventory Adjuster {token}", department=inventory_dept)

        Policy.objects.create(
            name=f"Purchasing View {token}",
            resource="purchasing.*",
            action="view",
            effect="allow",
        ).roles.add(purchasing_view_role)
        Policy.objects.create(
            name=f"Purchasing Receive {token}",
            resource="purchasing.order",
            action="receive",
            effect="allow",
        ).roles.add(purchasing_receive_role)
        Policy.objects.create(
            name=f"Sales Create {token}",
            resource="sales.order",
            action="create",
            effect="allow",
        ).roles.add(sales_create_role)
        Policy.objects.create(
            name=f"Customer View {token}",
            resource="customer.*",
            action="view",
            effect="allow",
        ).roles.add(sales_create_role)
        Policy.objects.create(
            name=f"Inventory View {token}",
            resource="inventory.*",
            action="view",
            effect="allow",
        ).roles.add(inventory_adjust_role)
        Policy.objects.create(
            name=f"Inventory Adjust {token}",
            resource="inventory.stock",
            action="adjust",
            effect="allow",
        ).roles.add(inventory_adjust_role)

        unauthorized = Employee.objects.create_user(
            email=f"unauthorized.{token}@amw.io",
            password="test123",
            first_name="Unauthorized",
            last_name="Audit",
        )
        purchasing_user = Employee.objects.create_user(
            email=f"purchasing.{token}@amw.io",
            password="test123",
            first_name="Purchasing",
            last_name="Audit",
        )
        purchasing_user.roles.add(purchasing_view_role, purchasing_receive_role)

        sales_user = Employee.objects.create_user(
            email=f"sales.{token}@amw.io",
            password="test123",
            first_name="Sales",
            last_name="Audit",
        )
        sales_user.roles.add(sales_create_role)

        inventory_user = Employee.objects.create_user(
            email=f"inventory.{token}@amw.io",
            password="test123",
            first_name="Inventory",
            last_name="Audit",
        )
        inventory_user.roles.add(inventory_adjust_role)

        supplier_category = SupplierCategory.objects.create(name=f"Audit Supplier Category {token}")
        supplier = Supplier.objects.create(name=f"Audit Supplier {token}", category=supplier_category)
        inventory_category = InventoryCategory.objects.create(name=f"Audit Inventory Category {token}")
        product = Product.objects.create(
            sku=f"AUD-{token[:4].upper()}-01",
            name=f"Audit Product {token}",
            category=inventory_category,
            current_stock=Decimal("25.0000"),
            wac_price=Decimal("50.0000"),
        )

        po = PurchaseOrder.objects.create(supplier=supplier, created_by=purchasing_user)
        po_item = PurchaseOrderItem.objects.create(
            order=po,
            product=product,
            quantity=Decimal("10.0000"),
            unit_cost=Decimal("55.0000"),
        )
        issue_order(po, purchasing_user)

        customer_category = CustomerCategory.objects.create(name=f"Audit Customer Category {token}")
        customer = Customer.objects.create(
            name=f"Audit Customer {token}",
            category=customer_category,
            shipping_address="Audit Address",
        )

        purchasing_detail_url = reverse("Purchasing:OrderDetail", args=[po.id])
        receive_url = reverse("Purchasing:ReceiveStock", args=[po.id])
        customer_detail_url = reverse("Sales:CustomerDetail", args=[customer.slug])
        adjust_url = reverse("Inventory:AdjustStock", args=[product.slug])

        client = Client(HTTP_HOST="localhost")

        anonymous_response = client.get(purchasing_detail_url)
        check(
            anonymous_response.status_code == 302 and "login" in anonymous_response.headers.get("Location", "").lower(),
            "Anonymous users are redirected to login on protected GET views",
            f"status={anonymous_response.status_code}",
        )

        client.force_login(unauthorized)
        forbidden_page = client.get(purchasing_detail_url)
        check(forbidden_page.status_code == 403, "Unauthorized GET access is denied with HTTP 403")
        check(
            "Permission Denied" in forbidden_page.content.decode(),
            "Unauthorized GET access renders the branded 403 page",
        )

        forbidden_receive = client.post(receive_url, HTTP_HX_REQUEST="true")
        check(forbidden_receive.status_code == 403, "Unauthorized HTMX receive is denied")
        check(
            "showToast" in forbidden_receive.headers.get("HX-Trigger", ""),
            "Unauthorized HTMX receive includes toast trigger headers",
        )
        client.logout()

        client.force_login(purchasing_user)
        allowed_page = client.get(purchasing_detail_url)
        check(allowed_page.status_code == 200, "Authorized purchasing user can open PO detail")

        allowed_receive = client.post(
            receive_url,
            {"items": f'[{{"item_id": {po_item.id}, "quantity": "2"}}]'},
            HTTP_HX_REQUEST="true",
        )
        check(allowed_receive.status_code == 200, "Authorized purchasing HTMX receive succeeds")
        check(
            allowed_receive.headers.get("HX-Refresh") == "true",
            "Successful receive returns HX-Refresh for UI reload",
        )
        client.logout()

        client.force_login(sales_user)
        sales_page = client.get(customer_detail_url)
        check(sales_page.status_code == 200, "Sales user can open customer detail")
        check("Create Order" in sales_page.content.decode(), "Sales user sees the Create Order action")
        client.logout()

        client.force_login(inventory_user)
        inventory_page = client.get(reverse("Inventory:ProductDetail", args=[product.slug]))
        check(inventory_page.status_code == 200, "Inventory user can open product detail")
        check(
            "Quick Stock Adjustment" in inventory_page.content.decode(),
            "Inventory user sees the Quick Stock Adjustment action",
        )

        invalid_adjust = client.post(
            adjust_url,
            {"action": "in", "quantity": "0"},
            HTTP_HX_REQUEST="true",
        )
        check(invalid_adjust.status_code == 400, "Invalid stock adjustment is rejected")
        check(
            "showToast" in invalid_adjust.headers.get("HX-Trigger", ""),
            "Invalid stock adjustment returns an HTMX toast header",
        )

        print("PASS: All security gates verified")
        transaction.set_rollback(True)


if __name__ == "__main__":
    main()
