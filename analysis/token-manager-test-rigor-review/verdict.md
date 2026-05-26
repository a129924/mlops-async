# TokenManager Rigor Verdict

## Analysis baseline (2026-05-22)

high_gap_count: 1
medium_gap_count: 2
low_gap_count: 0
decision_rule: high_gap_count > 0 => verdict=不夠嚴謹
verdict: 不夠嚴謹

gap_list:
  - id: C-004-auth-exception-pass-through
    severity: High
    reason: 缺少 `AuthException` 直接透傳的單元測試證據。
  - id: C-005-custom-expiry-skew-at-manager-level
    severity: Medium
    reason: 缺少 TokenManager 層自訂 expiry_skew 決策測試。
  - id: C-006-empty-storage-concurrency-fetch-dedup
    severity: Medium
    reason: 缺少 empty-storage 並發 fetch 去重測試。

## Current status after implementation closure (2026-05-23)

high_gap_count: 0
medium_gap_count: 0
low_gap_count: 0
decision_rule: high_gap_count > 0 => verdict=不夠嚴謹
verdict: 足夠嚴謹

closed_gap_list:
  - id: C-004-auth-exception-pass-through
    baseline_severity: High
    closed_by: tests/unit/core/test_token_manager.py::test_token_manager_re_raises_auth_exception_without_wrapping
    note: 直接驗證例外 identity 未變、`__cause__` 為 `None`，且舊 token state 保持不變。
  - id: C-005-custom-expiry-skew-at-manager-level
    baseline_severity: Medium
    closed_by:
      - tests/unit/core/test_token_manager.py::test_token_manager_reuses_near_expiry_token_when_custom_manager_skew_is_zero
      - tests/unit/core/test_token_manager.py::test_token_manager_refreshes_near_expiry_token_when_custom_manager_skew_is_large
    note: 以同一 near-expiry token 驗證 zero skew reuse 與 large skew refresh 的雙向決策。
  - id: C-006-empty-storage-concurrency-fetch-dedup
    baseline_severity: Medium
    closed_by: tests/unit/core/test_token_manager.py::test_token_manager_fetches_once_for_ten_concurrent_waiters_when_storage_is_empty
    note: 驗證 empty-storage fetch path 在 10 個 concurrent waiters 下只觸發 1 次 fetch。
