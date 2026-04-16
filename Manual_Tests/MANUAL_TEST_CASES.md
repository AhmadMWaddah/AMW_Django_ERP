# Manual Test Cases — AMW Django ERP

**Version:** 1.2
**Created:** 2026-04-08
**Related Plan:** `MANUAL_TEST_PLAN.md`

---

## Legend

| Field | Description |
|-------|-------------|
| **ID** | Unique test case identifier |
| **Role** | Which user persona executes this test |
| **Steps** | Action sequence to perform |
| **Expected** | What should happen if the system works correctly |
| **Actual** | Fill during execution — what actually happened |
| **Status** | Pass / Fail |
| **Comments** | Notes, screenshots reference, bug details |

---

## Active Test Cases

### Module 2: Inventory

### INV-002: Product Detail — Stock Ledger Visible

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Navigate to Inventory > Products<br>2. Click on "Frost-Free Refrigerator 500L"<br>3. Verify product details: SKU, category, stock level, WAC price<br>4. Verify stock ledger table shows transaction history<br>5. **If button appears unresponsive, open browser console (F12) and check for JavaScript errors or failed network requests** |
| **Expected** | Product detail page shows all fields. Ledger shows initial stock transaction. "View Full Ledger" link works. |
| **Actual** | Nothing Happens, No Success Toast, Button Just got Lighter Color as Clicked, No refresh No Stock Updated, Just Nothing. |
| **Status** | ⏳ Pending |
| **Comments** | |

---

### INV-003: Quick Stock Adjustment — Add Stock (HTMX)

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Navigate to a product detail page<br>2. Note current stock value<br>3. In "Quick Stock Adjustment" form, select "Add Stock"<br>4. Enter quantity: `10`<br>5. Click "Adjust" button<br>6. Verify toast notification appears<br>7. **If nothing happens, open browser console (F12 → Network tab) and verify the POST request fires and returns 200 with HX-Trigger header** |
| **Expected** | Success toast: "Added 10 to {SKU}. New stock: {new_value}". Page refreshes showing updated stock. Ledger shows new transaction entry. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: HTMX responses now use HttpResponse + headers (no JsonResponse). Global event delegation on document.body ensures buttons work repeatedly. |

---

### INV-004: Quick Stock Adjustment — Reduce Stock (HTMX)

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. On same product detail page<br>2. Select "Reduce Stock"<br>3. Enter quantity: `5`<br>4. Click "Adjust"<br>5. Verify toast notification |
| **Expected** | Success toast: "Removed 5 from {SKU}. New stock: {new_value}". Page refreshes. Stock decreased. Ledger shows reduction transaction. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Blocked by INV-003 — retest together. |

---

### INV-005: Quick Stock Adjustment — Repeated Clicks (Regression)

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. After INV-003, click "Adjust" again immediately<br>2. Enter different quantity: `3`<br>3. Click "Adjust"<br>4. Verify it works without requiring manual page refresh |
| **Expected** | Button remains functional. Second adjustment succeeds. Toast appears. Page refreshes. **Button works repeatedly without manual refresh.** |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | **Critical regression test for HTMX fix.** Fixed: global listeners on document.body survive HTMX swaps. |

---

### INV-006: Stock Adjustment — Permission Denied (Auditor)

| Field | Value |
|-------|-------|
| **Role** | Auditor |
| **Steps** | 1. Login as Auditor<br>2. Navigate to a product detail page<br>3. Verify "Quick Stock Adjustment" form is NOT visible |
| **Expected** | No adjustment form displayed. Only product info and ledger visible. |
| **Actual** | already have no permissions for this page |
| **Status** | ⏳ Pending |
| **Comments** | Auditor lacks `inventory.*:view` — needs re-seed to test. |

---

### INV-008: Stock Adjustment List — View Pending/Approved

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Navigate to Inventory > Stock Adjustments<br>2. Verify list shows any adjustments<br>3. Search by product name |
| **Expected** | List view works. Search filters. Status badges visible (Pending/Approved/Rejected/Executed). Pagination functional. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: Context now includes title, row_template, **pagination_data for table_frame.html. |

---

### Module 3: Purchasing

### PUR-003: Receive Stock Against PO (HTMX)

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Open a PO in "Issued" status<br>2. Use receive stock functionality<br>3. Enter quantities for items<br>4. Submit<br>5. Verify toast notification<br>6. **If button is missing, open browser console (F12) and check for template rendering errors or missing `can_receive_items` context variable** |
| **Expected** | Success toast. Page refreshes. PO status updates. Product stock levels increased. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: HTMX response now uses HttpResponse + headers. Context passes `can_receive_items` correctly. |

---

### PUR-004: Receive Stock — Permission Denied (Sales Manager)

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Login as Sales Manager<br>2. Navigate to Purchasing > Purchase Orders<br>3. Attempt to receive stock on a PO |
| **Expected** | 403 error or button not visible. Permission denied toast if attempted via HTMX. Purchasing sidebar should NOT be visible (correct behavior — Sales Manager lacks purchasing.*:view). |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Sales Manager should NOT see Purchasing sidebar (correct behavior). |

---

### Module 4: Sales & CRM

### SAL-003: Create Draft Order

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Navigate to a Customer detail page<br>2. Click "Create Order"<br>3. Verify redirected to new DRAFT order detail page<br>4. **If button is missing, open browser console (F12) and check for template errors or missing `can_create_order` context variable** |
| **Expected** | New order created with unique order number (#Eg-XXXXX format). Status = DRAFT. Line items empty. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: Context passes `can_create_order` via PolicyEngine check. |

---

### SAL-004: Add Line Item to Draft Order (HTMX Modal)

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Open a DRAFT order detail<br>2. Click "Add Product" button<br>3. Verify modal opens<br>4. Select a product, enter quantity and unit price<br>5. Click "Add Item"<br>6. Verify item added |
| **Expected** | Modal opens correctly. Form submits. Toast confirms. Page refreshes showing new line item. **Close modal and re-open — verify modal opens again (not destroyed).** |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | **Critical regression test for modal fix.** Fixed: global event delegation on document.body, modal uses style.display toggling (not destroy). |

---

### SAL-005: Confirm Order (HTMX POST)

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Open a DRAFT order with line items<br>2. Click "Confirm Order" button<br>3. Verify toast notification |
| **Expected** | Success toast: "Order {number} confirmed successfully." Page refreshes. Status changes to CONFIRMED. "Confirm" button no longer visible. Stock deducted for ordered items. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: HTMX response uses HttpResponse + HX-Refresh headers. |

---

### SAL-006: Confirm Order — Repeated Click (Regression)

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. After SAL-005, the page refreshes<br>2. Verify "Confirm Order" button is gone (status = CONFIRMED)<br>3. If button somehow remains, click it again |
| **Expected** | Button should NOT appear after confirmation (template condition hides it). If clicked via browser back, should get "Already confirmed" error toast. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | 405 for GET is correct behavior (endpoint is POST-only). |

---

### SAL-007: Void Order (HTMX POST)

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Open a CONFIRMED order<br>2. Click "Void Order" button<br>3. Verify toast notification |
| **Expected** | Success toast: "Order {number} voided. Stock restored." Page refreshes. Status = VOIDED. Stock levels restored for order items. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: HTMX response uses HttpResponse + HX-Refresh headers. 405 for GET is correct (POST-only). |

---

### SAL-008: Void Order — Repeated Click (Regression)

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. After SAL-007, verify "Void Order" button is gone<br>2. If button remains, click again |
| **Expected** | Button should NOT appear after voiding. If clicked, should get "Already voided" error. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | 405 for GET is correct behavior (endpoint is POST-only). |

---

### SAL-010: Order List — Confirm from Table Row

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Navigate to Sales > Orders<br>2. Find a DRAFT order in the table<br>3. Click "Confirm" button in the Actions column<br>4. Verify toast notification |
| **Expected** | Success toast. Page refreshes. Order status changes to CONFIRMED. Button removed from row. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: HTMX response uses HttpResponse + HX-Refresh headers. Context passes `can_confirm` correctly. |

---

### Module 5: Audit & Traceability

### AUD-002: Audit Log — After Stock Adjustment

| Field | Value |
|-------|-------|
| **Role** | Auditor |
| **Steps** | 1. Check audit log for entries from INV-003 and INV-004<br>2. Verify actor is "Warehouse Lead"<br>3. Verify before/after stock values recorded |
| **Expected** | Entries exist with correct actor, action type, product, old/new stock values. |
| **Actual** | |
| **Status** | ⏳ Pending |
| **Comments** | Blocked by INV-003/004. |

---

### AUD-003: Audit Log — After Order Confirmation

| Field | Value |
|-------|-------|
| **Role** | Auditor |
| **Steps** | 1. Check audit log for entries from SAL-005<br>2. Verify order confirmation logged with stock deduction details |
| **Expected** | Entry shows order number, status change (DRAFT → CONFIRMED), stock items deducted. |
| **Actual** | |
| **Status** | ⏳ Pending |
| **Comments** | Blocked by SAL-005. |

---

### Module 6: HTMX Regression (Cross-Module)

### HTMX-001: Pagination — Works Repeatedly

| Field | Value |
|-------|-------|
| **Role** | Any |
| **Steps** | 1. Navigate to any list view with pagination (Products, Customers, Orders)<br>2. Click "Next" page<br>3. Click "Previous" page<br>4. Click a specific page number<br>5. Repeat navigation 3+ times |
| **Expected** | Each pagination click loads new page content via HTMX. URL updates. No full page reload needed. Works consistently on every click. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: Inventory list views now pass correct pagination context (title, row_template, **pagination_data). |

---

### HTMX-003: Toast Notifications — Fire Every Time

| Field | Value |
|-------|-------|
| **Role** | Any |
| **Steps** | 1. Perform 3 consecutive HTMX POST actions (e.g., 3 stock adjustments)<br>2. Verify each action shows a toast notification |
| **Expected** | Each action produces a toast. Toasts don't stack or overlap. Each auto-dismisses after ~4 seconds. Success/error toasts display correct colors. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: Global htmx:afterOnLoad and htmx:responseError listeners on document.body. |

---

### HTMX-004: Modal — Open/Close/Reopen

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Open a DRAFT order<br>2. Click "Add Product" to open modal<br>3. Close modal (click X, click overlay, or press Escape)<br>4. Click "Add Product" again<br>5. Verify modal opens again |
| **Expected** | Modal opens every time. Close methods (X button, overlay click, Escape key) all work. Modal is not destroyed after close. |
| **Actual** | |
| **Status** | ⏳ Ready for Retest |
| **Comments** | Fixed in Phase 7.6: Modal uses style.display toggling (flex/none), not remove(). Global click/keydown listeners on document.body. |

---

### Module 7: Admin Panel

### ADM-001: Admin Login

| Field | Value |
|-------|-------|
| **Role** | Owner |
| **Steps** | 1. Login as `amw@amw.io`<br>2. Navigate to `/admin/`<br>3. Verify all models are manageable |
| **Expected** | Admin dashboard shows all registered models: Employees, Departments, Roles, Policies, Products, Categories, StockTransactions, Customers, SalesOrders, Suppliers, PurchaseOrders, AuditLogs. |
| **Actual** | |
| **Status** | ⏳ Pending |
| **Comments** | |

---

### ADM-002: Soft Delete — Restore Entity

| Field | Value |
|-------|-------|
| **Role** | Owner |
| **Steps** | 1. In admin, soft-delete a test customer<br>2. Verify it disappears from main list<br>3. Restore it via admin<br>4. Verify it reappears in main UI |
| **Expected** | Soft delete works. Restore works. Entity visible again in frontend. |
| **Actual** | i don't have any soft delete either in Admin or UI |
| **Status** | ⏳ Pending |
| **Comments** | |

---

## Verified Baseline

*Cases confirmed working. Moved here to keep active list focused.*

### IAM-001: Owner Login — Full Access ✅

| Field | Value |
|-------|-------|
| **Role** | Owner (`amw@amw.io` / `12`) |
| **Steps** | 1. Navigate to `http://localhost:8010`<br>2. Login as `amw@amw.io`<br>3. Verify dashboard loads<br>4. Check sidebar shows all module links (Inventory, Sales, Purchasing, Security, Audit) |
| **Expected** | Dashboard loads. All module links visible. No permission errors. Topbar shows "Ahmad Waddah". |
| **Status** | ✅ Verified |

---

### IAM-002: Warehouse Lead Login — Restricted Access ✅

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead (`warehouse.lead@amw.io` / `password123`) |
| **Steps** | 1. Login as `warehouse.lead@amw.io`<br>2. Check sidebar shows Inventory and Purchasing links<br>3. Verify Sales link is absent or inaccessible |
| **Expected** | Dashboard loads. Sidebar shows Inventory and Purchasing. Sales/CRM not visible or returns 403. |
| **Status** | ✅ Verified |

---

### IAM-003: Sales Manager Login — Restricted Access ✅

| Field | Value |
|-------|-------|
| **Role** | Sales Manager (`sales.manager@amw.io` / `password123`) |
| **Steps** | 1. Login as `sales.manager@amw.io`<br>2. Check sidebar shows Sales & CRM link<br>3. Verify Inventory adjustment is not accessible |
| **Expected** | Dashboard loads. Sales & CRM visible. Inventory adjustment returns 403 or hidden. |
| **Status** | ✅ Verified |

---

### IAM-004: Auditor Login — Read-Only Access ✅

| Field | Value |
|-------|-------|
| **Role** | Auditor (`auditor@amw.io` / `password123`) |
| **Steps** | 1. Login as `auditor@amw.io`<br>2. Navigate to Inventory > Products<br>3. Verify "Quick Stock Adjustment" form is NOT visible<br>4. Navigate to Audit Log<br>5. Verify audit entries are visible |
| **Expected** | Dashboard loads. No adjustment buttons visible. Audit log shows entries. Read-only enforced. |
| **Status** | ✅ Verified |

---

### IAM-005: Logout and Re-Login ✅

| Field | Value |
|-------|-------|
| **Role** | Any |
| **Steps** | 1. Login as any user<br>2. Click logout<br>3. Verify redirected to login page<br>4. Attempt to access `/inventory/products/` directly<br>5. Verify redirect back to login |
| **Expected** | Logout redirects to login. Direct URL access to protected pages redirects to login (not 403). |
| **Status** | ✅ Verified |

---

### INV-001: Product List — View and Search ✅

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Login as Warehouse Lead<br>2. Navigate to Inventory > Products<br>3. Verify 14 products displayed<br>4. Search for "Refrigerator" in search box<br>5. Verify results filter correctly |
| **Expected** | All 14 products visible with SKU, name, category, stock. Search filters to matching products. HTMX search works without full page reload. |
| **Status** | ✅ Verified |

---

### INV-007: Category List — View and Search ✅

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Navigate to Inventory > Categories<br>2. Verify 5 categories displayed<br>3. Search for "Kitchen"<br>4. Verify filter works |
| **Expected** | All categories visible. Search filters correctly. HTMX table update works. |
| **Status** | ✅ Verified |

---

### PUR-001: Supplier List — View and Search ✅

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Navigate to Purchasing > Suppliers<br>2. Verify suppliers are displayed<br>3. Search by name<br>4. Verify filter works |
| **Expected** | Supplier list loads. Search filters via HTMX. Category filter dropdown works. |
| **Status** | ✅ Verified |

---

### PUR-002: Purchase Order Detail — View ✅

| Field | Value |
|-------|-------|
| **Role** | Warehouse Lead |
| **Steps** | 1. Navigate to Purchasing > Purchase Orders<br>2. Click on an existing PO<br>3. Verify PO number, supplier, status, line items |
| **Expected** | PO detail page shows all fields. Line items table visible. Status badge correct. |
| **Status** | ✅ Verified |

---

### SAL-001: Customer List — View and Search ✅

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Login as Sales Manager<br>2. Navigate to Sales > Customers<br>3. Verify customers displayed<br>4. Search by name<br>5. Filter by category |
| **Expected** | Customer list loads. Search and category filter work via HTMX. |
| **Status** | ✅ Verified |

---

### SAL-002: Order List — View and Filter ✅

| Field | Value |
|-------|-------|
| **Role** | Sales Manager |
| **Steps** | 1. Navigate to Sales > Orders<br>2. Verify orders displayed<br>3. Filter by status (DRAFT, CONFIRMED)<br>4. Search by order number |
| **Expected** | Order list loads. Status filter works. Search works. "Confirm" button visible for DRAFT orders. |
| **Status** | ✅ Verified |

---

### SAL-009: Confirm Order — Permission Denied (Auditor) ✅

| Field | Value |
|-------|-------|
| **Role** | Auditor |
| **Steps** | 1. Login as Auditor<br>2. Navigate to Sales > Orders<br>3. Open a DRAFT order<br>4. Verify "Confirm Order" button is NOT visible |
| **Expected** | Confirm button hidden. If accessed via direct POST, returns 403 with toast. |
| **Actual** | Permissions denied |
| **Status** | ✅ Verified |

---

### AUD-001: Audit Log — View Entries ✅

| Field | Value |
|-------|-------|
| **Role** | Auditor |
| **Steps** | 1. Login as Auditor<br>2. Navigate to Audit Log<br>3. Verify entries exist from previous test actions |
| **Expected** | Audit log shows entries for stock adjustments, order confirmations, voids. Each entry shows actor, action, timestamp, before/after data. |
| **Status** | ✅ Verified |

---

### HTMX-002: Search Filter — Works Repeatedly ✅

| Field | Value |
|-------|-------|
| **Role** | Any |
| **Steps** | 1. On any list view, type a search query<br>2. Verify results filter<br>3. Clear search and press enter<br>4. Verify results restore<br>5. Search again with different term |
| **Expected** | Each search updates table content via HTMX. Works repeatedly without page refresh. |
| **Status** | ✅ Verified |

---

### HTMX-005: Permission Denied — Shows Branded 403 Page ✅

| Field | Value |
|-------|-------|
| **Role** | Auditor |
| **Steps** | 1. Login as Auditor<br>2. Try to access a restricted action via direct URL (e.g., `/inventory/products/`)<br>3. Verify response |
| **Expected** | Branded 403 error page with styled card, "Permission Denied" heading, and "Go to Dashboard" button. No raw white-screen text. |
| **Actual** | Previously showed white page with raw text. Now renders branded 403.html template. |
| **Status** | ✅ Verified |

---

## Summary Table

| Module | Active | Verified | Ready for Retest | Blocked |
|--------|--------|----------|------------------|---------|
| Identity & IAM | 0 | 5 | 0 | 0 |
| Inventory | 0 | 2 | 4 | 1 (INV-006) |
| Purchasing | 0 | 2 | 2 | 0 |
| Sales & CRM | 0 | 3 | 6 | 0 |
| Audit & Traceability | 2 | 1 | 0 | 1 (blocked) |
| HTMX Regression | 0 | 2 | 3 | 0 |
| Admin Panel | 2 | 0 | 0 | 0 |
| **Total** | **6** | **15** | **15** | **2** |

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-04-08 | Initial test cases created (37 cases across 7 modules) | Qwen |
| 2026-04-14 | v1.2: Restructured — moved verified cases to baseline, refined failed case steps with browser console checks, updated summary table | Qwen |
| 2026-04-14 | v1.2 audit closure: clarified pending IAM/HTMX cases with re-seed plus browser-verification steps after enforcement and UI fixes | Cod |
| 2026-04-15 | v1.3: Phase 7.6 fixes applied — reset 15 test cases to "Ready for Retest". Updated CREDENTIALS.md to match seed_erp.py emails. | Qwen |
