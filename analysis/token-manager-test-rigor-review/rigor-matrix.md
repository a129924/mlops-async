# TokenManager Rigor Matrix

| criterion_id | status | evidence_path | risk_level | notes |
| --- | --- | --- | --- | --- |
| C-001-inventory-completeness | covered | analysis/token-manager-test-rigor-review/testcase-inventory.md | Low | Inventory 已同步納入 `TM-008`~`TM-011`。 |
| C-002-token-lifecycle-core-paths | covered | tests/unit/core/test_token_manager.py | Low | reuse/fetch/refresh/cancellation/failure 主要路徑仍有完整證據。 |
| C-003-concurrency-refresh-dedup | covered | tests/unit/core/test_token_manager.py::test_token_manager_refreshes_once_for_ten_concurrent_waiters | Low | refresh path 併發去重維持既有證據。 |
| C-004-auth-exception-pass-through | covered | tests/unit/core/test_token_manager.py::test_token_manager_re_raises_auth_exception_without_wrapping | Low | Baseline 2026-05-22: missing（High）。現已由 identity-based pass-through 測試關閉。 |
| C-005-custom-expiry-skew-at-manager-level | covered | tests/unit/core/test_token_manager.py::{test_token_manager_reuses_near_expiry_token_when_custom_manager_skew_is_zero,test_token_manager_refreshes_near_expiry_token_when_custom_manager_skew_is_large} | Low | Baseline 2026-05-22: missing（Medium）。現已由雙向 skew 決策測試關閉。 |
| C-006-empty-storage-concurrency-fetch-dedup | covered | tests/unit/core/test_token_manager.py::test_token_manager_fetches_once_for_ten_concurrent_waiters_when_storage_is_empty | Low | Baseline 2026-05-22: missing（Medium）。現已覆蓋 `cached_token is None` 的 fetch 併發去重。 |
| C-007-reviewer-reproducibility | covered | analysis/token-manager-test-rigor-review/{testcase-inventory.md,rigor-matrix.md,verdict.md} | Low | baseline 與 closure evidence 皆已文件化，可供 reviewer 重現。 |
