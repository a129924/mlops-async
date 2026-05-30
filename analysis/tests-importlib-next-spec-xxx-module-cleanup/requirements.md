# tests-importlib-next-spec-xxx-module-cleanup — Requirements Baseline

## Status

**Frozen（可供 technical translation 使用）**

## Problem Statement

目前 `tests/` 內仍可能混用動態引入（`importlib`）與一般行為測試，導致測試意圖混淆、審查成本升高，且存在以 fixture/helper 包裝 `importlib` 規避規則的風險。本 topic 目標是把規則收斂為可驗證、可阻擋規避、可交接的需求基線。

## Frozen Inputs（已凍結）

1. 一般行為測試禁用 importlib，改 explicit import。
2. 僅 import contract 測試允許動態引入。
3. import contract 測試必須集中於 `tests/contracts/`。
4. 命名慣例：`test_import_contract_*`。
5. 行為測試 importlib 零容忍。
6. 無法判定案例一律 BLOCKED，交人工 recheck。
7. 任何影響 contract meaning（scope/handoff/close semantics）需 rollback alignment。
8. 禁止用 fixture/helper 包裝 importlib 來規避規則。
9. 僅處理 `tests/`；不碰 `src/`；不可進 implementation。

## Measurable Requirements

| ID | Actor | Condition | Observable Outcome | Metric / Decision Rule |
| --- | --- | --- | --- | --- |
| BR-01 | 測試維護者 | 當案例屬於一般行為測試 | 測試程式僅使用 explicit import，無 `importlib` 直接呼叫 | `tests/contracts/` 以外若出現 `importlib` 呼叫即不合格 |
| BR-02 | 測試維護者 | 當案例主題是 import contract | 可保留動態引入，且測試檔位於 `tests/contracts/` | 動態引入僅允許出現在 `tests/contracts/` |
| BR-03 | 測試維護者 | 當新增或調整 import contract 測試 | 檔名或測試名稱符合 `test_import_contract_*` 慣例 | 任一 import contract 測試不符命名即不合格 |
| BR-04 | Reviewer | 當執行規則稽核 | 行為測試對 `importlib` 為零容忍，含間接包裝路徑 | 若透過 fixture/helper 間接呼叫 `importlib`，仍判定違規 |
| BR-05 | Reviewer | 當單一測試無法判定「行為測試」或「import contract」 | 案例被標記為 BLOCKED 並進入人工 recheck 清單 | 不允許以預設猜測分類；無結論即 BLOCKED |
| BR-06 | Planner / Reviewer | 當擬議變更會改變 contract meaning（scope/handoff/close semantics） | 立即停止技術推進並回滾到 alignment 決策 | 一旦偵測語意改變，狀態必須轉為 rollback-alignment |
| BR-07 | 執行者 | 當進行本 topic 工作 | 變更範圍限定於 `tests/` 分支內容 | 若任何改動觸及 `src/`，即違反需求邊界 |
| BR-08 | Reviewer | 當交付評審 | 可明確列出「允許動態引入」「已改 explicit import」「BLOCKED」三類清單 | 三類清單缺一不可，否則不得標記 complete |

## Assumptions

1. `tests/contracts/` 是本 repo 可接受且持續存在的 import contract 測試聚合位置。
2. `test_import_contract_*` 命名規則可套用於本 topic 涵蓋的 contract 測試單元。
3. 人工 recheck 角色可取得足夠上下文判定 BLOCKED 案例。
4. 本次僅產出分析工件，不直接編修測試程式。

## Non-goals

1. 不重構 `src/` 模組匯出與 runtime import 機制。
2. 不重新定義既有 business/contract 的產品語意。
3. 不在本 topic 內完成實作、修測試或改 CI。
4. 不處理 `tests/` 以外檔案。

## Contradiction Register

| ID | Statement A | Statement B | Conflict | Resolution |
| --- | --- | --- | --- | --- |
| CR-01 | 只有 import contract 可用動態引入 | 無法判定案例不得猜測 | 執行上可能想先暫放於一般測試 | 凍結規則：無法判定一律 BLOCKED，不可暫放 |
| CR-02 | 強制集中於 `tests/contracts/` | 現況可能有散落 contract 測試 | 位置尚未收斂前難立即判定合規 | 凍結規則：可先標記遷移待辦；未集中前不得宣告 fully compliant |

## Extreme-boundary Checks

| Boundary Case | Expected Decision Rule | Outcome State |
| --- | --- | --- |
| 無網路/外部依賴降級（與 import 行為無關） | 不得以外部依賴失敗合理化 `importlib` 使用 | 規則維持不變 |
| 錯誤角色或缺少 reviewer | 不可自行解除 BLOCKED；需人工 recheck | BLOCKED |
| 流程中斷（僅完成部分分類） | 未完成三類清單不得 close | INCOMPLETE |
| 最小量（1 個案例）與尖峰量（大量案例） | 皆套用同一判定規則，不得批次豁免 | 規則維持不變 |
| handoff/close 壓線情境 | 若 contract meaning 受影響，必須 rollback alignment | BLOCKED/ROLLBACK |

## Blockers

| ID | Type | Description | Required Human Input |
| --- | --- | --- | --- |
| B-01 | Classification ambiguity | 個別案例無法穩定判定是否屬於 import contract | 指定人工 reviewer 做語意判讀並定版 |
| B-02 | Contract-meaning risk | 任何調整牽動 scope/handoff/close semantics | 產品/流程 owner 明確確認後再重啟 |

## Freeze Decision

- 本需求基線可供 technical translation。
- 但任何觸發 BR-05 或 BR-06 的案例，必須以 **BLOCKED/ROLLBACK** 路徑處理，不得以推測補齊。
