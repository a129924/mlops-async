# token-manager-test-rigor-review Specification

## Acceptance Criteria

1. `tests/unit/core/test_token_manager.py` 新增 `AuthException` pass-through 測試，並驗證原始例外 instance 未被包裝、未帶 `__cause__`、storage state 不變。
2. `tests/unit/core/test_token_manager.py` 新增兩個 manager-level custom skew 測試：同一 near-expiry token 在 `expiry_skew=0` 下 reuse、在 `expiry_skew=timedelta(minutes=5)` 下 refresh。
3. `tests/unit/core/test_token_manager.py` 新增 empty-storage 併發 fetch dedup 測試，10 個 waiters 僅觸發 1 次 fetch。
4. `analysis/token-manager-test-rigor-review/testcase-inventory.md`、`rigor-matrix.md`、`verdict.md` 必須反映新測試，並保留 baseline audit trail。
5. 若新測試未揭露 bug，`src/**` 不得有內容修改；若揭露 bug，僅允許最小修改 `src/mlops_async/core/auth.py` 且 public contract 不變。

## Behavioral Scenarios

### Scenario 1: TokenManager preserves AuthException identity
- **Given**: storage 內已有過期 token，fetcher 在 refresh path 丟出自訂 `AuthException`
- **When**: `TokenManager.get_access_token()` 執行 refresh
- **Then**: 呼叫端收到的例外必須是同一個原始 instance，且不帶 chained cause，storage 仍保留原本 token

### Scenario 2: manager-level custom skew changes decision path
- **Given**: 同一個 `expires_at = now + 30 seconds` 的 token
- **When**: `TokenManager(expiry_skew=timedelta(0))` 讀取 token
- **Then**: token 應被視為仍可用，不 refresh
- **And When**: `TokenManager(expiry_skew=timedelta(minutes=5))` 讀取同樣 near-expiry token
- **Then**: token 應被視為已過期並 refresh

### Scenario 3: empty-storage concurrency dedups fetch path
- **Given**: storage 為空，10 個 concurrent waiters 同時要求 token
- **When**: 第一個 waiter 進入 fetch path 並持有 refresh lock
- **Then**: 所有 waiters 都收到同一個 fetched token，fetch 僅執行一次，refresh 次數為零

### Scenario 4: audit trail reflects both baseline and closure
- **Given**: analysis baseline 曾將 `C-004`~`C-006` 標為 missing
- **When**: gap closure tests 完成並通過
- **Then**: matrix / verdict 必須保留 baseline findings，同時加入 closed-by evidence 與 current verdict

## Error / Edge Cases

- 若 `AuthException` 測試只驗證 type 而未驗證 instance identity，視為 acceptance 未達成。
- 若 custom skew 測試只覆蓋單一方向，視為 `C-005` 未關閉。
- 若 empty-storage concurrency 測試仍允許多次 fetch，視為 `C-006` 未關閉。
- 若更新 verdict 時抹除 baseline gap counts，視為 audit trail regression。
- 若 diff 涉及 `tests/unit/core/test_token_storage.py`、`test_auth_provider.py`、`test_auth_contract.py`，視為 scope violation。
