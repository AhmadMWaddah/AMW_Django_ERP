# AMW Django ERP - Phase Execution Plan: Phase 2

## 1. Document Purpose

This file is the working execution plan for Phase 2: Infrastructure & Core Identity.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 2`
- **Phase Name:** `Infrastructure & Core Identity`
- **Branch Name:** `phase-2`
- **Status:** `Planned`
- **Primary Goal:** `Establish Docker-backed services (PostgreSQL, Redis) and implement the custom Employee model.`
- **Depends On:** `Phase 1`
- **Manager Approval Required:** `Yes`

---

## 3. Phase Scope

### In Scope

- Docker Compose configuration for PostgreSQL and Redis
- Database connection settings in Django
- Custom `Employee` model extending `AbstractBaseUser`
- Admin integration for `Employee`
- Login and Logout functionality foundations

### Out of Scope

- Department, Role, or Policy logic - Deferred to Phase 3
- Business operations - Deferred to Phase 4+

### Required Outcomes

- PostgreSQL and Redis services running in Docker
- `Employee` model active and usable as the primary User model
- Django migrations successfully applied for custom user
- Basic authentication flows working

---

## 4. Constitutional Alignment

### Mandatory Checks

- `Employee` must be the identity anchor (Section 6.2)
- Environment-sensitive credentials must be managed via `.env`
- State changes remain atomic
- Template and static structure must follow Constitution Sections 7.2 and 7.3 even in early phases

### Notes for This Phase

- Implementing the custom user model must be done *before* applying standard Django migrations to avoid complex migration conflicts. This is a critical constitutional step.
- The `accounts` app must render through centralized root templates and extend `templates/layouts/base.html`.
- Reusable login form inputs must use shared fragments from `templates/_snipps_/`.
- Frontend cross-review rule: backend-delivered templates that use inline styles or bypass the centralized hierarchy must be rejected and corrected before acceptance.

---

## 5. Architecture Targets

### Modules / Apps Affected

- `core`
- `accounts` / `identity` (new app)
- `config`

### Main Files or Areas Expected

- `docker-compose.yml`
- `accounts/models.py` (Employee)
- `config/settings/base.py` (AUTH_USER_MODEL)
- `.env` (DB credentials)

### Data Model Impact

- `Employee`: `id`, `email`, `first_name`, `last_name`, `is_active`, `is_staff`, `date_joined`.

### Operational Impact

- `None` (focus is on identity scaffolding).

### UI / Template Impact

- `Authentication pages must use centralized root templates and static assets.`

### Infrastructure Impact

- PostgreSQL and Redis instances.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will first spin up the infrastructure (PostgreSQL) using Docker to ensure we have a persistent data store. Then, we will implement the `Employee` model and point Django to it using `AUTH_USER_MODEL` before any database migrations are run. This ensures a clean identity foundation.

### Sequencing Rule

1. Docker infrastructure (PostgreSQL, Redis)
2. Database settings configuration
3. `Employee` model implementation in new `accounts` app
4. Migration and superuser creation
5. Centralized template shell scaffolding for Phase 2 auth pages
6. Basic authentication testing (Login/Logout)

---

## 7. Parts Breakdown

### Part 1: Infrastructure Setup

- **Goal:** `Deploy supporting services via Docker.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `✅ Complete`

#### Tasks

1. **Task 2.1:** `Create docker-compose.yml for PostgreSQL and Redis`
   - Output: `Working docker-compose file`
   - Verification: `Run docker-compose up -d and confirm services are healthy`

2. **Task 2.2:** `Update config/settings/dev.py to use PostgreSQL`
   - Output: `Settings using psycopg2 and Docker-based DB`
   - Verification: `Confirm DB connection from Django shell`

### Part 2: Custom Identity

- **Goal:** `Establish the Employee model as the project's identity anchor.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `✅ Complete`

#### Tasks

1. **Task 2.3:** `Implement Employee model in accounts/`
   - Output: `Custom AbstractBaseUser implementation`
   - Verification: `Verify model definition matches Constitution Section 6.2`

2. **Task 2.4:** `Configure AUTH_USER_MODEL and run migrations`
   - Output: `Database schema with custom employee table`
   - Verification: `Create a superuser and log into Django admin`

### Part 3: Shared Template Shells

- **Goal:** `Establish the root template/static hierarchy required for Phase 2 authentication pages.`
- **Owner:** `Cod (Frontend AI)`
- **Status:** `✅ Complete`

#### Tasks

1. **Task 2.5:** `Create layouts/base.html and layouts/dashboard.html shells`
   - Output: `Centralized layout templates in templates/layouts/`
   - Verification: `Accounts pages extend layouts/base.html or layouts/dashboard.html`

2. **Task 2.6:** `Create reusable input fragment in templates/_snipps_/_input_.html`
   - Output: `Reusable input atom for login and future forms`
   - Verification: `Login page renders email/password inputs via shared snippet`

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `Identity tests: Create employee, verify email uniqueness`
- `Infrastructure tests: Verify data persistence after Docker restart`

### Manual Verification

- `Login to admin panel with superuser credentials`

---

## 10. Risks and Controls

### Known Risks

- `Migration conflicts when switching to custom User model mid-project`
- `Docker connectivity issues on certain OS versions`

### Controls / Mitigations

- `Implement custom user early (Phase 2) before extensive model development`
- `Use standard official Docker images (e.g., postgres:15-alpine)`

---

## 11. Open Questions

- `Should we use UUIDs or Integers for Employee IDs?`

---

## 12. Completion Checklist

- [x] PostgreSQL and Redis are available
- [x] `Employee` is active as the user model
- [x] Login/logout and admin support are working
- [x] No unexplained tracebacks

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 2 plan for infrastructure and identity.`
- `2026-03-28` - `Implemented` - `Created accounts app with custom Employee model, authentication views, admin integration, and AUTH_USER_MODEL wiring.`
- `2026-03-28` - `Implemented` - `Verified PostgreSQL and Redis Docker infrastructure using project ports 5433 and 6380 to avoid host conflicts.`
- `2026-03-28` - `Implemented` - `Established centralized template and static buckets in the project root and moved Phase 2 auth pages onto layouts/snippets without inline styles.`
- `2026-03-28` - `Hardened` - `Secured login next-parameter handling with allowed-host validation to prevent open redirects.`
- `2026-03-28` - `Hardened` - `Updated authentication redirects to use namespaced accounts URLs consistently.`
- `2026-03-28` - `Tested` - `Added Phase 2 identity tests covering employee creation, email uniqueness, superuser flags, and login/logout flow.`
- `2026-03-28` - `Verified` - `./utils/test_suite_runner.sh passes with 15 tests.`
- `2026-03-28` - `Verified` - `./utils/test_suite_runner.sh lint passes.`
- `2026-03-28` - `✅ COMPLETE` - `Phase 2 accepted after Cod review and remediation of security, navigation, and testing gaps.`

---

## 14. Final Summary

**Phase 2 is COMPLETE.**

### Delivered:
- ✅ Docker services: PostgreSQL (port 5433), Redis (port 6380)
- ✅ `accounts` app with custom `Employee` model
- ✅ `Employee` extends `AbstractBaseUser` with email authentication
- ✅ `AUTH_USER_MODEL = 'accounts.Employee'` configured
- ✅ Admin integration for Employee management
- ✅ Authentication views: login, logout, dashboard
- ✅ Secure login redirect handling with validated next URLs
- ✅ Namespaced auth navigation fixed
- ✅ Identity and authentication tests implemented
- ✅ Database migrations applied successfully
- ✅ Superuser created: `admin@amw-erp.local`

### Access:
- **Login:** http://localhost:8010/accounts/login/
- **Admin:** http://localhost:8010/admin/
- **Dashboard:** http://localhost:8010/accounts/dashboard/

**Ready for Phase 3: IAM & Security Framework**
