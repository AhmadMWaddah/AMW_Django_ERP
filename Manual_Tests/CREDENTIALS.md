# AMW Django ERP - Test Credentials

**Generated for:** Development & Manual Testing  
**Last Updated:** 2026-03-31

---

## 🔐 Employee Accounts

### Superuser / Owner

| Field            | Value                                           |
|------------------|-------------------------------------------------|
| **Email**        | `amw@amw.io`                                    |
| **Password**     | `12`                                            |
| **Role**         | Owner                                           |
| **Department**   | Executive                                       |
| **Permissions**  | Full system access (all resources, all actions) |
| **Admin Access** | ✅ Yes                                          |

---

### Other Employees (Default Password)

| Account                | Password         |
|------------------------|------------------|
| `stock.manager@amw.io` | `password123`    |
| `stock.clerk@amw.io`   | `password123`    |
| `sales.rep@amw.io`     | `password123`    |

---

### Inventory Manager

| Field            | Value                               |
|------------------|-------------------------------------|
| **Email**        | `stock.manager@amw.io`              |
| **Password**     | `password123`                       |
| **Role**         | Inventory Lead                      |
| **Department**   | Logistics                           |
| **Permissions**  | `inventory:*` (view, adjust, audit) |
| **Admin Access** | ❌ No                               |

---

### Inventory Clerk

| Field            | Value                               |
|------------------|-------------------------------------|
| **Email**        | `stock.clerk@amw.io`                |
| **Password**     | `password123`                       |
| **Role**         | Clerk                               |
| **Department**   | Logistics                           |
| **Permissions**  | `inventory:*` (view, adjust only)   |
| **Admin Access** | ❌ No                               |

---

### Sales Representative

| Field            | Value                               |
|------------------|-------------------------------------|
| **Email**        | `sales.rep@amw.io`                  |
| **Password**     | `password123`                       |
| **Role**         | Sales                               |
| **Department**   | Commercial                          |
| **Permissions**  | `sales:*` (view, create)            |
| **Admin Access** | ❌ No                               |

---

## 📁 Department Hierarchy

| Department | Code | Description                        |
|------------|------|------------------------------------|
| Executive  | -    | Executive management and ownership |
| Logistics  | -    | Warehouse, inventory, and shipping |
| Commercial | -    | Sales and customer relations       |

---

## 🔐 Policies

### Inventory Policies

| Policy Name       | Resource      | Action  | Effect |
|-------------------|---------------|---------|--------|
| Inventory: View   | `inventory.*` | `view`  | Allow  |
| Inventory: Adjust | `inventory.*` | `adjust`| Allow  |
| Inventory: Audit  | `inventory.*` | `audit` | Allow  |

### Sales Policies

| Policy Name    | Resource  | Action  | Effect |
|----------------|-----------|---------|--------|
| Sales: View    | `sales.*` | `view`  | Allow  |
| Sales: Create  | `sales.*` | `create`| Allow  |

### Executive Policies

| Policy Name            | Resource | Action | Effect |
|------------------------|----------|--------|--------|
| Executive: Full Access | `*`      | `*`    | Allow  |

---

## 🎭 Roles

| Role           | Department | Policies                       | Description                      |
|----------------|------------|--------------------------------|----------------------------------|
| Owner          | Executive  | Executive: Full Access         | Full system access               |
| Inventory Lead | Logistics  | Inventory: View, Adjust, Audit | Full inventory management        |
| Clerk          | Logistics  | Inventory: View, Adjust        | View and adjust stock (no audit) |
| Sales          | Commercial | Sales: View, Create            | Sales order management           |

---

## 📦 Product Catalog (Phase 4 Preparation)

### Categories

| Category         | Code |
|------------------|------|
| Major Appliances | MAJ  |
| Small Appliances | SML  |
| Kitchenware      | KIT  |

### Sample Products

| SKU          | Name                         | Category         | Unit |
|--------------|------------------------------|------------------|------|
| MAJ-FR-500   | Frost-Free Refrigerator 500L | Major Appliances | pcs  |
| MAJ-WM-CR159 | Washing Machine Crazy 159    | Major Appliances | pcs  |
| SML-IR-STM   | Steam Iron Pro               | Small Appliances | pcs  |
| MAJ-OV-ELC   | Electric Convection Oven     | Major Appliances | pcs  |

---

## 🧪 Quick Test Scenarios

### Scenario 1: IAM Policy Enforcement

```python
# Django shell
from security.logic.enforcement import PolicyEngine
from accounts.models import Employee

# Test Inventory Manager
manager = Employee.objects.get(email="stock.manager@amw.io")
engine = PolicyEngine(manager)

print(engine.has_permission("inventory.stock", "view"))    # True
print(engine.has_permission("inventory.stock", "adjust"))  # True
print(engine.has_permission("inventory.stock", "audit"))   # True
print(engine.has_permission("sales.order", "create"))      # False

# Test Inventory Clerk
clerk = Employee.objects.get(email="stock.clerk@amw.io")
engine = PolicyEngine(clerk)

print(engine.has_permission("inventory.stock", "view"))    # True
print(engine.has_permission("inventory.stock", "adjust"))  # True
print(engine.has_permission("inventory.stock", "audit"))   # False (not assigned)

# Test Sales Rep
sales = Employee.objects.get(email="sales.rep@amw.io")
engine = PolicyEngine(sales)

print(engine.has_permission("sales.order", "view"))        # True
print(engine.has_permission("sales.order", "create"))      # True
print(engine.has_permission("inventory.stock", "view"))    # False
```

### Scenario 2: Audit Log Verification

```python
# Django shell
from audit.models import AuditLog

# View all audit logs
logs = AuditLog.objects.all()
for log in logs:
    print(f"{log.timestamp} - {log.actor} - {log.action_code}")
```

---

## 🚀 Usage Instructions

### Seed Data Command

```bash
# Development mode (safe)
python manage.py seed_erp

# Production mode (NOT recommended)
python manage.py seed_erp --force
```

### Login URLs

- **Development Server:** http://localhost:8010
- **Django Admin:** http://localhost:8010/admin/
- **Health Check:** http://localhost:8010/health/

---

## ⚠️ Security Notice

**This file contains test credentials only.**

- **DO NOT** use these credentials in production
- **DO NOT** commit this file to version control (already in `.gitignore`)
- **ALWAYS** change passwords in production environments
- These accounts are for **development and testing purposes only**

---

*Generated by `python manage.py seed_erp` command*
