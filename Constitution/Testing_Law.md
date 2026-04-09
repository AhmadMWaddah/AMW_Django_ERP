# Testing Law - AMW Django ERP

**Extracted from Constitution Section 13**

## Testing Requirements

- Every critical business feature requires tests.
- Every bug fix should include regression protection where practical.
- Inventory, IAM, and sales-confirmation flows are high-priority test domains.
- Tests should validate business behavior, not only model creation.

## Verification Standard

At minimum, verification should cover:
- changed business rules,
- changed operation methods,
- permission-sensitive flows,
- and concurrency-sensitive logic where applicable.

## Manual Testing Documentation

All manual testing documentation, including test cases, test plans, and sensitive credentials or setup information, MUST be exclusively located within the `Manual_Tests/` directory. No manual testing-related files should exist outside this centralized location.

## Definition of Completion (Section 5)

A task, part, or phase is complete only when:
- the implementation matches the project law,
- the code is coherent and production-minded,
- the relevant tests exist,
- the relevant tests pass,
- execution is free of unexplained tracebacks or debug noise,
- and Ahmad approves the milestone when business scope or release status is affected.

**Completion Clarification:**
- "Relevant tests pass" means the tests that validate the changed business behavior, not only unrelated smoke checks.
- Temporary exceptions must be explicitly documented. They are not assumed.
