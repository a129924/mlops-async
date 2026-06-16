> **Workflow State Contract**
>
> - current_step: `create-agent-plan`
> - next_step: `plan-review`
> - status: `COMPLETE`
>
> **Bootstrap exception**
>
> - 此例外僅適用於 `repo-topic-plan-contract-governance`。
> - 例外用途僅限在 `plan/topic-plan-contract.md` 尚未存在時，允許本治理 topic 的 bootstrap `create-agent-plan` 與本次 bootstrap `plan-review` 先行使用既有 workflow-side contract 完成 planning handoff。
> - 此例外不得擴散到其他 topic，不得用來跳過 creator / review / publish gate；`plan/agent-handoff-workflow.md` 只可作為這兩個 bootstrap 動作的暫時 workflow-side 依據，不是 shared topic-plan contract，也不是永久替代品。

## Inputs

- Business guardrail input: `analysis/repo-topic-plan-contract-governance/requirements.md` (`sha256: 9dbb92456a7caf9fb7bbbca0662ac40736bc133c756d76dcfc03a2b20557b059`)
- Execution baseline input: `analysis/repo-topic-plan-contract-governance/technical-spec.md` (`sha256: e4d5d96d521e01240afcd2b39b43f6cc8b0746503eba74c532fe3cb5123e45a4`)
- Analysis-layer routing: strict mode. 本 topic plan 的 `Artifact Paths`、`Implementation Steps` 與 `Validation / Acceptance Checks` 100% 對映上述 `technical-spec.md`，並以 `requirements.md` 作為 business-intent guardrail。

## Goal / Outcome

- 為 `repo-topic-plan-contract-governance` 建立 repo-visible execution contract，讓後續 creator phase 能在嚴格治理邊界內建立 `plan/topic-plan-contract.md`，並完成必要的 consumer compatibility verification。
- 本 topic 完成後，repo 會有一份獨立的 shared topic-plan contract，且它與 `plan/agent-handoff-workflow.md` 的 workflow lifecycle / routing contract 角色保持分離。

## Scope

- **In scope**:
  - 維護本 topic 的 planning artifacts：
    - `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.plan.md`
    - `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.step.md`
  - 在後續 creator phase 建立 `plan/topic-plan-contract.md`。
  - 以 read-only 方式驗證下列 consumer / workflow surfaces 是否可由新 shared contract 直接滿足：
    - `plan/agent-handoff-workflow.md`
    - `.agents/skills/plan-creator/SKILL.md`
    - `.agents/skills/plan-creator/reference.md`
    - `.agents/skills/plan-reviewer/SKILL.md`
    - `.agents/skills/plan-reviewer/reference.md`
    - `.agents/skills/plan-reviewer/checklist.md`
    - `.github/prompts/create-agent-plan.prompt.md`

- **Out of scope**:
  - 本回合直接實作 `plan/topic-plan-contract.md`
  - 修改 `src/**` 或 `tests/**`
  - 修改其他 topic 的 `analysis/**` 或 `plan/**`
  - 修改 `plan/agent-handoff-workflow.md` 本體
  - 修改 `README.md`、`VERSION`、release artifacts 或任何 stable-library surfaces
  - 將 bootstrap exception 套用到其他 topic

## Locked Decisions

- 本 topic 是 **repo governance implementation topic**，不是 feature/topic implementation，也不是 review-only topic。
- `analysis/repo-topic-plan-contract-governance/technical-spec.md` 是 execution-facing source of truth；`analysis/repo-topic-plan-contract-governance/requirements.md` 是 business-intent guardrail。
- 後續 creator phase 的唯一 required creation target 是 `plan/topic-plan-contract.md`。
- `plan/agent-handoff-workflow.md` 持續只承載 workflow lifecycle / routing contract；不得被升格為 shared topic-plan contract，也不得被此 bootstrap exception 宣告為永久替代品。
- consumer compatibility verification 預設為 read-only。若發現 direct semantic contradiction，必須停止並回報，不得在本 topic 靜默擴張為多檔治理重寫。
- 本 topic **不涉及 stable-library surfaces**；不修改 `README.md`、`VERSION`、release notes，也不宣告 release timing。
- 本次 bootstrap exception 只授權 `repo-topic-plan-contract-governance` 的 bootstrap `create-agent-plan` 與本次 bootstrap `plan-review`；其他 topic 仍不得在缺少 `plan/topic-plan-contract.md` 時沿用此例外。

## Boundaries / Exclusions

- Planning actor 只負責建立本 topic 的 planning artifacts。
- Creator 只可在本 plan 鎖定的 exact artifact paths 內建立 shared contract，並對列舉的 validation surfaces 做 read-only 檢查。
- Reviewer 必須獨立評估本 topic 的 plan 與後續 creator draft，不得執行 creator implementation work。
- Main Agent 只負責後續 routing、publish、PR flow 與 merge orchestration；這些動作不屬於 creator steps。
- 若後續工作需要改寫 consumer wording、workflow body 或新增其他 shared governance surfaces，必須停止並拆出新 topic，而不是在本 topic 擴張 scope。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; 本 topic 不宣告 release lane，於 `merged` 終止。
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

- 此次 planning correction 完成後，下一個外部動作是對本 topic plan 執行 bootstrap `plan-review`；review 通過後，後續 creator phase 才可依標準路由進入 implementation work。
- publish 前仍遵守標準 Phase 4.5 planner-alignment gate。
- 若 creator 驗證時發現需要觸及 `plan/topic-plan-contract.md` 以外的修改路徑，或 validation surfaces 之間存在直接衝突，必須先回到 planning / human-check，而不是繼續擴張。
- bootstrap exception 只允許本 topic 合法完成 bootstrap `create-agent-plan` 與本次 bootstrap `plan-review`；不構成 repository-wide 狀態豁免。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/repo-topic-plan-contract-governance/requirements.md` | Planning actor | Frozen business guardrail for this governance topic |
| Topic technical spec baseline | `analysis/repo-topic-plan-contract-governance/technical-spec.md` | Planning actor | Frozen execution-facing baseline for this governance topic |
| Topic plan | `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.step.md` | Planning actor | Planning-phase artifact already established for this topic; creator consumes it as the step tracker, not as a creation target |
| Required creation target | `plan/topic-plan-contract.md` | Creator | Shared repo-level topic-plan contract to be authored in the later implementation phase |
| Read-only validation surface | `plan/agent-handoff-workflow.md` | Creator | Workflow lifecycle / routing contract boundary check |
| Read-only validation surface | `.agents/skills/plan-creator/SKILL.md` | Creator | Shared-contract consumer contract verification |
| Read-only validation surface | `.agents/skills/plan-creator/reference.md` | Creator | Shared-contract consumer reference verification |
| Read-only validation surface | `.agents/skills/plan-reviewer/SKILL.md` | Creator | Reviewer-side shared-contract consumer verification |
| Read-only validation surface | `.agents/skills/plan-reviewer/reference.md` | Creator | Reviewer-side shared-contract reference verification |
| Read-only validation surface | `.agents/skills/plan-reviewer/checklist.md` | Creator | Reviewer-side checklist compatibility verification |
| Read-only validation surface | `.github/prompts/create-agent-plan.prompt.md` | Creator | Prompt-side topic-plan contract compatibility verification |

Artifact path notes:

- `README.md`：本 topic 不修改。
- `VERSION`：本 topic 不修改。
- `src/**`：本 topic 不修改。
- `tests/**`：本 topic 不修改。
- 其他 topic 的 `analysis/**` / `plan/**`：本 topic 不修改。
- Listed validation surfaces are read-only by default. 若後續工作漂移到未列出的路徑，必須先修正本 plan，再繼續 implementation。

## Implementation Steps

1. 建立 `plan/topic-plan-contract.md`，明確定義 shared topic-plan contract 的 purpose 與 authority boundary，並在同一檔案中凍結 canonical required topic-plan sections、template 缺失或不可用時的 fallback behavior、contract-level blocking semantics，以及它與 `plan/agent-handoff-workflow.md` / `plan/<topic>/<topic>.plan.md` 的責任分界。
2. 以 read-only 方式驗證以下 surfaces 可由新 shared contract 直接滿足，而不需在本 topic 修改 consumer wording 或 workflow body：
   - `plan/agent-handoff-workflow.md`
   - `.agents/skills/plan-creator/SKILL.md`
   - `.agents/skills/plan-creator/reference.md`
   - `.agents/skills/plan-reviewer/SKILL.md`
   - `.agents/skills/plan-reviewer/reference.md`
   - `.agents/skills/plan-reviewer/checklist.md`
   - `.github/prompts/create-agent-plan.prompt.md`
3. 若 read-only 驗證發現 direct semantic contradiction 無法只靠 `plan/topic-plan-contract.md` 解決，停止並回報 divergence；不得在本 topic 靜默展開 consumer refresh、workflow rewrite 或其他治理面擴張。

## Validation / Acceptance Checks

- `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.plan.md` 與 `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.step.md` 存在於精確路徑。
- 後續 creator phase 完成後，`plan/topic-plan-contract.md` 必須存在於精確路徑。
- `plan/topic-plan-contract.md` 必須明確宣告：
  - required topic-plan sections
  - fallback behavior
  - contract-level blocking semantics
  - 與 `plan/agent-handoff-workflow.md` 的分責
  - 與 `plan/<topic>/<topic>.plan.md` 的分責
- `plan/agent-handoff-workflow.md` 不得被改寫成 shared contract 替代品。
- 列舉的 validation surfaces 必須能將新 shared contract 視為可讀 authority；若不能，creator 必須停止並回報，而不是擴張修改。
- 變更不得觸及 `src/**`、`tests/**`、`README.md`、`VERSION`、release artifacts、其他 topic 的 `analysis/**` / `plan/**`。
- Bootstrap exception 的適用範圍必須只留在本治理 topic，不得被文件語意擴張成 repository-wide fallback。
- Stable-library intent 必須保持明確 absent。

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

- 本 topic 不需要 release action。
- merge 後，shared contract 已正式落地時，本次 bootstrap exception 即告結束，不得再被其他 topic 引用為前例。
- 本 topic 在 `merged` 終止。

## Open Questions / Unresolved Items

- None at planning time. 若後續 creator 驗證發現 direct semantic contradiction，必須停止並拆出新的對齊 topic，而不是在本 topic 擴大修改面。
