# AMW Django ERP - Phase Execution Plan: Phase 6

## 1. Document Purpose

This file is the working execution plan for Phase 6: Purchasing & Procurement.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 6`
- **Phase Name:** `Purchasing & Procurement`
- **Branch Name:** `phase-6`
- **Status:** `Planned`
- **Primary Goal:** `Implement supplier workflows and stock receiving with valuation updates.`
- **Depends On:** `Phase 5`
- **Manager Approval Required:** `Yes`

---

## 3. Phase Scope

### In Scope

- `Supplier` and `SupplierCategory` models
- `PurchaseOrder` and `PurchaseOrderItem` models
- `StockReceipt` operation (Receiving logic)
- Automatic WAC update on receipt
- Integration with `inventory` operations

### Out of Scope

- Accounts Payable (AP) and Payments - Deferred
- Vendor returns - Deferred
- Landing cost calculations - Deferred

### Required Outcomes

- Functional supplier database
- Purchase orders with unit costs
- Automated stock increase on receipt confirmation
- Automatic WAC recalculation based on actual received cost

---

## 4. Constitutional Alignment

### Mandatory Checks

- Purchasing logic lives in `purchasing/operations/` (Section 6.1)
- Receiving must update stock valuation (Section 6.5)
- Every receipt must be auditable

### Notes for This Phase

- The `receive_stock()` operation is the authoritative point where inventory valuation is modified. It must be strictly controlled and tested.

---

## 5. Architecture Targets

### Modules / Apps Affected

- `purchasing` (new app)
- `inventory` (for stock increase and WAC)
- `audit` (for receipt history)

### Main Files or Areas Expected

- `purchasing/models.py` (Supplier, PurchaseOrder, PurchaseOrderItem)
- `purchasing/operations/receiving.py` (Intake logic)

### Data Model Impact

- `Supplier`: `name`, `email`, `address`, `category`
- `PurchaseOrder`: `supplier`, `po_number`, `status`, `total_cost`, `actor`
- `PurchaseOrderItem`: `po`, `product`, `quantity`, `unit_cost`

### Operational Impact

- `receive_items()`: Atomic operation to increase stock and update WAC valuation.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will build the supplier management system first. Then, we will implement the Purchase Order (PO) workflow. The core deliverable is the stock receiving operation, which must interact with the `inventory` app's stock adjustment and valuation logic. This ensures that every PO receipt is reflected in both the physical inventory count and the financial WAC valuation.

### Sequencing Rule

1. Supplier and Category models
2. PurchaseOrder and PurchaseOrderItem models
3. Integration with inventory operations for stock intake
4. Valuation update triggers on receipt
5. Verification of WAC recalculation after purchase receipt

---

## 7. Parts Breakdown

### Part 1: Procurement Foundations

- **Goal:** `Define suppliers and procurement structures.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 6.1:** `Implement Supplier and Category models`
   - Output: `Basic supplier registry`
   - Verification: `Unit tests for supplier creation`

2. **Task 6.2:** `Implement PurchaseOrder and PurchaseOrderItem models`
   - Output: `PO structure for ordering stock`
   - Verification: `Verify that PO totals calculate correctly`

### Part 2: Receiving & Valuation Intake

- **Goal:** `Implement the stock intake operation.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 6.3:** `Implement receive_items() operation`
   - Output: `Atomic logic that updates PO status and calls inventory.add_stock()`
   - Verification: `Test: Confirm stock count increases after receipt`

2. **Task 6.4:** `Validate WAC update during receipt`
   - Output: `Integration test between purchasing and inventory valuation`
   - Verification: `Verify WAC recalculates using the new purchase unit cost`

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `Intake check: Verify inventory count increases exactly by PO quantity`
- `Valuation check: Verify WAC matches manual math after receipt`
- `Status check: Verify PO moves to 'Closed' or 'Received' after completion`

### Manual Verification

- `Confirm that supplier details are correctly linked to products (optional)`

---

## 10. Risks and Controls

### Known Risks

- `Incorrect unit cost entry during receiving affecting WAC valuation`
- `Receiving items not on the original PO`

### Controls / Mitigations

- `Implement validation rules to ensure received quantity matches ordered quantity (or allow over-receiving within limits)`
- `Ensure only confirmed POs can be received`

---

## 11. Open Questions

- `Should we support back-ordering or partial receipts? (Deferred)`

---

## 12. Completion Checklist

- [ ] Supplier records exist and are usable
- [ ] Purchase orders can be created and tracked
- [ ] Stock receiving updates quantity and valuation (WAC)
- [ ] Every procurement action is auditable
- [ ] IAM rules protect purchasing operations

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 6 plan for Purchasing and Procurement.`

---

## 14. Final Summary

(TBD)
