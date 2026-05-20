# Correction / Delta Lifecycle Contract Alignment — Requirements

## Status

- **Status**: 凍結的業務基線
- **Topic**: `correction-delta-lifecycle-contract-alignment`
- **Target repo**: `mlops-async`
- **Source contract**: 已發布的 `agent-skills` correction / delta lifecycle
  contract，版本為 `0.58.0`
- **This round**: 本輪包含 analysis baseline、topic plan 與 governance workflow/planning surfaces 的對齊；不含 `src/**`、`tests/**`、release / tag 或 sample payload rewrite。

## Outcome

將 `mlops-async` 的本地 workflow-contract surfaces 與 `agent-skills`
已採用且已發布的 correction / delta lifecycle 規則對齊，讓未來在
`mlops-async` 內進行的 planner / creator / reviewer 工作，使用與
repository 的 `v0.9.2` sample topic 已隱含相同的 contract。

當此 topic 最終完成時：

1. 本地 workflow surfaces 會表達與已發布上游 contract 相同的
   correction-lifecycle 規則；
2. 本地 sample 會維持為 repo-visible evidence，而不會被提升為
   通用流程法則；
3. `mlops-async` 未來的 planners 與 reviewers 可以評估 correction /
   delta topics，而不必再從 sample-only evidence 猜測規則。

## Actors

- **Planner / maintainer**: 需要與 repository 已接受 governance baseline
  一致的本地 workflow contracts。
- **Creator**: 需要對 correction artifacts、parent backfill 與各角色擁有的
  Implementation Steps 有精確且有邊界的撰寫規則。
- **Reviewer**: 需要明確的 review checks，以確認 path exactness、role
  ownership、`review-log` 的條件性，以及 topic-scoped round-cap policy。
- **Main Agent**: 需要不依賴私有聊天記憶或 repo-specific 猜測的 routing
  規則。

## Measurable Requirements

| ID | Requirement | Acceptance signal |
| --- | --- | --- |
| R1 | `mlops-async` 的本地 workflow surfaces 必須直接編碼已發布的 correction / delta lifecycle contract，而不是只讓它隱含在 `v0.9.2` sample artifacts 中。 | 後續 implementation topic 會更新 topic plan 中列出的、具邊界的本地 workflow surfaces，且不再依賴 sample-only wording 來表達 lifecycle semantics。 |
| R2 | workflow body 必須維持只涵蓋 correction lifecycle / routing contract；field-level correction artifact schema 與長篇 examples 必須放在 reference / example surfaces。 | `plan/agent-handoff-workflow.md` 維持精簡，而詳細的 correction artifact guidance 會出現在 `plan-creator` 與 `plan-reviewer` 的 reference/example surfaces。 |
| R3 | 在接受 backfill 後，parent artifacts 必須被視為面向執行的 current truth；correction artifacts 必須維持為 historical truth。 | 本地 workflow 與 review guidance 會明確區分 parent current truth 與 correction historical truth。 |
| R4 | 只有在 reviewer feedback 會控制 routing 或涉及 multi-round rework 時，才必須要求 repo-visible `review-log` 或等價 handoff。 | 本地 plan-authoring 與 plan-review guidance 會明確寫出此條件，而不會把 `review-log` creation 普遍化。 |
| R5 | 任何 round cap 都必須被視為 topic policy，而不是 repository-wide invariant。 | 本地 guidance 允許宣告 topic caps，但不會把 `v0.9.2` 的三輪 sample 轉成通用法則。 |
| R6 | 執行與 review 的 evidence paths 必須精確、有邊界、repo-visible，且帶有 role labels。 | 本地 plan-authoring 與 plan-review surfaces 會拒絕 `merged implementation` 之類的模糊標籤，或過於寬泛的資料夾參照。 |
| R7 | Planner、creator、reviewer 與 Main Agent 的 ownership 必須維持分離。 | 本地 guidance 會拒絕在 creator `Implementation Steps` 內放入 reviewer-owned logging，並讓 routing work 保持在 creator scope 之外。 |
| R8 | 此 topic 不得把 `mlops-async` 的 domain payload 內化為 workflow law。 | 後續 implementation topic 只會停留在 workflow / planning surfaces，且不會修改 `src/**`、`tests/**`、`README.md`、`VERSION` 或 release artifacts。 |

## Assumptions

- `agent-skills` `0.58.0` 是此 lifecycle behavior 已核准的上游 contract baseline。
- `mlops-async` 有意保留相關 workflow surfaces 的本地副本，而不是從遠端共享套件取得。
- `core-concrete-client-delta-backfill` sample 仍然是有用的 evidence，但它不應繼續成為唯一可推導此 lifecycle contract 的地方。

## Non-goals

- 不修改 `src/mlops_async/**` 或 `tests/**` 之下的 production code 或 tests。
- 不在此 topic 內抽出新的 standalone correction / delta skill。
- 不處理 README、VERSION、tag 或 release-note 工作。
- 不改寫 `core-concrete-client-*` sample payload，除非後續另行規劃且僅限 wording 的 follow-up 明確證明有其必要。

## Surfaced Contradictions and Decisions

1. **Sample 與 contract wording 的落差**
   - 觀察：`v0.9.2` 已經記錄了被保留的 correction / delta sample 與已回填的 parent artifacts。
   - 風險：因為本地 workflow surfaces 較舊且較薄，未來 agents 可能會從 sample 推導出通用規則。
   - 決策：對齊 workflow surfaces，而不是 sample payload。

2. **`review-log` 可見性與過度擴張**
   - 觀察：sample 使用了 repo-visible `review-log`。
   - 風險：若盲目泛化該 sample，會迫使所有 review 都需要 review logs。
   - 決策：只有在 routing 或 multi-round rework 依賴它時，才把 `review-log` 內化為條件性規則。

3. **三輪 sample 與 repo-wide policy 的差異**
   - 觀察：sample 使用三輪的 creator / reviewer cap。
   - 風險：若到處複製，會形成錯誤的通用限制。
   - 決策：只將 round caps 保留為明確宣告的 topic policy。

## Extreme-boundary Checks

- 若未來的 alignment work 需要觸及 domain code、tests 或 release files，應停止並將該工作拆成另一個 topic。
- 若 `mlops-async` 有意偏離已發布的上游 contract，必須明確揭露這個 divergence；不可讓它以 silent drift 形式存在。
- 若詳細 correction schema 無法留在 workflow body 之外，應先停止並重新評估是否需要在 implementation 前建立獨立的 lifecycle reference。

## Freeze Decision

此 baseline 已為下游 technical translation 凍結。下一個最小且安全的動作，是建立一個只處理 governance 的 topic，更新 `mlops-async` 的本地 workflow surfaces，使其符合已發布的 lifecycle contract，同時讓 sample topic 維持為 evidence，而不是流程法則。
