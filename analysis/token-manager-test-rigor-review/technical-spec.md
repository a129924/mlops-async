# TokenManager 測試嚴謹度補強技術規格

## Status

- **READY-FOR-IMPLEMENTATION**（以 tests-first 關閉三個已識別 rigor gaps；production 修補僅為 contingency）

## Source baseline

- Business baseline: `analysis/token-manager-test-rigor-review/requirements.md`
- Translation scope: 補強 `TokenManager` 測試證據並同步 analysis artifacts；預期只改 `tests/unit/core/test_token_manager.py`，必要時最小修補 `src/mlops_async/core/auth.py`

## Requirement traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| IR-1 AuthException pass-through | 在 `tests/unit/core/test_token_manager.py` 新增 identity-based 直接透傳測試，驗證 `is original_error` 與 `__cause__ is None` | `mlops_async.core.auth.AuthException` 可被 subclass；`TokenManager` refresh path 可注入失敗 fetcher | 低 | feasible |
| IR-2 manager-level custom expiry_skew | 對同一 near-expiry token 撰寫兩個 path tests：`expiry_skew=0` reuse、`expiry_skew=5 minutes` refresh | `TokenManager.__init__(expiry_skew=...)` 與 `AccessToken.is_expired` | 低 | feasible |
| IR-3 empty-storage concurrency fetch dedup | 以 10 concurrent waiters 驗證 empty-storage fetch path 僅單次 fetch | 既有 `_BlockingTokenFetcher` helper 與 `asyncio.Event` 協調模式 | 低到中 | feasible |
| IR-4 scope control | 把 production 變更限制在 `src/mlops_async/core/auth.py` contingency only，其餘 related files 維持 inspect-only | plan/spec/step 邊界一致 | 低 | feasible |
| IR-5 analysis sync | 更新 inventory/matrix/verdict，保留 baseline gap 記錄並補上 closed-by evidence | 三個 analysis artifact 路徑已固定 | 低 | feasible |

## Technical tasks and artifacts

1. 更新 implementation contract 工件，使其從 analysis-only 改為 implementation topic：
   - `analysis/token-manager-test-rigor-review/requirements.md`
   - `analysis/token-manager-test-rigor-review/technical-spec.md`
   - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`
   - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`
   - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md`
2. 在 `tests/unit/core/test_token_manager.py` 新增以下測試：
   - `test_token_manager_re_raises_auth_exception_without_wrapping`
   - `test_token_manager_reuses_near_expiry_token_when_custom_manager_skew_is_zero`
   - `test_token_manager_refreshes_near_expiry_token_when_custom_manager_skew_is_large`
   - `test_token_manager_fetches_once_for_ten_concurrent_waiters_when_storage_is_empty`
3. 若新測試揭露 bug，只允許在 `src/mlops_async/core/auth.py` 做最小修補，且不得更動 public contract。
4. 同步更新 analysis outputs：
   - `analysis/token-manager-test-rigor-review/testcase-inventory.md`
   - `analysis/token-manager-test-rigor-review/rigor-matrix.md`
   - `analysis/token-manager-test-rigor-review/verdict.md`

### Artifact paths

- `analysis/token-manager-test-rigor-review/requirements.md`
- `analysis/token-manager-test-rigor-review/technical-spec.md`
- `analysis/token-manager-test-rigor-review/testcase-inventory.md`
- `analysis/token-manager-test-rigor-review/rigor-matrix.md`
- `analysis/token-manager-test-rigor-review/verdict.md`
- `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`
- `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`
- `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md`
- `tests/unit/core/test_token_manager.py`
- `src/mlops_async/core/auth.py`（contingency only）

## Feasibility / cost-of-realization

- **Implementation complexity**: 低（以單檔 unit tests 為主）。
- **Sequencing pressure**: 先凍結 implementation contract，再補測試，最後同步 analysis verdict。
- **Integration burden**: 低；不新增依賴，沿用既有 test helpers。
- **Operational overhead**: 低到中；需跑 pytest / pyright / ruff 驗證 workflow gate。

## Architecture-compliance self-check

| Dimension | Result | Note |
| --- | --- | --- |
| Async-first boundary | fits existing architecture | 測試補強不新增 async boundary；若 contingency patch 也只在既有 `TokenManager` 邏輯內 |
| Dependency direction boundary | fits existing architecture | 不新增依賴，仍由 `TokenManager -> TokenFetcher/TokenStorage` |
| Security/compliance | fits existing architecture | 純 unit-test 與 doc artifact 更新 |
| Observability/rollback support | fits existing architecture | analysis artifacts 保留 baseline 與 closure evidence |

## Conflicts and rollback triggers

### Material conflicts

1. 若 `AuthException` pass-through 測試只能以 `TokenFetchException` 綠燈，代表測試無法區分「直接透傳」與「重新包裝」：
   - 必須回退並改成 identity-based assertion。
2. 若 manager-level skew 只測單一方向，無法證明 `TokenManager` 使用自訂 skew：
   - 必須回退並補齊雙向決策測試。
3. 若 empty-storage concurrency 測試與 refresh path concurrency 測試沒有實質差異：
   - 視為 gap 未關閉，需明確覆蓋 `cached_token is None` 分支。

### Rollback-to-alignment triggers

1. failing business assumption: 「三個 gap 只靠 `test_token_manager.py` 即可關閉」
   technical contradiction: 任一 gap 需要改動 unrelated test file 才能驗證
   renegotiation needed: 是否拆出新 topic
2. failing business assumption: 「production 理應已支援三個 gap」
   technical contradiction: 新測試要求超出 `src/mlops_async/core/auth.py` 的修補
   renegotiation needed: 是否擴 scope 或停止

## Non-goal enforcement

- 不修改 `tests/unit/core/test_token_storage.py`、`tests/unit/core/test_auth_provider.py`、`tests/unit/core/test_auth_contract.py`。
- 不新增 public API 或變更 package exports。
- 不執行 commit/push/PR。
