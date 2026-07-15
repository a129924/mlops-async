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
- `_shared.py` 定義 `AuthTokenEndpoint`、`TokenEndpointClientError`、`TokenEndpointClientException`、credential validation（支援 PasswordTokenEndpointClient 的精確 `sas.ec` 空 secret 例外，但不放寬 client-credentials flow）、token parser 與 expiry conversion 的 shared pure logic。
- `client_credentials.py` 遷移既有 `TokenEndpointClient`，保留 body：`grant_type=client_credentials`、`client_id`、`client_secret`。
- `password.py` 定義 `PasswordTokenEndpointClient`，以 Basic client credentials 和 password form obtain token；refresh 重新 obtain。
- `token_endpoint_client.py` 僅 compatibility re-export，保留 `AuthTokenEndpoint`、`TokenEndpointClient`、`TokenEndpointClientError`、`TokenEndpointClientException` 的 internal import contract。
- 不建立 `core/auth/`，避免與 `core/auth.py` 同名造成 import ambiguity。

## Request and Error Contract

- Password constructor 顯式接收 injected `Client`、username、password、client ID、client secret 與 optional endpoint；username、password、client ID 一律拒絕空白或僅含空白字元的值。
- obtain 時 direct await `Client.request_json()`，method 為 `HttpMethod.POST`，path 為 `AuthTokenEndpoint.OAUTH_TOKEN.value`。
- PasswordTokenEndpointClient 的 client secret 預設拒絕空白或僅含空白字元的值；唯一例外是精確 `client_id == "sas.ec"` 時允許 `client_secret == ""`，但不允許僅含空白字元的 secret。任何其他 client ID 搭配空或空白 secret 必須以 `TokenEndpointClientError` 失敗且不得回顯值。`client_credentials.py` 對所有 client ID（含 `sas.ec`）維持既有 non-empty secret contract。
- headers 使用 `token_request_headers()` 加 Basic authorization；Basic 的編碼前組合固定為 `client_id:client_secret`，因此唯一例外的組合為 `sas.ec:`。form 用 `urlencode()` 形成 UTF-8 bytes，且只含三個 password-grant fields。
- response 必須為 object、有非空 `access_token`、且 `expires_in` 為非 bool 的正整數；expiry 為現行 UTC time 加上 `expires_in`。
- constructor/schema failure 使用 shared `TokenEndpointClientError`；transport、JSON 與 `CancelledError` 依現有 `TokenManager` boundary 傳遞／轉譯。

## Async Baseline

- async boundary 僅在兩個 concrete clients 的 fetch/refresh；shared logic 保持同步 pure logic。
- injected `Client` 的 create/share/close 維持外層 composition owner；clients 不呼叫 `aclose()` 或 context-manage transport。
- 每次 request 是單一 direct await；不新增 task、lock、retry、timeout、fan-out 或 queue。
- cancellation 直接傳遞；不新增 cleanup 或 timeout policy。

## Validation Contract

- fake transport record 僅保存 method、path、header names/auth scheme、form field names 與 boolean structural checks，不保存 raw sensitive values。
- 覆蓋 client-credentials regression（含 `sas.ec` 空 secret 仍拒絕）、compatibility imports、password request shape、`sas.ec` 空 secret Basic 行為、非 `sas.ec` 空 secret rejection、invalid input、schema failure、refresh-as-reobtain、Protocol/TokenManager expiry integration。
- 通過 scoped pytest、ruff、strict pyright 與 full pytest；commands 固定於 topic plan。

## P1 Corrective-Test Rework Workflow

P1 scope guards：`plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` 是 immutable historical evidence 且為 ReadOnly；禁止 rewrite 或 rerun `python-tdd-test-authoring`。`src/mlops_async/core/token_endpoint/client_credentials.py` 在 P1 亦是 ReadOnly 與 diff-free，維持 `require_non_empty_string()`；僅 `tests/unit/core/test_token_endpoint_client.py` 可新增 strict regression。`sas.ec` exception helper 僅屬 password，僅能由 `src/mlops_async/core/token_endpoint/password.py` 使用；P1 production diff 僅限 `_shared.py` 與 `password.py`。

此 exception 是 production implementation 完成後的 P1 rework，而非新 feature 的 initial TDD stage。`plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` 僅保留為舊 strict-non-empty contract 的 historical evidence；不得更新該 artifact、重跑 `python-tdd-test-authoring` 或要求新的 RED verdict。

在重新開啟的 Plan Review 核准後，Implementer 先於 `tests/unit/core/test_password_token_endpoint_client.py` 新增 `sas.ec` empty-secret acceptance 與 non-`sas.ec`/whitespace-secret rejection tests，並於 `tests/unit/core/test_token_endpoint_client.py` 新增 `sas.ec` empty-secret strict regression test。先執行這三個 corrective cases，再修改 `_shared.py` 與 `password.py`；完成後執行 topic plan 的 scoped/full validation，接續 Implementation Review 與 Code Review。
