> **Analysis layer — strict mode**
>
> `analysis/correction-delta-lifecycle-contract-alignment/requirements.md` and
> `analysis/correction-delta-lifecycle-contract-alignment/technical-spec.md`
> exist. This plan maps to that technical spec as the execution-facing baseline.
> Chat-time guidance may not widen or replace those artifacts without an explicit
> human `override`.

## Goal / Outcome

- 將 `mlops-async` 的本地 workflow 與 planning surfaces 對齊至已發布的
  `agent-skills` `0.58.0` correction / delta lifecycle contract。
- 當此 topic 完成時，`mlops-async` 應在本地 workflow surfaces 中承載這些
  lifecycle 規則，而不是讓它們只能從 `v0.9.2` sample topic 與 README wording
  中被還原推導。

## Scope

- **In scope**:
  - 更新 `plan/agent-handoff-workflow.md`
  - 更新 `.github/agents/python-implementation-workflow.agent.md`
  - 更新下方列出的、具邊界的本地 `plan-creator` surfaces
  - 更新下方列出的、具邊界的本地 `plan-reviewer` surfaces

- **Out of scope**:
  - `src/mlops_async/**`
  - `tests/**`
  - `README.md`、`VERSION`、release tags 或 release notes
  - 新的 standalone correction / delta skill extraction
  - 除非後續狹義且僅限 wording 的 topic 明確授權，否則不重寫
    `core-concrete-client-*` sample payload artifacts

## Locked Decisions

- 此 topic **僅止於 review-ready，且不涉及 stable-library surfaces**。
  它不會變更 `README.md`、`VERSION`、release timing 或 release metadata。
- 有邊界的 source of truth 是已發布的 `agent-skills` `0.58.0`
  correction / delta lifecycle contract，並凍結於：
  - `analysis/correction-delta-lifecycle-contract-alignment/requirements.md`
  - `analysis/correction-delta-lifecycle-contract-alignment/technical-spec.md`
- workflow body 必須維持只包含 lifecycle / routing contract。
- 詳細的 correction artifact schema 與長篇 examples 應放在 reference /
  example surfaces，而不是 workflow body。
- parent artifacts 在 accepted backfill 後會再次成為 current truth；
  correction artifacts 則維持 historical truth。
- `review-log` 或等價 handoff 只在 routing-controlling feedback 或
  multi-round rework 發生時才需要；它不是通用要求。
- 任何 round cap 都只是 topic policy，不得成為 repository-wide law。
- 此 topic 不會建立新的 standalone skill。

## Boundaries / Exclusions

- Planning actor 只擁有此 plan 與 analysis artifacts。
- Creator 的 implementation ownership 嚴格限制在下方列出的精確 artifact
  paths 內。
- Reviewer 擁有獨立的 plan / implementation verdicts；reviewer-owned work
  不得出現在 creator `Implementation Steps` 中。
- Main Agent 擁有 worktree、branch、routing、PR flow、publish routing 與
  post-merge orchestration。
- 若後續工作需要超出所列 artifact contract 的 paths，應先停止並修復此 plan，
  再繼續執行。

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: 遵循 canonical creator -> reviewer -> publish ->
  merge path；此 topic 於 `merged` 結束，且不宣告任何 release action。
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

路由備註：

- 在 publish 前使用標準的 Phase 4.5 planner-alignment rule。
- 此 topic 不宣告 topic-specific round cap 或強制 `review-log`；若未來 review
  routing 需要其中任一項，應先以精確的 repo-visible artifact path 與 policy note
  修復此 plan。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/correction-delta-lifecycle-contract-alignment/correction-delta-lifecycle-contract-alignment.plan.md` | Planning actor | 此 alignment topic 的 repo-visible execution contract |
| Topic requirements baseline | `analysis/correction-delta-lifecycle-contract-alignment/requirements.md` | Planning actor | 此下游 governance alignment 的凍結 business baseline |
| Topic technical spec baseline | `analysis/correction-delta-lifecycle-contract-alignment/technical-spec.md` | Planning actor | 此下游 governance alignment 的凍結 technical baseline |
| Workflow contract | `plan/agent-handoff-workflow.md` | Creator | 必須吸收已發布 correction / delta 規則的 repo-level lifecycle / routing contract |
| Python workflow consumer | `.github/agents/python-implementation-workflow.agent.md` | Creator | repo-level lifecycle contract 的 consumer，且必須與其維持對齊 |
| Plan creator reference | `.github/skills/plan-creator/reference.md` | Creator | correction lifecycle planning behavior 的本地摘要規則面 |
| Plan creator checklist | `.github/skills/plan-creator/checklist.md` | Creator | 針對 exact paths、slim workflow body、role boundaries 與條件性 `review-log` 的本地 authoring checks |
| Plan creator examples | `.github/skills/plan-creator/examples.md` | Creator | correction lifecycle contract 的本地正反例 |
| Plan creator artifact-path rule | `.github/skills/plan-creator/references/artifact-path-rule.md` | Creator | parent artifacts、correction artifacts 與條件性 handoff artifacts 的本地 exact-path rule |
| Plan creator role-boundary rule | `.github/skills/plan-creator/references/role-boundary-rule.md` | Creator | planner、creator、reviewer 與 Main Agent ownership 的本地 role-separation rule |
| Plan creator topic-plan template | `.github/skills/plan-creator/templates/topic-plan-template.md` | Creator | 必須承載已刷新 correction-lifecycle prompts 的本地 topic-plan skeleton |
| Plan reviewer reference | `.github/skills/plan-reviewer/reference.md` | Creator | 用於阻擋 correction-lifecycle contract errors 的本地 review basis |
| Plan reviewer checklist | `.github/skills/plan-reviewer/checklist.md` | Creator | 針對 exact paths、role ownership、條件性 `review-log` 與 topic policy wording 的本地 review checks |
| Plan reviewer examples | `.github/skills/plan-reviewer/examples.md` | Creator | 已刷新 lifecycle contract 的本地 approved / needs-rework examples |

路徑備註：

- `README.md`：此 topic 不變更。
- `VERSION`：此 topic 不變更。
- `.github/copilot-instructions.md`：此 topic 不變更。
- 將列出的 paths 視為可執行 contract。若後續工作漂移到 `src/**`、`tests/**`、
  release files 或 `core-concrete-client-*` payload artifacts，應先停止並修復此
  plan。

## Implementation Steps

1. 更新 `plan/agent-handoff-workflow.md`，使 workflow body 僅保留
   correction lifecycle / routing contract，並明確表達 current truth 與
   historical truth 的分離。
2. 更新 `.github/agents/python-implementation-workflow.agent.md`，使其維持為
   repo-level lifecycle contract 的 consumer，而不是變成互相競爭的 owner。
3. 更新列出的本地 `plan-creator` surfaces，使其要求：
   - 精確、具角色標示的 artifact paths
   - 精簡的 workflow-body wording
   - parent current truth 與 correction historical truth 的區分
   - 條件性的 `review-log`
   - topic-scoped round-cap policy
   - 將詳細 correction artifact guidance 放在 reference / examples，而不是
     workflow body
4. 更新列出的本地 `plan-reviewer` surfaces，使其能阻擋：
   - 模糊的 evidence paths
   - 出現在 creator implementation steps 內的 reviewer-owned work
   - 無條件的 `review-log` 要求
   - repository-wide 的 round-cap wording
   - 在 workflow body 中塞入詳細 correction schema 的膨脹寫法

## Validation / Acceptance Checks

- 此 plan 遵循 analysis-layer strict mode，並維持在凍結 technical-spec 的邊界內。
- 只有列出的 workflow / planning surfaces 可以被修改。
- `plan/agent-handoff-workflow.md` 必須維持精簡，不能變成詳細 correction schema dump。
- 本地 guidance 必須明確區分 parent current truth 與 correction historical truth。
- `review-log` 必須維持條件性，不得被普遍化。
- 任何 round-cap wording 都必須維持為 topic-scoped policy。
- Creator、reviewer、planning actor 與 Main Agent 的 ownership 必須維持分離。
- 此 topic 不得修改 `src/**`、`tests/**`、`README.md`、`VERSION` 或 release artifacts。

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

- merge 後，Main Agent 只有在收到明確的人類 resume message 後，才可執行一般的本地 sync flow。
- 此 topic 不包含任何 repository release action、README update、VERSION bump 或 tag action。
- 此 topic 於 `merged` 終止。

## Open Questions / Unresolved Items

無。
