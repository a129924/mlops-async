> **Analysis layer — strict mode**
>
> `analysis/codex-skill-projection/requirements.md` and
> `analysis/codex-skill-projection/technical-spec.md` exist. This plan maps to
> that technical spec as the execution-facing baseline.

## Goal / Outcome

- 建立一份 repo-visible 的 projection topic plan，凍結 `mlops-async` 後續將 32 個
  同名 skill canonicalize 到 `skills/` 並 materialize 到 `.codex/skills/` 的執行合約。
- 當此 topic 完成時，repo 內應有可審核、可追溯、且不混入 agents / blockers 的
  planning package，供後續 creator work 使用。

## Scope

- **In scope**:
  - `analysis/codex-skill-projection/requirements.md`
  - `analysis/codex-skill-projection/technical-spec.md`
  - `plan/codex-skill-projection/codex-skill-projection.plan.md`
  - `plan/codex-skill-projection/codex-skill-projection.step.md`
  - `plan/codex-skill-projection/codex-skill-projection.checklist.md`
  - 32 個同名 skill 的 future canonicalization / projection contract

- **Out of scope**:
  - `copilot-instructions-init`
  - `api-client-porting-implementer`
  - `api-client-porting-planner`
  - `.github/agents/*`
  - runtime implementation
  - `README.md`、`VERSION`、release action

## Locked Decisions

- 此 topic 是 planning / governance topic，不是 runtime implementation topic。
- `copilot-instructions-init` 明確排除，不納入 projection candidate set。
- 同名 skill 的 canonical source 一律鎖定為 `agent-skills/skills/<name>/`。
- `mlops-async/.github/skills/<name>/` 是現況 compatibility surface，不可升格為
  新 canonical truth。
- future target 必須分成：
  - canonical `skills/<name>/`
  - projected `.codex/skills/<name>/`
- future projection 執行只能使用 `platform-projection-adapter`，且必須遵守
  dry-run -> `--apply` -> optional `--force` gate。
- `.github/agents/*` 完全分流到 `custom-agent-codex-compat`。
- 此 topic **不涉及 stable-library surfaces**。

## Boundaries / Exclusions

- Planning actor 只擁有 analysis 與 plan package。
- Creator 後續若執行此 topic，不得把 scope 擴張到 blockers、agents、或 release files。
- Reviewer 只審查 planning contract，不審查 future implementation correctness。
- Main Agent 擁有 worktree、draft-plan commit、review routing、planner final gate、與
  wait-human-check orchestration。
- 若後續需要 `.codex/skills` 的 support files（如 README / provenance）且它們不在
  本 plan 的 artifact contract 內，必須先修正 plan，再進入 creator work。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: this planning topic has completed draft authoring and is
  ready for independent plan review; later publish routing remains out of scope
  for this execution round.
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

- This topic will enter independent plan review immediately after the draft plan
  commit.
- No release action is declared.
- Shared-file coordination warning: future edits under `skills/` or `.codex/skills/`
  may conflict with other worktrees if they touch the same skill names.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/codex-skill-projection/requirements.md` | Planning actor | Frozen business baseline for projection planning |
| Topic technical spec baseline | `analysis/codex-skill-projection/technical-spec.md` | Planning actor | Frozen execution-facing technical baseline |
| Topic plan | `plan/codex-skill-projection/codex-skill-projection.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/codex-skill-projection/codex-skill-projection.step.md` | Planning actor | Workflow-step evidence for this topic package |
| Topic checklist | `plan/codex-skill-projection/codex-skill-projection.checklist.md` | Planning actor | Author / reviewer / final-gate checks for this topic package |

Projection candidate set (future creator targets, exact directory pairs):

- `skills/business-intent-alignment/` -> `.codex/skills/business-intent-alignment/`
- `skills/business-to-technical-translation/` -> `.codex/skills/business-to-technical-translation/`
- `skills/git-branch-naming/` -> `.codex/skills/git-branch-naming/`
- `skills/git-commit-convention/` -> `.codex/skills/git-commit-convention/`
- `skills/git-post-merge-workflow/` -> `.codex/skills/git-post-merge-workflow/`
- `skills/git-release-management/` -> `.codex/skills/git-release-management/`
- `skills/plan-creator/` -> `.codex/skills/plan-creator/`
- `skills/plan-reviewer/` -> `.codex/skills/plan-reviewer/`
- `skills/plan-step-tracker/` -> `.codex/skills/plan-step-tracker/`
- `skills/python-api-signature/` -> `.codex/skills/python-api-signature/`
- `skills/python-async-await/` -> `.codex/skills/python-async-await/`
- `skills/python-async-planning/` -> `.codex/skills/python-async-planning/`
- `skills/python-class-design/` -> `.codex/skills/python-class-design/`
- `skills/python-code-review/` -> `.codex/skills/python-code-review/`
- `skills/python-context-management/` -> `.codex/skills/python-context-management/`
- `skills/python-data-model-methods/` -> `.codex/skills/python-data-model-methods/`
- `skills/python-docstrings/` -> `.codex/skills/python-docstrings/`
- `skills/python-error-handling/` -> `.codex/skills/python-error-handling/`
- `skills/python-implementation-review/` -> `.codex/skills/python-implementation-review/`
- `skills/python-library-architecture/` -> `.codex/skills/python-library-architecture/`
- `skills/python-model-selection/` -> `.codex/skills/python-model-selection/`
- `skills/python-module-boundaries/` -> `.codex/skills/python-module-boundaries/`
- `skills/python-naming/` -> `.codex/skills/python-naming/`
- `skills/python-package-layout/` -> `.codex/skills/python-package-layout/`
- `skills/python-plan-authoring/` -> `.codex/skills/python-plan-authoring/`
- `skills/python-plan-review/` -> `.codex/skills/python-plan-review/`
- `skills/python-serialization-boundaries/` -> `.codex/skills/python-serialization-boundaries/`
- `skills/python-tdd-test-authoring/` -> `.codex/skills/python-tdd-test-authoring/`
- `skills/python-testing-pytest/` -> `.codex/skills/python-testing-pytest/`
- `skills/python-type-hints-strict/` -> `.codex/skills/python-type-hints-strict/`
- `skills/sense-env-scaffold/` -> `.codex/skills/sense-env-scaffold/`
- `skills/worktree-manager/` -> `.codex/skills/worktree-manager/`

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, or `.github/agents/*`.
- Listed paths are an executable contract; if later work drifts outside them, stop
  and realign the plan before implementation continues.

## Implementation Steps

1. Freeze the 32-skill projection candidate inventory and exclusion set in the
   analysis layer.
2. Author a repo-visible topic plan that distinguishes canonical `skills/` from
   projected `.codex/skills/`, and that keeps `.github/skills/` as a compatibility
   surface only.
3. Record the future creator gate that imports `platform-projection-adapter` and
   uses only dry-run -> `--apply` -> optional `--force`.
4. Record the future creator boundary that explicitly excludes blockers, agents,
   and release files from this topic.
5. Create the topic step tracker and checklist so later workflow phases can verify
   authoring, review, and final-gate evidence without guessing.

## Validation / Acceptance Checks

- `analysis/codex-skill-projection/requirements.md` and `technical-spec.md` both
  exist and stay aligned on the 32-skill candidate set.
- `plan/codex-skill-projection/codex-skill-projection.plan.md`,
  `.step.md`, and `.checklist.md` all exist.
- No artifact in this topic references `copilot-instructions-init`,
  `api-client-porting-implementer`, `api-client-porting-planner`, or `.github/agents/*`
  as projection candidates.
- The plan explicitly states that future projection uses `platform-projection-adapter`
  and does not invent a second projection algorithm.
- Stable-library intent is explicit as absent.

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

- After merge, no repository release action is required for this topic.
- This topic does not proceed to publish routing in the current execution round.

## Open Questions / Unresolved Items

- None.
