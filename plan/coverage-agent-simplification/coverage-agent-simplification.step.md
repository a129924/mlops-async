# coverage-agent-simplification — Step Tracking

> **Executor**: Mark each implementation step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for implementation review.
> Update this file at:
> `plan/coverage-agent-simplification/coverage-agent-simplification.step.md`

## Workflow Stages

- [X] managed-worktree-created
- [X] correction-analysis-authoring
- [X] correction-plan-authoring
- [ ] human-plan-review
- [ ] parent-backfill
- [ ] implementation
- [ ] validation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 0. Create canonical managed worktree at `../mlops-async.worktrees/agent-20260522-coverage-agent-simplification` on branch `fix/a129924/coverage-agent-simplification`.
- [X] 1. Create `analysis/coverage-agent-simplification/requirements.md`.
- [X] 2. Create `analysis/coverage-agent-simplification/technical-spec.md`.
- [X] 3. Create `plan/coverage-agent-simplification/coverage-agent-simplification.plan.md`.
- [X] 4. Create `plan/coverage-agent-simplification/coverage-agent-simplification.spec.md`.
- [X] 5. Create `plan/coverage-agent-simplification/coverage-agent-simplification.step.md`.
- [ ] 6. Stop for human review before parent backfill or implementation edits.
- [ ] 7. Backfill `analysis/coverage-agent/requirements.md` and `analysis/coverage-agent/technical-spec.md`.
- [ ] 8. Backfill `plan/coverage-agent/coverage-agent.plan.md`, `.spec.md`, and `.step.md`.
- [ ] 9. Update `pyproject.toml` coverage fail-under to 90.
- [ ] 10. Update `.pre-commit-config.yaml` coverage-check hook name and `--cov-fail-under=90`.
- [ ] 11. Update `README.md` v0.10.4 coverage-agent wording without changing `VERSION` or `uv.lock`.
- [ ] 12. Delete `scripts/coverage_agent.py`.
- [ ] 13. Delete `tests/unit/test_coverage_agent.py`.
- [ ] 14. Search and remove stale current-truth references to `coverage_agent`, stub generation, and `assert False` helper behavior.
- [ ] 15. Run validation commands from the topic plan and confirm generated coverage JSON remains untracked.
