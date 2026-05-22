# TokenManager 測試嚴謹度盤點技術規格

## Status

- **INCOMPLETE**（可執行盤點，但尚未進入任何實作修補）

## Source baseline

- Business baseline: `analysis/token-manager-test-rigor-review/requirements.md`
- Translation scope: 分析現有 `TokenManager` 相關實作與測試證據，不修改 `src/` 與 `tests/`。

## Requirement traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| BR-1 完整 TestCase inventory | 從 `tests/unit/core/test_token_manager.py`, `test_token_storage.py`, `test_auth_provider.py`, `test_auth_contract.py` 抽取 case 清單，建立一致命名清單 | 測試檔可讀 | 低：單次盤點 | feasible |
| BR-2 coverage matrix | 建立「判準 × 證據」對照表（功能、並發、取消、錯誤、契約）並標 `covered/partial/missing` | 需對應 `src/mlops_async/core/auth.py` 與測試證據 | 中：需人工比對與分類 | feasible |
| BR-3 高風險門檻 | 定義風險規則：High 缺口 >0 則 verdict=不夠嚴謹；輸出風險分級與理由 | BR-2 完整矩陣 | 中：需一致分級標準 | feasible |
| BR-4 只收集資訊 | 僅產出 analysis/plan artifacts，不變更 `src/`、`tests/` | topic 邊界約束 | 低：流程控管 | feasible |
| BR-5 reviewer 可重現 | 輸出 artifact paths + 證據路徑 + verdict rule，供 reviewer 重跑判讀 | 人工 review gate | 中：文檔精確度要求 | feasible |

## Technical tasks and artifacts

1. 建立 `TestCase inventory`（case 名稱、檔案路徑、涵蓋面向）。
2. 建立 `rigor matrix`（判準、證據路徑、狀態、風險等級）。
3. 產出 `verdict` 與 `gap list`（含 High/Medium/Low 原因）。
4. 回寫 topic plan 的分析層對映狀態（已具備 requirements/technical-spec）。

### Artifact paths

- `analysis/token-manager-test-rigor-review/requirements.md`
- `analysis/token-manager-test-rigor-review/technical-spec.md`
- `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`

## Feasibility / cost-of-realization

- **Implementation complexity**: 低到中（以分析與比對為主）。
- **Sequencing pressure**: 需先鎖定判準，再做矩陣與風險判讀；否則結論不可重現。
- **Integration burden**: 低（僅讀現有程式與測試）。
- **Operational overhead**: 低（僅 human check 維護判準一致性）。

## Architecture-compliance self-check

| Dimension | Result | Note |
| --- | --- | --- |
| Async-first boundary | fits existing architecture | 只讀既有 async 實作，不改邊界 |
| Dependency direction boundary | fits existing architecture | 不新增依賴，只做證據映射 |
| Security/compliance | fits existing architecture | 無新增執行面，僅分析 |
| Observability/rollback support | fits with prerequisites | 需維持 artifact 可追溯路徑供 reviewer 重現 |

## Conflicts and rollback triggers

### Material conflicts

1. 若 inventory 與 matrix 結果互相矛盾（例如清單宣稱有案例但矩陣無證據）：
   - 視為 technical translation 不成立，回退到 requirements 對齊。
2. 若出現必須改碼才能判定的需求（超出「只收集資訊」）：
   - 回退到 alignment，請人類決定是否開新 implementation topic。

### Rollback-to-alignment triggers

1. failing business assumption: 「不改碼也可判定嚴謹度」
   technical contradiction: 關鍵判準無任何現有證據可觀察
   renegotiation needed: 是否允許新開 implementation topic 補測
2. failing business assumption: reviewer 可重現 verdict
   technical contradiction: artifact 不足以重建判斷
   renegotiation needed: 補足 matrix 欄位或調整判準精度

## Non-goal enforcement

- 不做 runtime coding / scaffolding。
- 不執行 `src/` 或 `tests/` 內容修改。
- 不進入 commit/push/PR 動作。
