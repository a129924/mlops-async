# Repo Topic-Plan Contract Governance — Technical Spec

## Status

- **Status**: 凍結的技術基線
- **Topic**: `repo-topic-plan-contract-governance`
- **Source baseline**:
  `analysis/repo-topic-plan-contract-governance/requirements.md`
- **This round**: 只建立 analysis baseline；不建立 `plan/topic-plan-contract.md`，
  不建立 topic plan，不修改 `src/**`、`tests/**` 或既有 `plan/**`

## Baseline Summary

目前 repo 已存在 workflow-side 與 consumer-side 的明確證據：

- `plan/agent-handoff-workflow.md` 已定義 workflow lifecycle、allowed
  transitions、reviewer handoff JSON 與 correction lifecycle routing。
- `plan/topic-plan-contract.md` 缺失。
- `.agents/skills/plan-creator/SKILL.md` 與 `reference.md` 已把
  `plan/topic-plan-contract.md` 定義為 shared repo-level authority，且要求它提供：
  - required topic-plan sections
  - fallback behavior
  - contract-level blocking semantics
- `.agents/skills/plan-reviewer/SKILL.md`、`reference.md`、`checklist.md`
  也把 `plan/topic-plan-contract.md` 列為 review basis。
- `.github/prompts/create-agent-plan.prompt.md` 要求產出的 topic plan
  「內容需符合 topic plan contract」。

因此，真正的技術缺口不是 workflow file 不存在，而是 shared topic-plan
contract 缺少 repo-visible artifact，導致 consumer 依賴存在、authority file
卻不存在。

## Technical Goal

定義後續 governance topic 的最小技術實現，使 repo 能補齊：

- `plan/topic-plan-contract.md`

並讓這個 artifact 在不改寫 workflow contract 的前提下，承接：

1. canonical required topic-plan sections；
2. template 缺失時的 fallback behavior；
3. contract-level blocking semantics；
4. shared repo governance contract 與 topic-local plan artifact 的明確邊界。

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 建立 exact shared contract path | 建立 `plan/topic-plan-contract.md` 作為 repo-visible artifact | `plan-creator`、`plan-reviewer`、`create-agent-plan` 的既有 consumer wording | 低；單一治理文件建立 | 可行 |
| R2 提供 section / fallback / blocking authority | 在新 contract 中定義 required sections、fallback behavior、contract-level blocking semantics | `.agents/skills/plan-creator/SKILL.md` 與 `reference.md` | 低到中；需精確對齊 consumer 預期 | 可行 |
| R3 與 workflow contract 分責 | 在新 contract 內明確宣告它不取代 `plan/agent-handoff-workflow.md`，並讓 workflow file 持續承載 execution contract | `plan/agent-handoff-workflow.md` | 低 | 可行 |
| R4 與 topic-local plan artifact 分責 | 在新 contract 內明確限制它只定義 repo-wide plan law，不承載單一 topic 的 scope / status / artifacts | `plan/<topic>/<topic>.plan.md` 的既有角色模型 | 低 | 可行 |
| R5 提供 template-absent fallback | 將 template 缺失時的 fallback 行為寫成明文 contract，而不是讓 agent 即席發明 | `.agents/skills/plan-creator/SKILL.md` 的 failure handling | 低 | 可行 |
| R6 維持 consumer 一致性 | 以 read-only 驗證方式檢查 `plan-creator`、`plan-reviewer`、`create-agent-plan` 與 workflow file 對新 contract 的理解是否一致 | 已存在的 consumer surfaces | 低；主要是對照與驗證 | 可行 |
| R7 維持 governance-only scope | 將 implementation topic 限縮為 shared contract artifact 與必要驗證，不擴張到 code、tests 或 release surfaces | `AGENTS.md`、本 topic 鎖定 intent | 低 | 可行 |

## Implementation-facing Workstreams

### Workstream 1 — Shared contract authoring

後續 implementation topic 的核心工作是建立 `plan/topic-plan-contract.md`，
且內容至少必須涵蓋：

1. shared contract 的 purpose 與 authority boundary；
2. canonical required topic-plan sections；
3. template 缺失或不可用時的 fallback behavior；
4. contract-level blocking semantics；
5. 與 `plan/agent-handoff-workflow.md` 的責任分界；
6. 與 `plan/<topic>/<topic>.plan.md` 的責任分界。

### Workstream 2 — Consumer compatibility verification

後續 implementation topic 必須以 read-only 方式驗證以下 consumer surfaces
確實能被新的 shared contract 滿足：

1. `.agents/skills/plan-creator/SKILL.md`
2. `.agents/skills/plan-creator/reference.md`
3. `.agents/skills/plan-reviewer/SKILL.md`
4. `.agents/skills/plan-reviewer/reference.md`
5. `.agents/skills/plan-reviewer/checklist.md`
6. `.github/prompts/create-agent-plan.prompt.md`
7. `plan/agent-handoff-workflow.md`

若這些 surfaces 與新 contract 的語意一致，則不應擴大 scope 去修改它們。

### Workstream 3 — Divergence handling

若後續 implementation 發現 consumer surfaces 對 shared contract 的期待彼此衝突，
必須停止並回報對齊需求，而不是在同一 topic 中靜默展開多檔治理重寫。

允許的最小處理原則：

- 先以 `plan/topic-plan-contract.md` 滿足既有明確依賴；
- 只有在直接矛盾阻擋合法 consumption 時，才可在後續 topic 中另行規劃 consumer refresh；
- 不得藉此 topic 偷渡 workflow body 重寫、plan template 重塑或 sample payload 對齊。

## Exact Planned Artifact Surface

後續 governance topic 的必要 target artifact 與驗證面如下：

- **Required creation target**
  - `plan/topic-plan-contract.md`

- **Analysis inputs**
  - `analysis/repo-topic-plan-contract-governance/requirements.md`
  - `analysis/repo-topic-plan-contract-governance/technical-spec.md`

- **Read-only validation surface**
  - `plan/agent-handoff-workflow.md`
  - `.agents/skills/plan-creator/SKILL.md`
  - `.agents/skills/plan-creator/reference.md`
  - `.agents/skills/plan-reviewer/SKILL.md`
  - `.agents/skills/plan-reviewer/reference.md`
  - `.agents/skills/plan-reviewer/checklist.md`
  - `.github/prompts/create-agent-plan.prompt.md`

此 topic 在 analysis 所凍結的最小技術實現，不要求預設修改上述 validation files。

## Architecture-compliance Self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo positioning | fits | 這是 repo governance artifact topic，不是 feature/topic implementation |
| Workflow separation | fits with prerequisites | 前提是新 contract 不取代 `plan/agent-handoff-workflow.md` |
| Consumer dependency model | fits | consumer 已明示依賴 shared contract，缺的是 artifact 本身 |
| Topic-local boundary | fits | shared contract 可保持 repo-wide；topic plan 繼續承載 local execution details |
| Code / test boundary | fits | 本 topic 不需觸及 `src/**` 或 `tests/**` |
| Release / stable-library intent | fits | 本 topic 應明確維持為非 stable-library、非 release 工作 |

## Constraints and Risks

| Issue | Type | Handling |
| --- | --- | --- |
| workflow contract 已存在且看似涵蓋部分 section 資訊 | substitution risk | 在 shared contract 明文禁止把 workflow file 當成替代 authority |
| shared contract 若寫得過大，容易膨脹成 template 或 topic-local plan | scope-bloat risk | 只寫 repo-wide section / fallback / blocking law，不放單一 topic payload |
| consumer wording 若存在未揭露分歧 | compatibility risk | 先以 read-only 驗證比對；若有直接矛盾，停止並回報，而不是靜默修補多處 |
| shared governance file 位於 `plan/**` | coordination risk | 在後續 implementation topic 中限定只新增 `plan/topic-plan-contract.md`，避免順手改寫其他 plan surfaces |

## Validation

必要檢查：

1. `plan/topic-plan-contract.md` 存在於精確路徑。
2. 新 contract 明確宣告：
   - required topic-plan sections
   - fallback behavior
   - contract-level blocking semantics
   - 與 `plan/agent-handoff-workflow.md` 的分責
   - 與 `plan/<topic>/<topic>.plan.md` 的分責
3. `plan-creator` 與 `plan-reviewer` 的既有引用，能直接把新 contract 視為可讀 authority，
   不需再依賴隱性 fallback。
4. 後續 implementation topic 未擴張到 `src/**`、`tests/**`、`README.md`、
   `VERSION` 或 release artifacts。

建議驗證指令：

```bash
test -f plan/topic-plan-contract.md
rg -n "topic-plan-contract" .agents .github plan
```

## Rollback-to-alignment Triggers

若發生以下情況，後續 implementation topic 應停止並回報，而不是繼續推進：

1. 建立 shared contract 仍不足以滿足 consumer，且需要在同一 topic 內大幅重寫
   `plan-creator`、`plan-reviewer` 或 workflow contract；
2. 新 contract 若不納入 topic-local payload、sample-specific wording 或
   release logic，就無法成立；
3. implementation scope 開始觸及 `src/**`、`tests/**`、`README.md`、
   `VERSION` 或其他與 shared planning law 無關的 surfaces；
4. 有人主張繼續以 `plan/agent-handoff-workflow.md` 直接替代 shared contract，
   使邊界再次失真。

## Final Technical Verdict

這個 governance gap 在技術上可由單一 repo-visible artifact 補齊，風險低，
但前提是 scope 嚴格維持在 `plan/topic-plan-contract.md` 的建立與 consumer
一致性驗證。安全的下游形狀是 shared contract authoring topic，而不是 workflow
重寫、feature implementation，或廣泛的 planning-surface overhaul。
