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

1. 計畫文件必須完整具備 python-plan-authoring 要求的 13 個章節，且順序正確。
2. `Decisions` 必須包含 `Async-planning status` 與 7 項標準決策欄位，不得留空。
3. 必須產出 `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`，且 `## Implementation Steps` 與本 plan 一致、皆為 `- [ ]` 初始狀態。
4. D1 判定為 `non-trivial` 時，必須產出 `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md`，含三段：`Acceptance Criteria`、`Behavioral Scenarios`、`Error / Edge Cases`。
5. 本 topic 的計畫工件不得引入 `src/**` 或 `tests/**` 的內容變更。

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

Candidate files to inspect:
- analysis/token-manager-test-rigor-review/requirements.md
- analysis/token-manager-test-rigor-review/technical-spec.md
- .github/skills/python-plan-authoring/templates/python-plan-template.md

## Implementation Steps

1. Open `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`, replace current structure with python-plan-authoring 13-section contract and fill all required decision fields.
2. Create `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md` using step template metadata (`topic`, `phase: plan-authoring`, `created`) and mirror every numbered implementation step as pending `- [ ]`.
3. Declare D1 verdict as `non-trivial` in planning notes and create `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md` with required three sections and TokenManager rigor scenarios.
4. Re-open the three artifacts and cross-check section order, async-planning status citation, mirrored step entries, and spec completeness before handing off for human review.

## Test Plan

Test file: `tests/unit/core/test_token_manager.py` (reference-only verification target; 本 topic 不改測試程式碼)

Test cases:
- Happy path: 驗證 plan/step/spec 三份工件都存在，且 plan 13-section 完整。
- Invalid input: 若 `Decisions` 任一欄位缺失或留空，標示 plan 為 INCOMPLETE。
- Edge case: `Async-planning status` 為 exempt 時，必須包含可審查的 exemption 證據句，不可只寫 `exempt`。
- Regression: 確認既有 analysis 路徑 (`requirements.md`, `technical-spec.md`) 仍被正確引用，未回退成 missing-analysis 警告。
- Backward compatibility: 確認 `src/**` 與 `tests/**` 無變更，維持現有 API/測試行為不受影響。

## Validation Commands

```
cd <repo-root>
git --no-pager status --short
uv run pytest tests/unit/core/test_token_manager.py -q -o addopts=''
Use existing project validation commands from pyproject.toml.
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
