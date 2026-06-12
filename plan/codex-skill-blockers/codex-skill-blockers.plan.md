> **Analysis layer — strict mode**
>
> `analysis/codex-skill-blockers/requirements.md` and
> `analysis/codex-skill-blockers/technical-spec.md` exist. This plan maps to
> that technical spec as the execution-facing baseline.

## Goal / Outcome

- 建立一份 repo-visible blocker topic plan，凍結兩個 `api-client-porting-*` skills
  不能直接進入 Codex skill projection 的執行合約。
- 當此 topic 停下時，repo 內應有一套可追溯的 blocker package，清楚說明：
  - 目前為何不能 projection
  - 未來還缺哪些 prerequisite

## Scope

- **In scope**:
  - `analysis/codex-skill-blockers/requirements.md`
  - `analysis/codex-skill-blockers/technical-spec.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.step.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`
  - `.github/skills/api-client-porting-implementer/`
  - `.github/skills/api-client-porting-planner/`

- **Out of scope**:
  - 同名可 projection skills
  - `.github/agents/*`
  - actual canonicalization
  - actual `.codex/skills` projection
  - `README.md`、`VERSION`

## Locked Decisions

- 這兩個 skill 屬 blocker topic，不可直接進入 projection lane。
- 在 future canonical `skills/api-client-porting-*` 真正存在前，不得規劃
  `platform-projection-adapter --apply`。
- 本 topic 只做到 draft plan commit，**不進 independent plan review**。
- 本 topic 是 planning / governance topic，不是 implementation topic。
- 此 topic **不涉及 stable-library surfaces**。

## Boundaries / Exclusions

- Planning actor 只建立 blocker package。
- Creator 後續不得把本 topic 擴張成 actual skill authoring，除非 human 另開新 topic。
- Reviewer 與 planner final gate 在本輪不進入；topic 明確停在 draft-plan commit 後。
- Main Agent 僅負責 draft commit routing，不假裝此 topic 已完成 full workflow。

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **Execution model**: this topic intentionally stops after draft plan commit and
  pauses before independent review.
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

- Topic pause point is **after draft plan commit, before review-ready handoff**.
- Do not advance to `review-ready` or `reviewer-in-progress` in this execution round.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/codex-skill-blockers/requirements.md` | Planning actor | Frozen blocker baseline |
| Topic technical spec baseline | `analysis/codex-skill-blockers/technical-spec.md` | Planning actor | Frozen execution-facing blocker baseline |
| Topic plan | `plan/codex-skill-blockers/codex-skill-blockers.plan.md` | Planning actor | Repo-visible execution contract for this blocker topic |
| Topic step tracker | `plan/codex-skill-blockers/codex-skill-blockers.step.md` | Planning actor | Workflow-step evidence for the paused draft lane |
| Topic checklist | `plan/codex-skill-blockers/codex-skill-blockers.checklist.md` | Planning actor | Authoring / pause-state validation for this topic |
| Current blocker source | `.github/skills/api-client-porting-implementer/` | Creator | Existing compatibility-only source that lacks canonical counterpart |
| Current blocker source | `.github/skills/api-client-porting-planner/` | Creator | Existing compatibility-only source that lacks canonical counterpart |
| Future prerequisite | `skills/api-client-porting-implementer/` | Creator | Required canonical source before any later projection topic |
| Future prerequisite | `skills/api-client-porting-planner/` | Creator | Required canonical source before any later projection topic |
| Future projected target | `.codex/skills/api-client-porting-implementer/` | Creator | Deferred projection target; not executable in this topic |
| Future projected target | `.codex/skills/api-client-porting-planner/` | Creator | Deferred projection target; not executable in this topic |

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, or `.github/agents/*`.
- Listed future prerequisite / projected paths are deferred targets, not files created in
  this execution round.

## Implementation Steps

1. Freeze the two-skill blocker inventory and the no-direct-projection rule in the
   analysis layer.
2. Author a repo-visible plan that records both current blocker sources and the
   future canonical prerequisites.
3. Create the topic step tracker and checklist.
4. Create a draft plan commit for this topic.
5. Pause the topic before independent review so later requirement expansion can
   happen without pretending the full workflow already ran.

## Validation / Acceptance Checks

- All five topic artifacts exist at their exact paths.
- The plan explicitly says this topic stops after draft plan commit.
- The plan does not claim `review-ready`, `reviewer-in-progress`, or `approved`.
- The plan does not authorize direct projection from `.github/skills/api-client-porting-*`.
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

- No repository release action is required for this topic.
- This topic does not proceed to publish routing in the current execution round.

## Open Questions / Unresolved Items

- Future canonicalization topic shape for `api-client-porting-implementer`
- Future canonicalization topic shape for `api-client-porting-planner`
