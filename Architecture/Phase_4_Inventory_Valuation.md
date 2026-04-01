# AMW Django ERP - Phase Execution Plan: Phase 4

## 1. Document Purpose

This file is the working execution plan for Phase 4: Inventory Architecture & Valuation.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 4`
- **Phase Name:** `Inventory Architecture & Valuation`
- **Branch Name:** `phase-4` (merged to `master`)
- **Status:** ✅ **COMPLETE**
- **Version Tag:** `v4.0-phase4-complete`
- **Primary Goal:** `Implement the product catalog, stock ledger, and Weighted Average Cost (WAC) engine.`
- **Depends On:** `Phase 3`
- **Manager Approval Required:** `Yes`
- **Completion Date:** 2026-03-31

---

## 3. Phase Scope

### In Scope

- `Category` and `Product` models with `SoftDeleteMixin` (Constitution 8.4)
- `StockAdjustment` model (Document-based adjustments with reason/actor)
- `StockTransaction` ledger model with explicit `change_type`
- `StockAdjustment` operations (Add/Reduce/Transfer)
- Weighted Average Cost (WAC) calculation logic with high precision
- Atomic stock updates with `select_for_update()`
- Unit of Measure (UoM) support for products
- SKU validation logic (Example: `WM-CR-159` for "Washing Machine Crazy 159")
- Integrated Audit Logging for non-quantity changes (Constitution 8.7)

### Out of Scope

- Sales integrations - Deferred to Phase 5
- Purchase integrations - Deferred to Phase 6
- Barcode generation - Optional/Deferred

### Required Outcomes

- Functional product and category hierarchy
- Automated WAC recalculation on incoming stock
- Atomic and concurrency-safe stock updates
- Full audit history of stock movements

---

## 4. Constitutional Alignment

### Mandatory Checks

- Inventory logic lives in `inventory/operations/` (Section 6.1)
- Stock valuation uses Weighted Average Cost (Section 6.5)
- State changes must be atomic and use locking (Section 6.6)
- Business state changes must produce audit logs (Section 6.7)

### Notes for This Phase

- `Product.current_stock` must never be edited directly from a view. All changes must flow through the `operations/` layer to ensure WAC and ledger consistency.

---

## 5. Architecture Targets

### Modules / Apps Affected

- `inventory` (new app)
- `core` (for `SoftDeleteMixin` and base model support)
- `iam` (for policy enforcement)
- `audit` (for movement logs)

### Main Files or Areas Expected

- `core/models.py` (Implement `SoftDeleteMixin` here)
- `inventory/models.py` (Category, Product, StockAdjustment, StockTransaction)
- `inventory/operations/stock.py` (Business logic)
- `inventory/logic/valuation.py` (WAC calculations)

### Data Model Impact

- `Product`: `sku` (validated), `name`, `category`, `uom` (pcs, kg, etc.), `current_stock`, `wac_price` (19,4 precision), `is_deleted` (Soft Delete)
- `StockAdjustment`: `product`, `type` (ADD/REDUCE), `quantity`, `reason`, `actor` (Employee), `timestamp` (Executes immediately in Phase 4)
- `StockTransaction`: `product`, `change_type` (INTAKE, ADJUST_ADD, ADJUST_REDUCE, SALE, PURCHASE, TRANSFER, RETURN), `quantity`, `unit_cost` (19,4 precision), `balance_after`, `location_note` (simple text), `timestamp`, `actor`

### Operational Impact

- `adjust_stock()`: Manual correction or initial intake (Creates `StockAdjustment`)
- `recalculate_wac()`: 
    - ✅ **Triggered on:** `PURCHASE`, `INTAKE`, `ADJUST_ADD` (cost-increasing)
    - ❌ **NOT Triggered on:** `SALE`, `ADJUST_REDUCE`, `TRANSFER` (quantity-only changes)
- `SoftDelete`: `Product.delete()` must use the mixin to set `is_deleted` rather than purging.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will start with the product and category models. Then, we will build the `StockTransaction` ledger to ensure every movement is recorded. The core of this phase is the `operations/stock.py` module, which will handle all mutations using `transaction.atomic` and `select_for_update`. Finally, we will implement and unit test the WAC engine to ensure valuation accuracy.

### Sequencing Rule

1. Product and Category models (with `SoftDeleteMixin` and `uom`)
2. StockTransaction ledger model with mandatory `change_type` codes
3. SKU validation logic and non-quantity `AuditLog` integration
4. Stock adjustment operations (Add/Reduce) with atomic protection
5. WAC valuation logic implementation (19,4 precision)
6. Concurrency and stress testing for stock updates

---

## 7. Parts Breakdown

### Part 1: Catalog Foundations

- **Goal:** `Define the core products and categories with soft delete and SKU validation.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 4.1:** `Implement Category and Product models`
   - Output: `Catalog models with SKU validation (e.g. WM-CR-159), UoM, and SoftDeleteMixin`
   - Verification: `Run unit tests for product creation and soft delete`

### Part 2: Stock Ledger and Operations

- **Goal:** `Implement atomic stock movements and the valuation engine.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 4.2:** `Implement StockTransaction model`
   - Output: `Ledger model for tracking every unit movement`
   - Verification: `Verify model records balance_after correctly`

2. **Task 4.3:** `Implement stock adjustment operation with WAC logic`
   - Output: `atomic adjust_stock() method in inventory/operations/`
   - Verification: `Validate WAC recalculation formula through multiple test cases`

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `WAC accuracy: (New Qty * New Cost + Old Qty * Old Cost) / (Total Qty)`
- `Concurrency check: Multiple simultaneous stock updates on the same SKU`
- `Policy enforcement: Ensure only authorized employees can adjust stock`

### Manual Verification

- `Confirm stock transactions appear in the ledger after each operation`

---

## 10. Risks and Controls

### Known Risks

- `Race conditions during high-volume stock updates`
- `Floating point precision errors in WAC calculation`

### Controls / Mitigations

- `Mandatory use of select_for_update() on Product rows`
- `Use DecimalField for all currency and cost-related fields`

---

## 11. Open Questions

- `Should we support multiple warehouses/locations in Phase 4? (Deferred for simplicity)`

---

## 12. Completion Checklist

- [x] Product catalog architecture exists with Soft Delete and UoM
- [x] SKU validation is implemented in the operation layer (Example: `WM-CR-159`)
- [x] WAC recalculation (19,4 precision) is implemented and tested
- [x] Stock updates are atomic and concurrency-safe
- [x] Inventory history is visible in the ledger with explicit types
- [x] Non-quantity product changes trigger standard AuditLogs
- [x] IAM rules protect inventory operations
- [x] StockAdjustment workflow with REJECTED status and required comment
- [x] StockTransaction immutability enforced in admin (no edit/delete)
- [x] 26 comprehensive tests passing (Category: 6, Product: 3, WAC: 6, StockTransaction: 2, StockOperations: 9)

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 4 plan for inventory and WAC valuation.`
- `2026-03-31` - `Implementation` - `Completed inventory app with models, operations, WAC engine, and tests.`
- `2026-03-31` - `Review` - `Addressed Gem's review: added REJECTED status, verified immutability, confirmed UoM/SoftDelete.`
- `2026-03-31` - ✅ **COMPLETE** - `Phase 4 merged to master (v4.0-phase4-complete). 104 tests passing, 26 inventory-specific.`

---

## 14. Final Summary

Phase 4 successfully delivered a production-ready inventory management system with:
- ✅ Product catalog with hierarchical categorization (Category, Product)
- ✅ Immutable stock transaction ledger (StockTransaction)
- ✅ Weighted Average Cost (WAC) valuation engine with 19,4 precision
- ✅ Atomic stock operations with concurrency safety (`select_for_update()`)
- ✅ Stock adjustment workflow with approval/rejection (StockAdjustment + rejection_comment)
- ✅ Comprehensive audit logging for all stock movements
- ✅ Full Django admin integration (all models registered)
- ✅ 26 unit and integration tests (all passing)
- ✅ Seed data with 5 products and initial stock levels ($44,625 total value)

All implementations follow Constitution Sections 6.1-6.7 (Operations-First, Atomic Safety, Audit Trail).

**Next Phase:** Phase 5 (Sales & CRM Workflows) - Customer management and atomic sales order workflows.

**Version:** v4.0-phase4-complete  
**Merged to Master:** 2026-03-31  
**Total Commits:** 9  
**Lines Added:** +2,391 | **Lines Removed:** -35

(TBD)
