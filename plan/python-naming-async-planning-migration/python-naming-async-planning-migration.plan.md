## Goal / Outcome

- Create a repo-visible migration contract for bringing `python-naming` and `python-async-planning` into `mlops-async`, including the minimum supporting refreshes required to keep existing installed skills internally consistent.
- Semantic warning: this topic is being authored without `analysis/python-naming-async-planning-migration/requirements.md` and `analysis/python-naming-async-planning-migration/technical-spec.md`; scope is based on explicit human direction plus completed review findings.

## Scope

- **In scope**:
  - add `.github/skills/python-naming/` from `agent-skills` into `mlops-async`
  - add `.github/skills/python-async-planning/` from `agent-skills` into `mlops-async`
  - refresh `mlops-async/.github/skills/python-plan-authoring/` artifacts that must align with the async-planning contract
  - refresh `mlops-async/.github/skills/python-plan-review/` artifacts that must align with the async-planning contract
  - update `mlops-async/.github/copilot-instructions.md` so installed-skill inventory and direct references stay accurate after the new skills land
  - verify that existing `python-code-review` and `python-docstrings` signposts to `python-naming` now resolve to an installed skill

- **Out of scope**:
  - migrating any other reviewed current-only skill
  - changing `README.md`, `VERSION`, git tags, or release timing
  - implementing unrelated shared-item refreshes already reviewed in earlier batches
  - changing workflow agents unless the later implementation finds a direct contract dependency and the plan is amended first

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**; no `README.md`, `VERSION`, or release action is part of this migration topic.
- This topic remains a **single migration topic** covering both `python-naming` and `python-async-planning`; do not split into separate topic plans unless a later human decision says so.
- `python-async-planning` is included in this migration topic by explicit human decision even though it was intentionally excluded from the earlier review track.
- `python-naming` must be migrated as a full skill folder because `mlops-async` already contains repo-local signposts to `python-naming` in installed skills.
- `python-async-planning` must not be migrated alone; the migration must also refresh `python-plan-authoring` and `python-plan-review` so the async-planning contract becomes enforceable inside `mlops-async`.
- Implementation must happen in the managed topic worktree on branch `plan/andrew/python-naming-async-planning-migration`, based on `dev`.

## Boundaries / Exclusions

- Keep this topic limited to skill installation and internal contract alignment for the two chosen skills.
- Do not reopen the broader candidate-review workflow inside this topic.
- Do not edit files outside the listed artifact paths without first updating this plan.
- Do not treat `.github/copilot-instructions.md` inventory updates as permission to change repo governance or contributor workflow wording beyond what the new installed skills require.
- Do not infer that `python-async-planning` requires unrelated changes to `python-implementation-workflow.agent.md`; if that becomes necessary, stop and amend the plan rather than drifting scope.

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops at merge and does not declare a release action
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

- No release action is planned for this topic.
- If implementation discovers additional dependency files outside the listed artifact paths, stop and repair this plan before continuing.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/python-naming-async-planning-migration/python-naming-async-planning-migration.plan.md` | Planning actor | Repo-visible execution contract for this migration topic |
| New skill | `.github/skills/python-naming/SKILL.md` | Creator | Install the naming-policy skill contract into `mlops-async` |
| New skill | `.github/skills/python-naming/reference.md` | Creator | Install the naming examples and edge-case reference used by `python-naming` |
| New skill | `.github/skills/python-async-planning/SKILL.md` | Creator | Install the async-planning skill contract into `mlops-async` |
| New skill | `.github/skills/python-async-planning/reference.md` | Creator | Install the async-planning reference guidance |
| New skill | `.github/skills/python-async-planning/examples.md` | Creator | Install the async-planning examples required by the skill folder |
| Supporting refresh | `.github/skills/python-plan-authoring/SKILL.md` | Creator | Reintroduce async-planning trigger/exemption contract into plan authoring |
| Supporting refresh | `.github/skills/python-plan-authoring/examples.md` | Creator | Keep plan-authoring examples aligned with async-planning expectations |
| Supporting refresh | `.github/skills/python-plan-authoring/templates/python-plan-template.md` | Creator | Add the repo-visible async-planning scaffold used by authored plans |
| Supporting refresh | `.github/skills/python-plan-review/SKILL.md` | Creator | Reintroduce async-planning review gates into plan review |
| Supporting refresh | `.github/skills/python-plan-review/checklist.md` | Creator | Keep plan-review checklist aligned with async-planning review checks |
| Supporting refresh | `.github/skills/python-plan-review/examples.md` | Creator | Keep plan-review examples aligned with async-planning review outcomes |
| Inventory update | `.github/copilot-instructions.md` | Creator | Update installed-skill inventory count and any direct references needed after migration |

Artifact path notes:

- This topic does **not** modify `README.md` or `VERSION`.
- Treat the listed paths as the executable contract for implementation and review.
- If later work needs to touch `docs/ARCHITECTURE.md` or another file not listed here, stop and amend the plan before editing.

## Implementation Steps

1. Inspect the source folders `../agent-skills/.github/skills/python-naming/` and `../agent-skills/.github/skills/python-async-planning/`, then copy the listed skill artifacts into the matching target paths under `mlops-async/.github/skills/`.
2. Refresh `mlops-async/.github/skills/python-plan-authoring/SKILL.md`, `examples.md`, and `templates/python-plan-template.md` from `agent-skills` so authored plans inside `mlops-async` can express `Async-planning status` and the required async-planning subsections.
3. Refresh `mlops-async/.github/skills/python-plan-review/SKILL.md`, `checklist.md`, and `examples.md` from `agent-skills` so review-time async trigger, exemption, and retrofit checks match the newly installed async-planning contract.
4. Update `mlops-async/.github/copilot-instructions.md` to reflect the new installed skill count and any direct references that should mention the newly installed skills.
5. Verify that existing `mlops-async/.github/skills/python-code-review/` and `mlops-async/.github/skills/python-docstrings/` references to `python-naming` now resolve to a real installed skill path without requiring further text changes.
6. Review the changed artifact set against this plan and stop for plan repair if any additional file path appears necessary.

## Validation / Acceptance Checks

- `mlops-async/.github/skills/python-naming/` exists and contains `SKILL.md` plus `reference.md`
- `mlops-async/.github/skills/python-async-planning/` exists and contains `SKILL.md`, `reference.md`, and `examples.md`
- `mlops-async/.github/skills/python-plan-authoring/SKILL.md` explicitly includes the async-planning contract language, and the plan template contains the async-planning scaffold
- `mlops-async/.github/skills/python-plan-review/SKILL.md` and `checklist.md` explicitly include async-planning trigger/exemption coverage and retrofit-required behavior
- `.github/copilot-instructions.md` no longer contains the stale `28 installed Agent Skills` count after the new skills are added
- existing installed skill references to `python-naming` resolve to an installed folder that now exists
- no unplanned file path outside `Artifact Paths` is modified

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

- No repository release action is required for this topic.
- After merge, normal local sync or worktree cleanup may happen under separate workflow routing, but no `VERSION` or tag action belongs to this migration topic.

## Open Questions / Unresolved Items

- None.
