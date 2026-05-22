# TokenManager 測試嚴謹度盤點需求基準

## Status

- **FROZEN**（可進入 technical translation）

## Problem Statement

- 使用者需要在**不修改任何程式碼**前，先判定 `TokenManager` 與其相關測試是否達到可接受的嚴謹度，並拿到可追溯的 TestCase 清單與缺口判讀依據。

## Actors / Boundaries

- **Primary actor**: 規劃/審查者（planner/reviewer）
- **Observed scope**:
  - `src/mlops_async/core/auth.py`（`TokenManager` / `AuthProvider` / `TokenFetcher` 契約）
  - `src/mlops_async/core/token_storage.py`
  - `tests/unit/core/test_token_manager.py`
  - `tests/unit/core/test_token_storage.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_auth_contract.py`
- **Out of scope actor action**: 實作/修測試/提交程式碼

## Measurable Requirements

| ID | Actor | Condition | Observable outcome | Metric / decision rule | Failure meaning |
| --- | --- | --- | --- | --- | --- |
| BR-1 | Planner | 開始本 topic 盤點 | 產出完整 TestCase inventory（含檔案與 case 名稱） | Inventory 覆蓋上述 observed scope 中所有現有 Token/Auth 相關 unit tests；遺漏數 = 0 | 無法信任盤點結論 |
| BR-2 | Planner | 進行「是否足夠嚴謹」判定 | 產出 coverage matrix（判準 × 證據） | 每個判準都必須有 `covered / partial / missing` 狀態與證據路徑 | 判斷落入主觀敘述 |
| BR-3 | Planner | 套用高嚴謹標準 | 產出風險分級結論 | `High` 缺口若 >0，最終 verdict 必須是「不夠嚴謹」；不可宣告通過 | 錯誤宣告「可接受」 |
| BR-4 | Planner | 僅收集資訊模式 | 產出不含實作變更的分析結果 | 變更範圍不得包含 `src/` 或 `tests/` 程式碼內容修改 | 違反 topic 邊界 |
| BR-5 | Reviewer | human check 時審閱 | 可獨立重現同一結論 | reviewer 可用 artifact paths 與 matrix 重新對照並得到同一 verdict | 審查不可重現 |

## Assumptions

1. `TokenManager` 行為契約以 `src/mlops_async/core/auth.py` 現況為準。
2. 測試嚴謹度是「證據充分性」判斷，不等同 coverage% 指標。
3. 本 topic 允許先產出分析與計畫，再決定是否進入後續實作 topic。

## Non-goals

1. 不新增或修改任何 production code。
2. 不新增或修改任何 test code。
3. 不執行 release/發版行為。

## Contradictions surfaced

1. **快速完成盤點** vs **高嚴謹標準**
   - 衝突點：快速盤點常省略邊界案例；高嚴謹要求完整邊界證據。
   - 決議：以高嚴謹為優先，允許 INCOMPLETE/不通過 verdict。
2. **只收集資訊** vs **希望得到足夠嚴謹結論**
   - 衝突點：不改測試時，結論可能只能是「有缺口」。
   - 決議：接受「不夠嚴謹」作為有效結果，不強行給通過結論。

## Extreme-boundary checks

1. **No network / degraded dependency**: 本 topic 為靜態盤點，不依賴外部網路；若測試需外部依賴，視為缺口訊號。
2. **Wrong role / missing approval**: 若無 reviewer/human check，verdict 僅為草案，不可視為最終核定。
3. **Interrupted / partial flow**: 若只完成 inventory 未完成 matrix，狀態必須標示 INCOMPLETE。
4. **Low-volume / peak-volume**: 盤點時需檢查並發場景是否具代表性（例如 refresh/fetch 高併發路徑）。

## Blockers

- 無硬阻塞；可進入 technical translation。
