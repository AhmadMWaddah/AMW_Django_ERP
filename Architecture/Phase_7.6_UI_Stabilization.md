# AMW Django ERP - Phase Execution Plan: Phase 7.6

## 1. Document Purpose
This file is the working execution plan for **Phase 7.6: UI Stabilization**.
It addresses critical UI regressions and HTMX lifecycle issues identified during manual testing of Phase 7.5.

---

## 2. Phase Identity
- **Phase Number:** `Phase 7.6`
- **Phase Name:** `UI Stabilization & HTMX Hardening`
- **Branch Name:** `fix-ui-stabilization`
- **Status:** `Planned`
- **Primary Goal:** `Fix the "work once" and "nothing happens" bugs by standardizing HTMX responses and implementing global event delegation.`
- **Depends On:** `Phase 7.5`

---

## 3. Phase Scope

### In Scope
- **HTMX Response Refactor:** Replace `JsonResponse` with empty string + headers for all state-changing HTMX endpoints.
- **JS Event Delegation:** Move modal/toast logic to global `document.body` listeners.
- **IAM/UI Mapping:** Fix missing "Receive", "Confirm", and "Add Item" buttons by auditing template context.
- **Modal Lifecycle:** Fix the "modal disappears" bug by ensuring proper DOM cleanup or display toggling.
- **Re-Seed Verification:** Ensure the database is in a clean state to verify fixes.

### Out of Scope
- New features or modules.
- Changes to business logic in `operations/`.
- Styling or layout changes.

---

## 4. Constitutional Alignment
- **HTMX-First (Section 7.1):** We are moving closer to pure HTMX patterns by removing JSON dependencies in the frontend.
- **Operations-First (Section 8.1):** Logic remains in operations; we are only fixing the *delivery* of the result to the UI.

---

## 5. Architecture Targets

### Modules / Apps Affected
- `static/scripts/toast_modal.min.js` (The heart of the fix)
- `inventory/views.py`, `sales/views.py`, `purchasing/views.py` (Standardizing responses)
- `templates/` (Auditing button visibility logic)

---

## 6. Implementation Strategy

### Part 1: The "Work Once" Fix (Global Delegation)
We will refactor `toast_modal.min.js`. Instead of waiting for `DOMContentLoaded`, we will use `htmx:afterSettle`. This ensures that even if HTMX replaces a piece of the page, the JavaScript still knows how to handle buttons and modals.

### Part 2: The "Nothing Happens" Fix (Standardized Responses)
HTMX works best with HTML or empty responses. We will stop sending `JsonResponse` to HTMX. When an adjustment is successful, we send a `204 No Content` or `200 OK` with an empty body and the `HX-Refresh` and `HX-Trigger` headers. This forces HTMX to follow its internal logic correctly.

### Part 3: IAM UI Audit
We will verify why the Warehouse Lead cannot see the "Receive" button. This is usually because the `can_receive_items` flag is calculated incorrectly or missing from the context in `order_detail` views.

---

## 7. Parts Breakdown

### Part 1: JS Hardening
1. **Task 7.6.1:** `Refactor toast_modal.min.js for Event Delegation`
   - Output: `Global listeners for click and keydown events.`
   - Verification: `Buttons work after multiple HTMX swaps without refresh.`

### Part 2: View Refactoring
1. **Task 7.6.2:** `Update inventory.AdjustStock to return 204/Headers`
   - Output: `Removes JsonResponse, uses HttpResponse(status=204) + Headers.`
2. **Task 7.6.3:** `Update sales.ConfirmOrder and void_order to return 204/Headers`
   - Output: `Consistent response pattern across all modules.`

### Part 3: Template & IAM Fixes
1. **Task 7.6.4:** `Audit Purchasing/Sales Order Detail Context`
   - Output: `Ensure can_receive_items and can_confirm are correctly passed.`
   - Verification: `Buttons appear for correct roles in manual tests.`

---

## 8. Verification Plan
- **Manual Test INV-003:** Stock adjustment must show toast and refresh page.
- **Manual Test INV-005:** Stock adjustment must work *twice* without refresh.
- **Manual Test PUR-003:** "Receive" button must be visible for Warehouse Lead.
- **Manual Test HTMX-004:** Modal must open/close/reopen consistently.

---
