# AMW Django ERP - Phase Execution Plan: Phase 5

## 1. Document Purpose

This file is the working execution plan for Phase 5: Sales & CRM Workflows.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md` (v2.2)
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 5`
- **Phase Name:** `Sales & CRM Workflows`
- **Branch Name:** `phase-5`
- **Status:** ✅ **COMPLETE**
- **Version Tag:** `v5.0-phase5-complete` (pending merge)
- **Primary Goal:** `Implement customer management and atomic sales order workflows with stock deduction.`
- **Depends On:** `Phase 4` (Inventory Architecture & Valuation)
- **Manager Approval Required:** `Yes`
- **Constitution Version:** v2.3
- **Completion Date:** 2026-04-01

---

## 3. Phase Scope

### In Scope

- `Customer` and `CustomerCategory` models (with SoftDeleteMixin)
- `SalesOrder` and `SalesOrderItem` models (with SoftDeleteMixin)
- Order totals calculation logic (Decimal 19,4 precision)
- `OrderConfirmation` operation (including stock deduction)
- Historical pricing preservation (snapshots)
- Customer shipping address snapshot at order time
- Order numbering system (#Eg-00001 format, configurable)
- Payment tracking (amount_paid field)
- Order state machine (Draft → Confirmed → Shipped → Voided)

### Out of Scope

- Shipping and Logistics tracking - Deferred
- Sales commissions - Deferred
- Credit limits - Deferred
- Partial fulfillment - Deferred

### Required Outcomes

- Functional customer database with categories
- Sales orders with snapshot pricing and shipping address
- Automated stock deduction on order confirmation via inventory operations
- Order status management (Draft -> Confirmed -> Shipped -> Voided)
- Payment tracking (Pending, Paid, Partially Paid)
- Inventory rollback on voided orders
- Atomic order numbering (#Eg-00001 format)

---

## 4. Constitutional Alignment

### Mandatory Checks (Constitution v2.2)

- **Operations-First (Section 8.1):** All sales logic in `sales/operations/`
- **Soft Delete (Section 8.4):** Customer, CustomerCategory, SalesOrder use SoftDeleteMixin
- **Snapshot Pricing (Section 9.2):** SalesOrderItem.snapshot_unit_price preserved at order time
- **Shipping Snapshot (Section 9.2):** Customer shipping address copied to SalesOrder at order time
- **Financial Precision (Section 9.5):** All currency fields use DecimalField(19,4)
- **Decimal Calculations (Section 9.5):** Python Decimal class with ROUND_HALF_UP
- **Order Numbering (Section 9.5):** Atomic, unique, generated in operations layer
- **Atomic Safety (Section 8.6):** transaction.atomic + select_for_update() for order confirmation
- **Audit Rule (Section 8.7):** All order state changes logged with before/after snapshots

### Notes for This Phase

- `SalesOrderItem.snapshot_unit_price` (19,4 precision) must be frozen at order time
- `SalesOrder.shipping_address_snapshot` must copy from Customer at order time
- Order confirmation must call `inventory.operations.stock.stock_out()` atomically
- Void operation must call inventory to add stock back atomically

---

## 5. Architecture Targets

### Modules / Apps Affected

- `sales` (new app)
- `inventory` (for stock reduction via operations layer)
- `audit` (for order history and state changes)

### Main Files or Areas Expected

- `sales/models.py` (Customer, CustomerCategory, SalesOrder, SalesOrderItem)
- `sales/operations/orders.py` (confirm_order, void_order, calculate_totals)
- `sales/logic/pricing.py` (Total calculations with Decimal precision)

### Data Model Impact

**Customer:**
- `name`, `email`, `phone`, `category` (FK to CustomerCategory)
- `shipping_address` (text, snapshotted to order)
- SoftDeleteMixin

**CustomerCategory:**
- `name`, `code` (auto-slug)
- SoftDeleteMixin

**SalesOrder:**
- `order_number` (atomic, unique, format: #Eg-00001)
- `customer` (FK)
- `status` (Draft, Confirmed, Shipped, Voided)
- `shipping_address_snapshot` (text, copied from Customer)
- `subtotal`, `tax_amount`, `total_amount` (Decimal 19,4)
- `amount_paid` (Decimal 19,4, for partial payment tracking)
- `payment_status` (Pending, Paid, Partially Paid)
- `payment_method` (COD, Bank Transfer, Credit Card)
- SoftDeleteMixin

**SalesOrderItem:**
- `order` (FK to SalesOrder)
- `product` (FK to Product)
- `quantity` (Decimal 19,4)
- `snapshot_unit_price` (Decimal 19,4, frozen at order time)
- `total_price` (Decimal 19,4, calculated: quantity × snapshot_unit_price)

### Operational Impact

- `confirm_order()`: Atomic operation - updates status to Confirmed, calls inventory.stock_out()
- `void_order()`: Atomic operation - updates status to Voided, calls inventory to add stock back
- `calculate_order_totals()`: Decimal precision calculations with ROUND_HALF_UP
- `generate_order_number()`: Atomic, unique order number generation

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will begin by establishing the customer model hierarchy with SoftDeleteMixin. Then, we will build the Sales Order structure with all snapshot fields and financial precision (19,4 Decimal). The most critical part is the `confirm_order()` operation, which must atomically interact with existing `inventory.operations.stock.stock_out()` to safely reduce stock levels using `transaction.atomic` and `select_for_update()`.

### Sequencing Rule

1. Customer and CustomerCategory models (with SoftDeleteMixin)
2. SalesOrder and SalesOrderItem models (with snapshot fields, Decimal 19,4)
3. Order numbering system (atomic, configurable prefix)
4. Integration with inventory operations for stock deduction
5. Order confirmation state machine (Draft → Confirmed → Shipped → Voided)
6. Payment tracking (amount_paid, payment_status, payment_method)
7. Void operation with inventory rollback
8. Verification of stock-down flows, pricing snapshots, and atomicity

---

## 7. Parts Breakdown

### Part 1: CRM & Order Foundations

- **Goal:** `Define customers, categories, and basic order structures with SoftDelete and snapshots.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `⏳ PENDING`

#### Tasks

1. **Task 5.1:** `Implement Customer and CustomerCategory models`
   - Output: `CRM models with SoftDeleteMixin, shipping_address field`
   - Verification: `Unit tests for customer creation, soft delete, category assignment`

2. **Task 5.2:** `Implement SalesOrder and SalesOrderItem models`
   - Output: `Order models with snapshot_unit_price (19,4), shipping_address_snapshot, SoftDeleteMixin`
   - Verification: `Verify that changing product price does not affect existing order items`

### Part 2: Order Fulfillment Operations

- **Goal:** `Implement the business logic for order processing with atomic safety.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `⏳ PENDING`

#### Tasks

1. **Task 5.3:** `Implement confirm_order() operation`
   - Output: `Atomic operation that updates status to Confirmed and calls inventory.operations.stock.stock_out()`
   - Verification: `Test: Confirm order fails if stock is insufficient (no state change)`

2. **Task 5.4:** `Implement void_order() operation with inventory rollback`
   - Output: `Atomic operation that updates status to Voided and adds stock back via inventory operations`
   - Verification: `Test: Voided orders restore stock, only works for non-Shipped orders`

3. **Task 5.5:** `Implement order total calculation logic`
   - Output: `Decimal precision methods for subtotal, tax, final total (ROUND_HALF_UP)`
   - Verification: `Verify calculations against manual math in tests`

4. **Task 5.6:** `Implement atomic order numbering system`
   - Output: `generate_order_number() with configurable prefix (ORDER_PREFIX setting)`
   - Verification: `Test: Order numbers are unique, sequential, format #Eg-00001`

### Part 3: Payment Tracking & Admin Integration

- **Goal:** `Implement payment tracking and Django admin integration.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `⏳ PENDING`

#### Tasks

1. **Task 5.7:** `Implement payment tracking fields and logic`
   - Output: `amount_paid field, payment_status choices (Pending, Paid, Partially Paid), payment_method choices`
   - Verification: `Test: Partial payments tracked correctly, payment status updates`

2. **Task 5.8:** `Register all sales models in Django admin`
   - Output: `sales/admin.py with Customer, CustomerCategory, SalesOrder, SalesOrderItem`
   - Verification: `Admin interface functional, order operations accessible`

### Part 4: Testing & Verification

- **Goal:** `Comprehensive test coverage for Phase 5 features.`
- **Owner:** `Qwen (Lead Developer)`
- **Status:** `⏳ PENDING`

#### Tasks

1. **Task 5.9:** `Write unit tests for models and snapshot preservation`
   - Output: `sales/tests/test_models.py with snapshot tests`
   - Verification: `All tests pass, pricing preserved after product price change`

2. **Task 5.10:** `Write integration tests for order operations`
   - Output: `sales/tests/test_operations.py with atomic operation tests`
   - Verification: `Tests verify atomic safety, inventory rollback, payment tracking`

---

## 8. Task Writing Rules

All tasks follow Constitution Section 4.5:
- Atomic and completable
- Clear output definition
- Verification criteria defined
- No partial implementations

---

## 9. Verification Plan

### Required Tests

- `Snapshot check: Verify pricing is preserved after product price change`
- `Shipping snapshot check: Verify shipping address preserved after customer address change`
- `Fulfillment check: Verify inventory reduction matches order quantities`
- `Atomicity check: Verify order is NOT confirmed if stock deduction fails`
- `Void rollback check: Verify voided orders restore stock atomically`
- `Order numbering check: Verify order numbers are unique and sequential`
- `Payment tracking check: Verify amount_paid and payment_status work correctly`

### Manual Verification

- `Confirm order status transitions correctly in admin panel (Draft → Confirmed → Shipped → Voided)`
- `Verify payment status updates (Pending → Partially Paid → Paid)`
- `Verify stock levels update correctly on confirm and void operations`

---

## 10. Risks and Controls

### Known Risks

- `Overselling (stock reduction race conditions)`
- `Price manipulation in the frontend`
- `Order number collision (non-atomic generation)`
- `Inventory rollback failure on void`

### Controls / Mitigations

- `Use select_for_update() on Products during order confirmation (Constitution 8.6)`
- `Perform final price calculations in backend operations layer only (Constitution 8.1)`
- `Generate order numbers atomically in operations layer with database locking (Constitution 9.5)`
- `Wrap void operation in transaction.atomic with inventory rollback verification`

---

## 11. Open Questions

- `Should we support partial fulfillment (shipping parts of an order)?` → **Deferred**
- `Should we add tax calculation logic or assume flat rate?` → **Flat rate for Phase 5**
- `Should payment tracking integrate with accounting later?` → **Design for future integration**

---

## 12. Completion Checklist

- [ ] Customer records with categories (SoftDeleteMixin)
- [ ] Sales orders preserve snapshot pricing (19,4 Decimal)
- [ ] Sales orders preserve shipping address snapshot
- [ ] Order confirmation deducts stock via inventory operations (atomic)
- [ ] Orders follow strict state machine (Draft → Confirmed → Shipped → Voided)
- [ ] Void operation restores stock atomically
- [ ] Order numbering is atomic and unique (#Eg-00001 format)
- [ ] Payment tracking works (amount_paid, payment_status, payment_method)
- [ ] All currency fields use DecimalField(19,4)
- [ ] Every order action is auditable (Constitution 8.7)
- [ ] All tests pass (models, operations, integration)
- [ ] Lint checks pass (ruff, black)
- [ ] Ahmad approval

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 5 plan for Sales and CRM.`
- `2026-04-01` - `Updated` - `Added Enterprise Locks per Gem's review: SoftDelete, snapshots, Decimal 19,4, order numbering, payment tracking, state machine.`
- `2026-04-01` - `Constitution v2.3` - `Added Section 9.2 (Sales Snapshots) and Section 9.5 (Financial Precision).`
- `2026-04-01` - `Implementation` - `Completed sales app with models, operations, pricing logic, and admin integration.`
- `2026-04-01` - `Testing` - `Implemented 34 comprehensive tests per Constitution Section 13.`
- `2026-04-01` - ✅ **COMPLETE** - `Phase 5 finalized. 138 total tests passing (34 sales-specific). Ready for merge to master.`

---

## 14. Final Summary

Phase 5 successfully delivered a production-ready Sales & CRM system with:
- ✅ Customer management with hierarchical categories (SoftDeleteMixin)
- ✅ Sales orders with snapshot pricing and shipping address preservation
- ✅ Atomic order confirmation with inventory integration (stock deduction)
- ✅ Order state machine (Draft → Confirmed → Shipped → Voided)
- ✅ Payment tracking (Pending, Partially Paid, Paid)
- ✅ Atomic order numbering (#Eg-00001, configurable prefix via ORDER_PREFIX setting)
- ✅ Financial precision (DecimalField 19,4, ROUND_HALF_UP)
- ✅ Void operation with automatic inventory rollback
- ✅ Comprehensive test coverage (34 tests, all passing)
- ✅ Full Django admin integration with bulk actions (Confirm, Void)

All implementations follow Constitution v2.3 Sections:
- **8.1** (Operations-First): All logic in `sales/operations/`
- **8.4** (Soft Delete): Customer, CustomerCategory, SalesOrder, SalesOrderItem
- **8.6** (Atomic Safety): `transaction.atomic` + `select_for_update()`
- **8.7** (Audit): All state changes logged with before/after snapshots
- **9.2** (Sales Snapshots): Price and shipping address frozen at order time
- **9.5** (Financial Precision): Decimal 19,4, ROUND_HALF_UP, atomic order numbering
- **13** (Testing): 34 tests covering models, operations, and integration

**Test Coverage:**
- Models: 11 tests (Customer, CustomerCategory, SalesOrder, SalesOrderItem)
- Operations: 10 tests (confirm_order, void_order, generate_order_number, update_payment)
- Pricing: 3 tests (line totals, order totals, rounding)
- Integration: 10 tests (stock deduction, rollback, snapshot integrity, insufficient stock)

**Next Phase:** Phase 6 (Purchasing & Procurement) - Supplier workflows and stock receiving.

**Version:** v5.0-phase5-complete  
**Branch:** phase-5  
**Start Date:** 2026-04-01  
**Completion Date:** 2026-04-01  
**Total Commits:** 4  
**Lines Added:** +1,404 | **Lines Removed:** -18  
**Test Suite:** 138 passed, 2 skipped ✅
