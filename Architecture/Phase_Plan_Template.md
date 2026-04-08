# AMW Django ERP - Phase Execution Plan Template

## 1. Document Purpose

This file is the reusable execution template for a single project phase.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

This file is not project law. It is the working execution plan for one phase.

---

## 2. Phase Identity

- **Phase Number:** `Phase X`
- **Phase Name:** `Replace With Phase Name`
- **Branch Name:** `phase-x`
- **Status:** `Planned | In Progress | Blocked | Complete`
- **Primary Goal:** `Write the main objective of this phase`
- **Depends On:** `List earlier phases or prerequisites`
- **Manager Approval Required:** `Yes / No`

---

## 3. Phase Scope

### In Scope

- `List the features, modules, or deliverables that belong in this phase`
- `Keep this concrete and phase-specific`

### Out of Scope

- `List what must not be done in this phase`
- `Use this to prevent phase drift`

### Required Outcomes

- `State what must exist by the end of the phase`
- `Focus on business and architectural outcomes`

---

## 4. Constitutional Alignment

The AI tool executing this phase must confirm alignment with the constitution before coding.

### Mandatory Checks

- Business logic remains in `operations/` modules where applicable
- Identity and IAM rules are respected
- HTMX-first frontend rule is respected where frontend work exists
- Critical state changes remain atomic and auditable
- Work is done sequentially and does not skip ahead without approval

### Notes for This Phase

- `Write phase-specific constitutional concerns here`
- `Example: this phase introduces stock changes, so transaction safety is mandatory`

---

## 5. Architecture Targets

### Modules / Apps Affected

- `core`
- `replace or add actual apps`

### Main Files or Areas Expected

- `app/models.py`
- `app/operations/`
- `templates/...`
- `static/...`
- `utils/...`

### Data Model Impact

- `List models to add or change`
- `List constraints, relationships, or deletion strategy notes`

### Operational Impact

- `List operations to add or modify`
- `Describe the business actions these operations represent`

### UI / Template Impact

- `List pages, fragments, modals, dashboards, or partials involved`

### Infrastructure Impact

- `List env, Docker, Celery, Redis, CI, scripts, or deployment changes if any`

---

## 6. Implementation Strategy

### Phase Strategy Summary

`Explain how this phase should be executed in 3-8 lines.`

Guidance:
- start with foundations before UI,
- build models before operations,
- build operations before views,
- and build tests alongside critical logic.

### Sequencing Rule

Work in this order unless there is a justified reason not to:
1. foundations and scaffolding
2. models and data rules
3. operations and business logic
4. views, templates, and UI behavior
5. tests and verification hardening
6. documentation and cleanup

---

## 7. Parts Breakdown

Each phase must be broken into parts. Each part must have a focused purpose.

### Part 1: `Replace With Part Name`

- **Goal:** `Describe the purpose of this part`
- **Owner:** `AI Tool / Person`
- **Status:** `Planned | In Progress | Blocked | Complete`
- **Dependencies:** `List dependencies if any`

#### Tasks

1. **Task X.1:** `Describe one atomic task`
   - Output: `What should exist after completion`
   - Verification: `How it will be checked`

2. **Task X.2:** `Describe one atomic task`
   - Output: `What should exist after completion`
   - Verification: `How it will be checked`

### Part 2: `Replace With Part Name`

- **Goal:** `Describe the purpose of this part`
- **Owner:** `AI Tool / Person`
- **Status:** `Planned | In Progress | Blocked | Complete`
- **Dependencies:** `List dependencies if any`

#### Tasks

1. **Task X.1:** `Describe one atomic task`
   - Output: `What should exist after completion`
   - Verification: `How it will be checked`

2. **Task X.2:** `Describe one atomic task`
   - Output: `What should exist after completion`
   - Verification: `How it will be checked`

Add more parts as needed. Keep tasks atomic. Avoid mixing unrelated work in one task.

---

## 8. Task Writing Rules

Every task in this file should follow these rules:

### General Rules
- One task should represent one clear outcome
- Tasks should be small enough to implement and verify cleanly
- Tasks should not mix backend, frontend, infra, and refactor work without a reason
- Each task should name the affected domain clearly
- Each task should include a verification method
- If a task changes business rules, tests are required

### Git Workflow
All git workflow rules (branch naming, commit format, merging, tagging) are defined in the **Constitution Section 6-7** only. Refer to `Constitution_AMW_DJ_ERP.md` for the authoritative specification.

### Task Examples

**Bad task example:**
- "Build inventory system"

**Good task example:**
- "Create `StockTransaction` model with movement type, quantity, employee, and timestamp fields"

---

## 9. Verification Plan

### Required Tests

- `List specific test modules or behaviors to validate`
- `Example: stock valuation recalculation`
- `Example: policy enforcement on protected operation`

### Manual Verification

- `List runtime or UI checks if needed`
- `Example: modal loads correctly through HTMX`

### Clean Execution Checks

- no unexplained tracebacks
- no debug prints
- no ignored failing tests
- no silent permission bypasses

---

## 10. Risks and Controls

### Known Risks

- `List technical or business risks`
- `Example: concurrent stock updates`
- `Example: incorrect WAC rounding`

### Controls / Mitigations

- `List how each risk is reduced`
- `Example: transaction.atomic + select_for_update`

---

## 11. Open Questions

- `List unresolved decisions that need Ahmad or architecture review`
- `Do not let open questions stay hidden during implementation`

---

## 12. Completion Checklist

A phase is complete only when all applicable items below are true:

- [ ] In-scope tasks are implemented
- [ ] Required tests are present
- [ ] Relevant tests pass
- [ ] Architecture remains aligned with the constitution
- [ ] Documentation and comments are updated where needed
- [ ] No unexplained warnings or debug noise remain
- [ ] Ahmad approval is recorded if required

---

## 13. Execution Log

Use this section while the phase is active.

### Entries

- `YYYY-MM-DD` - `Planned / Started / Updated / Blocked / Completed` - `Short factual note`

Example:
- `2026-03-27` - `Started` - `Initialized inventory phase plan and confirmed model-first execution order`

---

## 14. Final Summary

Fill this only when the phase is complete.

- **What Was Delivered:** `Short summary`
- **What Changed Architecturally:** `Short summary`
- **What Was Deferred:** `List deferred items`
- **Approval Status:** `Approved / Pending`

---

*Template Version: 11.0*
