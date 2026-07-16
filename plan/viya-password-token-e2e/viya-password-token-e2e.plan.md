# Viya password token E2E

## Goal

在明確 process opt-in 時，以真實 HTTPS 呼叫 SAS Viya password-grant token endpoint；只在 HTTP `200`、非空 `access_token` 與正整數 `expires_in` 都成立時通過。

## Non-goals

- 不會呼叫第二個 protected proof endpoint。
- 不會修改 `src/mlops_async/`、既有 client-credentials 流程或公開 API。
- 不會加入 mock、fake transport、fallback token、`verify=False` 或 CI 排程。
- 不會讀出、複製、提交或列印 `config/.env.test` 與任何 credential/token。
- 不會更新 README、VERSION、pyproject.toml、uv.lock 或發行版本。

## Current Context

- `src/mlops_async/core/token_endpoint/password.py` 已有內部 `PasswordTokenEndpointClient`，會以 password grant 呼叫 `/SASLogon/oauth/token`。
- `HttpClient` 可維持 TLS 驗證，`RequestTimeouts` 可提供總計 30 秒 timeout。
- `config/.env.test` 已由 `.gitignore` 忽略，且本 worktree 不存在該檔案；它必須由授權者安全 provision。

## Requirements

1. 僅 process environment 的 `RUN_VIYA_E2E=1` 可以啟用 marked E2E；一般 pytest 必須 skip，`pytest -m viya_e2e` 未 opt-in 必須 fail。
2. config loader 僅從 worktree `config/.env.test` 讀取 BASE_URL、USERNAME、PASSWORD、CLIENT_ID、CLIENT_SECRET，且忽略 config 中的 `RUN_VIYA_E2E`。
3. client secret 只在 `client_id=sas.ec` 且值為空字串時有效；其他 client secret 必須非空白。
4. E2E 僅接受非-loopback HTTPS origin，使用 `verify=True` 與 total timeout 30 秒。
5. 真實 request 的唯一成功條件是 exact HTTP 200、非空 access token 與未過期的 token expiry；TLS、DNS、timeout、HTTP、JSON 或 schema 問題都必須 fail。
6. assertion、traceback、log 與證據不得包含 username、password、client secret、Basic header、access token 或 response body。

## Decisions

- Async-planning status: triggered — cite trigger evidence: `PasswordTokenEndpointClient.fetch_access_token()`、`HttpClient.request()` 與 marked E2E 均為 async 外部 HTTP I/O，並有 30 秒 timeout 與 cancellation 邊界。
- Module/package placement: test-only code 位於 `tests/conftest.py`、`tests/integration/viya_e2e_config.py` 與 `tests/integration/test_viya_password_token_e2e.py`。
- New public API: no；不改 production package export 或 public client contract。
- Interface changes: no；僅新增 pytest hook、測試 helper 與測試案例。
- Breaking changes allowed: no；既有 unit tests 與 client-credentials 行為不得變更。
- New dependencies: no；只使用既有 pytest 與 package 依賴。
- Error handling strategy: config helper 只拋出不含 secret 的 `ViyaE2EConfigError`；E2E 將非 cancellation 的 runtime error 轉成 redacted `AssertionError`，`asyncio.CancelledError` 原樣傳播。
- Typing strategy: 所有新 helper 與測試支援函式均使用完整 Python type annotations；不使用 `Any` 或 suppressions。

### Async boundary decision

E2E 只在 async pytest test 內 await `PasswordTokenEndpointClient.fetch_access_token()`；不改 production async boundary。

### Resource lifecycle decision

每次 test 以 `async with HttpClient(...)` 建立並關閉真實 transport，不跨 test 共用 client 或 token。

### Concurrency model

單一 test、單一 token request；不做並行、retry、pooling 或 background task。

### Failure model

任何 config、transport、TLS、DNS、timeout、非 200、非 JSON 或 response schema 問題皆為 redacted test failure；不得轉為 pass、skip 或 fallback。

### Cancellation / timeout policy

`RequestTimeouts(total=30)` 是完整 request budget；`asyncio.CancelledError` 不攔截、不轉譯。

### Validation plan

單元測試驗證 loader；未 opt-in 時驗證 skip 與 explicit marker failure；配置存在且 opt-in 後才可執行真實 E2E，失敗不可偽裝成功。

### Handoff notes for the implementer

不得自行建立或輸出 `config/.env.test`；此檔不存在時不得聲稱 live E2E 成功。

## Public Contract / API Changes

沒有 public API change。`tests.integration.viya_e2e_config.load_viya_e2e_config(path: Path = ...) -> ViyaE2EConfig` 是 test-only helper；它可拋出 `ViyaE2EConfigError`，不屬於 package API。

## Affected Files / Modules

Likely affected files:

- `tests/__init__.py`
- `tests/conftest.py`
- `tests/integration/viya_e2e_config.py`
- `tests/integration/test_viya_password_token_e2e.py`
- `tests/unit/integration/test_viya_e2e_config.py`
- `analysis/viya-password-token-e2e/requirements.md`
- `analysis/viya-password-token-e2e/technical-spec.md`
- `plan/viya-password-token-e2e/viya-password-token-e2e.plan.md`
- `plan/viya-password-token-e2e/viya-password-token-e2e.spec.md`
- `plan/viya-password-token-e2e/viya-password-token-e2e.step.md`

Candidate files to inspect:

- `src/mlops_async/core/token_endpoint/password.py`
- `src/mlops_async/core/http_client.py`
- `pyproject.toml`

## Implementation Steps

1. In `plan/viya-password-token-e2e/*` and the managed worktree, record the contract and verify `config/.env.test` is ignored without reading its content.
2. Add `tests/integration/viya_e2e_config.py` and `tests/unit/integration/test_viya_e2e_config.py` for safe config parsing, required fields, URL safety and the `sas.ec` exception.
3. Add `tests/__init__.py` and `tests/conftest.py` so `viya_e2e` is registered, ordinary runs skip without process opt-in, and explicit marker selection fails without it.
4. Add `tests/integration/test_viya_password_token_e2e.py` to make the one real password-grant request, assert exact success, and redact all failure evidence.
5. Run targeted tests, regression tests, non-E2E suite, ruff and pyright; run the actual E2E only after external secure provisioning and report absence as not executed.

## Test Plan

- Happy path: `tests/integration/test_viya_password_token_e2e.py` requires real HTTP 200, nonempty token and future expiry only after opt-in and secure config.
- Invalid input: `tests/unit/integration/test_viya_e2e_config.py` rejects missing keys, malformed lines, non-HTTPS/loopback URLs and invalid client secret combinations without echoing values.
- Edge case: the same unit test accepts only an exact empty secret for `sas.ec`; it rejects whitespace secret values.
- Regression: existing `tests/unit/core/test_password_token_endpoint_client.py` and `tests/unit/core/test_token_endpoint_client.py` remain green.
- Backward compatibility: non-E2E pytest skips marked test; explicit `pytest -m viya_e2e` without opt-in fails rather than issuing a request or pretending success.
- Async validation: cancellation propagates, one transport is closed per test, and a total 30-second timeout is supplied.

## Validation Commands

- `uv run pytest --no-cov tests/unit/integration/test_viya_e2e_config.py -q`
- `uv run pytest --no-cov tests/integration/test_viya_password_token_e2e.py -q`
- `uv run pytest --no-cov -m viya_e2e -q` (expected nonzero when process opt-in is absent)
- `uv run pytest --no-cov tests/unit/core/test_password_token_endpoint_client.py tests/unit/core/test_token_endpoint_client.py -q`
- `uv run pytest --no-cov -m "not viya_e2e" -q`
- `uv run ruff check tests`
- `uv run pyright`

## Risks

- 真實 Viya endpoint 或 TLS trust chain 不可用時，E2E 會正確失敗；它不可被 unit evidence 覆蓋。
- config parser 若回顯輸入或 failure chain 未 redaction，可能使敏感資料出現在 CI / terminal。
- `config/.env.test` 未 secure provision 時，live validation 保持未執行。

## Rollback Plan

以 Git 回復本 topic 所新增的 `tests/`、`analysis/viya-password-token-e2e/` 與 `plan/viya-password-token-e2e/` 檔案；不需 rollback production code 或 migration。

## Open Questions

- 外部授權者需在此 managed worktree 安全 provision `config/.env.test`，並以 process environment 設定 `RUN_VIYA_E2E=1` 後才可執行 live E2E；這不是本次 implementation 的 blocker，因為它不影響 test harness 完成。
