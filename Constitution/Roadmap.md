# Roadmap - AMW Django ERP

**Extracted from Constitution Sections 14–16**

## 14. Project Modules & Domain Scope

The project should be organized around these major domains:

### 14.1 Foundation

- Core project configuration
- Utilities
- Environment setup
- Test framework
- Infrastructure bootstrap

### 14.2 Identity

- Custom `Employee`
- Authentication
- Admin integration
- Technical and business account separation

### 14.3 IAM and Security

- `Department`
- `Role`
- `Policy`
- Permission mixins
- Operation-level policy enforcement

### 14.4 Inventory

- `Category`
- `Product`
- Stock ledger
- Stock adjustment logic
- WAC valuation engine

### 14.5 Sales and CRM

- `Customer`
- `SalesOrder`
- `SalesOrderItem`
- Totals calculation
- Order confirmation and stock deduction

### 14.6 Purchasing

- `Supplier`
- `PurchaseOrder`
- `PurchaseOrderItem`
- Stock receipt and cost update

### 14.7 Frontend Foundation

- Layouts
- Atoms
- Shared components
- HTMX partials
- Dashboard and module pages

### 14.8 Async and Reporting

- Celery task execution
- Background document generation
- Reporting workflows
- Progress feedback patterns

---

## 15. Project Roadmap Law

The roadmap below remains part of project law because this project is being built in deliberate phases, not ad hoc feature drift.

### Phase 1: Foundation, Automation & Local Scaffolding ✅ COMPLETE

**Goal:** Initialize the project professionally with utility scripts and reproducible environment.

**Required outcomes:**

- ✅ `utils/` is in place
- ✅ Virtual environment workflow is defined
- ✅ Dependencies are locked
- ✅ Quality tooling is configured
- ✅ Django project and `core` app scaffolding exist
- ✅ Settings are environment-aware

### Phase 2: Infrastructure & Core Identity ✅ COMPLETE

**Goal:** Establish Docker-backed services and the custom `Employee` identity system.

**Required outcomes:**

- ✅ PostgreSQL and Redis are available
- ✅ `Employee` is active as the user model
- ✅ Login/logout and admin support are working

### Phase 3: IAM & Security Framework ✅ COMPLETE

**Goal:** Implement reusable policy-based authorization and centralized audit foundations.

**Required outcomes:**

- ✅ Department, Role, and Policy models exist
- ✅ Policy checks are reusable in Python
- ✅ Base operation security rules are enforced
- ✅ Activity logging foundation exists

### Phase 4: Inventory Architecture & Valuation ✅ COMPLETE

**Goal:** Build the product catalog, stock ledger, and weighted average cost engine.

**Required outcomes:**

- ✅ Category and product architecture exist
- ✅ Stock transactions are recorded in immutable ledger
- ✅ WAC recalculation is implemented (19,4 precision)
- ✅ Stock changes are atomic and concurrency-safe
- ✅ Inventory history is visible and auditable
- ✅ StockAdjustment workflow with approval/rejection
- ✅ 26 comprehensive tests (all passing)
- ✅ Full Django admin integration

**Tag:** `v4.0-phase4-complete` | **Merged:** 2026-03-31

### Phase 5: Sales & CRM Workflows ✅ COMPLETE

**Goal:** Implement customer management and atomic sales order workflows.

**Required outcomes:**

- ✅ Customer and CustomerCategory models with SoftDeleteMixin
- ✅ SalesOrder and SalesOrderItem models with snapshot pricing (19,4 precision)
- ✅ Snapshot pricing preserved (Constitution 9.2)
- ✅ Order confirmation drives stock deduction through inventory operations
- ✅ Order state machine: Draft → Confirmed → Shipped → Voided
- ✅ Atomic order numbering (#Eg-00001 format, configurable prefix)
- ✅ Payment tracking (Pending, Partially Paid, Paid)
- ✅ Void operation with inventory rollback
- ✅ 34 comprehensive tests (all passing)
- ✅ Full Django admin integration with bulk actions

**Tag:** `v5.0-phase5-complete` | **Status:** Ready for merge

### Phase 6: Purchasing & Procurement

**Goal:** Implement supplier workflows and stock receiving.

**Required outcomes:**

- Supplier and purchase order models exist
- Receiving stock updates quantity and valuation correctly

### Phase 7: Frontend Foundation & HTMX UI

**Goal:** Build reusable UI structure and consistent dynamic interactions.

**Required outcomes:**

- Base layouts exist
- Shared atoms and components exist
- HTMX modal and fragment patterns are established
- Responsive behavior is considered

### Phase 8: Async Tasks, Reporting & Hardening

**Goal:** Finalize background processing, reporting, and performance hardening.

**Required outcomes:**

- Celery is operational
- Long-running tasks can execute asynchronously
- Reporting workflows are available
- Obvious query inefficiencies are reviewed
- Production packaging is prepared

---

## 16. Final Rule

If an AI CLI tool produces output that is generic, vague, not tied to AMW Django ERP, or disconnected from the phases and modules defined here, that output is not compliant with project law.

This project requires concrete, phase-aware, architecture-aware execution.
