> **Analysis layer — strict mode**
>
> `analysis/codex-skill-blockers/requirements.md` and
> `analysis/codex-skill-blockers/technical-spec.md` exist. This rerun plan maps
> to that technical spec as the execution-facing migration-design baseline.

## Goal / Outcome

- 建立一份 repo-visible rerun topic plan，將舊的 blocker-only baseline 改寫成
  Codex porting workflow migration-design baseline。
- 當此 topic 停下時，repo 內應有一套可追溯的 rerun package，清楚說明：
  - 現有 `.github/skills/api-client-porting-*` 哪些語意要保留
  - 哪些 repo-specific contract 要抽離
  - 新的 `2 agent skills + 1 custom agent` 目標分工為何

## Inputs / Prerequisites

- Requirements baseline: `analysis/codex-skill-blockers/requirements.md`
- Technical baseline: `analysis/codex-skill-blockers/technical-spec.md`
- Workflow contract: `plan/agent-handoff-workflow.md`
- Prompt contract:
  - `.github/prompts/create-analysis.prompt.md`
  - `.github/prompts/create-agent-plan.prompt.md`
- Prior draft baseline commit replaced by this rerun: `639759c`

## Scope

- **In scope**:
  - `analysis/codex-skill-blockers/requirements.md`
  - `analysis/codex-skill-blockers/technical-spec.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.step.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`
  - `.github/skills/api-client-porting-planner/SKILL.md`
  - `.github/skills/api-client-porting-implementer/SKILL.md`
  - target design for `.agents/skills/api-client-porting-planner/SKILL.md`
  - target design for `.agents/skills/api-client-porting-implementer/SKILL.md`
  - target design for `.codex/agents/api-client-porting-workflow.agent.md`

- **Out of scope**:
  - 其他 `.github/skills/*`
  - actual `.agents/skills` materialization
  - actual `.codex/agents` materialization
  - runtime installation or load verification
  - `README.md`、`VERSION`

## Locked Decisions

- 本 topic 固定採用 `2 agent skills + 1 custom agent` 結構。
- `.github/skills/api-client-porting-*` 只作 bootstrap input，不是新的 authority。
- 新的 skill authority 目標是：
  - `.agents/skills/api-client-porting-planner/SKILL.md`
  - `.agents/skills/api-client-porting-implementer/SKILL.md`
- 新的 custom agent 目標是：
  - `.codex/agents/api-client-porting-workflow.agent.md`
- planner skill 保持 planning-only；implementer skill 保持 implementation-only；
  workflow agent 保持 orchestration-only。
- 本 topic creator pass 已完成，下一步是 independent plan review。
- 此 topic **不涉及 stable-library surfaces**。

## Boundaries / Exclusions

- Planning actor 只建立 rerun migration-design package。
- Creator 不得把本 topic 擴張成實際 artifact 建立，除非 human 另開新 topic。
- Main Agent 負責 review routing、fix routing、planner final gate 與 human-check handoff。
- 本 topic 不進 publish / merge / release routing。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: creator rerun work is complete, the plan is now ready for
  independent review, and this topic stops before publish / merge routing.
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

- Current handoff point is **review-ready**.
- This topic may advance through independent review and planner final gate, but
  it does not enter publish / merge routing in this execution round.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/codex-skill-blockers/requirements.md` | Planning actor | Frozen rerun migration baseline |
| Topic technical spec baseline | `analysis/codex-skill-blockers/technical-spec.md` | Planning actor | Frozen execution-facing migration-design baseline |
| Topic plan | `plan/codex-skill-blockers/codex-skill-blockers.plan.md` | Planning actor | Repo-visible execution contract for this rerun topic |
| Topic step tracker | `plan/codex-skill-blockers/codex-skill-blockers.step.md` | Planning actor | Workflow-step evidence for the rerun draft lane |
| Topic checklist | `plan/codex-skill-blockers/codex-skill-blockers.checklist.md` | Planning actor | Authoring / rerun-state validation for this topic |
| Bootstrap input | `.github/skills/api-client-porting-planner/SKILL.md` | Creator | Existing planner skill contract input for Codex-facing translation design |
| Bootstrap input | `.github/skills/api-client-porting-implementer/SKILL.md` | Creator | Existing implementer skill contract input for Codex-facing translation design |
| Future skill authority | `.agents/skills/api-client-porting-planner/SKILL.md` | Creator | Target planner skill authority after later implementation topic |
| Future skill authority | `.agents/skills/api-client-porting-implementer/SKILL.md` | Creator | Target implementer skill authority after later implementation topic |
| Future workflow agent | `.codex/agents/api-client-porting-workflow.agent.md` | Creator | Target Codex custom agent authority after later implementation topic |

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, `.github/skills/**`,
  `.agents/skills/**`, or `.codex/agents/**`.
- Listed future skill / agent paths are exact deferred targets, not files created in
  this execution round.
- If later work appears outside the listed paths, that is a plan-alignment
  problem and requires a plan update before continuing.

## Implementation Steps

1. Re-run the two-skill analysis baseline and replace the old blocker-only requirements.
2. Re-run the technical spec so it matches the selected `2 skills + 1 custom agent` design.
3. Author a repo-visible plan that records bootstrap inputs, future skill authorities,
   and the future workflow agent target.
4. Recreate the topic step tracker and checklist around the rerun migration-design semantics.
5. Create a new draft plan commit for this rerun topic.
6. Hand the rerun baseline to independent review so the replaced blocker-only
   baseline is no longer the review basis.

## Validation / Acceptance Checks

- All five topic artifacts exist at their exact paths.
- The plan explicitly cites both analysis inputs and the prompt / workflow contracts.
- The plan records exactly two target skills and one target custom agent.
- The plan truthfully claims `review-ready` and does not skip canonical review transitions.
- The plan does not authorize direct artifact creation under `.agents/skills/**` or `.codex/agents/**`.
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

- Whether later implementation should preserve sibling `reference.md` / `examples.md`
  layout as-is or normalize directory placement under `.agents/skills/*`
