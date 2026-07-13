# PasswordTokenEndpointClient Technical Specification

## Execution Source of Truth

本文件將 human 已鎖定的 architecture 轉為 execution contract。它與 `requirements.md` 一起形成 strict analysis layer；若後續需求與本文件衝突，須回到 Plan-Creator/human，不由 Implementer 重新設計。

## Architecture

```text
src/mlops_async/core/
  auth.py
  token_endpoint/
    __init__.py
    _shared.py
    client_credentials.py
    password.py
  token_endpoint_client.py
```

- `auth.py` 維持 `TokenEndpointClientProtocol`、`TokenManager`、`AuthProvider` 與 lifecycle/orchestration；不承載 OAuth grant request 實作。
- `_shared.py` 定義 `AuthTokenEndpoint`、`TokenEndpointClientError`、`TokenEndpointClientException`、non-empty credential validation、token parser 與 expiry conversion 的 shared pure logic。
- `client_credentials.py` 遷移既有 `TokenEndpointClient`，保留 body：`grant_type=client_credentials`、`client_id`、`client_secret`。
- `password.py` 定義 `PasswordTokenEndpointClient`，以 Basic client credentials 和 password form obtain token；refresh 重新 obtain。
- `token_endpoint_client.py` 僅 compatibility re-export，保留 `AuthTokenEndpoint`、`TokenEndpointClient`、`TokenEndpointClientError`、`TokenEndpointClientException` 的 internal import contract。
- 不建立 `core/auth/`，避免與 `core/auth.py` 同名造成 import ambiguity。

## Request and Error Contract

- Password constructor 顯式接收 injected `Client`、username、password、client ID、client secret 與 optional endpoint。
- obtain 時 direct await `Client.request_json()`，method 為 `HttpMethod.POST`，path 為 `AuthTokenEndpoint.OAUTH_TOKEN.value`。
- headers 使用 `token_request_headers()` 加 Basic authorization；form 用 `urlencode()` 形成 UTF-8 bytes，且只含三個 password-grant fields。
- response 必須為 object、有非空 `access_token`、且 `expires_in` 為非 bool 的正整數；expiry 為現行 UTC time 加上 `expires_in`。
- constructor/schema failure 使用 shared `TokenEndpointClientError`；transport、JSON 與 `CancelledError` 依現有 `TokenManager` boundary 傳遞／轉譯。

## Async Baseline

- async boundary 僅在兩個 concrete clients 的 fetch/refresh；shared logic 保持同步 pure logic。
- injected `Client` 的 create/share/close 維持外層 composition owner；clients 不呼叫 `aclose()` 或 context-manage transport。
- 每次 request 是單一 direct await；不新增 task、lock、retry、timeout、fan-out 或 queue。
- cancellation 直接傳遞；不新增 cleanup 或 timeout policy。

## Validation Contract

- fake transport record 僅保存 method、path、header names/auth scheme、form field names 與 boolean structural checks，不保存 raw sensitive values。
- 覆蓋 client-credentials regression、compatibility imports、password request shape、invalid input、schema failure、refresh-as-reobtain、Protocol/TokenManager expiry integration。
- 通過 scoped pytest、ruff、strict pyright 與 full pytest；commands 固定於 topic plan。
