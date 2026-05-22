# Coverage Agent — Python Implementation Plan

> **Analysis-layer routing: STRICT MODE**
> `analysis/coverage-agent/requirements.md` and
> `analysis/coverage-agent/technical-spec.md` have been backfilled by the
> `coverage-agent-simplification` correction topic.
>
> **Current truth:** enforce a 90% coverage gate and use pytest-cov JSON evidence for
> Agent / human triage. The previous custom helper and generated placeholder tests are
> superseded and must not be recreated.

---

## Goal / Outcome

Align the coverage workflow with repository governance:

- `pyproject.toml` and `.pre-commit-config.yaml` enforce **90%** unit-test coverage.
- pytest-cov writes `.coverage-reports/coverage.json` and `term-missing` output.
- Agents read Coverage.py JSON evidence and report scope gaps / human-review needs.
- `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py` remain deleted.
- Parent artifacts point to `coverage-agent-simplification` as the correction record.

---

## Scope

- **In scope**:
  - `pyproject.toml` coverage threshold alignment.
  - `.pre-commit-config.yaml` `coverage-check` name and entry alignment.
  - README status wording correction.
  - Parent analysis / plan / spec / step backfill.
  - Deletion of superseded helper artifacts.

- **Out of scope**:
  - No changes to `src/mlops_async/` library behavior.
  - No custom AST coverage mapper, parser, helper CLI, or generated placeholder tests.
  - No changes to `.github/skills/plan-step-tracker/scripts/step_tracker.py`.
  - No `VERSION`, `uv.lock`, git tag, or release action.
  - No committed `.coverage-reports/coverage.json`.

---

## Locked Decisions

- Coverage threshold is 90%.
- pytest-cov / Coverage.py JSON is the only machine-readable coverage evidence source.
- Agents may triage gaps but must not write tests automatically.
- The old helper / placeholder generation design is a superseded historical design.
- Correction artifacts remain at `analysis/coverage-agent-simplification/` and
  `plan/coverage-agent-simplification/`.

---

## Boundaries / Exclusions

- Do not generate `assert False` placeholders to satisfy coverage.
- Do not modify source files under `src/mlops_async/`.
- Do not alter manual pytest hook semantics in `.pre-commit-config.yaml`.
- Do not commit generated coverage JSON.

---

## Status / Allowed Transitions

- **Current**: `creator-in-progress` for accepted backfill and simplification implementation.
- **Execution model**: managed worktree -> correction implementation -> validation -> review -> publish -> PR -> merge.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `pr-open` -> `merged`
  - `merged` -> terminal

---

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Parent requirements | `analysis/coverage-agent/requirements.md` | Creator | Accepted backfill current truth |
| Parent technical spec | `analysis/coverage-agent/technical-spec.md` | Creator | Accepted backfill technical current truth |
| Parent plan | `plan/coverage-agent/coverage-agent.plan.md` | Creator | Accepted backfill execution contract |
| Parent spec | `plan/coverage-agent/coverage-agent.spec.md` | Creator | Accepted backfill acceptance scenarios |
| Parent step tracker | `plan/coverage-agent/coverage-agent.step.md` | Creator | Accepted backfill step record |
| Correction artifacts | `analysis/coverage-agent-simplification/*`, `plan/coverage-agent-simplification/*` | Planner / Creator | Historical correction record |
| Coverage config | `pyproject.toml` | Creator | 90% gate and JSON output |
| Coverage pre-commit hook | `.pre-commit-config.yaml` | Creator | Local coverage gate |
| README status text | `README.md` | Creator | User-facing wording correction |
| Deleted helper | `scripts/coverage_agent.py` | Creator | Superseded artifact removed |
| Deleted helper tests | `tests/unit/test_coverage_agent.py` | Creator | Superseded tests removed |

Artifact path notes:

- This topic does not modify `VERSION`, `uv.lock`, `.github/copilot-instructions.md`, or
  `.github/skills/plan-step-tracker/scripts/step_tracker.py`.
- `.coverage-reports/coverage.json` is validation evidence only and must remain untracked.

---

## Stable library metadata

- `README row`: describe v0.10.4 as 90% coverage gate plus pytest-cov JSON / human feedback triage.
- `VERSION bump`: none.
- `timing`: documentation correction occurs in this correction topic; no release action.
- `rationale`: README previously described deleted helper behavior.
- `release-note expectations`: none; no git tag.

---

## Implementation Steps

1. Confirm managed worktree and branch.
2. Backfill parent `analysis/coverage-agent/*` artifacts.
3. Backfill parent `plan/coverage-agent/*` artifacts.
4. Set coverage gate to 90 in `pyproject.toml`.
5. Update `.pre-commit-config.yaml` `coverage-check` hook name and `--cov-fail-under=90`.
6. Update README coverage-agent wording without changing release version sources.
7. Delete `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py`.
8. Search for stale helper / placeholder references and reword current-truth references.
9. Run validation commands and confirm generated coverage JSON remains untracked.

---

## Validation / Acceptance Checks

- `pyproject.toml` and `.pre-commit-config.yaml` use 90% coverage gate.
- README no longer describes helper-generated test placeholders.
- `scripts/coverage_agent.py` and `tests/unit/test_coverage_agent.py` do not exist.
- Parent artifacts state helper / placeholder generation is superseded, not active behavior.
- `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing` passes.
- `uv run pre-commit run coverage-check --all-files` passes.
- `uv run ruff check` passes.
- `uv run pyright` passes.
- Step tracker validation for `coverage-agent-simplification` passes.
- `git status --short` does not include `.coverage-reports/coverage.json`, `VERSION`, or `uv.lock`.

---

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

---

## Post-merge / release actions

No release action is required. After merge, follow repository post-merge cleanup from the managed
worktree context. Do not create a release tag for this correction topic.

---

## Open Questions / Unresolved Items

None.
