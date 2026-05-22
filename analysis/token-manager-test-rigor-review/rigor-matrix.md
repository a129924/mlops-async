# TokenManager Rigor Matrix

| criterion_id | status | evidence_path | risk_level | notes |
| --- | --- | --- | --- | --- |
| C-001-inventory-completeness | covered | analysis/token-manager-test-rigor-review/testcase-inventory.md | Low | 已列出 Token/Auth 相關既有 unit tests。 |
| C-002-token-lifecycle-core-paths | covered | tests/unit/core/test_token_manager.py | Low | reuse/fetch/refresh/cancellation/failure 主要路徑有測試證據。 |
| C-003-concurrency-refresh-dedup | covered | tests/unit/core/test_token_manager.py::test_token_manager_refreshes_once_for_ten_concurrent_waiters | Low | refresh path 併發去重已有證據。 |
| C-004-auth-exception-pass-through | missing | src/mlops_async/core/auth.py (except AuthException: raise) | High | 行為存在但缺 direct unit test，屬高風險缺口。 |
| C-005-custom-expiry-skew-at-manager-level | missing | src/mlops_async/core/auth.py (__init__(expiry_skew)) | Medium | storage 層有 skew 測試，manager 層自訂 skew 決策尚未直接驗證。 |
| C-006-empty-storage-concurrency-fetch-dedup | missing | src/mlops_async/core/auth.py + tests/unit/core/test_token_manager.py | Medium | 目前僅覆蓋 refresh 併發，未覆蓋 empty-storage fetch 併發去重。 |
| C-007-reviewer-reproducibility | covered | analysis/token-manager-test-rigor-review/{testcase-inventory.md,rigor-matrix.md,verdict.md} | Low | 判準、證據、風險與 verdict 規則已文檔化。 |
