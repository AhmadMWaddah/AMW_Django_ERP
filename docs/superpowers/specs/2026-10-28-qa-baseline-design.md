# QA Baseline Verification & Fixes — Design Spec

**Branch:** `Fix-QA-Baseline` (from master `ee9c830`, already checked out)
**Date:** 2026-10-28
**Owner:** Ahmad · **Status:** Approved (brainstorm decisions locked)

---

## 1. Goal

Establish a verifiably true quality baseline for AMW Django ERP on this machine so the Owner can point a prospective employer at a repo whose claims ("228 tests passing", clean lint, green Django check) are demonstrably correct right here, not just somewhere. This is a QA-verification-and-fixes task: run the full verification stack, fix every failure at root cause, commit fixes per-area, and re-run until 100% clean.

## 2. In Scope

- Full verification run on this machine:
  - `pytest` (settings: `config.settings.dev`, per `pyproject.toml`)
  - `ruff check .` (venv `.env_amw_erp` excluded via pyproject config — confirmed present)
  - `black --check .` (same exclusion)
  - `python manage.py check` with default settings (`config.settings.dev` per `manage.py`)
- Root-cause analysis of every failure, then fixes to code and/or tests (whichever is actually wrong).
- Pushing branch `Fix-QA-Baseline` to GitHub origin.
- Recording evidence (commands + results) in the implementation plan's verification log.
- Housekeeping within the already-cleaned working tree: resolve the residual `.gitignore` mode change (`100644 → 100755`) back to git baseline; keep the intentional added ignore line `Mock Agent.md`; leave `SAST-SCA_Report_AMW_Django_ERP_2026-04-28.docx` untracked.
- Establishing the actual interpreter/toolchain first: AGENTS.md names venv `.env_amw_erp/`, which does not exist at repo root today; global `pytest`, `ruff`, `black` resolve at `~/.local/bin/`. The plan must confirm the working interpreter before trusting any verification result.

## 3. Out of Scope (Non-Goals)

- **Deployment work of any kind.** OCI VM hosting, external/static Postgres, Celery-in-production, prod settings hardening, demo-data seeding for deployment — all of these are being discussed in other sessions and MUST NOT be specced, planned, or implemented here.
- No merge to `master` and no tagging — that requires Owner approval per `Constitution/Orchestrator_Law.md` (Stage 8) and is explicitly out of scope.
- No changes to anything under `Constitution/`.
- No new features, no refactors unrelated to verification failures, no roadmap work.
- No weakening, skipping, or deletion of tests to make suites pass.
- No commits changing the claimed project facts in AGENTS.md (e.g., editing the 228-test claim) without actually producing a verified count.

## 4. Preconditions (verified at time of writing)

| Item | State |
|---|---|
| Branch | `Fix-QA-Baseline` checked out, HEAD `ee9c830` (= master) |
| Working tree | Cleaned: previously observed 238 chmod-mode diffs restored; remaining diffs are only the `.gitignore` content/mode state and the untracked SAST docx |
| `.gitignore` | Real diff is one added line `Mock Agent.md` plus residual mode change. (Note: brainstorm summary said `.sisyphus/`; that line is already committed upstream — the actual added line is `Mock Agent.md`. Spec follows the repository's observed state.) |
| Untracked file | `SAST-SCA_Report_AMW_Django_ERP_2026-04-28.docx` — stays untracked, never committed |
| Expected baseline | 228 tests passing per AGENTS.md — claim unverified as of this spec |
| Known tool hazard | `utils/test_suite_runner.sh` hardcodes `VENV_PATH=.env_amw_dj_erp` while AGENTS.md names `.env_amw_erp`; if the wrapper is used and fails on venv path, that itself is a QA finding to root-cause (fix the script or run tooling directly) |

## 5. Proposed Architecture (Decision Structure)

This is not a code-architecture change; the "architecture" here is the fix-decision discipline and commit structure.

### 5.1 Fix-Decision Rules (mandatory)

For every failure, in order:

1. **Root-cause first, per systematic-debugging discipline.** No fix before a written one-paragraph diagnosis: what fails, where, why. An "environment" diagnosis must be proven (missing migration path, absent dependency, wrong settings) rather than assumed.
2. **Fix code if the code is wrong.** A test failed, and the business behavior under test is incorrect or drifted: fix the implementation. Business rules stay in `operations/` modules; fixes respect `Architecture_Law.md` (atomic stock changes, WAC hooks, soft-delete inheritance, PolicyEngine authorization).
3. **Fix the test only if the test is wrong.** A test fails, implementation behavior is correct per project law, but the test asserts different or weaker behavior than intended: correct the test to assert the intended behavior, and say why in the commit description.
4. **Never disable to get green.** No `skip`, no `xfail`, no deletion, no commented-out tests as the fix. Skips introduced anywhere before this task are suspect and must be surfaced in the verification log.
5. **No silent drift.** If a fix seems to require changing a project law or a documented number (e.g., the 228 count in AGENTS.md), stop and state it to the Owner explicitly; do not edit law files.

### 5.2 Verification Loop

```
FULL BASELINE RUN (services up → pytest → ruff → black → manage.py check)
   → diagnose each failure (root cause)
   → fix per 5.1 (one concern per fix)
   → re-run the failing gate, then the full stack
   → repeat until all four gates green, no flakes on re-run
Max 5 full fix cycles; beyond that, escalate to Owner (Orchestrator_Law retry limits).
```

Services: tests may require PostgreSQL 15 and Redis 7. Check with `bash utils/infra_manage.sh status` and start them if needed before the first run; the infra step is part of PREPARE, not of the deliverable.

### 5.3 Commit Protocol

- Every fix committed via `bash utils/git_task_commit.sh "<Title>" "<Description>"` (multi-message format per `Constitution/Git_Law.md`).
- Title prefixes per `Constitution/Git_Law.md`: `Fix:` for code and housekeeping fixes, `Test:` for test corrections, `Docs:` for documentation updates where a fix is documented. Title < 72 chars. Description explains WHAT and WHY.
- One concern per commit; per-area commits where practical (e.g., an inventory fix separate from an IAM fix). The utility script's built-in lint gate runs local lint before each commit.
- Evidence of verification runs goes into the plan's verification log (staged alongside plan execution, not into repo docs).
- Push `Fix-QA-Baseline` to `origin` after commits are green: `git push -u origin Fix-QA-Baseline`.

## 6. Files To Change

Unknown until the first verification run — the failure inventory drives it. Expected candidates, based on repo facts:

| Likely file class | Why |
|---|---|
| `utils/test_suite_runner.sh` | Hardcoded venv path `.env_amw_dj_erp` may not match the machine's actual environment |
| Test files under each domain app | Failures surfaced by pytest; test corrections only where tests are wrong |
| `inventory/operations/`, `sales/operations/`, `purchasing/operations/` or adjacent code | Business-logic fixes if root cause is implementation drift |
| `.gitignore` | Restore mode to `100644` (content: keep `Mock Agent.md` line) |
| No changes anywhere under `Constitution/` | Hard constraint |

New files: none planned. If a verification-log evidence file is desired in-repo later, that is a plan-level choice, not a spec requirement.

## 7. Testing Strategy (Acceptance Criteria)

Definition of done — all must be empirically true at the end, from a fresh shell on this machine:

1. **Branch on origin:** branch `Fix-QA-Baseline` exists on GitHub (`git ls-remote --heads origin Fix-QA-Baseline` returns this branch) with all work pushed; local branch is not ahead of origin.
2. **pytest green:** `pytest` exits 0. The actual passing test count is recorded in the verification log (any difference from the AGENTS.md claim of 228 must be accounted for by test changes made during fixes and named in the log — never by unexplained drift).
3. **No flakes:** the suite passes again on one immediate re-run (same interpreter, same services).
4. **Lint clean:** `ruff check .` and `black --check .` both exit 0 across the working tree with venv excluded by pyproject config (verified: both `[tool.ruff].exclude` and `[tool.black].exclude` cover `.env_amw_erp` / `.env_amw_dj_erp`).
5. **Django check clean:** `python manage.py check` exits 0 with default settings (`config.settings.dev`, the default in `manage.py`).
6. **Commit convention:** every fix lands through the multi-message commit format with a clear title/description; one area per commit where practical.
7. **Evidence captured:** commands + results for all four gates are in the plan's verification log.
8. **Working-tree end state:** `git status --porcelain` shows exactly: `.gitignore` with only the `Mock Agent.md` addition (mode reset), nothing else modified, and the SAST docx file untracked.

Each criterion is testable by the command shown or by direct inspection; the plan operationalizes the exact sequence.

## 8. Risks & Mitigations

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | Test infra requires running services (Postgres, Redis); if they are down or half-up, failures will masquerade as code failures | False-positive bug inventory; wasted fix cycles | Root-cause discipline (5.1 rule 1): prove service-level causes first (connection refused vs. assertion diff). `infra_manage.sh status` before the first run. Use pytest's own connection errors to distinguish. |
| 2 | Environment mismatch: AGENTS.md names venv `.env_amw_erp`, which is absent; tooling currently resolves globally (`~/.local/bin`) | Wrong interpreter runs the suite → misleading results; lint gate in commit script may target the wrong venv | Plan must first establish and record the actual working interpreter (check `manage.py check` under each candidate), then use it for every gate. Fix `test_suite_runner.sh` venv path only as a QA finding, not a blind refactor. |
| 3 | Resource-needs surface mid-task: secrets for `pytest` env (e.g., DB creds), storage, or a missing dependency | Blocked runs | Fix locally what law permits; if a needed secret/config is Owner-held, escalate the need explicitly — do not invent credentials or commit them. Security scan discipline applies before every commit. |
| 4 | Failure count is large enough to sprawl beyond "small task" | Scope creep into feature work | 5-cycle limit from Orchestrator_Law applied to full fix cycles; per-area commits keep the diff reviewable; anything touching architecture or law goes to Owner. Deployment drift is forbidden (Section 3). |
| 5 | Pre-commit lint gate in `git_task_commit.sh` fails on the very commit that fixes lint | Chicken-and-egg block | Root-cause the gate's invocation first (fix the script or its pinned paths); do not bypass the gate without Owner's say. |

## 9. Decision Summary

- **Purpose:** verifiable quality baseline on this machine for job-seeking credibility; not a feature task.
- **Approach:** "Fix everything" — full verification stack, root-cause every failure, fix code and/or tests per project law, re-run until 100% clean; never disable tests to get green.
- **Branch/flow:** all work on `Fix-QA-Baseline`; push to origin in scope; merge/tag to `master` NOT in scope (Owner approval required per Orchestrator_Law).
- **Preserved working-tree state:** `.gitignore` keeps the `Mock Agent.md` ignore line (mode restored to `100644`); SAST docx stays untracked.
- **Tooling preference:** direct gate commands (`pytest`, `ruff check .`, `black --check .`, `manage.py check`); `utils/test_suite_runner.sh` used only once its hardcoded venv path is resolved.
- **Guardrails:** no Constitution changes, no features, no deployment work, max 5 fix cycles, evidence logged for every gate.
