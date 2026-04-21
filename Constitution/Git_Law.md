# Git & Branching Law - AMW Django ERP

**Extracted from Constitution Sections 6 and 7**

## 1. Branching Rules (Section 6.1–6.2)

- **Never commit directly to `master`.**
- All work in branches.
- Remote-first workflow expected.

**Branch Naming (MANDATORY PascalCase):**

| Type         | Format                  | Example                             |
|--------------|-------------------------|-------------------------------------|
| Errors/Fixes | `Fix-{Name}`            | `Fix-HTMX-Stability`                |
| Features     | `Feature-{Name}`        | `Feature-Open-Redirect-Protection`  |
| Phases       | `Phase-{Number}-{Name}` | `Phase-8-Async-Hardening`           |

**When to Use Each:**

- **`Fix-{Name}`**: Bug fixes, error corrections, and issue resolutions
- **`Feature-{Name}`**: New features, enhancements, and updates outside active phase scope
- **`Phase-{Number}-{Name}`**: New phase development work

**Workflow Rule:**

1. All work happens in appropriately named branches
2. Merge to `master` only after Ahmad confirms and approves
3. Branch names MUST match the format exactly — no silent drift to alternative naming

## 2. Commit Format (Section 6.3)

**Multi-Message Format (MANDATORY):**

```bash
git commit -m "prefix Title" -m "Detailed description"
```

**Using the utility script (RECOMMENDED):**

```bash
bash utils/git_task_commit.sh "Title" "Description"
```

**Title Prefixes:**

- `Phase X:` — Phase features (e.g., `Phase 2:`, `Phase 3:`)
- `Fix:` — Bug fixes
- `Feature:` — New features
- `Refactor:` — Code refactoring
- `Docs:` — Documentation updates
- `Test:` — Test additions or modifications

**Rules:**

- Title under 72 characters
- Description explains WHAT and WHY (not HOW)
- Both title and description are mandatory
- Local lint check runs before commit

## 3. Merge Rule (Section 6.4)

- Merge to `master` only after Ahmad confirms deliverables.
- Architecture-sensitive changes reviewed before merge.
- Use `utils/git_phase_finish.sh` for automated phase completion.

## 4. Phase Completion & Tagging (Section 6.5)

**Tag Format:** `v{phase-number}.0-phase{phase-number}-complete`

**Examples:**

- `v1.0-phase1-complete`
- `v2.0-phase2-complete`
- `v3.0-phase3-complete`

**Automated Process:**

```bash
bash utils/git_phase_finish.sh <phase-number> [version-tag]
```

**What the script does:**

1. Runs full test suite (must pass)
2. Runs lint checks (must pass)
3. Merges phase branch to master
4. Creates annotated version tag
5. Pushes master and tags to GitHub
6. Optionally cleans up phase branch

## 5. CI/CD Enforcement (Section 7)

CI Pipeline (GitHub Actions) runs on all pushes/PRs:

1. **Lint Check** (Ruff + Black)
2. **Test Suite** (pytest with PostgreSQL)
3. **Django Check** (dev and prod settings)
4. **Build Verification** (Docker image)

**No PR shall merge unless CI is Green.**
