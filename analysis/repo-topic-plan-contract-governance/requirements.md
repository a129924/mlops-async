# Repo Topic-Plan Contract Governance — Requirements

## Status

- **Status**: 凍結的業務基線
- **Topic**: `repo-topic-plan-contract-governance`
- **Target repo**: `mlops-async`
- **This round**: 只建立 analysis baseline；不建立 `plan/topic-plan-contract.md`，不進入 `create-agent-plan`，不修改 `src/**`、`tests/**` 或 `plan/**`

## Outcome

為 `mlops-async` 補齊一個 repo-level shared governance contract 的明確需求基線，
讓未來 topic 的 `create-agent-plan` 能以 `plan/topic-plan-contract.md` 作為
repo-visible fallback authority，而不是繼續把 `plan/agent-handoff-workflow.md`
或聊天上下文當成替代來源。

當此 governance topic 在後續流程真正完成時：

1. `plan/topic-plan-contract.md` 會存在於 repo 可見路徑，並可被
   `plan-creator`、`plan-reviewer` 與 `create-agent-plan` 直接讀取；
2. shared repo governance contract、workflow execution contract、
   topic-local plan artifact 這三者的邊界會被明確區分；
3. 未來 topic 的計畫建立流程，不再因 shared topic-plan contract 缺失而
   落入隱性 fallback 或非法前進。

## Actors

- **PlanCreator / planning actor**: 需要一個可讀取的 repo-level shared contract，
  來決定 required sections、fallback behavior 與 blocking semantics。
- **PlanReviewer**: 需要與 PlanCreator 共用同一份 repo-visible authority，
  才能對 topic plan 做一致的 blocking review。
- **Main Agent / prompt runner**: 需要能在 `create-agent-plan` 前後以
  repo-visible contract 進行合法 routing，而不是依賴私有聊天記憶。
- **Human maintainer**: 需要讓 repo governance 以檔案形式存在，方便未來 topic
  重複使用與審計。

## Evidence Baseline

目前 repo 狀態已提供下列可觀察事實：

- `plan/agent-handoff-workflow.md` 存在，但其內容定位為 workflow lifecycle /
  routing contract。
- `plan/topic-plan-contract.md` 目前缺失。
- `.agents/skills/plan-creator/SKILL.md`、`.agents/skills/plan-creator/reference.md`、
  `.agents/skills/plan-reviewer/SKILL.md`、`.agents/skills/plan-reviewer/reference.md`、
  `.agents/skills/plan-reviewer/checklist.md` 以及
  `.github/prompts/create-agent-plan.prompt.md` 都把 topic-plan contract 視為
  明確依賴或審查基礎。

## Measurable Requirements

| ID | Actor | Condition | Requirement | Acceptance signal |
| --- | --- | --- | --- | --- |
| R1 | PlanCreator / PlanReviewer | 當任一 topic 進入 `create-agent-plan` 或 plan review 時 | repo 必須提供精確路徑為 `plan/topic-plan-contract.md` 的 shared topic-plan contract。 | `plan/topic-plan-contract.md` 存在且可讀；consumer 不需改以聊天上下文或其他檔案猜測其存在。 |
| R2 | PlanCreator | 當 shared contract 被讀取時 | shared contract 必須定義 required topic-plan sections、fallback behavior 與 contract-level blocking semantics。 | 新 contract 可直接滿足 `plan-creator` skill 所列的 shared-contract 輸入與 validation 需求。 |
| R3 | PlanCreator / Main Agent | 當 `plan/agent-handoff-workflow.md` 與 shared contract 一起被使用時 | workflow contract 與 shared topic-plan contract 必須維持不同責任邊界，不可互相冒充。 | `plan/agent-handoff-workflow.md` 仍只承載 workflow lifecycle / routing；`plan/topic-plan-contract.md` 承載 topic-plan section / fallback / blocking contract。 |
| R4 | PlanCreator / PlanReviewer | 當 authoring 或 review `plan/<topic>/<topic>.plan.md` 時 | shared contract 必須明確區分 repo-level governance contract 與 topic-local plan artifact。 | shared contract 只定義 repo-wide planning law，不直接承載任一 topic 的 `Goal / Outcome`、`Scope`、status 或 artifact paths。 |
| R5 | PlanCreator | 當 topic-plan template 缺失、局部失真，或需確認 canonical section authority 時 | shared contract 必須可作為 fallback authority，而不是要求 agent 臨場發明 plan shape。 | contract 明確提供 fallback behavior，且能支持 `plan-creator` 在 template 不可用時停止猜測並依 contract 前進。 |
| R6 | PlanReviewer / Main Agent | 當 repo 進行 plan review 與後續 routing 時 | 所有已知 consumer 對 shared contract 的角色理解必須一致。 | 不允許再把 `plan/agent-handoff-workflow.md` 單獨視為 topic-plan section authority；review basis 需能明確包含 shared contract。 |
| R7 | Human maintainer | 當此 governance topic 進入後續 create-agent-plan 與 implementation topic 時 | 此工作必須維持為 repo governance artifact topic，而不是擴張成 feature/topic implementation。 | 後續 scope 只處理 shared contract 與其必要的消費一致性檢查；不得藉此 topic 進入 `src/**`、`tests/**`、`README.md`、`VERSION` 或 release artifacts。 |

## Assumptions

- 目前缺口的核心不是 workflow lifecycle 缺失，而是 shared topic-plan contract
  缺失。
- 現有 consumer wording 已足以證明 `plan/topic-plan-contract.md` 是既定依賴，
  不是新的需求發明。
- 後續若要讓 `create-agent-plan` 合法前進，最小必要條件是提供 repo-visible
  shared contract，而不是重新解釋 prompt 或 skill wording。

## Non-goals

- 不在本步驟直接建立 `plan/topic-plan-contract.md`。
- 不在本步驟直接建立任何 `plan/<topic>/<topic>.plan.md`。
- 不修改 `src/**`、`tests/**`、`README.md`、`VERSION` 或 release artifacts。
- 不把 `plan/agent-handoff-workflow.md` 重寫成 shared topic-plan contract 的替身。
- 不把 shared contract 擴張成單一 topic 的具體實作計畫。

## Surfaced Contradictions and Decisions

1. **已存在 workflow contract，但 shared contract 缺失**
   - 觀察：`plan/agent-handoff-workflow.md` 已存在且包含 workflow 狀態與流程規則。
   - 風險：若直接拿它替代 shared topic-plan contract，會混淆 execution contract
     與 plan-section authority。
   - 決策：新增獨立的 `plan/topic-plan-contract.md`；不得將 workflow file 視為替身。

2. **shared repo governance contract 與 topic-local plan artifact 的角色不同**
   - 觀察：`plan/<topic>/<topic>.plan.md` 應承載單一 topic 的 scope、steps、
     artifacts 與 routing state。
   - 風險：若把 shared contract 寫成 topic-local plan，後續 topic 仍無法共用。
   - 決策：shared contract 只承載 repo-wide topic-plan law；topic-local details
     留在各 topic plan。

3. **consumer 已明確依賴 shared contract，但 repo 尚未提供檔案**
   - 觀察：`plan-creator`、`plan-reviewer` 與 `create-agent-plan` 都已把
     `plan/topic-plan-contract.md` 視為輸入或 review basis。
   - 風險：若不補齊，後續 planning workflow 會卡在 hidden fallback。
   - 決策：後續 governance topic 的最小目標就是補齊該檔案，而不是擴大成多主題治理重寫。

## Extreme-boundary Checks

- **Template 不可用情境**：shared contract 仍必須足以提供 canonical section
  authority 與 fallback semantics；若做不到，則表示需求尚未滿足。
- **錯誤替代情境**：若後續 implementation 只更新 consumer wording、卻未建立
  `plan/topic-plan-contract.md`，視為失敗。
- **邊界擴張情境**：若後續工作需要修改 `src/**`、`tests/**`、`README.md`、
  `VERSION` 或 release artifacts，必須停止並拆出另一個 topic。
- **高重複使用情境**：此 contract 必須能被多個未來 topic 重複引用；若內容仍綁定
  單一 sample topic，則不符合 repo-level shared contract 的目標。

## Freeze Decision

此 baseline 已凍結，可供後續 `create-agent-plan` 使用。下游 topic 的最小安全動作，
是建立一個只處理 repo governance contract 的 topic plan，並以
`plan/topic-plan-contract.md` 作為唯一 required target artifact。
