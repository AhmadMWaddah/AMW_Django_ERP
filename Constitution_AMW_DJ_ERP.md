# AMW Django ERP - Project Law for AI CLI Agents

**Version:** 2.2 (Enterprise Grade)
**Last Updated:** 2026-04-01

---

# Block A: Project Identity (Who & What)

## 1. Purpose of This File

This file is the operational law of the AMW Django ERP project.

It exists so that any AI CLI tool, coding agent, assistant, reviewer, or automation worker used in this repository follows:
- the same project identity,
- the same engineering methodology,
- the same architectural rules,
- the same execution discipline,
- and the same delivery standards.

This file is intentionally concrete. It is not a vague manifesto. It defines how this project must be built.

---

## 2. What This Project Is

AMW Django ERP is a Django-based ERP system intended for real business operations.

It is designed to cover these core areas:
- employee identity and authentication,
- policy-based access control,
- inventory and stock valuation,
- customer and sales workflows,
- supplier and purchasing workflows,
- audit logging and traceability,
- reporting and asynchronous processing,
- and a maintainable server-rendered frontend.

This is not a generic starter template and not a toy demo. Every implementation choice should support long-term maintainability, business correctness, and operational clarity.

---

## 3. Authority and Roles

- **Manager:** Ahmad
  - Final owner of scope, release approval, and business decisions.
- **Consultant AI / Architecture Auditor:** Gem
  - Reviews overall architectural alignment and strategic consistency.
- **Backend & Logic Lead:** Qwen
  - Owns business logic, data integrity, IAM enforcement, and backend operations design.
- **Frontend & UI Lead / Cross-Reviewer:** Cod
  - Owns HTMX-based interaction, template architecture, and frontend consistency.

### Role Rule

- Ahmad is the final business authority.
- AI agents may propose alternatives, but they must not override this law without explicit approval.
- If multiple AI tools are used, they must behave as collaborators under the same constitution, not as independent authors with conflicting methods.

---

# Block B: Execution & Delivery Law (How We Work)

## 4. Mandatory Behavior for Any AI CLI Tool

Every AI CLI tool working on this project must obey the following:

### 4.1 Read Before Writing

- Read the relevant files before making architectural or code decisions.
- Do not assume the structure, naming, or workflow without verifying local project context.

### 4.2 Work Sequentially

- Execute work phase by phase.
- Within a phase, work part by part.
- Within a part, work task by task.
- Do not jump ahead to later phases unless Ahmad explicitly approves it.

### 4.3 Stay Concrete

- Do not replace project-specific requirements with generic best-practice filler.
- Do not abstract away project identity, modules, or workflow details.
- When writing documentation or code, keep it aligned with AMW Django ERP specifically.

### 4.4 Respect Existing Direction

- Do not rewrite the project into a different stack or methodology unless Ahmad explicitly requests a change.
- Do not introduce architecture that conflicts with the operations-first model, custom employee identity, policy-based IAM, or HTMX-first frontend direction.

### 4.5 Finish at Task Level

- A task should be completed cleanly before moving to the next task.
- If a task is too large, split it into smaller atomic sub-tasks rather than partially implementing it.

### 4.6 No Hidden Business Logic

- Never hide core business rules inside views, signals, templates, or scattered helper functions.
- Business workflows must remain visible and auditable in explicit operation modules.

### 4.7 No Silent Drift

- If a code change requires changing project law, architecture, or roadmap assumptions, the AI tool must state that explicitly rather than drifting silently.

---

## 5. Definition of Completion

A task, part, or phase is complete only when:
- the implementation matches the project law,
- the code is coherent and production-minded,
- the relevant tests exist,
- the relevant tests pass,
- execution is free of unexplained tracebacks or debug noise,
- and Ahmad approves the milestone when business scope or release status is affected.

### Completion Clarification

- "Relevant tests pass" means the tests that validate the changed business behavior, not only unrelated smoke checks.
- Temporary exceptions must be explicitly documented. They are not assumed.

---

## 6. Git & Branching Law

### 6.1 Branching

- Do not commit directly to `master`.
- All work should happen in branches.
- Remote-first workflow is expected when repository hosting is active.

### 6.2 Branch Naming

The original phase naming is preserved conceptually, but branch names used in Git should be machine-safe.

**Branch Naming Convention:**

| Branch Type        | Format          | Example                 |
|--------------------|-----------------|-------------------------|
| **Phase Branch**   | `phase-X`       | `phase-4`               |
| **Feature Branch** | `feature-{name}`| `feature-seed_erp`      |
| **Fix Branch**     | `fix-{name}`    | `fix-login_bug`         |
| **Hotfix Branch**  | `hotfix-{name}` | `hotfix-security_patch` |

**When to Use Each:**

- **Phase branches** (`phase-X`): Active development of planned phase work
- **Feature branches** (`feature-{name}`): New features outside active phase scope (e.g., utility commands, enhancements)
- **Fix branches** (`fix-{name}`): Bug fixes after phase merged to master
- **Hotfix branches** (`hotfix-{name}`): Critical production fixes

**Workflow Rule:**

1. **During Active Phase Development:** All work goes in `phase-X` branch
2. **After Phase Merge to Master:** 
   - New features → `feature-{name}` branch
   - Bug fixes → `fix-{name}` branch
3. **Merge to Master:** After Ahmad confirms and approves

### 6.3 Commits - Multi-Message Format

**MANDATORY:** All commits MUST use the two-part commit format for audit clarity.

**Format:**
```bash
git commit -m "branch-prefix Title" -m "Detailed description"
```

**Using the utility script (RECOMMENDED):**
```bash
bash utils/git_task_commit.sh "Title" "Description"

# Examples:
bash utils/git_task_commit.sh "phase-2: Employee Model" "Added AbstractBaseUser with email authentication"
bash utils/git_task_commit.sh "Fix: Navigation bug" "Changed bare URLs to namespaced accounts:dashboard"
bash utils/git_task_commit.sh "Feature: Open redirect protection" "Added Django's url_has_allowed_host_and_scheme"
```

**Title Prefixes:**
- `phase-X:` - For phase-related features (e.g., `phase-2:`, `phase-3:`)
- `Fix:` - For bug fixes
- `Feature:` - For new features
- `Refactor:` - For code refactoring
- `Docs:` - For documentation updates
- `Test:` - For test additions or modifications

**Rules:**
- Title should be concise (under 72 characters)
- Description should explain WHAT and WHY (not HOW)
- Both title and description are mandatory
- Use the utility script `utils/git_task_commit.sh` for consistency
- **Local Quality Gate:** The commit script runs mandatory lint checks before allowing commits

### 6.4 Merge Rule

- Merge to `master` only after Ahmad confirms deliverables and fixes.
- Architecture-sensitive changes should be reviewed before merge.
- Use `utils/git_phase_finish.sh` for automated phase completion and merging.

### 6.5 Phase Completion and Tagging

**MANDATORY:** Each completed phase MUST be:
1. Merged to `master` branch
2. Tagged with a version tag
3. Pushed to GitHub with tags

**Tag Format:** `v{phase-number}.0-phase{phase-number}-complete`

**Examples:**
- `v1.0-phase1-complete`
- `v2.0-phase2-complete`
- `v3.0-phase3-complete`

**Automated Process:**
```bash
bash utils/git_phase_finish.sh <phase-number> [version-tag]

# Examples:
bash utils/git_phase_finish.sh 3           # Auto-generates tag: v3.0-phase3-complete
bash utils/git_phase_finish.sh 3 v3.0     # Custom tag
```

**What the script does:**
1. Runs full test suite (must pass)
2. Runs lint checks (must pass)
3. Merges phase branch to master
4. Creates annotated version tag
5. Pushes master and tags to GitHub
6. Optionally cleans up phase branch

---

## 7. CI/CD & Automation Law

### 7.1 CI Defender (GitHub Actions)

**MANDATORY:** All pushes and pull requests MUST pass CI checks.

**CI Pipeline Jobs:**
1. **Lint Check** - Ruff and Black formatting
2. **Test Suite** - Full pytest coverage with PostgreSQL
3. **Django Check** - System check for dev and prod settings
4. **Build Verification** - Docker image build success

**No PR shall be merged unless the CI Defender is Green.**

### 7.2 Local Quality Gate

**MANDATORY:** All commits MUST pass lint checks before entering Git history.

**Enforcement:**
- `utils/git_task_commit.sh` runs mandatory lint check
- Ruff must pass (with I001 ignored for import sorting)
- Black must pass (auto-formats if needed)
- Commit blocked if lint fails

### 7.3 Phase Completion Automation

**MANDATORY:** Phase completion MUST use the automated script.

**Script:** `utils/git_phase_finish.sh`

**Automated Steps:**
1. Run full test suite (must pass)
2. Run lint checks (must pass)
3. Merge phase branch to master
4. Create version tag
5. Push to GitHub
6. Cleanup phase branch (optional)

**Usage:**
```bash
bash utils/git_phase_finish.sh <phase-number> [version-tag]
```

### 7.4 Milestone Tagging

**MANDATORY:** Each completed phase MUST be tagged.

**Tag Format:** `v{phase-number}.0-phase{phase-number}-complete`

**Examples:**
- `v1.0-phase1-complete`
- `v2.0-phase2-complete`
- `v3.0-phase3-complete`

**Benefits:**
- Instant rollback capability
- Clear historical milestones
- Production deployment markers

---

# Block C: Architectural Law (The Design Rules)

## 8. Core Architecture Law

### 8.1 Operations-First Business Logic

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

### 8.2 Identity Anchor

- The project must use a custom `Employee` model extending `AbstractBaseUser`.
- This is a foundational decision, not an optional enhancement.
- All identity-aware modules must be designed around this model from the start.

### 8.3 IAM Strategy

- IAM follows this model: `Employee -> Department -> Role -> Policies`
- Policy checks must be reusable from Python code.
- Access control must not exist only in templates or view decorators.

### 8.4 Soft Delete Rule

- Soft delete is the default for core business entities that may need restoration or historical visibility.
- Audit logs, immutable ledgers, and technical records are allowed to remain hard-persistent where appropriate.
- If a model does not use soft delete, there should be a deliberate reason.

### 8.5 Stock Valuation Rule

- Inventory valuation uses Weighted Average Cost (WAC).
- WAC must be recalculated automatically on stock-in flows that affect valuation.
- Stock updates must not allow silent corruption of quantity, cost, or audit history.

### 8.6 Atomic Safety Rule

- Concurrency-sensitive state changes must run inside `transaction.atomic`.
- Inventory-changing flows must use locking such as `select_for_update()` where row contention is possible.

### 8.7 Audit Rule

- Business-critical state changes must be logged.
- Audit records must capture:
  - actor,
  - action,
  - target,
  - timestamp,
  - and meaningful before/after change data where applicable.

---

## 9. Domain Implementation Standards

### 9.1 Inventory

- `Product.current_stock` must be treated as a controlled field, not casually edited from arbitrary code paths.
- Stock movement should be represented by a transaction ledger, not only by direct field mutation.
- WAC formula must be implemented deterministically and tested.

### 9.2 Sales

- Order confirmation must be an operation, not a view-side shortcut.
- Sales order item pricing must preserve snapshot values at time of order.
- Customer shipping address must be snapshotted at order time (not referenced).
- SalesOrder and related entities use SoftDeleteMixin (Constitution 8.4).

### 9.3 Purchasing

- Stock receiving must be the authoritative point for purchase-driven stock increases.
- Valuation updates must happen through receiving logic, not through disconnected side effects.

### 9.4 IAM

- Every protected workflow must be capable of policy validation before execution.
- Do not hardcode permission decisions in many unrelated places.

### 9.5 Financial Precision

- All currency fields must use `DecimalField(max_digits=19, decimal_places=4)`.
- Monetary calculations must use Python's `Decimal` class (not `float`).
- Rounding must use `ROUND_HALF_UP` for consistency across all financial operations.
- Order numbering must be atomic, unique, and generated in the operations layer (e.g., `#Eg-00001`).

---

## 10. Frontend & Template Law

### 10.1 Rendering Strategy

- The project frontend is server-rendered using Django templates.
- HTMX is the primary engine for dynamic UI interactions.
- JavaScript helpers may support HTMX behavior, but must not replace the HTMX-first approach without approval.

### 10.2 Template Hierarchy

- `templates/layouts/` - high-level structural shells such as `base.html` and `dashboard.html`
- `templates/_snipps_/` - global atoms such as buttons and inputs
- `templates/_snipps_/_button_.html` - global atoms such as buttons and inputs HTML files
- `templates/components/` - global shared sections such as navbar, sidebar, and cards
- `templates/<module>/components/` - module-specific fragments
- `templates/<module>/pages/` - full pages rendered by views

### 10.3 Asset Placement

- CSS belongs in `static/styles/`
- JavaScript belongs in `static/scripts/`
- Avoid inline styles
- Theme values should use CSS custom properties
- Brand colors should align with the `Brand/` directory assets and references

### 10.4 Interaction Rule

- Dynamic updates, row injection, modal content loading, and partial refreshes should use HTMX by default.
- jQuery may be used as a support tool, not as the main frontend architecture.

---

# Block D: Engineering Standards (The Quality)

## 11. Approved Stack & Tools

### 11.1 Technology Stack

| Layer        | Technology                     |
|--------------|--------------------------------|
| Backend      | Python, Django                 |
| Database     | PostgreSQL                     |
| Frontend     | HTMX, Django Templates, CSS    |
| JS Support   | jQuery only when justified     |
| Async        | Celery + Redis                 |
| Testing      | `pytest`, `pytest-django`      |
| Dev Port     | `8010`                         |

### 11.2 Utility Scripts

Official project scripts live in `utils/` and include:
1. `git_task_commit.sh` - Atomic commits with lint check
2. `git_phase_finish.sh` - Phase completion automation
3. `env_factory.sh` - Virtual environment management
4. `test_suite_runner.sh` - Unified testing interface
5. `db_manage_dev.sh` - Database operations
6. `infra_manage.sh` - Docker infrastructure management

### 11.3 Script Rule

- AI tools should prefer project utility scripts when they exist and are appropriate for the task.
- If a required script is missing, incomplete, or broken, the tool may work around it temporarily but should note the gap.

### 11.4 Environment Rule

- Development setup should remain repeatable.
- Settings should be split clearly by environment.
- Environment-sensitive behavior must be controlled explicitly, not by accidental defaults.

### 11.5 Python Style: Double Quotes

**MANDATORY:** Use double quotes (`"`) for all Python strings.

**Examples:**
```python
# CORRECT (Double quotes)
name = "Employee"
error = "Invalid email or password"

# INCORRECT (Single quotes)
name = 'Employee'
error = 'Invalid email or password'
```

**Rationale:**
- Consistency across the codebase
- Easier string interpolation with f-strings
- Matches Django and modern Python conventions

---

## 12. Documentation & Commenting Law

- Use docstrings for classes, operation methods, and non-trivial utilities.
- Comments must explain why, not repeat what the code already says.
- Import statements MUST be managed automatically by Ruff/isort (no manual section headers).
- Avoid manual import organization; let automation handle consistency.

**Automated Import Management:**
- Ruff (with isort rules) automatically sorts all imports
- No manual `# -- Section --` headers in import blocks
- CI enforces consistent import ordering across the codebase

---

## 13. Testing & Verification Law

- Every critical business feature requires tests.
- Every bug fix should include regression protection where practical.
- Inventory, IAM, and sales-confirmation flows are high-priority test domains.
- Tests should validate business behavior, not only model creation.

### Verification Standard

At minimum, verification should cover:
- changed business rules,
- changed operation methods,
- permission-sensitive flows,
- and concurrency-sensitive logic where applicable.

---

# Block E: Roadmap & Final Rules

## 14. Project Modules & Domain Scope

The project should be organized around these major domains:

### 14.1 Foundation
- core project configuration
- utilities
- environment setup
- test framework
- infrastructure bootstrap

### 14.2 Identity
- custom `Employee`
- authentication
- admin integration
- technical and business account separation

### 14.3 IAM and Security
- `Department`
- `Role`
- `Policy`
- permission mixins
- operation-level policy enforcement

### 14.4 Inventory
- `Category`
- `Product`
- stock ledger
- stock adjustment logic
- WAC valuation engine

### 14.5 Sales and CRM
- `Customer`
- `SalesOrder`
- `SalesOrderItem`
- totals calculation
- order confirmation and stock deduction

### 14.6 Purchasing
- `Supplier`
- `PurchaseOrder`
- `PurchaseOrderItem`
- stock receipt and cost update

### 14.7 Frontend Foundation
- layouts
- atoms
- shared components
- HTMX partials
- dashboard and module pages

### 14.8 Async and Reporting
- Celery task execution
- background document generation
- reporting workflows
- progress feedback patterns

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

### Phase 5: Sales & CRM Workflows
**Goal:** Implement customer management and atomic sales order workflows.

**Required outcomes:**
- Customer records exist
- Sales orders and order items exist
- Snapshot pricing is preserved
- Order confirmation drives stock deduction through operations

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

---

*Project Law Version: 2.0 (Enterprise Grade)*  
*Reorganized: 2026-03-30*
