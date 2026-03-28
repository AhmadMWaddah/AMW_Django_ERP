# AMW Django ERP - Project Law for AI CLI Agents

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

## 6. Core Architecture Law

### 6.1 Operations-First Business Logic

- Core business logic must live in `operations/` modules inside each app.
- Views are request/response orchestration layers, not business rule containers.
- The following are mandatory examples of operation-layer logic:
  - stock adjustments,
  - stock valuation changes,
  - order confirmation,
  - purchasing receipt,
  - policy checks,
  - audit-producing state changes.

Example pattern:
- `inventory/operations/stock.py`
- `sales/operations/orders.py`
- `purchasing/operations/receiving.py`

### 6.2 Identity Anchor

- The project must use a custom `Employee` model extending `AbstractBaseUser`.
- This is a foundational decision, not an optional enhancement.
- All identity-aware modules must be designed around this model from the start.

### 6.3 IAM Strategy

- IAM follows this model:
  - `Employee -> Department -> Role -> Policies`
- Policy checks must be reusable from Python code.
- Access control must not exist only in templates or view decorators.

### 6.4 Soft Delete Rule

- Soft delete is the default for core business entities that may need restoration or historical visibility.
- Audit logs, immutable ledgers, and technical records are allowed to remain hard-persistent where appropriate.
- If a model does not use soft delete, there should be a deliberate reason.

### 6.5 Stock Valuation Rule

- Inventory valuation uses Weighted Average Cost.
- WAC must be recalculated automatically on stock-in flows that affect valuation.
- Stock updates must not allow silent corruption of quantity, cost, or audit history.

### 6.6 Atomic Safety Rule

- Concurrency-sensitive state changes must run inside `transaction.atomic`.
- Inventory-changing flows must use locking such as `select_for_update()` where row contention is possible.

### 6.7 Audit Rule

- Business-critical state changes must be logged.
- Audit records must capture:
  - actor,
  - action,
  - target,
  - timestamp,
  - and meaningful before/after change data where applicable.

---

## 7. Frontend & Template Law

### 7.1 Rendering Strategy

- The project frontend is server-rendered using Django templates.
- HTMX is the primary engine for dynamic UI interactions.
- JavaScript helpers may support HTMX behavior, but must not replace the HTMX-first approach without approval.

### 7.2 Template Hierarchy

- `templates/layouts/`
  - high-level structural shells such as `base.html` and `dashboard.html`
- `templates/_snipps_/`
  - global atoms such as buttons and inputs
- `templates/_snipps_/_button_.html`
  - global atoms such as buttons and inputs HTML files
- `templates/components/`
  - global shared sections such as navbar, sidebar, and cards
- `templates/<module>/components/`
  - module-specific fragments
- `templates/<module>/pages/`
  - full pages rendered by views

### 7.3 Asset Placement

- CSS belongs in `static/styles/`
- JavaScript belongs in `static/scripts/`
- Avoid inline styles
- Theme values should use CSS custom properties
- Brand colors should align with the `Brand/` directory assets and references

### 7.4 Interaction Rule

- Dynamic updates, row injection, modal content loading, and partial refreshes should use HTMX by default.
- jQuery may be used as a support tool, not as the main frontend architecture.

---

## 8. Tools, Environment, and Execution Standards

### 8.1 Approved Stack

| Layer        | Technology                     |
|--------------|--------------------------------|
| Backend      | Python, Django                 |
| Database     | PostgreSQL                     |
| Frontend     | HTMX, Django Templates, CSS    |
| JS Support   | jQuery only when justified     |
| Async        | Celery + Redis                 |
| Testing      | `pytest`, `pytest-django`      |
| Dev Port     | `8010`                         |

### 8.2 Utility Scripts

Official project scripts live in `utils/` and include:
1. `git_task_commit.sh`
2. `env_factory.sh`
3. `test_suite_runner.sh`
4. `db_manage_dev.sh`
5. `infra_manage.sh`

### 8.3 Script Rule

- AI tools should prefer project utility scripts when they exist and are appropriate for the task.
- If a required script is missing, incomplete, or broken, the tool may work around it temporarily but should note the gap.

### 8.4 Environment Rule

- Development setup should remain repeatable.
- Settings should be split clearly by environment.
- Environment-sensitive behavior must be controlled explicitly, not by accidental defaults.

---

## 9. Git and Delivery Law

### 9.1 Branching

- Do not commit directly to `master`.
- All work should happen in branches.
- Remote-first workflow is expected when repository hosting is active.

### 9.2 Branch Naming

The original phase naming is preserved conceptually, but branch names used in Git should be machine-safe.

Recommended branch style:
- `phase-1`
- `phase-2`
- `phase-3`
- `phase-4`
- `fix-fix_name`

### 9.3 Commits

- Commit by atomic task or a small set of tightly related tasks.
- Commit messages should clearly state the task and reason.
- Large mixed commits are discouraged.

### 9.4 Merge Rule

- Merge to `master` only after Ahmad confirms deliverables and fixes.
- Architecture-sensitive changes should be reviewed before merge.

---

## 10. Documentation and Commenting Law

- Use docstrings for classes, operation methods, and non-trivial utilities.
- Comments must explain why, not repeat what the code already says.
- Use clear section headers where they improve readability in large files.

Preferred section styles:
- Python or Bash: `# -- Section Name --`
- HTML: `<!-- -- Section Name -- -->`
- CSS or JS: `/* -- Section Name -- */`

---

## 11. Project Modules and Domain Scope

The project should be organized around these major domains:

### 11.1 Foundation

- core project configuration
- utilities
- environment setup
- test framework
- infrastructure bootstrap

### 11.2 Identity

- custom `Employee`
- authentication
- admin integration
- technical and business account separation

### 11.3 IAM and Security

- `Department`
- `Role`
- `Policy`
- permission mixins
- operation-level policy enforcement

### 11.4 Inventory

- `Category`
- `Product`
- stock ledger
- stock adjustment logic
- WAC valuation engine

### 11.5 Sales and CRM

- `Customer`
- `SalesOrder`
- `SalesOrderItem`
- totals calculation
- order confirmation and stock deduction

### 11.6 Purchasing

- `Supplier`
- `PurchaseOrder`
- `PurchaseOrderItem`
- stock receipt and cost update

### 11.7 Frontend Foundation

- layouts
- atoms
- shared components
- HTMX partials
- dashboard and module pages

### 11.8 Async and Reporting

- Celery task execution
- background document generation
- reporting workflows
- progress feedback patterns

---

## 12. Project Roadmap Law

The roadmap below remains part of project law because this project is being built in deliberate phases, not ad hoc feature drift.

### Phase 1: Foundation, Automation & Local Scaffolding

Goal:
- initialize the project professionally,
- build the utility scripts,
- and establish a reproducible local environment.

Required outcomes:
- `utils/` is in place
- virtual environment workflow is defined
- dependencies are locked
- quality tooling is configured
- Django project and `core` app scaffolding exist
- settings are environment-aware

### Phase 2: Infrastructure & Core Identity

Goal:
- establish Docker-backed services and the custom `Employee` identity system.

Required outcomes:
- PostgreSQL and Redis are available
- `Employee` is active as the user model
- login/logout and admin support are working

### Phase 3: IAM & Security Framework

Goal:
- implement reusable policy-based authorization and centralized audit foundations.

Required outcomes:
- department, role, and policy models exist
- policy checks are reusable in Python
- base operation security rules are enforced
- activity logging foundation exists

### Phase 4: Inventory Architecture & Valuation

Goal:
- build the product catalog, stock ledger, and weighted average cost engine.

Required outcomes:
- category and product architecture exist
- stock transactions are recorded
- WAC recalculation is implemented
- stock changes are atomic and concurrency-safe
- inventory history is visible and auditable

### Phase 5: Sales & CRM Workflows

Goal:
- implement customer management and atomic sales order workflows.

Required outcomes:
- customer records exist
- sales orders and order items exist
- snapshot pricing is preserved
- order confirmation drives stock deduction through operations

### Phase 6: Purchasing & Procurement

Goal:
- implement supplier workflows and stock receiving.

Required outcomes:
- supplier and purchase order models exist
- receiving stock updates quantity and valuation correctly

### Phase 7: Frontend Foundation & HTMX UI

Goal:
- build reusable UI structure and consistent dynamic interactions.

Required outcomes:
- base layouts exist
- shared atoms and components exist
- HTMX modal and fragment patterns are established
- responsive behavior is considered

### Phase 8: Async Tasks, Reporting & Hardening

Goal:
- finalize background processing, reporting, and performance hardening.

Required outcomes:
- Celery is operational
- long-running tasks can execute asynchronously
- reporting workflows are available
- obvious query inefficiencies are reviewed
- production packaging is prepared

---

## 13. Required Implementation Standards by Domain

### 13.1 Inventory

- `Product.current_stock` must be treated as a controlled field, not casually edited from arbitrary code paths.
- Stock movement should be represented by a transaction ledger, not only by direct field mutation.
- WAC formula must be implemented deterministically and tested.

### 13.2 Sales

- Order confirmation must be an operation, not a view-side shortcut.
- Sales order item pricing must preserve snapshot values at time of order.

### 13.3 Purchasing

- Stock receiving must be the authoritative point for purchase-driven stock increases.
- Valuation updates must happen through receiving logic, not through disconnected side effects.

### 13.4 IAM

- Every protected workflow must be capable of policy validation before execution.
- Do not hardcode permission decisions in many unrelated places.

---

## 14. Testing and Verification Law

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

## 15. Final Rule

If an AI CLI tool produces output that is generic, vague, not tied to AMW Django ERP, or disconnected from the phases and modules defined here, that output is not compliant with project law.

This project requires concrete, phase-aware, architecture-aware execution.

---

*Project Law Version: 1.0*
