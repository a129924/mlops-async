> **Analysis layer — strict mode**
>
> `analysis/codex-skill-blockers/requirements.md` and
> `analysis/codex-skill-blockers/technical-spec.md` exist. This rerun plan maps
> 100% to that technical spec as the execution-facing implementation baseline.

## Goal / Outcome

- 建立一份 repo-visible rerun implementation topic plan，將舊的 design-only
  baseline 改寫成 creator 之後真的要建檔的 execution contract。
- 當此 topic 停下時，repo 內應有一套可追溯的 implementation draft package，清楚說明：
  - 哪些 bootstrap input 會被拿來翻譯
  - creator 這一輪會直接建立哪些 exact artifact files
  - 哪些 repo-specific contract 只能保留為 optional/default input

## Inputs / Prerequisites

- Requirements baseline: `analysis/codex-skill-blockers/requirements.md`
- Technical baseline: `analysis/codex-skill-blockers/technical-spec.md`
- Workflow contract: `plan/agent-handoff-workflow.md`
- Prompt contract:
  - `.github/prompts/create-analysis.prompt.md`
  - `.github/prompts/create-agent-plan.prompt.md`
- Bootstrap input files:
  - `.github/skills/api-client-porting-planner/SKILL.md`
  - `.github/skills/api-client-porting-planner/reference.md`
  - `.github/skills/api-client-porting-planner/examples.md`
  - `.github/skills/api-client-porting-planner/templates/family-map.md`
  - `.github/skills/api-client-porting-implementer/SKILL.md`
  - `.github/skills/api-client-porting-implementer/reference.md`
  - `.github/skills/api-client-porting-implementer/examples.md`
  - `.github/skills/api-client-porting-implementer/templates/porting-result.md`

## Scope

- **In scope**:
  - `analysis/codex-skill-blockers/requirements.md`
  - `analysis/codex-skill-blockers/technical-spec.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.plan.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.step.md`
  - `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`
  - `.agents/skills/api-client-porting-planner/SKILL.md`
  - `.agents/skills/api-client-porting-planner/reference.md`
  - `.agents/skills/api-client-porting-planner/examples.md`
  - `.agents/skills/api-client-porting-planner/templates/family-map.md`
  - `.agents/skills/api-client-porting-implementer/SKILL.md`
  - `.agents/skills/api-client-porting-implementer/reference.md`
  - `.agents/skills/api-client-porting-implementer/examples.md`
  - `.agents/skills/api-client-porting-implementer/templates/porting-result.md`
  - `.codex/agents/api-client-porting-workflow.agent.md`

- **Out of scope**:
  - 其他 `.github/skills/*`
  - runtime installation / load verification
  - `README.md`
  - `VERSION`

## Locked Decisions

- 本 topic 是 **implementation topic**，不是 design-only / blocker-only topic。
- `.github/skills/api-client-porting-*` 只作 bootstrap input，不是新的 authority。
- creator implementation scope 固定為：
  - `.agents/skills/api-client-porting-planner/SKILL.md`
  - `.agents/skills/api-client-porting-planner/reference.md`
  - `.agents/skills/api-client-porting-planner/examples.md`
  - `.agents/skills/api-client-porting-planner/templates/family-map.md`
  - `.agents/skills/api-client-porting-implementer/SKILL.md`
  - `.agents/skills/api-client-porting-implementer/reference.md`
  - `.agents/skills/api-client-porting-implementer/examples.md`
  - `.agents/skills/api-client-porting-implementer/templates/porting-result.md`
  - `.codex/agents/api-client-porting-workflow.agent.md`
- planner artifact set 必須保留 planning-only 核心語意。
- implementer artifact set 必須保留 implementation-only 核心語意。
- workflow agent 必須保持 orchestration-only。
- 本 rerun 只做到新的 draft plan commit，**不進 reviewer / fix / planner final gate**。
- 此 topic **不涉及 stable-library surfaces**。

## Boundaries / Exclusions

- Planning actor 只重跑 implementation baseline，不直接建立最終 artifact。
- Creator 後續只能在列舉的 exact artifact paths 內實作。
- Main Agent 這一輪只做到 draft plan commit routing，不前進 reviewer gate。
- 本 topic 不進 publish / merge / release routing。

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **Execution model**: this topic reruns analysis and planning artifacts to
  produce a new implementation baseline, then stops after a new draft plan
  commit and before any reviewer gate begins.
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

- Topic pause point is **after new draft plan commit, before review-ready handoff**.
- Do not advance to `review-ready`, `reviewer-in-progress`, or any later gate in this execution round.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/codex-skill-blockers/requirements.md` | Planning actor | Frozen rerun implementation baseline |
| Topic technical spec baseline | `analysis/codex-skill-blockers/technical-spec.md` | Planning actor | Frozen execution-facing implementation baseline |
| Topic plan | `plan/codex-skill-blockers/codex-skill-blockers.plan.md` | Planning actor | Repo-visible execution contract for this implementation topic |
| Topic step tracker | `plan/codex-skill-blockers/codex-skill-blockers.step.md` | Planning actor | Workflow-step evidence for the pre-review implementation draft lane |
| Topic checklist | `plan/codex-skill-blockers/codex-skill-blockers.checklist.md` | Planning actor | Authoring / scope validation for this implementation topic |
| Bootstrap input | `.github/skills/api-client-porting-planner/SKILL.md` | Creator | Existing planner skill contract input for Codex-facing implementation |
| Bootstrap input | `.github/skills/api-client-porting-planner/reference.md` | Creator | Existing planner supporting reference input |
| Bootstrap input | `.github/skills/api-client-porting-planner/examples.md` | Creator | Existing planner examples input |
| Bootstrap input | `.github/skills/api-client-porting-planner/templates/family-map.md` | Creator | Existing planner template input |
| Bootstrap input | `.github/skills/api-client-porting-implementer/SKILL.md` | Creator | Existing implementer skill contract input for Codex-facing implementation |
| Bootstrap input | `.github/skills/api-client-porting-implementer/reference.md` | Creator | Existing implementer supporting reference input |
| Bootstrap input | `.github/skills/api-client-porting-implementer/examples.md` | Creator | Existing implementer examples input |
| Bootstrap input | `.github/skills/api-client-porting-implementer/templates/porting-result.md` | Creator | Existing implementer template input |
| Creator artifact | `.agents/skills/api-client-porting-planner/SKILL.md` | Creator | New planner skill contract artifact |
| Creator artifact | `.agents/skills/api-client-porting-planner/reference.md` | Creator | New planner supporting reference artifact |
| Creator artifact | `.agents/skills/api-client-porting-planner/examples.md` | Creator | New planner examples artifact |
| Creator artifact | `.agents/skills/api-client-porting-planner/templates/family-map.md` | Creator | New planner template artifact |
| Creator artifact | `.agents/skills/api-client-porting-implementer/SKILL.md` | Creator | New implementer skill contract artifact |
| Creator artifact | `.agents/skills/api-client-porting-implementer/reference.md` | Creator | New implementer supporting reference artifact |
| Creator artifact | `.agents/skills/api-client-porting-implementer/examples.md` | Creator | New implementer examples artifact |
| Creator artifact | `.agents/skills/api-client-porting-implementer/templates/porting-result.md` | Creator | New implementer template artifact |
| Creator artifact | `.codex/agents/api-client-porting-workflow.agent.md` | Creator | New Codex workflow agent artifact |

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, or any path outside the listed files.
- Listed creator artifact paths are executable implementation scope, not deferred design targets.
- If later work appears outside the listed paths, that is a plan-alignment problem and requires a plan update before continuing.

## Implementation Steps

1. Re-run the implementation requirements baseline and replace the old design-only requirements.
2. Re-run the technical spec so it matches the selected implementation artifact set.
3. Recreate the topic plan, step tracker, and checklist around exact creator implementation scope.
4. Freeze creator implementation scope for the planner skill artifact set:
   - `.agents/skills/api-client-porting-planner/SKILL.md`
   - `.agents/skills/api-client-porting-planner/reference.md`
   - `.agents/skills/api-client-porting-planner/examples.md`
   - `.agents/skills/api-client-porting-planner/templates/family-map.md`
5. Freeze creator implementation scope for the implementer skill artifact set:
   - `.agents/skills/api-client-porting-implementer/SKILL.md`
   - `.agents/skills/api-client-porting-implementer/reference.md`
   - `.agents/skills/api-client-porting-implementer/examples.md`
   - `.agents/skills/api-client-porting-implementer/templates/porting-result.md`
6. Freeze creator implementation scope for the custom workflow agent artifact:
   - `.codex/agents/api-client-porting-workflow.agent.md`
7. Freeze validation requirements that the new skill / agent artifacts must stay semantically aligned with the bootstrap inputs while downgrading repo-specific contract to optional/default input.
8. Create a new draft plan commit for this rerun implementation topic.

## Validation / Acceptance Checks

- All five topic artifacts exist at their exact paths.
- The plan explicitly cites both analysis inputs and all bootstrap input files.
- `Artifact Paths` list exact creator artifact file paths, not only directories.
- The plan records creator implementation scope for two skill artifact sets and one workflow agent artifact.
- The plan does not place actual `.agents/skills/*` or `.codex/agents/*` creation in out of scope.
- The plan does not claim `review-ready`, `reviewer-in-progress`, or `approved`.
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

- None for the draft implementation baseline. Any new artifact outside the declared scope requires a plan update before creator execution.
