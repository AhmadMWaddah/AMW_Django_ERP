# 📋 AGENTS.md — AMW Django ERP

> Django 4.2 · HTMX frontend · PostgreSQL · Redis
> Core domains: **Inventory** (WAC valuation), **Sales**, **Purchasing**, **IAM**, **Audit**

---

## ⚡ Critical Setup

```bash
# Bootstrap environment
bash utils/env_factory.sh setup
source .env_amw_dj_erp/bin/activate

# Start infrastructure (PostgreSQL + Redis via Docker)
bash utils/infra_manage.sh start

# Run migrations
bash utils/db_manage_dev.sh migrate

# Seed test data
python manage.py seed_erp
```

> **Database:** PostgreSQL only. SQLite not supported. Port `5433` locally (`5432` in Docker).

---

## 🛠️ Essential Commands

### 🧪 Testing

```bash
bash utils/test_suite_runner.sh          # All tests
bash utils/test_suite_runner.sh unit     # Unit only
bash utils/test_suite_runner.sh coverage # With coverage

pytest path/to/tests.py -v               # Single test
```

### 🔍 Linting

```bash
black . && ruff check --fix .
```

### ✅ Django Checks

```bash
python manage.py check --settings=config.settings.dev
python manage.py check --deploy --settings=config.settings.prod
```

### 🗄️ Migrations

```bash
python manage.py makemigrations --settings=config.settings.dev
bash utils/db_manage_dev.sh migrate
```

---

## 🏛️ Architecture Rules
> Enforced by **Planner**

- **Business logic** lives in `operations/` modules, NOT views:
  - `inventory/operations/stock.py` — `stock_in`, `stock_out`, `adjust_stock`
  - `sales/operations/orders.py` — `create_order`, `confirm_order`, `void_order`
  - `purchasing/operations/orders.py` — `issue_order`, `receive_items`, `cancel_order`

- **Policy enforcement** is server-side via `PolicyEngine` (`security/logic/enforcement.py`):
  - All state-changing POST endpoints use `@require_permission()`
  - HTMX requests return JSON with 403; normal requests raise `PermissionDenied`

- **Soft delete** is default. All core models inherit `SoftDeleteModel`. Use `.delete()` for soft delete, `.undelete()` to restore.

- **WAC recalculation** happens only on stock-in (`PURCHASE`, `INTAKE`, `ADJUST_ADD`). Stock-out does NOT recalculate WAC.

- **Concurrency safety:** `stock_in`/`stock_out` use `select_for_update()` within `transaction.atomic`.

- **Audit logging:** All critical changes logged via `audit.logic.logging.log_audit()` with before/after snapshots.

- **Planner** is responsible for: `Architecture_Law.md`, `Orchestrator_Law.md`, `Roadmap.md`, `Stack_and_Tools_Law.md`

---

## ✏️ Code Style & Implementation
> Enforced by **Coder**

- Double quotes only for all Python strings.
- Run `black . && ruff check --fix .` before commit.
- Ruff handles imports — do not manually sort.
- No `# -- Section --` comment headers in import blocks.

**Coder responsibilities:** Write clean, production-ready code following the architecture rules. Implement features in the correct `operations/` modules. Use the audit logging and concurrency patterns described.

Responsible for: `CICD_Law.md`, `Frontend_Law.md`, `Inventory_Law.md`, `Purchasing_Law.md`, `Sales_Law.md`

---

## 🔎 Code Review & Quality Gates
> Enforced by **Reviewer**

- Ensure all code adheres to the architecture rules.
- Verify that business logic is not in views.
- Check that soft delete is used correctly.
- Confirm WAC recalculation only on stock-in operations.
- Validate that `select_for_update()` is used in concurrent stock operations.

Reviewer also enforces: documentation standards (docstrings, inline comments for complex logic), git conventions, testing requirements, code style (double quotes, black/ruff compliance).

Responsible for: `Documentation_Law.md`, `Git_Law.md`, `Style_Law.md`, `Testing_Law.md`

---

## 🌿 Git Conventions
> Enforced by **Reviewer**

```bash
bash utils/git_task_commit.sh "Title" "Description"
bash utils/git_phase_finish.sh <phase> [tag]
```

- **Branch names** (PascalCase): `Fix-{Name}`, `Feature-{Name}`, `Phase-{Number}-{Name}`
- **Commit prefixes:** `Phase X:`, `Fix:`, `Feature:`, `Refactor:`, `Docs:`, `Test:`

---

## 📁 Key Files

| Path | Purpose |
|------|---------|
| `config/settings/base.py` | AUTH_USER_MODEL, INSTALLED_APPS |
| `core/models.py` | SoftDeleteModel, TimeStampedModel bases |
| `accounts/models.py` | Employee model (AbstractBaseUser, email login) |
| `security/logic/enforcement.py` | PolicyEngine, require_permission decorator |
| `Constitution/` | Project law documents (each agent reads their assigned files) |

---

## 🧪 Testing
> Enforced by **Reviewer**

- **Test markers:** `unit`, `integration`, `slow`, `wac`, `iam`
- Fixtures in `Manual_Tests/conftest.py`
- Manual test docs in `Manual_Tests/` directory only
- New code must include appropriate tests: unit for business logic, integration for endpoints
- The Reviewer will ensure the test suite passes before any merge.

---

## 🚀 CI Pipeline
> Enforced by **Coder**

Runs on every push/PR:

```
lint (ruff + black) → test → django-check → docker-build
```

No PR merges unless CI is green. The Coder must ensure the pipeline is always green before requesting a review.

---

## 👤 Agent Responsibility Summary

> All agents must read and follow the rules in their assigned law files before completing any task.

| Agent | Primary Law Files |
|-------|------------------|
| 🗺️ **Planner** | `Architecture_Law.md`, `Orchestrator_Law.md`, `Roadmap.md`, `Stack_and_Tools_Law.md` |
| 💻 **Coder** | `CICD_Law.md`, `Frontend_Law.md`, `Inventory_Law.md`, `Purchasing_Law.md`, `Sales_Law.md` |
| 🔎 **Reviewer** | `Documentation_Law.md`, `Git_Law.md`, `Style_Law.md`, `Testing_Law.md` |
