# Manual Test Plan — AMW Django ERP

**Version:** 1.2
**Created:** 2026-04-08
**Status:** Active

---

## 1. Purpose

This document defines the strategy, scope, and execution workflow for manual testing of the AMW Django ERP system. It complements the automated test suite (217+ pytest cases) by validating real user interactions, HTMX behavior, visual feedback, and end-to-end business flows that automated tests cannot fully cover.

---

## 2. Testing Strategy: Role-Based

Testing follows the **user role** model defined in `seed_erp.py`. Each role has specific permissions and workflows. This ensures we test both **functionality** and **authorization** simultaneously.

| Role | Email | Focus Areas |
|------|-------|-------------|
| **Owner (Superuser)** | `amw@amw.io` | Full system access, all modules, admin panel |
| **Warehouse Lead** | `warehouse.lead@amw.io` | Inventory adjustments, stock ledger, purchasing, receiving |
| **Sales Manager** | `sales.manager@amw.io` | Customer management, order creation, confirmation, voiding |
| **Auditor** | `auditor@amw.io` | Read-only inventory audit, viewing audit logs, no modifications |

---

## 3. Testing Order

Execute in this sequence to respect data dependencies:

| Order | Module | Rationale |
|-------|--------|-----------|
| 1 | **Identity & IAM** | Login/logout, permission enforcement |
| 2 | **Inventory** | Products and stock levels must exist before sales/purchasing |
| 3 | **Purchasing** | Stock receiving workflows |
| 4 | **Sales & CRM** | Order confirmation consumes stock |
| 5 | **Audit & Reporting** | Verify logs capture all previous actions |
| 6 | **HTMX Regression** | Re-test interactive buttons after data changes |

---

## 4. Test Data Reference

All test data is seeded by:
```bash
python manage.py seed_erp --force
```

See `seed_erp.py` for the complete data catalog:
- **4 Departments:** Executive, Logistics, Commercial, Finance
- **4 Employee personas:** Owner, Warehouse Lead, Sales Manager, Auditor
- **14 Products** across 5 categories with initial stock levels
- **4 Customer categories** + sample customers
- **Sales orders** in various states
- **Suppliers** and **purchase orders**

---

## 5. Execution Workflow

1. **Start the dev server:** `python manage.py runserver 8010`
2. **Open browser** to `http://localhost:8010`
3. **Login** with the role being tested
4. **Execute test cases** from `MANUAL_TEST_CASES.md` in order
5. **Record results:** Fill Actual, Status (Pass/Fail), and Comments for each case
6. **Switch role** (logout → login as next role) and repeat
7. **Report findings** to the team with screenshots for failures

---

## 6. Pass/Fail Criteria

| Status | Meaning |
|--------|---------|
| **Pass** | Expected behavior matches actual, no errors, UI responds correctly |
| **Fail** | Behavior differs from expected, UI breaks, error toast/traceback appears, button unresponsive |

---

## 7. Known Issues Being Tested

- HTMX buttons that "work once then stop" — verify fix allows repeated clicks
- Modal dialogs that disappear after first close — verify re-open works
- Toast notifications not appearing after HTMX POST — verify HX-Trigger fires
- Page not refreshing after Confirm/Void Order — verify HX-Refresh header
- Branded 403 page renders instead of raw white-screen text

---

## 8. Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-04-08 | Initial manual test plan created | Qwen |
| 2026-04-14 | v1.2: Updated seed command to `--force` for granular policies, added 403 page note | Qwen |
