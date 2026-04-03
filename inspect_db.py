
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from security.models import Department, Role, Policy

Employee = get_user_model()

print("="*40)
print("AMW ERP - DATABASE INSPECTION")
print("="*40)

print("\n[1] IDENTITY CHECK")
superuser = Employee.objects.filter(email="amw@amw.io").first()
if superuser:
    print(f"Superuser: {superuser.email}")
    print(f"Is Superuser: {superuser.is_superuser}")
    print(f"Is Staff: {superuser.is_staff}")
    print(f"Assigned Roles: {[r.name for r in superuser.roles.all()]}")
else:
    print("CRITICAL: amw@amw.io NOT FOUND")

print("\n[2] DEPARTMENT STRUCTURE")
for d in Department.objects.all():
    print(f"Department: {d.name}")

print("\n[3] ROLE & POLICY ATTACHMENT")
for r in Role.objects.all():
    policies = [p.name for p in r.policies.all()]
    print(f"Role: {r.name} ({r.department.name})")
    print(f"  -> Policies: {policies}")

print("\n[4] DATA COVERAGE (MODELS)")
from inventory.models import Product
from sales.models import SalesOrder
from purchasing.models import PurchaseOrder

print(f"Products in system: {Product.objects.count()}")
print(f"Sales Orders in system: {SalesOrder.objects.count()}")
print(f"Purchase Orders in system: {PurchaseOrder.objects.count()}")
print("="*40)
