# AMW Django ERP - Phase Execution Plan: Phase 1

## 1. Document Purpose

This file is the working execution plan for Phase 1: Foundation, Automation & Local Scaffolding.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 1`
- **Phase Name:** `Foundation, Automation & Local Scaffolding`
- **Branch Name:** `phase-1`
- **Status:** `✅ COMPLETE`
- **Primary Goal:** `Establish a professional, reproducible local development environment with official utility scripts and Django core scaffolding.`
- **Depends On:** `None`
- **Manager Approval Required:** `Yes`
- **Completion Date:** `2026-03-28`

---

## 3. Phase Scope

### In Scope

- Creation of `utils/` scripts (`git_task_commit.sh`, `env_factory.sh`, etc.)
- Virtual environment setup (`.env_amw_dj_erp/`)
- Dependency management (initially `requirements.txt` or `pyproject.toml`)
- Quality tooling configuration (`pytest`, `ruff`/`flake8`, `black`/`prettier`)
- Django project initialization and `core` app scaffolding
- Environment-aware settings architecture (`base.py`, `dev.py`, `prod.py`)

### Out of Scope

- Infrastructure setup (Docker, Redis, etc.) - Deferred to Phase 2
- Custom `Employee` model - Deferred to Phase 2
- IAM or business logic - Deferred to Phase 3/4

### Required Outcomes

- Functional `utils/` directory with mandatory scripts
- Active and reproducible virtual environment workflow
- Documented dependency locking mechanism
- Working Django project with environment-aware settings
- Base `core` app created for shared utilities and foundations

---

## 4. Constitutional Alignment

### Mandatory Checks

- No business logic in views/signals (even in foundations)
- Work is done sequentially and does not skip ahead
- Official project scripts are used for tasks where they exist

### Notes for This Phase

- This phase is about *enabling* the constitution. The utility scripts must enforce the standards (e.g., `git_task_commit.sh` ensuring atomic commits).

---

## 5. Architecture Targets

### Modules / Apps Affected

- `core` (newly created)
- `config` (project settings)

### Main Files or Areas Expected

- `utils/*.sh`
- `config/settings/`
- `requirements.txt` / `pyproject.toml`
- `.gitignore` (update)

### Data Model Impact

- `None` (standard Django models only if required for internal settings)

### Operational Impact

- `None` (foundational scripts only)

### UI / Template Impact

- `None` (frontend begins in Phase 7)

### Infrastructure Impact

- `env_factory.sh` will manage the local Python environment.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will build the automation tools first to ensure that every subsequent step is tracked and committed according to project law. We will then establish the environment and initialize the Django project with a clean, split-settings architecture.

### Sequencing Rule

1. Foundational `utils/` scripts (Commit tools first)
2. Environment factory and dependency locking
3. Django project initialization and split settings
4. `core` app scaffolding
5. Verification of environment repeatability

---

## 7. Parts Breakdown

### Part 1: Utility & Automation Scaffolding

- **Goal:** `Build the mandatory scripts listed in the Constitution.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `✅ Complete`

#### Tasks

1. **Task 1.1:** `Create git_task_commit.sh in utils/`
   - Output: `Executable script for atomic task-based commits`
   - Verification: `Run a test commit using the script`

2. **Task 1.2:** `Create env_factory.sh in utils/`
   - Output: `Script to build and rebuild the .env_amw_dj_erp/ environment`
   - Verification: `Execute and confirm environment creation`

### Part 2: Django Project Initialization

- **Goal:** `Initialize Django with environment-aware settings.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `✅ Complete`

#### Tasks

1. **Task 2.1:** `Initialize Django project structure with split settings`
   - Output: `Project files in place with config/settings/{base,dev,prod}.py`
   - Verification: `Run python manage.py check --settings=config.settings.dev`

2. **Task 2.2:** `Create core app and register it`
   - Output: `core app directory and registration in INSTALLED_APPS`
   - Verification: `Verify core app exists and is recognized`

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `Check for existence and executability of all utils/ scripts`
- `Verify environment-aware settings load correctly for dev environment`

### Manual Verification

- `Confirm .env_amw_dj_erp/ is correctly isolated and ignored by git`

---

## 10. Risks and Controls

### Known Risks

- `Environment mismatch between local dev and scripts`
- `Complexity in split settings early on`

### Controls / Mitigations

- `Use env_factory.sh as the single source of truth for environment creation`
- `Document settings hierarchy clearly in base.py`

---

## 11. Open Questions

- `Should we use pyproject.toml (modern) or requirements.txt (standard)?`

---

## 12. Completion Checklist

- [x] In-scope tasks are implemented
- [x] Required tests are present
- [x] Relevant tests pass
- [x] Architecture remains aligned with the constitution
- [x] Ahmad approval is recorded if required

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 1 plan based on constitutional roadmap.`
- `2026-03-28` - `Implemented` - `Created official utility scripts in utils/ for environment setup, testing, database operations, infrastructure management, and task-based commits.`
- `2026-03-28` - `Implemented` - `Initialized Django project scaffolding with split settings in config/settings/{base,dev,prod}.py and registered the core app.`
- `2026-03-28` - `Implemented` - `Added core foundational models and health/error handling scaffold in the core app.`
- `2026-03-28` - `Verified` - `Django development settings check passed via python manage.py check --settings=config.settings.dev.`
- `2026-03-28` - `Verified` - `Project linting passed via ./utils/test_suite_runner.sh lint.`
- `2026-03-28` - `Verified` - `Phase 1 test suite passed via ./utils/test_suite_runner.sh with 8 tests passing.`
- `2026-03-28` - `Verified` - `Production deploy check executed successfully via python manage.py check --deploy --settings=config.settings.prod with only the expected weak local secret key warning.`
- `2026-03-28` - `Hardened` - `Updated git_task_commit.sh to require a real Git repository and commit staged changes only.`
- `2026-03-28` - `Hardened` - `Updated env_factory.sh with setup and init-git bootstrap commands.`
- `2026-03-28` - `Hardened` - `Updated test_suite_runner.sh to use the virtual environment toolchain directly and export DJANGO_SETTINGS_MODULE instead of relying on pytest CLI plugin flags.`
- `2026-03-28` - `Hardened` - `Moved Docker host ports to PostgreSQL 5433 and Redis 6380 so the project can coexist with local services already using 5432/6379.`
- `2026-03-28` - `Hardened` - `Registered Django Debug Toolbar URLs in config/urls.py to fix the djdt namespace error during development.`
- `2026-03-28` - `Consolidated` - `Removed redundant root-level Phase 1 completion files and merged the final completion record into this architecture document.`
- `2026-03-28` - `✅ COMPLETE` - `Phase 1 accepted as complete after Cod review, script hardening, documentation consolidation, and final verification.`

---

## 14. Final Summary

**Phase 1 is complete and approved for transition to Phase 2.**

### Delivered

- `utils/` now contains the official project scripts:
  - `git_task_commit.sh`
  - `env_factory.sh`
  - `test_suite_runner.sh`
  - `db_manage_dev.sh`
  - `infra_manage.sh`
- Django project scaffolding exists with split settings in `config/settings/`.
- The `core` app is present and registered, with foundational models and basic health/error handling.
- Quality tooling is configured in `pyproject.toml`.
- Docker and local environment bootstrap files are present (`docker-compose.yml`, `Dockerfile`, `.env.example`).
- PostgreSQL is explicitly enforced as the mandatory database engine in base settings.

### Verification Outcome

- `./utils/test_suite_runner.sh lint` passes.
- `./utils/test_suite_runner.sh` passes.
- `python manage.py check --settings=config.settings.dev` passes.
- `python manage.py check --deploy --settings=config.settings.prod` runs successfully.
- The only remaining deploy warning is that the local secret key in `.env` should be replaced with a stronger value before real production use.

### Closeout Notes

- Phase 1 documentation has been consolidated into this official phase plan instead of separate root-level completion files.
- The project is ready to proceed to `Phase 2: Infrastructure & Core Identity`.
