# Viya Password Token E2E Requirements

## Goal

以真實 SAS Viya 的 password grant 驗證 `PasswordTokenEndpointClient` 可取得有效 token response。

## In-Scope

- 僅 `POST /SASLogon/oauth/token` 的 password grant。
- HTTP `200`、非空 `access_token`、正整數 `expires_in` 驗證。
- `config/.env.test` 的安全 test-only 設定載入與 `viya_e2e` opt-in gate。

## Out-of-Scope

- Protected proof endpoint、public `AuthClient`、production runtime 或 client-credentials 行為。
- CI、release metadata、retry、refresh-token flow。

## Acceptance Requirements

1. E2E 僅在 process environment 的 `RUN_VIYA_E2E=1` 時可連線；config 檔中的同名 key 必須忽略。
2. `config/.env.test` 必須提供 base URL、username、password、client ID、client secret；僅 `sas.ec` 可使用明確空 secret。
3. 測試必須使用 TLS verify 與 30 秒 total timeout，禁止 mock、fake transport、fallback token 與 `verify=False`。
4. 任一 TLS、DNS、timeout、非 200、非 JSON 或 token schema failure 都必須 fail，且不輸出 credential、token、Basic header 或 response body。
