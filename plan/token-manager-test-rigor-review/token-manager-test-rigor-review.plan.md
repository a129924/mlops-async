# token-manager-test-rigor-review Plan (python-plan-authoring)

## Goal

在不修改 `src/` 與 `tests/` 程式碼前提下，凍結一份可審查、可執行的 TokenManager 測試嚴謹度盤點合約，供後續 creator 依序產出 inventory、matrix 與 verdict。

## Non-goals

- 不新增或修改任何 production code（`src/**`）。
- 不新增或修改任何測試實作（`tests/**`）。
- 不執行 commit、push、PR、merge、release。

## Current Context

- 需求基準已存在：`analysis/token-manager-test-rigor-review/requirements.md`（FROZEN）。
- 技術規格已存在：`analysis/token-manager-test-rigor-review/technical-spec.md`（INCOMPLETE, analysis-only）。
- 現有 topic plan 已建立於 `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`，但先前未符合 python-plan-authoring 13-section 合約。
- 目標程式與測試邊界主要位於：
  - `src/mlops_async/core/auth.py`
  - `src/mlops_async/core/token_storage.py`
  - `tests/unit/core/test_token_manager.py`
  - `tests/unit/core/test_token_storage.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_auth_contract.py`

## Requirements

1. 必須產出 `analysis/token-manager-test-rigor-review/testcase-inventory.md`，涵蓋既有 Token/Auth 相關 unit tests，遺漏數為 0。
2. 必須產出 `analysis/token-manager-test-rigor-review/rigor-matrix.md`，每個判準都要有 `covered|partial|missing` 與證據路徑。
3. 必須產出 `analysis/token-manager-test-rigor-review/verdict.md`，且強制包含規則：`High` 缺口數 > 0 時 verdict 必為「不夠嚴謹」。
4. `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md` 的步驟必須與本 plan 的 `## Implementation Steps` 一致，且初始為 `- [ ]`。
5. 本 topic 的計畫/分析工件不得引入 `src/**` 或 `tests/**` 內容變更。

## Decisions

- Async-planning status: exempt — cite exemption evidence: 本 topic 僅建立/修訂 planning 與 analysis 工件，未引入新的 async boundary、resource lifecycle、concurrency、timeout 或 cancellation 行為改動。
- Module/package placement: 規劃工件放置於 `plan/token-manager-test-rigor-review/`，分析工件維持於 `analysis/token-manager-test-rigor-review/`。
- New public API: no — 不新增公開函式/類別/方法。
- Interface changes: no — 不修改既有 `TokenManager`/`AuthProvider`/`TokenFetcher` 對外介面。
- Breaking changes allowed: no — 本 topic 為分析與規劃，不允許破壞性變更。
- New dependencies: no — 不新增相依套件。
- Error handling strategy: 規劃層若發現證據不足，標示 `INCOMPLETE` 並明列缺口，不以模糊敘述掩蓋。
- Typing strategy: 計畫不新增 Python runtime 代碼；若引用 signature 與型別，沿用現有嚴格型別契約，不引入 `Any` 擴張。

## Public Contract / API Changes

No public API changes.

## Affected Files / Modules

Likely affected files:
- plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md
- plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md
- plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md
- analysis/token-manager-test-rigor-review/technical-spec.md
- analysis/token-manager-test-rigor-review/testcase-inventory.md
- analysis/token-manager-test-rigor-review/rigor-matrix.md
- analysis/token-manager-test-rigor-review/verdict.md

Candidate files to inspect:
- analysis/token-manager-test-rigor-review/requirements.md
- analysis/token-manager-test-rigor-review/technical-spec.md
- tests/unit/core/test_token_manager.py
- tests/unit/core/test_token_storage.py
- tests/unit/core/test_auth_provider.py
- tests/unit/core/test_auth_contract.py

## Implementation Steps

1. 建立 `analysis/token-manager-test-rigor-review/testcase-inventory.md`：列出每個既有 Token/Auth 測試 case（`case_id`、`file_path`、`test_name`、`covers_area`）。
2. 建立 `analysis/token-manager-test-rigor-review/rigor-matrix.md`：以判準為列，填入 `criterion_id`、`status`（covered/partial/missing）、`evidence_path`、`risk_level`、`notes`。
3. 建立 `analysis/token-manager-test-rigor-review/verdict.md`：彙總 `high_gap_count`、`medium_gap_count`、`low_gap_count` 與最終 `verdict`，並套用 `high_gap_count > 0 => verdict=不夠嚴謹`。
4. 回讀 `requirements.md`、`technical-spec.md`、`plan.md`、`step.md` 與三個主體輸出檔，檢查 BR-1~BR-5 對齊後再交付 human review。

## Test Plan

Test file: `analysis/token-manager-test-rigor-review/rigor-matrix.md`（文件驗證為主；本 topic 不改測試程式碼）

Test cases:
- Happy path: 三個主體輸出檔（inventory/matrix/verdict）都存在，且欄位完整。
- Invalid input: matrix 任一列缺 `status` 或 `evidence_path` 時，標示為 INCOMPLETE。
- Edge case: `high_gap_count > 0` 時 verdict 必須是「不夠嚴謹」。
- Regression: 確認 `requirements.md` BR-1~BR-5 可在輸出檔找到對應證據。
- Backward compatibility: 確認 `src/**` 與 `tests/**` 無內容變更。

## Validation Commands

```
git --no-pager status --short
test -f analysis/token-manager-test-rigor-review/testcase-inventory.md
test -f analysis/token-manager-test-rigor-review/rigor-matrix.md
test -f analysis/token-manager-test-rigor-review/verdict.md
rg -n "high_gap_count|verdict|decision_rule" analysis/token-manager-test-rigor-review/verdict.md
rg -n "criterion_id|status|evidence_path|risk_level" analysis/token-manager-test-rigor-review/rigor-matrix.md
```

## Risks

- 若 plan 與 step/spec 版本不同步，reviewer 可能無法依同一合約判斷完成度，造成 review-ready 判定偏差。

## Rollback Plan

- Revert via git:
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md`

## Open Questions

- 是否需要在本 topic 追加 repo-visible `rigor-matrix.md` 作為 reviewer 快速檢視入口？（owner: @a129924）
