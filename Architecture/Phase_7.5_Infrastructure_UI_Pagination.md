# AMW Django ERP - Phase Execution Plan: Phase 7.5

## 1. Document Purpose
This file is the working execution plan for Phase 7.5: Infrastructure UI & Global Pagination.
It bridges the gap between the foundation frontend (Phase 7) and the async hardening (Phase 8).

---

## 2. Phase Identity
- **Phase Number:** `Phase 7.5`
- **Phase Name:** `Infrastructure UI & Global Pagination`
- **Branch Name:** `phase-7.5`
- **Status:** `Planned`
- **Primary Goal:** `Complete the detail views for Audit, Security, and Accounts apps and implement global 20-item pagination.`
- **Depends On:** `Phase 7`

---

## 3. Phase Scope

### In Scope
- **Audit UI:** Functional List and Detail views for `AuditLog`.
- **Security Detail UI:** Detail pages for `Department`, `Role`, and `Policy`.
- **Accounts Detail UI:** `Employee` profile/detail page.
- **Global Pagination:** 20-item-per-page logic applied to ALL list views in the system.
- **Pagination Snippet:** A reusable `_pagination.html` atom.

### Required Outcomes
- Users can view and search audit logs with before/after data snapshots.
- Users can click any infrastructure entity (Employee, Role, etc.) to see full details/memberships.
- All lists (Products, Customers, Suppliers, etc.) use consistent pagination.

---

## 4. Implementation Strategy

### Sequencing Rule
1. **Pagination Foundation:** Create the snippet and a shared utility for Paginator.
2. **Audit UI:** Build the logs list and detail view (crucial for traceability).
3. **Security Detail UI:** Expand the existing list views with functional detail links.
4. **Accounts Detail UI:** Complete the Employee profile view.
5. **Global Rollout:** Apply pagination to existing business apps (Inventory, Sales, Purchasing).

---

## 5. Parts Breakdown

### Part 1: Pagination Framework
1. **Task 7.5.1:** `Create templates/_snipps_/_pagination.html`
   - Output: `Reusable snippet for HTMX-compatible pagination controls.`
2. **Task 7.5.2:** `Create core/utils.py (or similar) pagination helper`
   - Output: `Standardized Python function to handle Paginator(20) logic.`

### Part 2: Audit & Security UI
1. **Task 7.5.3:** `Audit UI implementation`
   - Output: `audit/urls.py, views.py, and templates for list/detail.`
2. **Task 7.5.4:** `Security Detail Views`
   - Output: `Detail views for Department (with children/employees), Role (with policies), and Policy (with usage).`

### Part 3: Employee Profile & Global Rollout
1. **Task 7.5.5:** `Employee Detail View`
   - Output: `Profile page showing employee info, department, and roles.`
2. **Task 7.5.6:** `Apply pagination to all 12+ list views`
   - Output: `Inventory, Sales, Purchasing, Accounts, and Security lists all paginated.`

---
