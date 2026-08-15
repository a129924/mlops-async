# AuthClient refresh-token public API 技術規格

## Goal

在 `src/mlops_async/clients/auth_client.py` 增加最小、公開且完全型別化的 async refresh
委派入口，且不擴張 core 或 package-root surface。

## Non-Goal

- 不修改 `src/mlops_async/core/auth.py` 的 protocols 或 `TokenManager`。
- 不修改 `src/mlops_async/core/token_storage.py`、token-endpoint clients、transport、依賴或
  root exports。
- 不修改 VERSION、`pyproject.toml`、`uv.lock`、release、tag、commit、push 或 PR。
- 不增加 timeout、retry、lock、cache、context manager 或併發 fan-out。

## In-Scope

- 在 `AuthClient` 所在 module 定義 `AuthClientRefreshTokenError`，並實作
  `async def refresh_access_token(self, token: AccessToken) -> AccessToken`。
- 使用現有 runtime-checkable `TokenEndpointClientProtocol` 判斷有 refresh token 時的
  collaborator 能力。
- 於 `tests/unit/clients/test_auth_client.py` 擴充分支、取消與 exception-chain coverage。
- 更新 `README.md` 的 English 與繁體中文 `AuthClient` public-surface 段落，使其準確描述
  新 refresh API 與既有 import boundary。
- 建立本 topic 的 requirements、technical spec、plan、step tracker 與 spec artifacts。

## Out-Of-Scope

- `AuthClient.__init__` 型別或 `get_access_token()` 的控制流程、例外語意與呼叫次數。
- 任何 `mlops_async` package-root re-export 或 public facade wiring。
- live E2E、憑證、VPN、測試環境設定與 token JSON。

## ReadOnly

- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/__init__.py`
- `src/mlops_async/clients/__init__.py`
- `VERSION`, `pyproject.toml`, `uv.lock`
- `tests/integration/**`, `config/.env.test`

## Written

- `analysis/auth-client-refresh-token-public-api/requirements.md`
- `analysis/auth-client-refresh-token-public-api/technical-spec.md`
- `plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.plan.md`
- `plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.step.md`
- `plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.spec.md`

## Deleted

- None.

## Modify

- `src/mlops_async/clients/auth_client.py`
- `tests/unit/clients/test_auth_client.py`
- `README.md`

## Frozen Design

- `AuthClientRefreshTokenError` lives beside `AuthClient`; it is intentionally not re-exported
  from `mlops_async`.
- `refresh_access_token()` first examines `token.refresh_token`. If it is `None`, it awaits
  `self._token_endpoint_client.fetch_access_token()` exactly once and does not require the full
  protocol.
- If a refresh token exists, it must require `TokenEndpointClientProtocol`. A fetch-only
  collaborator raises `AuthClientRefreshTokenError` and does not receive a fetch call.
- A full collaborator receives the exact token object through its refresh method. Cancellation
  is re-raised unchanged. Every other `Exception` raised by that refresh is translated to
  `AuthClientRefreshTokenError` with `raise ... from exc`.
- No separate timeout, retry, cleanup, resource ownership or concurrency mechanism is added.

## TestCase

1. Absent `refresh_token`: fetch-only collaborator is accepted; fetch is awaited once and the
   exact fetched token is returned.
2. Present `refresh_token` with full collaborator: refresh is awaited once with the same token;
   fetch is not called.
3. Present `refresh_token` with fetch-only collaborator: `AuthClientRefreshTokenError` is
   raised and neither unsupported refresh nor fallback fetch occurs.
4. Full collaborator cancellation: the same `asyncio.CancelledError` escapes unchanged.
5. Full collaborator ordinary failure: `AuthClientRefreshTokenError` is raised with the original
   error as `__cause__`.
6. Regression: existing constructor compatibility and `get_access_token()` behavior stay intact.
7. Public documentation: `README.md` 的 English 與繁體中文 `AuthClient` public-surface
   段落列出 `refresh_access_token()`、其 absent-token fetch 行為、present-token full-protocol
   requirement、`AuthClientRefreshTokenError` 與無 package-root export。

## Validation Commands

在 native Windows host 上，所有 Python/uv commands 必須透過 `windows-wsl-dev` 指定的
WSL route 執行：

```text
uv run --frozen python -m pytest tests/unit/clients/test_auth_client.py
uv run --frozen python -m ruff format --check src/mlops_async/clients/auth_client.py tests/unit/clients/test_auth_client.py
uv run --frozen python -m ruff check src/mlops_async/clients/auth_client.py tests/unit/clients/test_auth_client.py
uv run --frozen python -m pyright
uv run --frozen python -m tach check
git diff --check
```
