# CI/CD & Automation Law - AMW Django ERP

**Extracted from Constitution Section 7**

## 7.1 CI Defender (GitHub Actions)

**MANDATORY:** All pushes and pull requests MUST pass CI checks.

**CI Pipeline Jobs:**

1. **Lint Check** — Ruff and Black formatting
2. **Test Suite** — Full pytest coverage with PostgreSQL
3. **Django Check** — System check for dev and prod settings
4. **Build Verification** — Docker image build success

**No PR shall be merged unless the CI Defender is Green.**

## 7.2 Local Quality Gate

**MANDATORY:** All commits MUST pass lint checks before entering Git history.

**Enforcement:**

- `utils/git_task_commit.sh` runs mandatory lint check
- Ruff must pass (with `I001` ignored for import sorting)
- Black must pass (auto-formats if needed)
- Commit blocked if lint fails

## 7.3 Phase Completion Automation

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

## 7.4 Milestone Tagging

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
