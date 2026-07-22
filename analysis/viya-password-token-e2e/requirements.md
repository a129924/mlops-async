# Viya Password Token E2E Requirements

## Goal

以真實 SAS Viya 的 password grant 驗證 `PasswordTokenEndpointClient` 可取得有效 token response。

## In-Scope

- 僅 `POST /SASLogon/oauth/token` 的 password grant。
- HTTP `200`、非空 `access_token`、正整數 `expires_in` 驗證。
- `config/.env.test` 的安全 test-only 設定載入與 `viya_e2e` opt-in gate。
- framework 使用者必須以 `VIYA_E2E_TLS_MODE` 明確選擇 `system`、`insecure` 或
  `ca_bundle`；E2E 將選擇結果傳給 `HttpClient`，不做 fallback 或 mode switch。

## Out-of-Scope

- Protected proof endpoint、public `AuthClient`、production runtime 或 client-credentials 行為。
- CI、release metadata、retry、refresh-token flow。

## Acceptance Requirements

1. E2E 僅在 process environment 的 `RUN_VIYA_E2E=1` 時可連線；config 檔中的同名 key 必須忽略。
2. `config/.env.test` 必須提供 base URL、username、password、client ID、client secret
   與非空白 TLS mode；僅 `sas.ec` 可使用明確空 secret。
3. TLS mode contract：
   - `system` 傳入 `verify=True`；
   - `insecure` 傳入 `verify=False`，並固定警告 TLS verification 已明確停用；
   - `ca_bundle` 要求非空白 `VIYA_E2E_CA_BUNDLE`，建立 caller-provided
     `ssl.SSLContext`；CA bundle 不得出現在其他 mode。
4. 公司內部環境使用 `insecure` 是 framework 使用者的明確設定，不是 mock、
   fallback、mode switch 或 skip-as-success；30 秒 total timeout 維持不變。
5. 任一 config、TLS、DNS、timeout、非 200、非 JSON 或 token schema failure 都必須
   fail，且不輸出 URL、credential、token、Basic header、response body 或 config 內容。

## Evidence Interpretation

- HTTPS request 成功只證明真實 HTTPS endpoint 回應且 token success contract 成立。
- `insecure` success 必須描述為
  `live password-token E2E passed with TLS verification explicitly disabled`。
- `TLS trust verified` 只可由啟用 certificate verification 的成功 run 支持；本次
  post-merge live evidence 使用 `insecure`，不得作此宣稱。

## Current Validation Evidence

- Post-merge non-E2E：pytest `311 passed, 9 skipped, 1 deselected`、Ruff passed、
  Pyright `0 errors, 0 warnings`。
- Post-merge live E2E：`1 passed, 320 deselected`；真實 network request、HTTP `200`、
  nonempty token、positive expiry；TLS verification 明確停用。
- E2E branch 尚未 merge 到 `dev`；merge-to-dev 維持 pending human boundary。
