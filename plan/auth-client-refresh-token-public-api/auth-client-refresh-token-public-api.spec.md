# AuthClient refresh-token public API Specification

## Acceptance Criteria

1. `AuthClient` 在 `mlops_async.clients.auth_client` 新增公開
   `async def refresh_access_token(self, token: AccessToken) -> AccessToken` 與
   `AuthClientRefreshTokenError`，不新增 package-root export。
2. `token.refresh_token is None` 時，方法接受 fetch-only collaborator，await
   `fetch_access_token()` 一次並回傳相同結果。
3. `token.refresh_token is not None` 時，方法只接受完整
   `TokenEndpointClientProtocol` collaborator 並 await `refresh_access_token(token)` 一次；
   不得 fetch fallback。
4. present-token + fetch-only collaborator raises `AuthClientRefreshTokenError`；完整
   collaborator 的 cancellation 原樣傳播；其他 `Exception` 必須 chain 至
   `AuthClientRefreshTokenError`。
5. `README.md` 的 English 與繁體中文 `AuthClient` public-surface 段落記錄 refresh API、
   absent-token fetch、present-token full-protocol requirement、error 與 import boundary；
   不宣稱 package-root export、version 或 release 變更。
6. `AuthClient.__init__`、`get_access_token()`、core、dependencies、root export、version 和
   release surface 均不改變。

## Behavioral Scenarios

### Scenario 1: Absent refresh token retains fetch behavior

- **Given**: 一個 `AccessToken` 的 `refresh_token` 是 `None`，且 AuthClient 收到
  fetch-only collaborator。
- **When**: caller awaits `refresh_access_token(token)`。
- **Then**: collaborator 的 fetch 被 await 一次，回傳 token identity 不變，且不要求
  refresh capability。

### Scenario 2: Present refresh token uses full collaborator

- **Given**: 一個有 refresh token 的 `AccessToken` 與 full token-endpoint collaborator。
- **When**: caller awaits `refresh_access_token(token)`。
- **Then**: collaborator refresh 被 await 一次並收到同一個 token；fetch call count 為零。

### Scenario 3: Fetch-only collaborator cannot refresh present token

- **Given**: 一個有 refresh token 的 `AccessToken` 與 fetch-only collaborator。
- **When**: caller awaits `refresh_access_token(token)`。
- **Then**: 立即 raise `AuthClientRefreshTokenError`，且不呼叫 fetch fallback。

### Scenario 4: Failure and cancellation boundary

- **Given**: full collaborator 在 refresh 時分別 raise `asyncio.CancelledError` 或一般
  `Exception`。
- **When**: caller awaits method。
- **Then**: cancellation 是原 instance；一般 error 被 `AuthClientRefreshTokenError` 包裝且
  original error 是 `__cause__`。

### Scenario 5: Existing API remains compatible

- **Given**: fetch-only collaborator 與既有 AuthClient caller。
- **When**: caller 建構 client 並 await `get_access_token()`。
- **Then**: constructor 仍接受 collaborator，get method 仍只 fetch 一次並回傳結果。

### Scenario 6: Public documentation matches the refresh contract

- **Given**: topic implementation includes the new public refresh API.
- **When**: independent Implementer updates `README.md`.
- **Then**: the English and Traditional Chinese `AuthClient` public-surface paragraphs describe
  the locked refresh behavior and retain direct module import/no package-root export boundaries;
  VERSION and release metadata remain unchanged.

## Error / Edge Cases

- `refresh_token is None` 是正常 fallback input，不可拋出 `AuthClientRefreshTokenError`。
- present token 與不具 full protocol 的 collaborator 是明確能力錯誤，不可降級為 fetch。
- `asyncio.CancelledError` 不可被 error translation 捕捉或鏈結。
- 僅一般 `Exception` 在 full-refresh await 時轉譯；不得為此新增 retry、timeout 或 cleanup。
