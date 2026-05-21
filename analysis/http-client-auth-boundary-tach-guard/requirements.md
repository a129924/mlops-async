# http-client-auth-boundary-tach-guard requirements baseline

## Status

- `FROZEN` — ready for topic-plan authoring

## Problem Statement

`docs/standards/http-client-auth-boundary.md` 已經固定 auth / request boundary 的依賴方向，
但 `tach.toml` 目前仍只治理粗粒度的 `mlops_async` / `_repo_hooks` 模組，尚未把
`mlops_async.core` 與 `mlops_async.transport` 的最小單向依賴顯式化。結果是後續若有人把
auth/request 邏輯反向塞回 transport 層，repo 目前缺少一個可在本機與 pre-commit 階段提早
攔下的 machine-checkable guardrail。

## Actors and Consumption Boundary

1. **Primary actor — repo maintainer / reviewer**
   - 需要一個可重複執行的結構 guardrail，判斷 auth/request boundary 是否仍維持既定方向。
   - 不應每次只靠人工比對文件與 import 來發現反向依賴。
2. **Secondary actor — 後續修改 `core` / `transport` 的 Agent 或 contributor**
   - 在引入新的跨模組 import 前，需要知道最小允許邊界是什麼。
   - 若 guardrail 與文件或現況衝突，必須停下而不是自行擴張治理面。

## Measurable Requirements

| ID | Actor | Condition | Observable Outcome | Metric / Decision Rule | Failure Meaning |
| --- | --- | --- | --- | --- | --- |
| BR-1 | repo maintainer / reviewer | 後續變更觸及 `mlops_async.core` 與 `mlops_async.transport` 邊界 | repo 有一個可執行的最小結構 guardrail 來固定依賴方向 | `tach.toml` 必須明確表達：`mlops_async.transport` 可依賴 `mlops_async.core`，`mlops_async.core` 不可反向依賴 `mlops_async.transport`；若 `core` / `transport` 需要依賴 package root `mlops_async`，只能限於既有 base-exception entry layer 等現有 root-level contract | 反向依賴只能靠人工 review 發現，boundary 容易回漂 |
| BR-2 | 後續 Agent / contributor | 準備新增或修改 `core` / `transport` 之間的 import | local validation 能在 merge 前指出該依賴是否越界 | 在 current tree 上，`uv run tach check` 必須可執行並通過；未來若出現 `core -> transport` 反向依賴，guardrail 應成為 failure signal | 結構規則存在但無法被日常工作流使用，等於沒有 guardrail |
| BR-3 | repo maintainer / reviewer | 本 topic 補 guardrail 時 | scope 仍維持最小 auth/request boundary，而不是升格成全面模組治理 | topic 只允許新增或調整表達 `mlops_async`、`mlops_async.core`、`mlops_async.transport` 與既有 `_repo_hooks` 所必需的最小 `tach.toml` 規則；若需要額外 package family 或更廣泛重排，必須視為超出 baseline | topic scope 漂移成一般模組重整，失去原本要保護的 auth-boundary 焦點 |
| BR-4 | repo maintainer / reviewer | `tach.toml` 擬新增的 guardrail 與 `docs/standards/http-client-auth-boundary.md`、現況 import graph 或相關 current-state 文件不一致 | Agent 不自行平均解讀，而是停下交人工決策 | 若分析發現文件、程式碼、`tach.toml` 語意不一致，topic 必須標記 blocker；不得以偷偷放寬規則或改寫邊界描述來繞過 | repo 會同時存在彼此衝突的 boundary source of truth |
| BR-5 | repo maintainer / reviewer | guardrail 補上後，README 或 contributing 文件中原有 current-state 描述變得不正確 | 與 `tach` 使用方式直接相關的文件同步更新到不自相矛盾 | 若 `README.md` 或 `.github/CONTRIBUTING.md` 仍宣稱只治理粗粒度 `mlops_async` / `_repo_hooks`，則 topic 未完成；若 wording 仍正確，則可保持不變 | 文件與實際 guardrail 漸行漸遠，後續 Agent / contributor 會得到錯誤上下文 |
| BR-6 | repo maintainer / reviewer | analysis/plan 已完成，但 creator 發現 `tach` 無法只表達這條最小邊界 | topic 會明確停在 blocker，而不是被強迫擴 scope 完成 | 若最小 guardrail 需要 broader module restatement、會影響與 auth/request boundary 無關的模組，必須停止並交人工決策 | 為了完成 topic 而把 repo 結構治理一次性放大，破壞 incremental policy |

## Assumptions

1. 目前 `src/mlops_async/transport/http_client.py` 依賴 `mlops_async.core.*`，而 `src/mlops_async/core/**` 尚未反向依賴 `mlops_async.transport`。
2. `src/mlops_async/exceptions.py` 是 package-root base exception entry layer，`core` / `transport` 對該 root-level contract 的既有依賴可視為 minimal guardrail 內的既存結構。
3. 補 `tach.toml` guardrail 不需要改動 runtime behavior 或 auth implementation 本體。
4. 若需要同步 README / contributing wording，屬於 current-state 文件校正，不代表 stable public API 行為改變。

## Non-goals

1. 不重新設計 auth/request boundary 本身。
2. 不修改 `src/mlops_async/**` 或 `tests/**` 的 runtime / test 行為。
3. 不把 `tach.toml` 擴張成涵蓋與 auth/request boundary 無關的廣泛模組治理。
4. 不引入 VERSION bump、release note、tag、或其他 release action。
5. 不新增 `analysis/<topic>/technical-spec.md` 作為本 topic 的必要前置條件。

## Extreme-Boundary Checks

1. **Wrong actor**
   - 非 `core` / `transport` boundary topic 的 Agent，不需要被這個 guardrail topic 強迫重對齊其他模組治理。
2. **Partial completion**
   - 若只有 requirements/plan，或只更新文件但沒有可執行的 `tach.toml` guardrail，topic 不算完成。
3. **Over-broad governance**
   - 若 creator 需要順手新增更多 package/module 規則才能讓 `tach` 通過，必須先停下；這不視為「順便補一下」。
4. **Documentation drift**
   - 若 guardrail 已變更，但 README / contributing 的 current-state 描述仍留在舊狀態，視為 topic 未完成。

## Contradiction Log

1. **想現在就補 guardrail vs 需要先做更完整分析**
   - Statement A：使用者希望把 `tach.toml` guardrail 當成下一階段，並在同 topic 內完成。
   - Statement B：使用者明確要求先做更完整分析，不要直接把最小規則寫進去就算完成。
   - Decision：topic 現在就啟動，但順序固定為 **worktree -> requirements -> plan -> tach implementation**；analysis/plan 先於任何 `tach.toml` 修改。
2. **需要更強 guardrail vs 保持 incremental 治理**
   - Statement A：repo 需要一個可以攔下 `core -> transport` 反向依賴的 machine-checkable 規則。
   - Statement B：repo 目前 `tach` 採 incremental policy，不應因單一 topic 直接升格成全面模組重整。
   - Decision：本 topic 只允許最小 auth-boundary guardrail；若 `tach` 語法或現況要求更廣泛治理，停止並交人工決策。
3. **只改 `tach.toml` vs 同步 current-state 文件**
   - Statement A：這個 topic 的核心是 guardrail，不想擴張成文件整理。
   - Statement B：若 current-state 文件仍描述舊的治理範圍，topic 完成後會留下新的語意落差。
   - Decision：README / `.github/CONTRIBUTING.md` 只有在 current-state wording 失真時才列入同步修正；不主動擴張到其他文件。

## Blockers

- None for this business baseline.

## Handoff Boundary for Plan Authoring

此 baseline 已凍結下列需求，不需要在 topic plan 中重新發明：

1. topic 目標是補上 **最小** auth-boundary `tach.toml` guardrail，而不是一般模組重整。
2. 順序固定為：先 analysis/plan，再決定與執行 `tach.toml` 修改。
3. package root `mlops_async` 目前作為 base exception entry layer；`core` / `transport` 對該 root-level contract 的既有依賴可在 guardrail 中被保留，但不得藉此重新放寬 `core` / `transport` 的其他跨層依賴。
4. 若 `tach.toml`、`docs/standards/http-client-auth-boundary.md`、現況 import graph 或 current-state 文件互相衝突，creator 必須停下交人工決策。
5. `README.md` 與 `.github/CONTRIBUTING.md` 只有在 guardrail 變更會讓既有 current-state 說法失真時才可同步修改。
6. 本 topic 不包含 runtime/test/release 變更。
