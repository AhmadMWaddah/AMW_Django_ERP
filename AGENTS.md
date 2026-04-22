# AMW Django ERP: Core Instructions

## 1. Core Directives

- **Constitution First:** Before starting any task, agents MUST index and follow all files in the `./Constitution/` directory.
- **Workflow Logic:** Adhere strictly to `Orchestrator_Law.md` for all execution steps.
- **Task Alignment:** Read `Roadmap.md` to identify the current phase and pending tasks before execution.
- **Project Identity:** This is a PRODUCTION ERP system, NOT a demo. Every implementation choice must support long-term maintainability, business correctness, and operational clarity.

---

## 2. Domain Modules

The project consists of 8 core modules organized by business domain:

| Module | Purpose | Key Models |
|--------|---------|------------|
| `accounts/` | Employee identity & authentication | Employee (AbstractBaseUser) |
| `security/` | IAM & Policy enforcement | Department, Role, Policy |
| `audit/` | Audit logging | AuditLog |
| `inventory/` | Product catalog & stock | Category, Product, StockTransaction, StockAdjustment |
| `sales/` | CRM & order workflows | Customer, SalesOrder, SalesOrderItem |
| `purchasing/` | Supplier & procurement | Supplier, PurchaseOrder, PurchaseOrderItem |
| `reporting/` | Async report generation | ReportJob |
| `core/` | Base models & utilities | SoftDeleteModel (base class) |

---

## 3. Technical Laws

### Architecture (MANDATORY)
- **Operations-First:** All business logic MUST be in `operations/` modules within each app. NEVER put business logic in views, signals, or templates.
- **Server-Side Authorization:** Use PolicyEngine for all state-changing POST endpoints (returns 403 + HTMX toast on denial).
- **Soft Delete:** All business entities inherit from `SoftDeleteModel` - supports restoration.
- **WAC Valuation:** Weighted Average Cost recalculates automatically on stock-in (19,4 precision).
- **Atomic Safety:** Use `transaction.atomic` + `select_for_update()` for all stock changes.
- **Audit Trail:** Before/after snapshots recorded for all critical changes.

### Stack
- **Backend:** Python 3.12, Django 4.2 LTS
- **Database:** PostgreSQL 15
- **Cache/Broker:** Redis 7
- **Frontend:** HTMX-first (server-rendered, no heavy JS frameworks)
- **Async:** Celery 5
- **Quality:** ruff, black, pytest

### Code Quality
- Run lint before commit: `ruff check .` and `black --check .`
- All tests must pass: `pytest`
- No type suppression (`as any`, `@ts-ignore`)
- No empty catch blocks

**CRITICAL: Never lint virtual environment**
- NEVER run `black .`, `ruff check .`, or similar on the entire project
- The venv is `.env_amw_erp/` - it is already excluded in `pyproject.toml`
- If you must lint specific files, target only them: `black path/to/file.py`

---

## 4. Git & Branching

### Branch Naming (PascalCase - MANDATORY)
| Type | Format | Example |
|------|--------|--------|
| Fixes | `Fix-{Name}` | `Fix-HTMX-Stability` |
| Features | `Feature-{Name}` | `Feature-Open-Redirect-Protection` |
| Phases | `Phase-{Number}-{Name}` | `Phase-8-Async-Hardening` |

### Commit Format (Multi-Message - MANDATORY)
```bash
# REQUIRED: Use the utility script
bash utils/git_task_commit.sh "Title" "Description"

# Title prefixes: Phase X:, Fix:, Feature:, Refactor:, Docs:, Test:
# Title under 72 characters
# Description explains WHAT and WHY (not HOW)
```

### Phase Completion
```bash
bash utils/git_phase_finish.sh <phase-number> [version-tag]
# Runs: tests → lint → merge → tag → push
```

---

## 5. Development Workflow (Orchestrator Law)

### Stage Sequence (MANDATORY order)
```
PREPARE (check services) → PLANNING → CREATE_BRANCH → CODING → 
UNIT_TESTING → REVIEWING → DOCUMENTATION → PUSH_TO_BRANCH → 
HUMAN_APPROVAL → MERGE_TO_MASTER
```

### On Failure
- **Test fails OR Review rejects:** Go back to PLANNING, then full cycle again
- **Max cycles:** 5, then escalate to human (Owner = Ahmad)

### Team Roles
| Role | Responsibility |
|------|-------------|
| **Owner** (Ahmad) | Final scope, release approval, business decisions |
| **Developer** | Implementation, business logic, data integrity |
| **Reviewer** | Code review, quality gates |

---

## 6. Utility Scripts (utils/)

| Script | Purpose |
|--------|---------|
| `git_task_commit.sh` | Atomic multi-message commits with lint |
| `git_phase_finish.sh` | Phase merge + tagging automation |
| `env_factory.sh` | Environment bootstrap (setup/create/install) |
| `test_suite_runner.sh` | Testing & linting (unit/coverage/lint) |
| `db_manage_dev.sh` | DB operations (migrate/shell/createsuperuser) |
| `infra_manage.sh` | Docker services (start/stop/logs/status) |

---

## 7. Testing & Quality Assurance

### Required Commands
```bash
# Before commit (lint check)
ruff check .
black --check .

# Run tests
pytest  # or: bash utils/test_suite_runner.sh

# With coverage
pytest --cov=. --cov-report=html
```

### Django Checks
```bash
python manage.py check
python manage.py check --deploy  # prod settings
```

---

## 8. Business Rules (Reference)

### Inventory
- `Product.current_stock` is CONTROLLED - do not edit directly
- Stock movement via transaction ledger only
- WAC recalculation on stock-in
- Stock Adjustments require approval workflow

### Sales
- Order confirmation MUST be an operation (not view shortcut)
- Snapshot pricing preserved at order time
- State machine: Draft → Confirmed → Shipped → Voided
- Void operation rolls back inventory

### Purchasing
- Stock receiving is authoritative for purchase-driven stock increases
- Receiving triggers WAC recalculation

---

## 9. Quick Reference

### Default Credentials
- **Owner:** `amw@amw.io` / `12`
- **Warehouse Lead:** `warehouse.lead@amw.io` / `password123`
- **Sales Manager:** `sales.manager@amw.io` / `password123`

### Access Points
- Dev Server: http://localhost:8010
- Django Admin: http://localhost:8010/admin/
- Health Check: http://localhost:8010/health/

### Status
- All 8 phases ✅ COMPLETE (228 tests passing)
- Branch: `master` (stable baseline)
