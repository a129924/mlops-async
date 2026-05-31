# tests-remove-nonessential-xxx-module-helpers — Technical Specification

## Status

**Ready（含 blocker routing）**

## Translation Gate Check

- Baseline source: `analysis/tests-remove-nonessential-xxx-module-helpers/requirements.md`
- Gate result: **PASS**（需求可追溯、邊界明確、BLOCKED 規則完整）

## Technical Objective

將凍結需求翻譯為可執行的 implementation plan：在 `tests/` 全域移除非必要 helper-style imports，僅保留 import-contract 目的例外，並建立可稽核的分類與阻塞機制。

## Workflow Gate Alignment（python-implementation-workflow）

- Phase 1 Plan Review：本 technical-spec 與 plan/step/spec 需可審核且單一 topic。
- Phase 2 TDD Assessment：若 red-tests-ready 不成立或 context 不足，須回補，不得跳 gate。
- Phase 3 Implementation Gate：僅依 `step.md` 的 `## Implementation Steps` 完成度判定。
- Phase 4/5 Review：若 `needs-rework`，固定回 Phase 3 內迴圈。

## Requirement Traceability

| Business Req | Technical Realization | Planned Evidence |
| --- | --- | --- |
| BR-01 | 對 `tests/**` 建立 helper-style usage 全域盤點與移除策略 | helper usage inventory + rewrite 清單 |
| BR-02 | 建立 import-contract 例外判定規則（path/importability/contract only） | allowed 清單含每案 rationale |
| BR-03 | 把 patch-before-import 納入同一例外規則，不得獨立豁免 | classification decision log |
| BR-04 | 輸出 allowed / rewrite / BLOCKED 三類交接證據 | 三類清單與摘要統計 |
| BR-05 | 設計 ambiguous case routing 為 BLOCKED | BLOCKED registry + owner 欄位 |
| BR-06 | 實作範圍護欄僅限 tests | diff scope check（`tests/**` only） |
| BR-07 | 增加反規避檢核（fixture/helper 搬移） | anti-bypass guard test / review checklist |

## Classification Rule（核心）

1. **Import-contract test**：主要斷言為 import path、importability、module contract；可保留必要 helper-style import。
2. **Behavior test**：主要斷言為功能/流程/錯誤處理行為；helper-style import 必須移除。
3. **patch-before-import**：僅在 (1) 類別內可接受；其餘一律重寫。
4. 無法穩定歸類者：標記 **BLOCKED**，不得自動分類。

## Workstreams

### WS-1：全域盤點與初步分類（tests 全樹）
- 產出：helper-style usage inventory、初版分類表。

### WS-2：分類審核與 BLOCKED 分流
- 產出：allowed / rewrite / BLOCKED 三類清單（含每案理由）。

### WS-3：行為測試重寫設計
- 產出：rewrite blueprint（顯式 import 方案、fixture 去規避檢查點）。

### WS-4：驗收與護欄
- 產出：零容忍驗收清單（behavior tests helper-style usage = 0）與 scope guard（no `src/**` change）。

## Feasibility Conflicts / Blockers

| ID | Source Req | Conflict | Action |
| --- | --- | --- | --- |
| TB-01 | BR-05 | 部分測試僅靠靜態閱讀難以判定分類 | 維持 BLOCKED，交人工定版 |
| TB-02 | BR-07 | helper 可能被搬入 fixture 造成偽合規 | 實作 anti-bypass guard；未覆蓋前不得宣告完成 |

## Technical Freeze Decision

本 technical spec 可作為後續 implementation planning 依據；實作期若遇分類歧義，必須走 **BLOCKED**，不得猜測放行。
