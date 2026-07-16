# Viya Password Token E2E Technical Specification

## Execution Source of Truth

本 topic 以 `PasswordTokenEndpointClient` 的既有 password-grant contract 為 runtime baseline；不修改 production auth code。

## Design

- `tests/conftest.py` 動態註冊 `viya_e2e`，並以 process-level `RUN_VIYA_E2E=1` 保護真實網路。
- `tests/integration/viya_e2e_config.py` 只讀 worktree 的 `config/.env.test`，使用無 dependency 的 `KEY=value` parser；loader 忽略 `RUN_VIYA_E2E`。
- `tests/integration/test_viya_password_token_e2e.py` 直接將真實 `HttpClient` 傳給 password client，並以真實 httpx response event hook 只保留 status code；它不 mock 或替換 transport。
- `HttpClient` 使用 `verify=True` 與 `RequestTimeouts(total=30)`；token response 只接受 exact status `200`。

## Security Contract

- config file 必須先通過 `git check-ignore`；不自動複製、建立或輸出。
- base URL 必須為非 loopback HTTPS origin。
- username、password、secret、Authorization header、access token 與 response body 不得出現在 failure evidence。
- `asyncio.CancelledError` 直接傳遞；其他 transport/status/JSON/schema failures 轉成已遮罩 pytest failure。
