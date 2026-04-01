# AMW Django ERP - Phase Execution Plan: Phase 3

## 1. Document Purpose

This file is the working execution plan for Phase 3: IAM & Security Framework.

It must be used together with:
- `Constitution_AMW_DJ_ERP.md`
- the current repository state
- Ahmad's latest instructions for the phase

---

## 2. Phase Identity

- **Phase Number:** `Phase 3`
- **Phase Name:** `IAM & Security Framework`
- **Branch Name:** `phase-3`
- **Status:** ✅ **COMPLETE**
- **Primary Goal:** `Implement a policy-based authorization system and a centralized audit logging engine.`
- **Depends On:** `Phase 2`
- **Manager Approval Required:** `Yes`

---

## 3. Phase Scope

### In Scope

- `Department`, `Role`, and `Policy` models ✅
- Policy check utility (Python-first, Section 6.3) ✅
- Global `AuditLog` model and operation decorator ✅
- Integration of IAM rules into the custom `Employee` model ✅

### Out of Scope

- Specific inventory policies - Deferred to Phase 4
- Specific sales policies - Deferred to Phase 5
- Frontend UI for IAM - Deferred to Phase 7

### Required Outcomes

- Functional security hierarchy (Employee -> Department -> Role -> Policies) ✅
- Reusable policy enforcement mechanism in Python ✅
- Centralized audit record capture for state changes ✅
- Base operation security rules enforced at the logic layer ✅

---

## 4. Constitutional Alignment

### Mandatory Checks

- Policy checks must be reusable from Python (Section 6.3) ✅
- Access control must not exist *only* in templates or view decorators ✅
- Audit records must capture actor, action, target, and timestamp (Section 6.7) ✅

### Notes for This Phase

- This phase defines how *every* future operation will be secured. It must be robust and easy for other developers (Qwen, Cod) to use.

---

## 5. Architecture Targets

### Modules / Apps Affected

- `accounts` (Employee enhancements)
- `security` (Implemented as security app)
- `audit` (New app)

### Main Files or Areas Expected

- `security/models.py` (Department, Role, Policy) ✅
- `security/logic/enforcement.py` (The check engine) ✅
- `audit/models.py` (AuditLog) ✅
- `audit/logic/logging.py` (The logger engine) ✅

### Data Model Impact

- `Department`: `name`, `slug`, `parent` ✅
- `Role`: `name`, `department`, `policies` ✅
- `Policy`: `name`, `slug`, `resource`, `action`, `effect` (Allow/Deny) ✅
- `AuditLog`: `actor`, `action_code`, `content_type`, `object_id`, `before_data`, `after_data` ✅

### Operational Impact

- Every business operation must now involve a policy check. ✅

---

## 6. Implementation Strategy

### Phase Strategy Summary

We will build the IAM models first to establish the hierarchy. Then, we will develop a Python-centric enforcement engine (mixins or decorators) that can be used inside `operations/` modules. Simultaneously, we will implement the `AuditLog` model and a consistent way to record changes before/after they happen in the operation layer.

### Sequencing Rule

1. IAM models (Department, Role, Policy) ✅
2. Policy enforcement engine (the "Check" logic) ✅
3. Audit model and foundational logging logic ✅
4. Integration with existing `Employee` model ✅
5. Verification of policy-based blocking/allowing ✅

---

## 7. Parts Breakdown

### Part 1: IAM Foundations

- **Goal:** `Establish the model hierarchy for departments, roles, and policies.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 3.1:** `Implement Department, Role, and Policy models in security/`
   - Output: `Models with appropriate relationships` ✅
   - Verification: `Run tests: verify employee -> role -> policy traversal` ✅

2. **Task 3.2:** `Create policy check engine (Python helper)`
   - Output: `Function: employee_has_policy(employee, policy_code)` ✅
   - Verification: `Unit test for various permission scenarios` ✅

### Part 2: Audit Engine

- **Goal:** `Create a central repository for business-critical activity logs.`
- **Owner:** `Gem (Consultant AI)`
- **Status:** ✅ **COMPLETE**

#### Tasks

1. **Task 3.3:** `Implement AuditLog model in audit/`
   - Output: `AuditLog model with JSONFields for change tracking` ✅
   - Verification: `Run migrations and verify model structure` ✅

2. **Task 3.4:** `Create operation logging decorator/utility`
   - Output: `Utility to log state changes in an atomic transaction` ✅
   - Verification: `Verify log creation after a mock state-changing operation` ✅

---

## 8. Task Writing Rules

(Adhering to standard rules from template...)

---

## 9. Verification Plan

### Required Tests

- `IAM traversal: Employee -> Role -> Policy check` ✅
- `Audit capture: verify 'before' and 'after' snapshots in log` ✅

### Manual Verification

- `Confirm that an employee without a policy is blocked from a mock operation` ✅

---

## 10. Risks and Controls

### Known Risks

- `Performance overhead of frequent policy checks`
- `Complexity in tracking many 'before'/'after' changes in audit logs`

### Controls / Mitigations

- `Implement simple caching for policy lookups` ✅
- `Focus audit logging only on business-critical state changes, not minor field updates` ✅

---

## 11. Open Questions

- `Do we need hierarchical policies (parent/child roles)?` -> Implemented basic hierarchy in Departments.

---

## 12. Completion Checklist

- [x] Department, Role, and Policy models exist
- [x] Policy checks are reusable in Python
- [x] Centralized audit foundation exists
- [x] Access control is not limited to templates
- [x] Email normalization properly fixed
- [x] CI/CD pipeline hardened

---

## 13. Execution Log

- `2026-03-28` - `Planned` - `Initialized Phase 3 plan for IAM and security.`
- `2026-03-30` - ✅ **COMPLETE** - `Phase 3 finalized, verified, and ready for merge.`

---

## 14. Final Summary

Phase 3 has successfully established the security and audit backbone of AMW Django ERP. All critical logic is now protected by policy enforcement, and every state change is traceable through the audit log. The system is now ready for Phase 4 (Inventory).
