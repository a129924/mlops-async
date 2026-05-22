# coverage-agent-simplification — Topic Plan

> **Analysis-layer routing: STRICT MODE**
>
> `analysis/coverage-agent-simplification/requirements.md` and
> `analysis/coverage-agent-simplification/technical-spec.md` exist and define the
> execution-facing source of truth for this correction topic.
>
> This topic does not silently override the original `coverage-agent` analysis. It creates a
> correction source of truth first, then backfills parent artifacts after review approval.

## Goal / Outcome

Create the `coverage-agent-simplification` correction topic so the repository no longer treats a
custom coverage helper and auto-generated test stubs as required current behavior.

When complete:

- Coverage gate semantics are aligned to 90%.
- pytest-cov JSON remains the only machine-readable coverage evidence source.
- `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py` are removed.
- `README.md` describes coverage JSON triage / human feedback, not stub generation.
- Parent `coverage-agent` artifacts are backfilled to point at this correction topic as current truth.

## Scope

- **In scope**:
  - Create correction artifacts:
    - `analysis/coverage-agent-simplification/requirements.md`
    - `analysis/coverage-agent-simplification/technical-spec.md`
    - `plan/coverage-agent-simplification/coverage-agent-simplification.plan.md`
    - `plan/coverage-agent-simplification/coverage-agent-simplification.spec.md`
    - `plan/coverage-agent-simplification/coverage-agent-simplification.step.md`
  - Backfill parent artifacts:
    - `analysis/coverage-agent/requirements.md`
    - `analysis/coverage-agent/technical-spec.md`
    - `plan/coverage-agent/coverage-agent.plan.md`
    - `plan/coverage-agent/coverage-agent.spec.md`
    - `plan/coverage-agent/coverage-agent.step.md`
  - Align coverage gate:
    - `pyproject.toml`
    - `.pre-commit-config.yaml`
  - Correct README wording:
    - `README.md`
  - Delete overdesigned helper artifacts:
    - `scripts/coverage_agent.py`
    - `tests/unit/test_coverage_agent.py`

- **Out of scope**:
  - No changes to `src/mlops_async/` behavior.
  - No GitHub Actions / CI coverage gate.
  - No custom AST coverage mapper, coverage parser, or stub generator.
  - No modification to `.github/skills/plan-step-tracker/scripts/step_tracker.py`.
  - No `VERSION`, `uv.lock`, or git tag change.
  - No committed `.coverage-reports/coverage.json`.

## Locked Decisions

- Use canonical managed worktree path:
  `../mlops-async.worktrees/agent-20260522-coverage-agent-simplification`.
- Branch:
  `fix/a129924/coverage-agent-simplification`.
- Coverage threshold is 90%, matching existing repo governance.
- Delete `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py`.
- README is a stable surface and will be corrected, but this topic has `VERSION` no-bump and no tag.
- pytest-cov JSON is the only machine-readable coverage evidence source.
- Correction artifacts are historical decision records; parent artifacts become current truth only after accepted backfill.
- No `review-log` artifact is required because routing does not depend on multi-round reviewer feedback.
- No round cap is declared for this topic.

## Boundaries / Exclusions

- Do not reinterpret coverage gate failure as permission to generate placeholder tests.
- Do not keep stale current-truth references to deleted helper artifacts.
- Do not edit implementation files under `src/mlops_async/`.
- Do not change release version sources (`VERSION`, `uv.lock`, git tag).
- Do not edit in the main worktree; all changes occur in the managed worktree.
- Stop after correction plan/spec/step authoring for human review before parent backfill or implementation edits.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: managed worktree -> correction analysis -> correction plan/spec/step -> human review -> creator implementation -> reviewer -> publish -> PR -> merge. This topic has no release action; `merged` is terminal.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- Worktree creation precedes all repo-visible edits.
- Managed worktree path:
  `../mlops-async.worktrees/agent-20260522-coverage-agent-simplification`.
- Human review gate occurs after correction analysis / plan / spec / step authoring and before parent backfill.
- Shared planning and governance files may conflict with other worktrees; coordinate before backfill if other worktrees touch the same paths.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Correction requirements | `analysis/coverage-agent-simplification/requirements.md` | Planning actor | New business baseline for simplification |
| Correction technical spec | `analysis/coverage-agent-simplification/technical-spec.md` | Planning actor | Execution-facing correction source of truth |
| Correction topic plan | `plan/coverage-agent-simplification/coverage-agent-simplification.plan.md` | Planning actor | Repo-visible execution contract |
| Correction spec | `plan/coverage-agent-simplification/coverage-agent-simplification.spec.md` | Planning actor | Acceptance scenarios for the correction |
| Correction step tracker | `plan/coverage-agent-simplification/coverage-agent-simplification.step.md` | Creator | Implementation Gate step source |
| Parent requirements | `analysis/coverage-agent/requirements.md` | Creator | Current truth after accepted backfill |
| Parent technical spec | `analysis/coverage-agent/technical-spec.md` | Creator | Current truth after accepted backfill |
| Parent plan | `plan/coverage-agent/coverage-agent.plan.md` | Creator | Current truth after accepted backfill |
| Parent spec | `plan/coverage-agent/coverage-agent.spec.md` | Creator | Current truth after accepted backfill |
| Parent step tracker | `plan/coverage-agent/coverage-agent.step.md` | Creator | Current truth after accepted backfill |
| Coverage config | `pyproject.toml` | Creator | 90% coverage gate and JSON output |
| Coverage pre-commit hook | `.pre-commit-config.yaml` | Creator | Local coverage gate |
| README status text | `README.md` | Creator | Stable surface wording correction |
| Removed helper | `scripts/coverage_agent.py` | Creator | Delete superseded helper |
| Removed helper tests | `tests/unit/test_coverage_agent.py` | Creator | Delete tests for removed helper |

Artifact path notes:

- This topic modifies `README.md`.
- This topic does not modify `VERSION`, `uv.lock`, `.github/copilot-instructions.md`, or `.github/skills/plan-step-tracker/scripts/step_tracker.py`.
- `.coverage-reports/coverage.json` is generated validation evidence only and must remain untracked.
- If implementation drifts outside listed paths, stop and update the plan before continuing.
- Correction artifacts are historical truth; parent artifacts are current truth after accepted backfill.
- Correction closure requires parent artifact backfill to be complete before the topic can be treated as current truth.

## Stable library metadata

- `README row`: update the v0.10.4 status entry so it describes 90% coverage gate plus pytest-cov JSON / human feedback triage. Remove claims that `scripts/coverage_agent.py` generates stubs.
- `VERSION bump`: no bump; `VERSION`, `pyproject.toml` version, and `uv.lock` package version remain unchanged.
- `timing`: README correction happens during `publish-in-progress`; no release step.
- `rationale`: README currently describes a helper that this correction deletes, so the user-facing status text must be corrected without implying a new release.
- `release-note expectations`: none; no git tag.

## Implementation Steps

1. Confirm the managed worktree and branch are active.
2. Create correction analysis artifacts under `analysis/coverage-agent-simplification/`.
3. Create correction plan/spec/step artifacts under `plan/coverage-agent-simplification/`.
4. Stop for human review before parent backfill.
5. After approval, backfill parent `analysis/coverage-agent/*` and `plan/coverage-agent/*`.
6. Set coverage gate to 90 in `pyproject.toml` and `.pre-commit-config.yaml`.
7. Update README coverage-agent wording without changing release version sources.
8. Delete `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py`.
9. Search for stale helper / stub references and remove or reword current-truth references.
10. Run validation commands and confirm generated coverage JSON remains untracked.

## Validation / Acceptance Checks

- `git worktree list` shows the managed worktree at
  `../mlops-async.worktrees/agent-20260522-coverage-agent-simplification`.
- `pyproject.toml` and `.pre-commit-config.yaml` use 90% coverage gate.
- `README.md` no longer describes stub generation.
- `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py` do not exist.
- Parent artifacts point to this correction topic and no longer treat stub generation as current truth.
- `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing` passes.
- `uv run pre-commit run coverage-check --all-files` passes.
- `uv run ruff check` passes.
- `uv run pyright` passes.
- `uv run python .github/skills/plan-step-tracker/scripts/step_tracker.py check_impl_steps_succeeded coverage-agent-simplification` passes when implementation steps are complete.
- `git status --short` does not include `.coverage-reports/coverage.json`, `VERSION`, or `uv.lock`.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release action is required.

After merge, run the repository post-merge workflow from the managed worktree context:

1. Confirm the PR is merged into `dev`.
2. Use `worktree-manager` release semantics for
   `../mlops-async.worktrees/agent-20260522-coverage-agent-simplification`.
3. Keep destructive deletion separate from release; do not remove the worktree unless an explicit remove request passes the worktree-manager safety gate.
4. Do not create a release tag for this topic.

## Open Questions / Unresolved Items

None.
