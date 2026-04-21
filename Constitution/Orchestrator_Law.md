# Orchestrator Law - AMW Django ERP

**Version:** 3.0 (Workflow Orchestration)
**Extracted from:** Constitution Sections 1–7
**Last Updated:** 2026-04-21

## 1. Available Models

### Primary Models (Complex Tasks)
- **big-pickle** - Complex planning, error fixes, new features
- **MiniMax M2.5** - Main coding, bug fixing
- **nemotron-3-super** - Code review, security checks

### Small Models (Simple Tasks)
- **ollama/qwen2.5-coder:7b** - Unit testing
- **ollama/deepseek-coder:6.7b** - Documentation, Git push
- **ollama/gemma:4** - Branch creation, Git merge


---

## 2. Project Identity (Sections 1–2)

This file is the operational law of the AMW Django ERP project.
It exists so that any AI CLI tool, coding agent, assistant, reviewer, or automation worker follows the same project identity, engineering methodology, architectural rules, execution discipline, and delivery standards.

**What This Project Is:**

AMW Django ERP is a Django-based ERP system for real business operations covering:
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

## 3. Team Roles

| Role                | Responsibility                                                      |
|---------------------|---------------------------------------------------------------------|
| **Owner**           | Ahmad - Final owner of scope, release approval, business decisions |
| **Developer**       | Implementation, business logic, data integrity, backend operations |
| **Reviewer**        | Code review, quality gates, testing verification                   |

## 4. Mandatory Development Behaviors (Section 4)

Every AI agent MUST:

- **4.1 Read Before Writing** - Verify local project context, do not assume structure.
- **4.2 Work Sequentially** - Phase → Part → Task. No jumping ahead without approval.
- **4.3 Stay Concrete** - No generic best-practice filler. AMW Django ERP specific only.
- **4.4 Respect Existing Direction** - No stack/methodology rewrites without explicit approval.
- **4.5 Finish at Task Level** - Complete cleanly or split into atomic sub-tasks.
- **4.6 No Hidden Business Logic** - Business rules in explicit `operations/` modules, never in views/signals/templates.
- **4.7 No Silent Drift** - If change requires altering project law, state it explicitly.

## 5. Completion Definition (Section 5)

Task complete when:
- Implementation matches project law
- Code is coherent and production-minded
- Relevant tests exist and pass
- No unexplained tracebacks or debug noise
- Ahmad approves (if business scope/release affected)

## 6. Git & Branching (Section 6)

**Branch Naming (PascalCase):**
- `Fix-{Name}` - Bug fixes
- `Feature-{Name}` - New features
- `Phase-{Number}-{Name}` - Phase development

**Commit Format:**
```bash
git commit -m "prefix Title" -m "Detailed description"
# Use: utils/git_task_commit.sh "Title" "Description"


Phase Completion:

    Merge to master only after Ahmad approval

    Tag format: v{phase}.0-phase{phase}-complete

    Use: utils/git_phase_finish.sh <phase-number>

7. CI/CD (Section 7)

    All PRs must pass CI (lint, test, Django check, build)

    Local commits blocked if lint fails


---

## 8. Workflow Stages (Section 8)

The complete development workflow stages in execution order:

### Stage 1: PLANNING
- **Agent:** big-pickle (Planner)
- **Input:** Task description from Owner
- **Output:** Detailed execution plan with task breakdown
- **Next Stage:** CREATE_BRANCH

### Stage 2: CREATE_BRANCH
- **Agent:** ollama/gemma:4 (GitBranchCreator)
- **Input:** Execution plan from Planner
- **Output:** Git feature branch created locally and on remote
- **Next Stage:** CODING
- **Rule:** Check if branch already exists. If yes, skip creation. If no, create new branch with name: `Feature-{Name}` or `Fix-{Name}`

### Stage 3: CODING
- **Agent:** MiniMax M2.5 (Coder)
- **Input:** Execution plan from Planner
- **Output:** Implementation code, modified/created files
- **Next Stage:** UNIT_TESTING

### Stage 4: UNIT_TESTING
- **Agent:** ollama/qwen2.5-coder:7b (UnitTester)
- **Input:** Implemented code from Coder
- **Output:** Test results, pass/fail report
- **On Success:** → REVIEWING
- **On Failure:** → PLANNING (for fix plan)

### Stage 5: REVIEWING
- **Agent:** nemotron-3-super (Reviewer)
- **Input:** Code + Test results
- **Output:** Review report (APPROVED / NEEDS_FIX)
- **On APPROVED:** → DOCUMENTATION
- **On NEEDS_FIX:** → PLANNING (for fix plan)

### Stage 6: DOCUMENTATION
- **Agent:** ollama/deepseek-coder:6.7b (DocWriter)
- **Input:** Approved code from Reviewer
- **Output:** Updated README, docs, comments
- **Next Stage:** PUSH_TO_BRANCH

### Stage 7: PUSH_TO_BRANCH
- **Agent:** ollama/deepseek-coder:6.7b (GitPusher)
- **Input:** Documented code
- **Output:** Committed and pushed to feature branch
- **Next Stage:** HUMAN_APPROVAL
- **Rule:** Only push code that passed testing and review (correct, clean code)

### Stage 8: HUMAN_APPROVAL
- **Agent:** Owner (Ahmad)
- **Input:** Review report + Branch status
- **Output:** APPROVED / REJECTED
- **On APPROVED:** → MERGE_TO_MASTER
- **On REJECTED:** → PLANNING (for fix plan)

### Stage 9: MERGE_TO_MASTER
- **Agent:** ollama/gemma:4 (GitMerger)
- **Input:** Owner approval received
- **Output:** PR created, branch merged to master
- **Branch Cleanup:** Delete BOTH local AND remote branch after merge
- **Command:**
  ```bash
  git branch -d Feature-Name        # Local branch
  git push origin --delete Feature-Name  # Remote branch
  ```
- **Status:** COMPLETE


---

## 7. Iteration Limits (Section 9)

### Retry Limits
- **Workflow Cycle Limit:** 5 retries maximum
- **Meaning:** Complete workflow (Stage 1 → Stage 8) can run up to 5 times
- **After Limit Reached:** Escalate to human (Owner)

### Per-Stage Retry Logic
```
Workflow Run 1 → FAIL → Workflow Run 2 → FAIL → Workflow Run 3 → FAIL → Workflow Run 4 → FAIL → Workflow Run 5 → FAIL → HUMAN
```

### Stage-Specific Limits
| Stage | Retry Behavior |
|-------|----------------|
| PLANNING | If plan fails: retry (max 2x), then human |
| CREATE_BRANCH | If fails: retry (max 2x), then human |
| CODING | If code fails: retry (max 2x), then go to PLANNING for fixes |
| UNIT_TESTING | If tests fail: retry (2x), then go to PLANNING for fixes |
| REVIEWING | If rejected: go to PLANNING for fixes |
| DOCUMENTATION | If fails: retry (max 2x), then human |
| PUSH_TO_BRANCH | If fails: retry (max 2x), then human |
| MERGE_TO_MASTER | If fails: retry (max 2x), then human |


---

## 8. Error Escalation Rules (Section 10)

### Fallback Mechanism: REMOVED
- No fallback to secondary/backup models
- Any failure → direct escalation to appropriate stage or human

### Escalation Flow
```
Error Occurs
    ↓
Is it in retry limit? YES → Retry same stage
    ↓ NO
Is workflow limit reached? YES → ESCALATE TO HUMAN
    ↓ NO
Move to appropriate previous stage
```

### Escalation Triggers (Direct to Human)
1. All 5 workflow cycles exhausted
2. Planner fails to create valid plan after 2 attempts
3. Code generation fails completely
4. Critical security issues found
5. Owner explicitly requests human intervention

### No Fallback = Direct to Human
- Primary model fails → Retry same stage same model
- Retry exhausted → Previous stage for fixes
- All cycles exhausted → Human intervention required


---

## 9. Task Model Assignment (Section 11)

### Primary Model Assignments (Complex Tasks)

| Task Type | Model | When to Use |
|-----------|---------------|-------------|
| Complex Planning | big-pickle | Architecture, Phase planning, AND Planning error fixes, AND Planning new features |
| Main Coding | MiniMax M2.5 | Feature implementation, business logic, AND Fixing coding errors |
| Code Review | nemotron-3-super | Full reviews, security checks, deep analysis |

### Small Model Assignments (Simple Tasks - Balanced)

| Task Type | Exact Model | Why This Model |
|-----------|-------------|----------------|
| Create Git Branch | ollama/gemma:4 | Lightweight, quick branch creation |
| Unit Testing | ollama/qwen2.5-coder:7b | Good for running/executing tests |
| Documentation | ollama/deepseek-coder:6.7b | Good at writing text content |
| Git Commit/Push | ollama/deepseek-coder:6.7b | Good git operations |
| Git Merger | ollama/gemma:4 | Lightweight for simple merge task |

### Stage Order Reference
| Stage # | Stage Name | Agent | Model |
|---------|-----------|-------|-------|
| 1 | PLANNING | Planner | big-pickle |
| 2 | CREATE_BRANCH | GitBranchCreator | ollama/gemma:4 |
| 3 | CODING | Coder | MiniMax M2.5 |
| 4 | UNIT_TESTING | UnitTester | ollama/qwen2.5-coder:7b |
| 5 | REVIEWING | Reviewer | nemotron-3-super |
| 6 | DOCUMENTATION | DocWriter | ollama/deepseek-coder:6.7b |
| 7 | PUSH_TO_BRANCH | GitPusher | ollama/deepseek-coder:6.7b |
| 8 | HUMAN_APPROVAL | Owner | Human |
| 9 | MERGE_TO_MASTER | GitMerger | ollama/gemma:4 |


---

## 10. Workflow Execution Rules (Section 12)

### Standard Workflow (No Errors)
```
PLANNING → CODING → TESTING → REVIEWING → DOCUMENTATION → PUSH_TO_BRANCH → HUMAN_APPROVAL → MERGE_TO_MASTER
```

### Standard Workflow (No Errors)
```
PLANNING → CREATE_BRANCH → CODING → UNIT_TESTING → REVIEWING → DOCUMENTATION → PUSH_TO_BRANCH → HUMAN_APPROVAL → MERGE_TO_MASTER
```

### With Errors (Test Fails OR Review Rejects)
**"If test fails OR review rejects, go back to PLANNING to plan the fix. Then do full cycle: CREATE_BRANCH → CODING → UNIT_TESTING → REVIEWING → DOCUMENTATION → PUSH → HUMAN → MERGE. Continue full cycles until passes or reach limit."**

```
Error at UNIT_TESTING or REVIEWING:
   Go back to PLANNING (Stage 1)
   → CREATE_BRANCH → CODING → UNIT_TESTING → REVIEWING → DOCUMENTATION → PUSH_TO_BRANCH → HUMAN_APPROVAL → MERGE_TO_MASTER
   
   If fail again → repeat FULL CYCLE again
   Continue until PASS or reach 5 limit → HUMAN
```

### With New Features Requested (During or After Review)
**"If Owner/Reviewer asks for NEW features, go back to PLANNING to plan the feature. Then do a FULL CYCLE from beginning. Complete all 9 stages. After completing cycle, check if more features needed. If yes, start new full cycle. If no, continue to merge."**

```
New Feature Request:
   Go back to PLANNING (Stage 1)
   → CREATE_BRANCH → CODING → UNIT_TESTING → REVIEWING → DOCUMENTATION → PUSH_TO_BRANCH → HUMAN_APPROVAL → MERGE_TO_MASTER
   
   This is a FULL CYCLE, not mini-cycle
   After merge, check for more features
   If more → start new full cycle
   If done → COMPLETE
```

### Key Rules
1. **Always complete full workflow cycle** - Never skip stages in order
2. **Never skip stages** - Order must be: Planning → Coding → Testing → Reviewing → Docs → Push → Human → Merge
3. **Retry within limits** - Max 5 complete cycles, then human
4. **Only push correct, tested code** - Never push broken or untested code to branch
5. **Never merge without Owner approval** - Always get Ahmad's approval first
6. **On any error/reject: go to Stage 1** - Go back to Planning to plan the fix



