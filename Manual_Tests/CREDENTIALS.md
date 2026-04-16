# AMW Django ERP - Test Credentials

**Generated for:** Development & Manual Testing
**Last Updated:** 2026-04-15

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

### Other Employees (Default Password: `password123`)

| Account                     | Email                        | Role            |
|-----------------------------|------------------------------|-----------------|
| Warehouse Lead              | `warehouse.lead@amw.io`      | Warehouse Lead  |
| Sales Manager               | `sales.manager@amw.io`       | Sales Manager   |
| Auditor                     | `auditor@amw.io`             | Auditor         |

---

### Warehouse Lead

| Field            | Value                                                             |
|------------------|-------------------------------------------------------------------|
| **Email**        | `warehouse.lead@amw.io`                                           |
| **Password**     | `password123`                                                     |
| **Role**         | Warehouse Lead                                                    |
| **Department**   | Logistics                                                         |
| **Permissions**  | `inventory.*:view`, `inventory.*:adjust`, `inventory.*:audit`, `purchasing.*:view`, `purchasing.*:manage`, `purchasing.order:create`, `purchasing.order:issue`, `purchasing.order:receive`, `purchasing.order:cancel` |
| **Admin Access** | ❌ No                                                             |
| **Sidebar**      | Inventory, Purchasing                                             |

---

### Sales Manager

| Field            | Value                                                             |
|------------------|-------------------------------------------------------------------|
| **Email**        | `sales.manager@amw.io`                                            |
| **Password**     | `password123`                                                     |
| **Role**         | Sales Manager                                                     |
| **Department**   | Commercial                                                        |
| **Permissions**  | `sales.*:view`, `sales.*:manage`, `sales.order:create`, `sales.order:confirm`, `sales.order:void`, `sales.order:add_item`, `customer.*:view`, `customer.*:manage` |
| **Admin Access** | ❌ No                                                             |
| **Sidebar**      | Sales & CRM                                                       |

---

### Auditor

| Field            | Value                                                             |
|------------------|-------------------------------------------------------------------|
| **Email**        | `auditor@amw.io`                                                  |
| **Password**     | `password123`                                                     |
| **Role**         | Auditor                                                           |
| **Department**   | Finance                                                           |
| **Permissions**  | `audit.*:view`, `audit.*:manage`, `inventory.*:audit`             |
| **Admin Access** | ❌ No                                                             |
| **Sidebar**      | Audit Log (read-only access to Inventory)                         |

---

## 📁 Department Hierarchy

| Department | Code | Description                        |
|------------|------|------------------------------------|
| Executive  | -    | Executive management and ownership |
| Logistics  | -    | Warehouse, inventory, and shipping |
| Commercial | -    | Sales and customer relations       |
| Finance    | -    | Financial oversight and auditing   |

---

## 📋 Policies

### Inventory Policies

| Policy Name       | Resource      | Action  | Effect |
|-------------------|---------------|---------|--------|
| Inventory: View   | `inventory.*` | `view`  | Allow  |
| Inventory: Adjust | `inventory.*` | `adjust`| Allow  |
| Inventory: Audit  | `inventory.*` | `audit` | Allow  |

### Purchasing Policies

| Policy Name       | Resource           | Action   | Effect |
|-------------------|--------------------|----------|--------|
| Purchasing: View  | `purchasing.*`     | `view`   | Allow  |
| Purchasing: Manage| `purchasing.*`     | `manage` | Allow  |
| Purchasing: Create| `purchasing.order` | `create` | Allow  |
| Purchasing: Issue | `purchasing.order` | `issue`  | Allow  |
| Purchasing: Receive| `purchasing.order`| `receive`| Allow  |
| Purchasing: Cancel| `purchasing.order` | `cancel` | Allow  |

### Sales Policies

| Policy Name     | Resource       | Action     | Effect |
|-----------------|----------------|------------|--------|
| Sales: View     | `sales.*`      | `view`     | Allow  |
| Sales: Manage   | `sales.*`      | `manage`   | Allow  |
| Sales: Create   | `sales.order`  | `create`   | Allow  |
| Sales: Confirm  | `sales.order`  | `confirm`  | Allow  |
| Sales: Void     | `sales.order`  | `void`     | Allow  |
| Sales: Add Item | `sales.order`  | `add_item` | Allow  |

### Customer Policies

| Policy Name       | Resource     | Action   | Effect |
|-------------------|--------------|----------|--------|
| Customer: View    | `customer.*` | `view`   | Allow  |
| Customer: Manage  | `customer.*` | `manage` | Allow  |

### Audit Policies

| Policy Name     | Resource   | Action   | Effect |
|-----------------|------------|----------|--------|
| Audit: View     | `audit.*`  | `view`   | Allow  |
| Audit: Manage   | `audit.*`  | `manage` | Allow  |

### Executive Policy

| Policy Name            | Resource | Action | Effect |
|------------------------|----------|--------|--------|
| Executive: Full Access | `*`      | `*`    | Allow  |

---

## 🎭 Roles

| Role            | Department | Policies                                                                 | Description                              |
|-----------------|------------|--------------------------------------------------------------------------|------------------------------------------|
| Owner           | Executive  | Executive: Full Access                                                   | Full system access                       |
| Warehouse Lead  | Logistics  | Inventory: View/Adjust/Audit, Purchasing: View/Manage/Create/Issue/Receive/Cancel | Full inventory and purchasing access |
| Sales Manager   | Commercial | Sales: View/Manage/Create/Confirm/Void/Add Item, Customer: View/Manage   | Sales and customer management            |
| Auditor         | Finance    | Audit: View/Manage, Inventory: Audit                                     | Audit oversight and inventory reconciliation |

---

## 📦 Product Catalog

### Categories

| Category         | Code |
|------------------|------|
| Major Appliances | MAJ  |
| Small Appliances | SML  |
| Kitchenware      | KIT  |
| Cleaning & Home  | CLN  |
| Electronics      | ELC  |

### Sample Products (14 total)

| SKU          | Name                         | Category         |
|--------------|------------------------------|------------------|
| MAJ-FR-500   | Frost-Free Refrigerator 500L | Major Appliances |
| MAJ-WM-CR159 | Washing Machine Crazy 159    | Major Appliances |
| MAJ-OV-ELC   | Electric Convection Oven     | Major Appliances |
| MAJ-AC-12    | Split AC 12000 BTU           | Major Appliances |
| SML-IR-STM   | Steam Iron Pro               | Small Appliances |
| SML-VL-18    | Vacuum Cleaner 1800W         | Small Appliances |
| SML-HD-22    | Hair Dryer 2200W             | Small Appliances |
| KIT-BL-HSP   | High-Speed Blender           | Kitchenware      |
| KIT-TS-4S    | 4-Slice Toaster              | Kitchenware      |
| KIT-MX-5L    | Stand Mixer 5L               | Kitchenware      |
| CLN-AF-2L    | Air Freshener 2L             | Cleaning & Home  |
| CLN-VC-3L    | Floor Cleaner 3L             | Cleaning & Home  |
| ELC-LED-55   | LED TV 55 inch 4K            | Electronics      |
| ELC-SB-21    | Soundbar 2.1 Channel         | Electronics      |

---

## 🧪 Quick Test Scenarios

### Scenario 1: IAM Policy Enforcement

```python
# Django shell
from security.logic.enforcement import PolicyEngine
from accounts.models import Employee

# Test Warehouse Lead
wh = Employee.objects.get(email="warehouse.lead@amw.io")
engine = PolicyEngine(wh)

print(engine.has_permission("inventory.stock", "view"))    # True
print(engine.has_permission("inventory.stock", "adjust"))  # True
print(engine.has_permission("purchasing.order", "receive")) # True
print(engine.has_permission("sales.order", "create"))      # False

# Test Sales Manager
sm = Employee.objects.get(email="sales.manager@amw.io")
engine = PolicyEngine(sm)

print(engine.has_permission("sales.order", "confirm"))     # True
print(engine.has_permission("sales.order", "void"))        # True
print(engine.has_permission("customer.*", "view"))         # True
print(engine.has_permission("inventory.stock", "adjust"))  # False

# Test Auditor
au = Employee.objects.get(email="auditor@amw.io")
engine = PolicyEngine(au)

print(engine.has_permission("audit.*", "view"))            # True
print(engine.has_permission("inventory.*", "audit"))       # True
print(engine.has_permission("inventory.stock", "adjust"))  # False
print(engine.has_permission("sales.order", "view"))        # False
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

# Force mode (overwrites existing data)
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
