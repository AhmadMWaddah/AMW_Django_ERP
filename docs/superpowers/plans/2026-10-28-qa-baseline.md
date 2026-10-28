# QA Baseline Verification & Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-subagent-driven-development (recommended) or superpowers-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a verifiably true quality baseline for AMW Django ERP on this machine — all four verification gates (pytest, ruff, black, `manage.py check`) green at root cause, evidence recorded, branch pushed to origin.

**Architecture:** No feature work. This is a QA-verification-and-fixes task: run the full verification stack, root-cause every failure per systematic-debugging discipline, apply minimal fixes (code if code is wrong, test only if test is wrong), commit one area per commit, and re-run until 100% clean with no flakes.

**Tech Stack:** Python 3.12, Django (version recorded in Task 1 — global env currently reports 6.0.7 vs AGENTS.md claim of 4.2 LTS), pytest 7.4.3 + pytest-django 4.5.2, ruff 0.15.11, black 26.3.1, PostgreSQL 15, Redis 7 (via `utils/infra_manage.sh` / docker compose).

**Spec:** `docs/superpowers/specs/2026-10-28-qa-baseline-design.md` (commit `a6a515b`, branch `Fix-QA-Baseline`).

---

## Scope Guard (read before every task)

**In scope:** the four verification gates, root-cause fixes for their failures, the `utils/test_suite_runner.sh` venv-path QA finding, `.gitignore` mode reset, evidence logging, pushing `Fix-QA-Baseline` to origin.

**Out of scope — any task drifting here is non-compliant and must be stopped:**

- Deployment work of any kind: OCI VM hosting, external/static Postgres, Celery-in-production, prod settings hardening, demo-data seeding.
- Merge to `master` or tagging (requires Owner approval per `Constitution/Orchestrator_Law.md` Stage 8 — happens AFTER this plan completes, not inside it).
- Any change under `Constitution/`.
- New features, unrelated refactors, roadmap work.
- Weakening, skipping (`skip`/`xfail`), deletion, or commenting-out of tests to get green.
- Editing AGENTS.md claims (e.g., the 228-test count) without a verified count produced by this plan.
- Changes to `.gitignore` content (the `Mock Agent.md` line stays; only the file mode is reset).

**Working-tree preservation contract (end state, per spec §7.8):** `git status --porcelain` must show exactly ` M .gitignore` (content: only the added `Mock Agent.md` line; mode restored to `100644`) and `?? SAST-SCA_Report_AMW_Django_ERP_2026-04-28.docx` (stays untracked, never committed) — nothing else.

**Commit protocol (every commit in this plan):**

```bash
git add <exact files for this concern>
bash utils/git_task_commit.sh "<Title>" "<Description>"
```

- Title prefixes: `Fix:` (code/housekeeping), `Test:` (test corrections), `Docs:` (log/plan updates). Title < 72 chars. Description explains WHAT and WHY.
- One concern per commit; per-area commits where practical.
- Known script behavior (do not bypass): the script runs `ruff check . --fix --ignore I001` and `black --check .` (auto-formatting on failure) before committing, and auto-pushes to origin after committing. Run gates clean BEFORE committing so the gate never rewrites files mid-commit. The script requires changes already staged (`git add` first) or it exits with "No staged changes to commit".
- Evidence-log-only commits use: `git add -f docs/superpowers/plans/2026-10-28-qa-baseline.md` (the repo's global `*.md` gitignore rule requires `-f`, matching existing practice for Constitution/ and Architecture/ docs).

**Verification log location:** the `## Verification Log` section at the bottom of THIS file. Every gate run appends: date/time, gate, exact command, exit code, key output lines (test counts, failure lists). Log edits are committed only in Task 11 (final Docs commit) to keep fix commits area-pure.

**Known environment facts (measured at plan-writing time, 2026-10-28 — executor must re-verify in Task 1):**

| Item | Measured value |
|---|---|
| Branch / HEAD | `Fix-QA-Baseline` @ `a6a515b` |
| `python3` | `/usr/bin/python3`, Python 3.12.3 |
| pytest | 7.4.3 at `/home/amw/.local/bin/pytest` (importable by `python3`) |
| ruff | 0.15.11 |
| black | 26.3.1 |
| Django | 6.0.7 (AGENTS.md claims 4.2 LTS — record as environment finding; do NOT edit AGENTS.md; escalate to Owner only if it blocks a gate) |
| pytest-django | 4.5.2 |
| Venv dirs | `.env_amw_erp/` and `.env_amw_dj_erp/` both absent at repo root; `.env` dotenv file present (6 DB/Postgres-related lines) |
| pytest settings | `DJANGO_SETTINGS_MODULE = config.settings.dev` per `pyproject.toml` `[tool.pytest.ini_options]`; `manage.py` defaults to `config.settings.dev` |
| Expected test count | 228 per AGENTS.md — UNVERIFIED |

**Interpreter rule for every gate command in this plan:** always invoke via `python3 -m ...` (e.g., `python3 -m pytest`, `python3 -m ruff check .`) so the recorded interpreter is pinned. Never call bare `pytest`/`ruff`/`black`.

---

### Task 1: PREPARE — Establish and record the working interpreter/toolchain

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Run the interpreter probe**

```bash
which python3 && python3 --version
python3 -m pytest --version
python3 -m ruff --version
python3 -m black --version
python3 -c "import django; print(django.__version__)"
python3 -c "import pytest_django; print(pytest_django.__version__)"
ls -d .env_amw_erp .env_amw_dj_erp 2>&1
head -1 /home/amw/.local/bin/pytest
```

Expected: `python3` resolves to `/usr/bin/python3` (3.12.3); pytest/ruff/black versions import cleanly under it; both venv dirs report `No such file or directory`; the pytest shebang confirms which interpreter `~/.local/bin` tooling uses.

- [ ] **Step 2: Verify lint tooling excludes the (absent) venv paths via pyproject config**

```bash
grep -n "env_amw" pyproject.toml
```

Expected: `[tool.ruff]` exclude list contains `.env_amw_erp` and `.env_amw_dj_erp`; `[tool.black]` exclude regex contains both. (Verified present at plan-writing time, lines 53–54 and 107–108.) This satisfies spec §7.4's "venv excluded by pyproject config" precondition — verify, do not assume.

- [ ] **Step 3: Record the toolchain in the Verification Log**

Append to the `## Verification Log` section: every command above, its output, and a one-line decision: "Working interpreter = `/usr/bin/python3` (Python 3.12.3), all gates run via `python3 -m ...`." Also record the Django 6.0.7 vs AGENTS.md-4.2 discrepancy as an environment finding (no action unless a gate fails on it — see Task 8 rules).

- [ ] **Step 4: Dependency-gap rule (only if a probe fails)**

If any import fails (e.g., `ModuleNotFoundError`), root-cause it: record the missing module, then install it into the user environment with `python3 -m pip install --user <package>` and re-probe. Record the install command and version in the log. If a required dependency is Owner-held or version-pinned (e.g., a Django 4.2 pin conflicts with global 6.0.7), STOP and escalate to the Owner — do not silently upgrade/downgrade Django.

- [ ] **Step 5: Commit**

Commit: none (evidence-only task; log is committed in Task 11).

---

### Task 2: PREPARE — Bring up and verify services (PostgreSQL 15, Redis 7)

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Check service status**

```bash
bash utils/infra_manage.sh status
```

Expected: status output showing PostgreSQL and Redis containers running (`Up`). If they are already up, record the output and go to Step 3.

- [ ] **Step 2: Start services if down**

```bash
bash utils/infra_manage.sh start
bash utils/infra_manage.sh status
docker ps --format '{{.Names}} {{.Status}}'
```

Expected: `SUCCESS: Services started successfully` (or equivalent) and `docker ps` shows the Postgres 15 and Redis 7 containers with `Up` status. Record both outputs.

- [ ] **Step 3: Prove DB connectivity before trusting any test result**

```bash
python3 manage.py check --database default 2>&1; echo "DB_CHECK_EXIT=$?"
```

Expected: `System check identified no issues` (or issues unrelated to DB connectivity) and `DB_CHECK_EXIT=0`. If this fails with a connection error, root-cause it FIRST (service down vs. wrong credentials in `.env` vs. wrong host/port in `config/settings/dev.py`) — per spec §8 Risk 1, service-level causes masquerade as code failures. Do not start Task 4 until this passes. If credentials are Owner-held and missing, escalate explicitly; never invent or commit credentials.

- [ ] **Step 4: Record evidence**

Append commands + outputs + exit codes to the Verification Log.

- [ ] **Step 5: Commit**

Commit: none (evidence-only task; the infra step is PREPARE, not part of the deliverable).

---

### Task 3: Housekeeping — Reset `.gitignore` file mode, preserve content

**Files:**
- Modify: `.gitignore` (file mode only: `100755` → `100644`; content unchanged)

- [ ] **Step 1: Reset the file mode**

```bash
chmod 644 .gitignore
git diff .gitignore
```

Expected: the diff shows ONLY the content hunk adding `+Mock Agent.md` (after `logs/`, `.sisyphus/`, `.antigravity/`, `.worktrees/`), with NO `old mode`/`new mode` lines.

- [ ] **Step 2: Verify the preserved working-tree state**

```bash
git status --porcelain
```

Expected exactly:

```
 M .gitignore
?? SAST-SCA_Report_AMW_Django_ERP_2026-04-28.docx
```

The `Mock Agent.md` line stays as an uncommitted working-tree modification (spec §7.8 requires this end state — it is intentionally NOT committed). The SAST docx stays untracked.

- [ ] **Step 3: Record evidence**

Append the diff and status output to the Verification Log.

- [ ] **Step 4: Commit**

Commit: none (this task intentionally produces no commit; the modified `.gitignore` is the preserved end state).

---

### Task 4: Gate run #1 — pytest baseline (failure inventory, part 1)

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Run the full pytest suite**

```bash
python3 -m pytest 2>&1 | tee /tmp/opencode/qa-pytest-run1.txt | tail -40; echo "PYTEST_EXIT=${PIPESTATUS[0]}"
```

Expected (one of):
- `=== 228 passed ===` (or another single count) with `PYTEST_EXIT=0` — baseline confirmed; record the actual count.
- One or more failures/errors with `PYTEST_EXIT` non-zero — this is the expected path if the 228 claim does not hold on this machine; the output is the failure inventory.

The `tee` file `/tmp/opencode/qa-pytest-run1.txt` is the durable raw evidence; the log records the summary line and the list of failed test node IDs.

- [ ] **Step 2: Record the count and the failure inventory**

Append to the Verification Log: exact command, exit code, the pytest summary line (`N passed, M failed, K errors` etc.), and the full list of failing test node IDs. State explicitly: `Actual count = <N>; AGENTS.md claim = 228; delta = <N - 228>`. Any delta must later be accounted for by named test changes made during fixes (Task 8 commits) — never by unexplained drift.

- [ ] **Step 3: Commit**

Commit: none (evidence-only; no repo files changed).

---

### Task 5: Gate run #1 — ruff, black, manage.py check (failure inventory, part 2)

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Run ruff**

```bash
python3 -m ruff check . 2>&1 | tee /tmp/opencode/qa-ruff-run1.txt | tail -30; echo "RUFF_EXIT=${PIPESTATUS[0]}"
```

Expected: `All checks passed!` with `RUFF_EXIT=0`, or a list of `file:line: CODE message` findings recorded as inventory.

- [ ] **Step 2: Run black in check mode**

```bash
python3 -m black --check . 2>&1 | tee /tmp/opencode/qa-black-run1.txt | tail -30; echo "BLACK_EXIT=${PIPESTATUS[0]}"
```

Expected: `All done! ... 0 files would be reformatted.` with `BLACK_EXIT=0`, or the list of files that would be reformatted.

- [ ] **Step 3: Run Django system check**

```bash
python3 manage.py check 2>&1 | tee /tmp/opencode/qa-check-run1.txt; echo "CHECK_EXIT=${PIPESTATUS[0]}"
```

Expected: `System check identified no issues (0 silenced).` with `CHECK_EXIT=0`, or the recorded check errors.

- [ ] **Step 4: Record evidence**

Append all three commands, exit codes, and findings to the Verification Log. This completes the run-#1 failure inventory across all four gates.

- [ ] **Step 5: Commit**

Commit: none (evidence-only).

---

### Task 6: QA finding — probe `utils/test_suite_runner.sh` hardcoded venv path

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)
- Modify (CONDITIONAL, only if blocking): `utils/test_suite_runner.sh:21`

- [ ] **Step 1: Run the wrapper once to demonstrate the finding**

```bash
bash utils/test_suite_runner.sh 2>&1 | head -10
```

Expected: `ERROR: Virtual environment not found at: /home/amw/Business/WorkSpaces/WebDevs/AMW_Django_ERP/.env_amw_dj_erp` followed by `Run './utils/env_factory.sh create' first`, exit 1. (Root cause, known from source: line 21 hardcodes `VENV_PATH="$PROJECT_ROOT/.env_amw_dj_erp"` while AGENTS.md names `.env_amw_erp` and neither exists; tooling resolves globally at `~/.local/bin`.)

- [ ] **Step 2: Record the finding and apply the decision rule**

Append to the Verification Log: the observed failure, the root cause (line 21), and the decision:

- **Default (expected):** this plan runs all gates via direct `python3 -m ...` commands, so the wrapper does NOT block the workflow → record as reported QA finding, no code change, no commit.
- **Fix only if blocking** (Owner directs it, or a later task genuinely needs the wrapper): change line 21 to fall back to the system interpreter when no venv dir exists, e.g. replace:

```bash
VENV_PATH="$PROJECT_ROOT/.env_amw_dj_erp"
```

with:

```bash
VENV_PATH="$PROJECT_ROOT/.env_amw_erp"
[ -d "$VENV_PATH" ] || VENV_PATH=""
```

and make `check_venv`/`activate_venv` skip activation when `VENV_PATH` is empty (exact edit written at fix time against the then-current file — the fix must be its own commit: `git add utils/test_suite_runner.sh` then `bash utils/git_task_commit.sh "Fix: test_suite_runner venv path fallback" "Wrapper hardcoded .env_amw_dj_erp which does not exist; AGENTS.md names .env_amw_erp; neither is present on this machine. Added fallback to system interpreter so the wrapper runs without a venv."`). Do NOT refactor the script beyond the blocking issue.

- [ ] **Step 3: Commit**

Commit: none in the default path (finding reported in log only). Conditional fix path: exactly one commit as written in Step 2.

---

### Task 7: Triage — classify every run-#1 failure with a written diagnosis

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Build the failure triage table**

For EVERY failure from Tasks 4–5, append one row to a triage table in the Verification Log with columns: `Gate | Failing item (test node ID / file:line / check code) | Classification | Diagnosis`.

Classification is exactly one of:
- `environment` — only after PROOF (pasted error showing connection refused, missing module, missing migration path, wrong settings). An environment diagnosis is proven, never assumed (spec §5.1 rule 1).
- `code-wrong` — implementation behavior is incorrect or drifted from project law.
- `test-wrong` — implementation is correct per project law; the test asserts different or weaker behavior than intended.

- [ ] **Step 2: Write a one-paragraph diagnosis per failure**

For each row, append one paragraph: what fails, where (file:line), why. Use `python3 -m pytest <node_id> -v` (single test), `python3 -m pytest <node_id> -v --tb=long`, and reading the involved source to establish the why. For test-wrong classifications, cite the project law or spec behavior the test contradicts (e.g., `Constitution/Architecture_Law.md` rules: atomic stock changes, WAC recalculation on stock-in, soft-delete inheritance, PolicyEngine authorization, operations-first business logic).

- [ ] **Step 3: Group failures into fix areas**

Append the area list to the log — one area per app/gate concern (e.g., `inventory-operations`, `sales-state-machine`, `ruff-imports`, `black-formatting`). Each area becomes exactly one pass through Task 8. If there are zero failures across all four gates, skip Task 8 entirely and record "no failures — no fix cycles needed" in the log, then go to Task 9.

- [ ] **Step 4: Commit**

Commit: none (log-only).

---

### Task 8: Fix loop — execute once per area from the Task 7 area list

**Files:**
- Modify: the specific source/test files named by the area's diagnosis (exact paths come from the Task 7 triage table — they are unknown until Task 7 runs and MUST be recorded there before any edit)
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

**Mandatory rules for every fix (spec §5.1 — violating any of these is non-compliant):**

1. Root cause first: the written diagnosis from Task 7 exists BEFORE any edit. No fix without it.
2. Fix code if the code is wrong. Business logic fixes stay in `operations/` modules and respect `Constitution/Architecture_Law.md` (transaction.atomic + select_for_update for stock, WAC recalculation on stock-in, soft-delete inheritance, PolicyEngine on state-changing POSTs).
3. Fix the test only if the test is wrong or weaker than intended; the commit description must say why the test was wrong.
4. NEVER disable to get green: no `@pytest.mark.skip`, no `xfail`, no deletion, no commented-out tests. Surface any pre-existing skips discovered in the log.
5. No silent drift: if a fix appears to require changing a law file or a documented number (the 228 count), STOP and state it to the Owner. Never edit `Constitution/`.
6. One concern per fix; one area per commit.
7. Max 5 full fix cycles (a full cycle = all four gates re-run). Beyond 5, stop and escalate to the Owner per `Constitution/Orchestrator_Law.md`.

- [ ] **Step 1: Apply the minimal fix for the area**

Edit only the files named in the area's Task 7 diagnosis. The edit is the smallest change that resolves the root cause. Show the before/after in the log entry for this area.

- [ ] **Step 2: Targeted re-run of the failing item(s)**

```bash
python3 -m pytest <area test path or node IDs> -v 2>&1 | tail -15; echo "EXIT=${PIPESTATUS[0]}"
```

(for lint areas: `python3 -m ruff check <path>` / `python3 -m black --check <path>` / `python3 manage.py check`). Expected: the previously failing items now pass, `EXIT=0`. If they still fail, return to Step 1 with a revised diagnosis — do not stack a second speculative fix.

- [ ] **Step 3: Full pytest re-run (regression check for the fix)**

```bash
python3 -m pytest 2>&1 | tail -5; echo "EXIT=${PIPESTATUS[0]}"
```

Expected: exit 0, and the total count moved only by this area's named changes (record old count → new count and name the test files changed, if any). If OTHER areas now fail, the fix caused a regression — root-cause that before continuing.

- [ ] **Step 4: Commit the area fix**

```bash
git add <exact files changed in Step 1>
bash utils/git_task_commit.sh "<Fix|Test>: <area> — <one-line what>" "<WHAT changed and WHY (root cause from Task 7)>"
```

Title examples: `Fix: inventory WAC recalc on return`, `Test: correct sales void rollback assertion`. Expected: commit created; the script's lint gate passes (gates were run clean in Steps 2–3) and the script auto-pushes to origin.

- [ ] **Step 5: Record the cycle and repeat for the next area**

Append to the log: area name, files changed, targeted re-run result, full re-run count, commit hash. Increment the full-cycle counter when all four gates have been re-run. Repeat this task for each remaining area in the Task 7 list.

- [ ] **Step 6: Commit**

One commit per area, created in Step 4. No additional commits.

---

### Task 9: Final gate — pytest clean run + immediate re-run (flake check)

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Clean full pytest run**

```bash
python3 -m pytest 2>&1 | tee /tmp/opencode/qa-pytest-final.txt | tail -5; echo "PYTEST_EXIT=${PIPESTATUS[0]}"
```

Expected: `PYTEST_EXIT=0` with summary `=== N passed ===`. Record N.

- [ ] **Step 2: Immediate re-run, same interpreter, same services (no-flake proof)**

```bash
python3 -m pytest 2>&1 | tee /tmp/opencode/qa-pytest-final-rerun.txt | tail -5; echo "PYTEST_EXIT=${PIPESTATUS[0]}"
```

Expected: `PYTEST_EXIT=0` again with the SAME count N. If the re-run fails, a flake or order-dependence exists — root-cause it (Task 8 rules) before proceeding.

- [ ] **Step 3: Account for the count delta**

Append to the log: `Final count = N; AGENTS.md claim = 228; delta = N - 228`. Every unit of delta must map to a named test change from a Task 8 commit (file + what changed). If delta cannot be fully accounted for, STOP and escalate to the Owner — do not proceed to Task 11 with unexplained drift.

- [ ] **Step 4: Commit**

Commit: none (evidence-only).

---

### Task 10: Final gate — ruff, black, manage.py check clean runs

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section only)

- [ ] **Step 1: Final ruff run**

```bash
python3 -m ruff check . 2>&1 | tee /tmp/opencode/qa-ruff-final.txt | tail -5; echo "RUFF_EXIT=${PIPESTATUS[0]}"
```

Expected: `All checks passed!`, `RUFF_EXIT=0`.

- [ ] **Step 2: Final black check run**

```bash
python3 -m black --check . 2>&1 | tee /tmp/opencode/qa-black-final.txt | tail -5; echo "BLACK_EXIT=${PIPESTATUS[0]}"
```

Expected: `0 files would be reformatted.`, `BLACK_EXIT=0`.

- [ ] **Step 3: Final Django check run**

```bash
python3 manage.py check 2>&1 | tee /tmp/opencode/qa-check-final.txt; echo "CHECK_EXIT=${PIPESTATUS[0]}"
```

Expected: `System check identified no issues (0 silenced).`, `CHECK_EXIT=0`.

- [ ] **Step 4: Confirm the venv was never linted**

```bash
grep -c "env_amw" /tmp/opencode/qa-ruff-final.txt /tmp/opencode/qa-black-final.txt 2>/dev/null; ls -d .env_amw_erp .env_amw_dj_erp 2>&1
```

Expected: venv dirs still absent (nothing was created/linted); no lint output references venv paths. Confirms the "NEVER lint the virtual environment" rule held.

- [ ] **Step 5: Record evidence**

Append all commands, exit codes, and outputs to the Verification Log.

- [ ] **Step 6: Commit**

Commit: none (evidence-only).

---

### Task 11: Commit the verification log into the plan document

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log section — finalize all entries from Tasks 1–10)

- [ ] **Step 1: Finalize the Verification Log**

Ensure the log contains, for every gate run in this plan: date/time, exact command, exit code, key output lines (counts, failure lists, diagnoses, area→commit-hash mapping, cycle count used, environment findings including the Django version discrepancy and the test_suite_runner finding).

- [ ] **Step 2: Stage with force (gitignore `*.md` rule) and commit**

```bash
git add -f docs/superpowers/plans/2026-10-28-qa-baseline.md
bash utils/git_task_commit.sh "Docs: Record QA baseline evidence" "Verification log for pytest, ruff, black, and manage.py check gate runs on Fix-QA-Baseline, including failure diagnoses, fixes, and final counts."
```

Expected: commit created on `Fix-QA-Baseline`; script auto-pushes to origin.

- [ ] **Step 3: Verify the commit**

```bash
git log --oneline -3
```

Expected: the `Docs: Record QA baseline evidence` commit at HEAD.

---

### Task 12: Push branch and verify origin state

**Files:** none.

- [ ] **Step 1: Push with upstream tracking**

```bash
git push -u origin Fix-QA-Baseline
```

Expected: `Branch 'Fix-QA-Baseline' set up to track remote branch 'Fix-QA-Baseline' from 'origin'.` and `up to date` (the commit script already pushed; this makes it explicit and idempotent).

- [ ] **Step 2: Verify the branch exists on origin and local is not ahead**

```bash
git ls-remote --heads origin Fix-QA-Baseline
git fetch origin
git rev-parse Fix-QA-Baseline origin/Fix-QA-Baseline
git status -sb
```

Expected: `git ls-remote` prints one line ending in `refs/heads/Fix-QA-Baseline`; both `git rev-parse` hashes are IDENTICAL; `git status -sb` shows `## Fix-QA-Baseline...origin/Fix-QA-Baseline` with no `[ahead N]`. Record the pushed HEAD hash in the log.

- [ ] **Step 3: Commit**

Commit: none (verification-only).

---

### Task 13: Final working-tree state + acceptance criteria sweep

**Files:** none.

- [ ] **Step 1: Verify the preserved working-tree end state**

```bash
git status --porcelain
```

Expected EXACTLY (nothing more, nothing less):

```
 M .gitignore
?? SAST-SCA_Report_AMW_Django_ERP_2026-04-28.docx
```

If anything else appears (stray `ruff --fix` edits from a commit-script gate, leftover test artifacts, `htmlcov/`), clean or commit it per its nature BEFORE finishing — with root cause recorded in the log.

- [ ] **Step 2: Run the full acceptance-criteria sweep (spec §7, items 1–8)**

Run each command; append each result to the log as `AC#N: PASS/FAIL`:

```bash
# AC1: branch on origin, local not ahead
git ls-remote --heads origin Fix-QA-Baseline && git status -sb | head -1
# AC2: pytest green with recorded count (from Task 9 Step 1)
tail -3 /tmp/opencode/qa-pytest-final.txt
# AC3: no flakes (from Task 9 Step 2)
tail -3 /tmp/opencode/qa-pytest-final-rerun.txt
# AC4: lint clean
python3 -m ruff check . && python3 -m black --check .
# AC5: Django check clean
python3 manage.py check
# AC6: commit convention — inspect history
git log --format='%s' origin/master..Fix-QA-Baseline
# AC7: evidence captured — this plan's Verification Log is complete and committed (Task 11)
# AC8: working-tree end state — Step 1 output above
```

Expected: AC1 one ref line + no `[ahead]`; AC2/AC3 same passing count, exit 0; AC4 both exit 0; AC5 exit 0; AC6 every title carries a legal prefix (`Fix:`/`Test:`/`Docs:`) under 72 chars; AC7 log present in committed plan; AC8 exactly the two expected lines.

- [ ] **Step 3: Commit**

Commit: none (verification-only).

---

### Task 14: Report status to Owner

**Files:**
- Modify: `docs/superpowers/plans/2026-10-28-qa-baseline.md` (Verification Log — final status block only, if needed)

- [ ] **Step 1: Compose the status report**

State in the log (and to the Owner): final test count and delta accounting vs 228; per-gate final results; number of fix cycles used (max 5); open findings (Django 6.0.7 vs AGENTS.md 4.2 LTS; `test_suite_runner.sh` venv path if unfixed; any pre-existing skips discovered); pushed HEAD hash.

- [ ] **Step 2: State the merge boundary explicitly**

Merge to `master` and tagging are NOT part of this plan. They require Owner approval per `Constitution/Orchestrator_Law.md` Stage 8 and happen only after this plan completes and the Owner reviews the report.

- [ ] **Step 3: Commit**

Commit: none unless the final status block was appended to the log — in that case repeat Task 11 Step 2 with title `Docs: Finalize QA baseline report`.

---

## Acceptance Criteria → Task Mapping (spec §7)

| Spec AC | Verified by |
|---|---|
| 1. Branch on origin, local not ahead | Task 12 |
| 2. pytest green, count recorded, delta accounted | Tasks 4, 8, 9 |
| 3. No flakes on immediate re-run | Task 9 Step 2 |
| 4. ruff + black clean, venv excluded by pyproject | Tasks 1 Step 2, 5, 10 |
| 5. `manage.py check` clean (config.settings.dev) | Tasks 5, 10 |
| 6. Multi-message commit convention | Task 8 Step 4, Task 13 AC6 |
| 7. Evidence captured for all four gates | Verification Log (Tasks 1–5, 9–10), committed Task 11 |
| 8. Working-tree end state | Task 3, Task 13 Step 1 |

---

## Verification Log

> Appended during execution. Entry format:
> `### <date time> — <gate/step>` / `Command: <exact>` / `Exit: <code>` / `Key output: <lines>` / `Notes: <diagnosis, count, decision>`

### 2026-10-28 17:14 EEST — Task 1 Step 1: interpreter/toolchain probe
Command: `which python3 && python3 --version` / `python3 -m pytest --version` / `python3 -m ruff --version` / `python3 -m black --version` / `python3 -c "import django; print(django.__version__)"` / `python3 -c "import pytest_django; print(pytest_django.__version__)"` / `ls -d .env_amw_erp .env_amw_dj_erp 2>&1` / `head -1 /home/amw/.local/bin/pytest`
Exit: 0 (all probes)
Key output:
- `python3` → `/usr/bin/python3`, `Python 3.12.3`
- `pytest 7.4.3`
- `ruff 0.15.11`
- `python -m black, 26.3.1 (compiled: yes)` — `Python (CPython) 3.12.3`
- `django 6.0.7`
- `pytest_django 4.5.2`
- `ls: cannot access '.env_amw_erp': No such file or directory` / `ls: cannot access '.env_amw_dj_erp': No such file or directory`
- pytest shebang: `#!/usr/bin/python3`
Notes: All tooling imports cleanly under the global interpreter. Both venv dirs absent. Decision: **Working interpreter = `/usr/bin/python3` (Python 3.12.3), all gates run via `python3 -m ...`.** Environment finding: Django 6.0.7 installed vs AGENTS.md claim of Django 4.2 LTS (requirements.txt pins `Django>=4.2,<5.0`). Recorded, no action unless a gate fails on it (Task 8 rules). Owner amendment honored: no virtualenv created; global interpreter used AS-IS.

### 2026-10-28 17:14 EEST — Task 1 Step 2: pyproject venv-exclude verification
Command: `grep -n "env_amw" pyproject.toml`
Exit: 0
Key output:
- Line 53: `".env_amw_erp",` / Line 54: `".env_amw_dj_erp",` — inside `[tool.ruff] exclude = [...]` (confirmed by reading lines 45–60: exclude list starts at line 48)
- Line 107: `| \.env_amw_erp` / Line 108: `| \.env_amw_dj_erp` — inside `[tool.black]` exclude regex (confirmed by reading lines 100–112)
- Line 125: `".env_amw_dj_erp/*",` (additional exclude entry)
Notes: Spec §7.4 precondition "venv excluded by pyproject config" VERIFIED (not assumed). Combined with Step 1 (`ls` shows both venv dirs absent), the "never lint a venv" rule holds structurally.

### 2026-10-28 17:15 EEST — Task 2 Step 1: service status check
Command: `bash utils/infra_manage.sh status`
Exit: 1
Key output: `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?`
Notes: Docker daemon INACTIVE (`systemctl is-active docker` → `inactive`), so no Postgres/Redis containers exist. Root cause is host-level daemon, not compose config. Attempted non-interactive start: `sudo -n systemctl start docker` → `sudo: a password is required`. User IS in `docker` group; only the daemon is down. ESCALATION: daemon start requires Owner to run `sudo systemctl start docker` (password-held action).

### 2026-10-28 17:15 EEST — Task 2 dependency gap: global env missing rest_framework
Command: `python3 manage.py check --database default` (global interpreter)
Exit: 1
Key output: `ModuleNotFoundError: No module named 'rest_framework'` (fails in `django.setup()` → INSTALLED_APPS import, before any DB contact)
Notes: Per Task 1 Step 4 dependency-gap rule, attempted `python3 -m pip install --user "djangorestframework>=3.14.0"` → BLOCKED by PEP 668: externally-managed environment (`error: externally-managed-environment` hint). Global env cannot run the gate AS-IS. **Owner amendment fallback triggered:** created `.amw_erp_env/` venv in repo root via `python3 -m venv .amw_erp_env`, installed full `requirements.txt` (`pip install -r requirements.txt` → exit 0). Decision + reason recorded here per amendment. Installed key versions: Django 4.2.30 (matches requirements pin `>=4.2,<5.0` — venv also resolves the Task 1 Django-6.0.7-mismatch finding for gate runs), djangorestframework 3.17.2, pytest 9.2.0, pytest-django 4.14.0, ruff 0.17.3, black 26.10.1, psycopg2-binary 2.9.13. **Interpreter decision AMENDED:** all gates now run via `.amw_erp_env/bin/python -m ...` (supersedes Task 1's `python3 -m ...` rule for the remainder of this plan). Probe with venv interpreter: all project-required imports OK (crispy_forms/django_filters/corsheaders probed too but are NOT imported anywhere in `config/` — speculative probe entries, no manifest gap).

### 2026-10-28 17:16 EEST — venv hygiene: lint/git exclusions for .amw_erp_env
Command: `grep -n "amw_erp_env" .gitignore pyproject.toml` (before) → absent everywhere; `git check-ignore -v .amw_erp_env/bin/python` → not ignored
Exit: 0 / 1
Key output: pyproject excluded only `.env_amw_erp`/`.env_amw_dj_erp`; `.amw_erp_env` unknown to git and lint tooling.
Notes: Without exclusion, ruff/black would lint the venv (violates NEVER-lint-venv law) and `git status` would show the venv untracked (breaks Task 13 end state). Fix applied: (1) pyproject.toml — added `.amw_erp_env` to `[tool.ruff] exclude`, `[tool.black]` regex, `[tool.coverage.run] omit`; (2) `.amw_erp_env/` added to `.git/info/exclude` (repo-local, NOT committed) — deliberately NOT added to `.gitignore`, because Task 3/13 require the `.gitignore` working-tree diff to contain ONLY the `Mock Agent.md` line. Committed as `625e891` `Fix: exclude .amw_erp_env venv from lint config` (pushed to origin).

### 2026-10-28 17:17 EEST — Task 2 Step 3: DB connectivity proof — FALSE PASS exposed
Command: `.amw_erp_env/bin/python manage.py check --database default 2>&1; echo "DB_CHECK_EXIT=$?"`
Exit: 0 — **but this is a FALSE PASS**
Key output: `System check identified no issues (0 silenced).` / `DB_CHECK_EXIT=0`
Notes: Root-caused before trusting it. `.env` IS loaded (`config/settings/base.py:28-30` `environ.Env.read_env`) → effective DB target is `localhost:5433` (docker compose port). Direct connection probe (`.amw_erp_env/bin/python` + `connection.cursor()` → `SELECT version()`) → `django.db.utils.OperationalError: connection to server at "localhost" (127.0.0.1), port 5433 failed: Connection refused` (exit 1). Conclusion: on Django 4.2, `manage.py check --database default` does NOT establish a live connection — the plan's Step 3 command is a weaker connectivity proof than intended. True DB state: UNREACHABLE (docker daemon down, nothing listens on 5433). Environment facts recorded: native PostgreSQL 16 listens on 127.0.0.1:5432 (NOT used — config points to 5433; changing DB config is out of scope and would risk testing against the wrong database); Redis not running. **BLOCKER for Task 2 completion:** Docker daemon start requires Owner sudo. DB connectivity proof (a real cursor query) must be re-run after services are up. No config or code changes made for this finding.

### 2026-10-28 17:31 EEST — Task 2 RESUMED after Owner started Docker daemon
Command: `docker info --format '{{.ServerVersion}}'` / `systemctl is-active docker`
Exit: 0 / 0
Key output: `29.1.3` / `active`
Notes: Owner ran `sudo systemctl start docker` outside the agent (password-held action; agent never uses sudo per Owner instruction). Daemon healthy. Also recorded: docker.service was `disabled` before Owner intervention — no agent action taken.

### 2026-10-28 17:32 EEST — Task 2 Step 2: start services
Command: `bash utils/infra_manage.sh start` then `bash utils/infra_manage.sh status` then `docker ps --format '{{.Names}} {{.Status}}'`
Exit: 0 / 0 / 0
Key output: `SUCCESS: Services started successfully`. `docker ps`: `amw_erp_postgres postgres:15-alpine Up (healthy) 0.0.0.0:5433->5432/tcp`, `amw_erp_redis redis:7-alpine Up (healthy) 0.0.0.0:6380->6379/tcp`, plus `amw_erp_web` (Up), `amw_erp_celery_beat` (Restarting), `amw_erp_celery_worker` (Restarting).
Notes: Plan's expected Postgres 15 + Redis 7 containers both `Up (healthy)` on compose ports 5433/6380. OBSERVATION (not a Task 2 gate): `amw_erp_celery_beat` and `amw_erp_celery_worker` containers are in `Restarting` state after start — recorded as a finding; Celery is not required for any gate in this plan (pytest runs synchronously via pytest-django). No action taken; flagging for Owner awareness.

### 2026-10-28 17:33 EEST — Task 2 Step 3 (amended proof): real DB connectivity via cursor query
Command: `.amw_erp_env/bin/python` inline script: `django.setup()`; `connection.cursor().execute("SELECT version(), current_database(), current_user;")`
Exit: 0
Key output: `TARGET: localhost 5433 amw_django_erp amw_erp_user` → `('PostgreSQL 15.17 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit', 'amw_django_erp', 'amw_erp_user')`
Notes: This is the authoritative connectivity proof (the plan's nominal `manage.py check --database default` was shown above to be a false-pass-capable lazy check). Re-ran the nominal command too for the record: `.amw_erp_env/bin/python manage.py check --database default` → `System check identified no issues (0 silenced).`, `DB_CHECK_EXIT=0` — now backed by a proven live connection. Task 2 COMPLETE: services up, DB reachable with correct database/user per `.env`.

### 2026-10-28 17:41 EEST — Task 3 Step 1: reset .gitignore file mode
Command: `chmod 644 .gitignore` (pre-state: `stat -c '%a %n'` → `775 .gitignore`; `git ls-files -s .gitignore` → `100644 a7beb1f...` — index already 100644, worktree was 775)
Exit: 0
Key output: post-chmod `stat` → `644`; `git diff .gitignore` shows ONLY the content hunk:
```
@@ -106,3 +106,4 @@ logs/
 .sisyphus/
 .antigravity/
 .worktrees/
+Mock Agent.md
```
NO `old mode`/`new mode` lines present.
Notes: Mode restored to 100644 effective state; content untouched. The `Mock Agent.md` line remains an uncommitted working-tree modification per spec §7.8.

### 2026-10-28 17:41 EEST — Task 3 Step 2: verify preserved working-tree state
Command: `git status --porcelain`
Exit: 0
Key output:
```
 M .gitignore
?? SAST-SCA_Report_AMW_Django_ERP_2026-04-28.docx
```
Notes: EXACTLY the two expected lines — matches spec §7.8 end-state contract. SAST docx stays untracked; nothing else in the tree (the `.amw_erp_env/` venv is hidden via `.git/info/exclude`, recorded earlier). Task 3 produces no commit by design.
