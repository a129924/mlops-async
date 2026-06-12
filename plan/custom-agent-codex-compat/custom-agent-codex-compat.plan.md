> **Analysis layer — strict mode**
>
> `analysis/custom-agent-codex-compat/requirements.md` and
> `analysis/custom-agent-codex-compat/technical-spec.md` exist. This plan maps
> to that technical spec as the execution-facing baseline.

## Goal / Outcome

- 建立一份 repo-visible custom-agent compatibility topic plan，凍結
  `.github/agents/python-implementation-workflow.agent.md` 目前只能停在 governance
  / compatibility planning lane 的執行合約。
- 當此 topic 停下時，repo 內應有一套可追溯的 draft package，清楚說明：
  - 目前 agent compatibility 缺什麼治理契約
  - 為何不能直接前進到 `.codex/agents`

## Scope

- **In scope**:
  - `analysis/custom-agent-codex-compat/requirements.md`
  - `analysis/custom-agent-codex-compat/technical-spec.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`
  - `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md`
  - `.github/agents/python-implementation-workflow.agent.md`

- **Out of scope**:
  - `.github/skills/*`
  - `.codex/skills/*`
  - `.codex/agents/*` implementation
  - runtime implementation
  - `README.md`、`VERSION`

## Locked Decisions

- `.github/agents/python-implementation-workflow.agent.md` 是此 topic 的單一分析對象。
- `custom-agent-codex-compat` 不得假設 `.codex/agents` 已有現成治理契約。
- 本 topic 只做到 draft plan commit，**不進 independent review**。
- `platform-projection-adapter` 不能當成 agent compatibility solution。
- 本 topic 是 planning / governance topic，不是 runtime implementation topic。
- 此 topic **不涉及 stable-library surfaces**。

## Boundaries / Exclusions

- Planning actor 只建立 custom-agent planning package。
- Creator 後續不得把本 topic 擴張成 `.codex/agents/*` implementation，除非 human
  另開 topic 並補治理契約。
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
- Do not advance to `review-ready` or beyond in this execution round.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/custom-agent-codex-compat/requirements.md` | Planning actor | Frozen agent-compatibility baseline |
| Topic technical spec baseline | `analysis/custom-agent-codex-compat/technical-spec.md` | Planning actor | Frozen execution-facing agent-compatibility baseline |
| Topic plan | `plan/custom-agent-codex-compat/custom-agent-codex-compat.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md` | Planning actor | Workflow-step evidence for the paused draft lane |
| Topic checklist | `plan/custom-agent-codex-compat/custom-agent-codex-compat.checklist.md` | Planning actor | Authoring / pause-state validation for this topic |
| Current source artifact | `.github/agents/python-implementation-workflow.agent.md` | Creator | Existing agent artifact under compatibility-only surface |
| Future prerequisite | `.codex/agents/` | Creator | Deferred future governance surface; not yet authorized for implementation |

Artifact path notes:

- This topic does **not** modify `.github/agents/python-implementation-workflow.agent.md`
  in the current execution round.
- `.codex/agents/` is listed only as a deferred prerequisite surface, not as an
  implemented target.

## Implementation Steps

1. Freeze the single-agent scope and the governance-gap analysis in the analysis
   layer.
2. Author a repo-visible plan that records current source evidence, missing
   `.codex/agents` contracts, and the no-adapter-shortcut rule.
3. Create the topic step tracker and checklist.
4. Create a draft plan commit for this topic.
5. Pause the topic before independent review so future governance decisions can
   be added without pretending the full workflow already ran.

## Validation / Acceptance Checks

- All five topic artifacts exist at their exact paths.
- The plan explicitly says `.codex/agents` governance is missing.
- The plan does not claim direct `.codex/agents` implementation is authorized.
- The plan does not use `platform-projection-adapter` as an agent solution.
- The plan does not claim `reviewer-in-progress` or `approved`.
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

- What exact `.codex/agents` path / folder contract should future governance adopt?
- What validation contract should future agent compatibility topic require?
