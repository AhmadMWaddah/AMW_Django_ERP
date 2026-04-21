# Architecture Law - AMW Django ERP

**Extracted from Constitution Section 8**

## 8.1 Operations-First Business Logic

- Core business logic must live in `operations/` modules inside each app.
- Views are request/response orchestration layers, not business rule containers.
- The following are mandatory examples of operation-layer logic:
  - stock adjustments,
  - stock valuation changes,
  - order confirmation,
  - purchasing receipt,
  - policy checks,
  - audit-producing state changes.

**Example pattern:**
- `inventory/operations/stock.py`
- `sales/operations/orders.py`
- `purchasing/operations/receiving.py`

## 8.2 Identity Anchor

- The project must use a custom `Employee` model extending `AbstractBaseUser`.
- This is a foundational decision, not an optional enhancement.
- All identity-aware modules must be designed around this model from the start.

## 8.3 IAM Strategy

- IAM follows this model: `Employee -> Department -> Role -> Policies`
- Policy checks must be reusable from Python code.
- Access control must not exist only in templates or view decorators.

## 8.4 Soft Delete Rule

- Soft delete is the default for core business entities that may need restoration or historical visibility.
- Audit logs, immutable ledgers, and technical records are allowed to remain hard-persistent where appropriate.
- If a model does not use soft delete, there should be a deliberate reason.

## 8.5 Stock Valuation Rule

- Inventory valuation uses Weighted Average Cost (WAC).
- WAC must be recalculated automatically on stock-in flows that affect valuation.
- Stock updates must not allow silent corruption of quantity, cost, or audit history.

## 8.6 Atomic Safety Rule

- Concurrency-sensitive state changes must run inside `transaction.atomic`.
- Inventory-changing flows must use locking such as `select_for_update()` where row contention is possible.

## 8.7 Audit Rule

- Business-critical state changes must be logged.
- Audit records must capture:
  - actor,
  - action,
  - target,
  - timestamp,
  - and meaningful before/after change data where applicable.

---

## 9.4 IAM Domain Rules

- Every protected workflow must be capable of policy validation before execution.
- Do not hardcode permission decisions in many unrelated places.

## 9.5 Financial Precision

- All currency fields must use `DecimalField(max_digits=19, decimal_places=4)`.
- Monetary calculations must use Python's `Decimal` class (not `float`).
- Rounding must use `ROUND_HALF_UP` for consistency across all financial operations.
- Order numbering must be atomic, unique, and generated in the operations layer (e.g., `#Eg-00001`).
