# AMW Django ERP - Phase Execution Plan: Phase 8

## 1. Document Purpose

This file is the working execution plan for Phase 8: Async Tasks, Reporting & Hardening.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 8`
- **Phase Name:** `Async Tasks, Reporting & Hardening`
- **Branch Name:** `phase-8`
- **Status:** `Planned`
- **Primary Goal:** `Finalize asynchronous processing, reporting workflows, and system-wide performance hardening.`
- **Depends On:** `Phase 7`
- **Manager Approval Required:** `Yes`

---

## 3. Phase Scope

### In Scope

- Celery and Redis integration for async tasks
- Background reporting (Inventory valuation report, Sales summary)
- Performance review (N+1 query identification and optimization)
- Logging and monitoring foundations
- Production-ready packaging (Gunicorn/WhiteNoise/Docker settings)

### Out of Scope

- Real-time WebSocket notifications - (Optional/Deferred)
- External BI tool integrations - (Deferred)

### Required Outcomes

- Celery worker and beat operational in Docker
- Asynchronous document/report generation
- Optimized database queries for core workflows
- Comprehensive logging and error tracking
- Production settings locked and verified

---

## 4. Constitutional Alignment

### Mandatory Checks

- Performance hardening must not obscure business logic visibility
- Reporting must align with the "Architecture targets" (Section 11.8)
- Audit logs remain the source of truth for all historical reports

### Notes for This Phase

- Hardening is not just about speed; it's about reliability. Ensuring that background tasks have retry logic and proper failure logging is essential project law.

---

## 5. Architecture Targets

### Modules / Apps Affected

- `reporting` (new app)
- `config` (production settings)
- All existing apps (for optimization)

### Main Files or Areas Expected

- `celery.py` (Project-level config)
- `reporting/tasks.py` (Background report logic)
- `config/settings/prod.py` (Hardened settings)

### Data Model Impact

- `ReportJob`: `actor`, `type`, `status`, `result_file`, `created_at`

### Operational Impact

- Long-running tasks (e.g., month-end inventory valuation) move to the background.

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will first integrate Celery with the existing Redis instance. Then, we will build a dedicated `reporting` app that uses Celery to generate heavy business reports without blocking the user interface. Simultaneously, we will perform a system-wide audit of database queries to ensure the ERP remains fast as data grows. Finally, we will lock down production-ready configurations.

### Sequencing Rule

1. Celery and Redis configuration
2. Reporting app and background task logic
3. Performance audit and query optimization (select_related/prefetch_related)
4. Logging and monitoring setup
5. Production settings and container hardening

---

## 7. Parts Breakdown

### Part 1: Asynchronous Processing

- **Goal:** `Offload heavy work to background workers.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 8.1:** `Configure Celery and Redis in Docker`
   - Output: `Working Celery worker and beat services`
   - Verification: `Run a mock task and confirm execution in logs`

2. **Task 8.2:** `Implement background report generation`
   - Output: `Reporting app that generates CSV/PDF reports asynchronously`
   - Verification: `User triggers report and gets notified when it's ready`

### Part 2: Hardening & Optimization

- **Goal:** `Prepare the system for real-world load.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** `Planned`

#### Tasks

1. **Task 8.3:** `Query optimization audit`
   - Output: `Refactored views/operations with optimized ORM calls`
   - Verification: `Compare query counts before and after refactoring using django-debug-toolbar`

2. **Task 8.4:** `Production settings lockdown`
   - Output: `Hardened prod.py with secure headers and environment variables`
   - Verification: `Run python manage.py check --deploy`

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `Async reliability: Verify task retries on failure`
- `Optimization check: Ensure no dashboard page exceeds 50 queries`
- `Production check: Verify DEBUG=False behavior`

### Manual Verification

- `Confirm that long-running reports do not block the main UI thread`

---

## 10. Risks and Controls

### Known Risks

- `Stale data in background reports`
- `Redis memory exhaustion during heavy task loads`

### Controls / Mitigations

- `Timestamp reports clearly and include the data cutoff point`
- `Configure Redis memory eviction policies and monitor worker queues`

---

## 11. Open Questions

- `Do we need a dedicated storage bucket (e.g., S3) for generated reports?`

---

## 12. Completion Checklist

- [ ] Celery and Redis are fully operational
- [ ] Reporting workflows generate documents asynchronously
- [ ] Core queries are optimized for performance
- [ ] Production settings are secured and verified
- [ ] No unexplained debug noise remains

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 8 plan for Async Tasks and Hardening.`

---

## 14. Final Summary

(TBD)
