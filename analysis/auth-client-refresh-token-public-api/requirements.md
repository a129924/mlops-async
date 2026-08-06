# AuthClient refresh-token public API 需求基線

## Goal

在不改變既有 `AuthClient` 建構子或 `get_access_token()` 行為的前提下，提供可由
`mlops_async.clients.auth_client` 直接匯入的公開非同步
`refresh_access_token(token: AccessToken) -> AccessToken`。

## Non-Goal

- 不改變 `TokenManager`、token endpoint 實作或 grant 選擇策略。
- 不改變 `mlops_async.core`、相依套件、package root export、版本或 release。
- 不新增快取、生命週期、重試、timeout、背景工作或 live E2E。
- 不變更既有 `AuthClient.__init__()` 與 `get_access_token()` 的公開契約。

## Requirements

1. `AuthClient.refresh_access_token(token)` 必須是 async 方法，接收並回傳
   `AccessToken`。
2. 當輸入 token 沒有 `refresh_token` 時，方法必須呼叫既有 collaborator 的
   `fetch_access_token()`，並回傳其結果。
3. 當輸入 token 有 `refresh_token` 且 collaborator 支援完整
   `TokenEndpointClientProtocol` 時，方法必須呼叫其 `refresh_access_token(token)`；
   不得改走 fetch fallback。
4. 當輸入 token 有 `refresh_token` 但 collaborator 僅支援 fetch protocol 時，方法
   必須拋出新的 `AuthClientRefreshTokenError`。
5. `asyncio.CancelledError` 必須原樣向外傳播；完整 collaborator 在 refresh 時拋出的
   其他 `Exception` 必須以 `AuthClientRefreshTokenError` 轉譯並保留 exception chaining。
6. 新例外僅是 `mlops_async.clients.auth_client` 的 public surface；不得新增 package-root
   export。
7. `README.md` 的 English 與繁體中文 `AuthClient` public-surface 段落必須更新，說明
   `refresh_access_token()` 的能力邊界、無 refresh token 時的 fetch 行為、完整 collaborator
   要求與 `AuthClientRefreshTokenError`；既有 direct import 與無 package-root export 的說明
   必須保留正確。

## Business Constraints

- 無 refresh token 是已支援的正常狀態，不可視為 API 錯誤。
- 有 refresh token 卻缺少 refresh 能力時，錯誤必須明確，不能悄悄執行較弱的 fetch
  行為。
- 驗證僅涵蓋 unit/static checks；外部憑證與 live token endpoint 均不在本 topic。

## Acceptance Signals

- 單元測試可分別證明 absent-token fallback、full collaborator refresh、fetch-only
  error、取消不轉譯與一般例外 chaining。
- 原有 constructor/get-access-token 測試仍通過，證明向後相容。
- README 的兩個 `AuthClient` public-surface 段落與已凍結的 API、fallback、error 與
  package-root 邊界一致。
