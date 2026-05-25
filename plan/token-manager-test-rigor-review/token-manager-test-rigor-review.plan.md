# token-manager-test-rigor-review Plan (python-plan-authoring)

## Goal

以最小實作範圍補齊 `TokenManager` 的三個已識別 rigor gaps，並同步更新 analysis artifacts，使 topic 從「已證明不夠嚴謹」收斂到「以具體單元測試關閉缺口」的可審查狀態。

## Non-goals

- 不修改 `tests/unit/core/test_token_storage.py`、`tests/unit/core/test_auth_provider.py`、`tests/unit/core/test_auth_contract.py`。
- 不做 `TokenManager` 廣義重構、public API 變更或 async boundary redesign。
- 不執行 commit、push、PR、merge、release。

## Current Context

- analysis baseline 已識別三個 gaps：
  - `C-004-auth-exception-pass-through`（High）
  - `C-005-custom-expiry-skew-at-manager-level`（Medium）
  - `C-006-empty-storage-concurrency-fetch-dedup`（Medium）
- `src/mlops_async/core/auth.py` 目前看起來已支援三個行為，但缺少直接測試證據。
- 相關檢視檔案仍包含：
  - `tests/unit/core/test_token_storage.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_auth_contract.py`
  這些檔案在本 topic 保持 inspect-only，不作修改。
- 預期主要實作檔為 `tests/unit/core/test_token_manager.py`；`src/mlops_async/core/auth.py` 只在新測試揭露真 bug 時做 contingency patch。

## Requirements

1. `tests/unit/core/test_token_manager.py` 必須新增 `AuthException` 直接透傳測試，並驗證例外 identity 未變、未被 chained、且 token state 不變。
2. `tests/unit/core/test_token_manager.py` 必須新增 manager-level custom `expiry_skew` 雙向測試：同一 near-expiry token 在 `expiry_skew=0` 下 reuse、在 `expiry_skew=5 minutes` 下 refresh。
3. `tests/unit/core/test_token_manager.py` 必須新增 empty-storage 高併發 fetch 去重測試：10 個 waiters 僅 1 次 fetch、0 次 refresh。
4. 若新測試直接通過，`src/**` 不得有內容變更；若失敗，僅允許最小修補 `src/mlops_async/core/auth.py`，且 public contract 不變。
5. `analysis/token-manager-test-rigor-review/testcase-inventory.md`、`rigor-matrix.md`、`verdict.md` 必須同步反映新測試與 gap closure，並保留 baseline audit trail。

## Decisions

- Async-planning status: exempt — 本 topic 主要是 unit tests 與 analysis artifact 補強，不新增 async boundary；若 contingency patch 發生，也僅在既有 `TokenManager` 邏輯內調整。
- Module/package placement: 新測試集中在 `tests/unit/core/test_token_manager.py`；analysis 與 plan 工件維持既有 topic 路徑。
- New public API: no — 不新增公開函式/類別/方法。
- Interface changes: no — `TokenManager` / `AuthProvider` / `TokenFetcher` 對外契約不變。
- Breaking changes allowed: no — 僅補測試證據與必要最小修補。
- New dependencies: no — 沿用既有 `pytest` / `pytest-asyncio`。
- Error handling strategy: 若新增測試揭露例外處理錯誤，只修正最小責任點，並保留 `AuthException` 直接透傳與 generic exception translation contract。
- Typing strategy: 沿用既有嚴格型別與 test helpers，不引入 `Any` 或型別逃逸。

## Public Contract / API Changes

No public API changes.

## Affected Files / Modules

Likely affected files:
- analysis/token-manager-test-rigor-review/requirements.md
- analysis/token-manager-test-rigor-review/technical-spec.md
- analysis/token-manager-test-rigor-review/testcase-inventory.md
- analysis/token-manager-test-rigor-review/rigor-matrix.md
- analysis/token-manager-test-rigor-review/verdict.md
- plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md
- plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md
- plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md
- tests/unit/core/test_token_manager.py
- src/mlops_async/core/auth.py (contingency only)

Candidate files to inspect:
- tests/unit/core/test_token_storage.py
- tests/unit/core/test_auth_provider.py
- tests/unit/core/test_auth_contract.py

## Implementation Steps

1. 更新 `requirements.md`、`technical-spec.md`、`plan.md`、`step.md`、`spec.md`，把 topic 從 analysis-only 改為 implementation contract，並明確鎖定 `C-004`~`C-006` 三個 gaps。
2. 在 `tests/unit/core/test_token_manager.py` 新增以下 gap-closure tests：
   - `test_token_manager_re_raises_auth_exception_without_wrapping`
   - `test_token_manager_reuses_near_expiry_token_when_custom_manager_skew_is_zero`
   - `test_token_manager_refreshes_near_expiry_token_when_custom_manager_skew_is_large`
   - `test_token_manager_fetches_once_for_ten_concurrent_waiters_when_storage_is_empty`
3. 執行 pytest 驗證新測試；若揭露 production bug，僅在 `src/mlops_async/core/auth.py` 做最小修補並重跑驗證。
4. 更新 `testcase-inventory.md`、`rigor-matrix.md`、`verdict.md` 與 `step.md`，把 baseline 缺口標記為已關閉並保留 audit trail。

## Test Plan

Test files:
- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_token_storage.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_auth_contract.py`

Test cases:
- Happy path: `expiry_skew=0` 時 near-expiry token 應直接 reuse，不 fetch / refresh。
- Error / exception: `AuthException` 由 fetcher 丟出時，`TokenManager` 必須直接透傳原始 instance。
- Boundary / edge: 同一 near-expiry token 在大 skew 下必須 refresh，證明 manager-level skew plumbing 生效。
- State / side effects: 發生 `AuthException` 或併發 fetch 時，storage state 與 fetch/refresh call counts 必須符合 contract。
- Integration points: empty-storage 10 併發 waiters 經由 shared lock 僅觸發一次 fetch。

## Validation Commands

```bash
git --no-pager status --short
uv run pytest tests/unit/core/test_token_manager.py tests/unit/core/test_token_storage.py tests/unit/core/test_auth_provider.py tests/unit/core/test_auth_contract.py -q
uv run pytest tests/ -q
uv run pyright
uv run ruff check .
```

## Risks

- 若只新增單向 skew 測試，可能誤判 `TokenManager` 已正確使用自訂 skew。
- 若 `AuthException` 測試未驗證 identity，可能留下「重新包裝也會綠」的 false confidence。
- 若 analysis artifacts 只改 current verdict 而不保留 baseline，會失去本 topic 的審查歷史。

## Rollback Plan

- Revert via git:
  - `analysis/token-manager-test-rigor-review/requirements.md`
  - `analysis/token-manager-test-rigor-review/technical-spec.md`
  - `analysis/token-manager-test-rigor-review/testcase-inventory.md`
  - `analysis/token-manager-test-rigor-review/rigor-matrix.md`
  - `analysis/token-manager-test-rigor-review/verdict.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md`
  - `tests/unit/core/test_token_manager.py`
  - `src/mlops_async/core/auth.py` (if modified)

## Open Questions

- 無；本 topic scope 已鎖定為三個 gap closure tests + 必要最小同步工件更新。
