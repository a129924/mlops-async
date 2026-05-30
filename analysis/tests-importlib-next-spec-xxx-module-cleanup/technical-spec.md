# tests-importlib-next-spec-xxx-module-cleanup — Technical Specification

## Status

**Ready（含 blocker routing）**

## Translation Gate Check

- Baseline source: `analysis/tests-importlib-next-spec-xxx-module-cleanup/requirements.md`
- Gate result: **PASS**（需求可讀、可追溯、含 blocker 與 rollback 規則）

## Technical Objective

在**不進 implementation**前提下，提供可執行的技術翻譯：定義分類機制、工作流、成本與依序關係，確保後續實作只在 `tests/` 內推進，且與既有 `tests-importlib-plan-review` 決策一致。

## Requirement Traceability

| Business Req | Technical Realization | Planned Artifacts / Evidence | Feasibility |
| --- | --- | --- | --- |
| BR-01 | 建立「行為測試=explicit import only」分類規則，作為掃描與審核基準 | 行為測試違規清單（analysis 附錄或 review 證據） | 高 |
| BR-02 | 建立「動態引入僅限 `tests/contracts/`」路徑白名單規則 | contract 測試路徑盤點結果 | 高 |
| BR-03 | 建立 `test_import_contract_*` 命名檢核規則 | 命名不符清單與修正建議 | 高 |
| BR-04 | 檢查 direct + indirect importlib（fixture/helper wrapper） | wrapper 偵測案例清單 | 中 |
| BR-05 | 建立不可判定即 BLOCKED 的分流機制 | BLOCKED registry + human recheck queue | 高 |
| BR-06 | 建立 contract-meaning 變更偵測與 rollback trigger | rollback 事件紀錄格式 | 中 |
| BR-07 | 設定 scope guard（僅 `tests/`） | 變更範圍檢核紀錄 | 高 |
| BR-08 | 定義交付最小證據包（三類清單） | allow/rewrite/blocked 三類輸出 | 高 |

## Workstreams

### WS-1：測試案例盤點與分類規則凍結
- 內容：定義行為測試 vs import contract 的判定條件與優先順序。
- 產出：分類決策表、不可判定條件。
- 依賴：requirements frozen。
- 成本：**M**（規則精度要求高）。

### WS-2：路徑與命名合規翻譯
- 內容：把 `tests/contracts/` 集中與 `test_import_contract_*` 轉成可檢查條件。
- 產出：路徑白名單規則、命名檢核規則。
- 依賴：WS-1。
- 成本：**S**。

### WS-3：反規避機制（fixture/helper wrapper）
- 內容：辨識直接與間接 `importlib` 使用，防止包裝規避。
- 產出：wrapper 偵測規則與違規範例類型。
- 依賴：WS-1。
- 成本：**M-L**（需處理多型態呼叫鏈）。

### WS-4：BLOCKED 與 rollback 流程對齊
- 內容：定義無法判定與 contract-meaning 受影響時的停止與回滾流程。
- 產出：BLOCKED registry schema、rollback 觸發條件。
- 依賴：WS-1~WS-3。
- 成本：**M**（流程一致性風險高）。

### WS-5：交接證據包定義
- 內容：整理 allow/rewrite/blocked 三類清單與 reviewer recheck 入口。
- 產出：handoff 最小證據格式。
- 依賴：WS-2~WS-4。
- 成本：**S**。

## Sequencing / Cost / Staffing Pressure

1. 先 WS-1（否則後續無統一判定）。
2. 並行 WS-2、WS-3（互不阻塞但共用分類準則）。
3. 進入 WS-4 收斂風險路徑。
4. 最後 WS-5 封裝交接。

- 最低人力：1 planner + 1 reviewer。
- 壓力點：WS-3（反規避）與 WS-4（rollback 邊界）最易產生灰區。
- 營運負擔：主要是人工 recheck queue 維護，非執行期 runtime 成本。

## Architecture-Compliance Self-check

| Check Item | Result | Notes |
| --- | --- | --- |
| 僅處理 `tests/`，不碰 `src/` | PASS | 與 topic 邊界一致 |
| 不進 implementation | PASS | 本文件僅技術翻譯與流程規範 |
| 與既有 `tests-importlib-plan-review` 一致 | PASS | 延續「語意一致 + 不確定即停」原則 |
| 禁止 fixture/helper 規避 | PASS | 以 WS-3 明確納入 |
| contract meaning 變更需 rollback | PASS | WS-4 定義強制觸發 |

## Feasibility Conflicts / Blockers

| ID | Source Req | Conflict | Impact | Action |
| --- | --- | --- | --- | --- |
| TB-01 | BR-05 | 部分案例語意可能無法僅靠靜態資訊判定 | 無法自動完成全量分類 | 保持 BLOCKED，交人工 recheck |
| TB-02 | BR-06 | handoff/close 語意邊界若未有 owner 決議會停滯 | 無法合法 close topic | 啟動 rollback alignment，待 owner 決策 |

## Rollback Triggers

以下任一成立，必須停止並回到 business-intent alignment：

1. 需放寬「行為測試 importlib 零容忍」才可推進。
2. 需允許 `tests/contracts/` 以外動態引入才可完成需求。
3. 需改寫 `test_import_contract_*` 命名規則才可落地。
4. 為了交付而接受 fixture/helper 包裝 `importlib`。
5. 任何變更觸及 contract meaning（scope/handoff/close semantics）。

## Untranslatable Items

- 無新增不可翻譯 requirement。
- 但 BR-05 屬於「可翻譯但需人工決策完成」類型；不可自動閉環。

## Technical Freeze Decision

本 technical spec 可作為後續 implementation planning 的凍結輸入；執行時必須嚴格套用 BLOCKED/ROLLBACK 路徑，不得以推測補洞。
