---
topic: coverage-agent
phase: accepted-backfill
created: 2025-07-07
backfilled_by: coverage-agent-simplification
---

# coverage-agent — Step Tracking

> **Executor**: This parent step tracker has been backfilled by the
> `coverage-agent-simplification` correction topic.
> The previous helper / placeholder-generation steps are superseded and are not active work.

## Workflow Stages

- [X] original-plan-authoring
- [X] original-plan-review
- [X] original-implementation
- [X] correction-backfill

## Implementation Steps

- [X] 1. Configure pytest-cov to produce `.coverage-reports/coverage.json` and `term-missing` evidence.
- [X] 2. Keep `.coverage` and `.coverage-reports/` ignored.
- [X] 3. Set `[tool.coverage.report].fail_under = 90`.
- [X] 4. Keep the existing `pytest` pre-commit hook on `stages: [manual]`.
- [X] 5. Configure `coverage-check` as the active local 90% coverage gate.
- [X] 6. Supersede the old custom helper / generated-placeholder design via `coverage-agent-simplification`.
- [X] 7. Remove `scripts/coverage_agent.py` from the active execution contract.
- [X] 8. Remove `tests/unit/test_coverage_agent.py` from the active execution contract.
- [X] 9. Validate coverage, pre-commit coverage-check, ruff, pyright, and correction step tracking before review.
