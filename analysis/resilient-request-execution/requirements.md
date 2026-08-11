# Resilient Request Execution Requirements

## Goal

在不改變公開 API 或既有例外契約的前提下，於 `Requester` 邊界為已驗證的 `GET`/`HEAD` 提供有界的暫時失敗重試、一次條件式 401 token refresh，以及至多一次 replay。

## Non-Goal

- 不將重試或 replay 擴展到 `GET`/`HEAD` 以外的方法。
- 不對 token endpoint 原始請求加入 resilience 行為。
- 不增加公開 client、facade、DI surface、背景工作、live E2E 或 release 工作。

## In-Scope

- 以 core 內部 failure carrier 傳遞連線、timeout 與 response failure 的必要 metadata。
- 在 `Requester` 的私有 decorator state machine 處理符合資格的單一 canonical request primitive。
- 在同一既有 token 的條件下，透過 `TokenManager.refresh_if_current` 協調並行的 401 refresh。
- 保存 transport 例外物件 identity、message、context 與 properties，並附加 failure metadata。
- 更新受影響的架構與 auth-boundary 文件，並加入單元測試。

## Out-Of-Scope

- `POST`、`PUT`、`PATCH`、`DELETE` 或其他非 `GET`/`HEAD` 的 retry/replay。
- token endpoint retry、token endpoint refresh 或 raw `TokenEndpointClient.request_json` 的 decorator 路徑。
- 公開 API、facade、建構子、依賴注入、background task、live Viya E2E、README、VERSION、`pyproject.toml`、`uv.lock`、release note、commit、push 或 PR。

## ReadOnly

- 公開 family constructors、exports 與所有公開 API。
- raw token route（`TokenEndpointClient.request_json`）。
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/*`。
- live Viya E2E 與 release surfaces。

## Written

- `analysis/resilient-request-execution/requirements.md`
- `analysis/resilient-request-execution/technical-spec.md`
- `plan/resilient-request-execution/resilient-request-execution.plan.md`
- `plan/resilient-request-execution/resilient-request-execution.step.md`
- `src/mlops_async/core/request_failure.py`
- `tests/unit/core/test_request_failure.py`
- `tests/unit/core/test_request_resilience.py`

## Modify

- `src/mlops_async/core/client.py`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/transport/exceptions.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_client_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/transport/test_http_client.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`

## Deleted

- None.

## Evidence and Risk Boundary

此 requirements baseline 是依據明確的人類核准聊天 contract 撰寫，不是由 live Viya runtime、request-shape gate 或 OpenAPI 行為推論。未取得 endpoint runtime proof 前，禁止將 `POST` 或其他非 `GET`/`HEAD` 方法納入 retry 或 replay；任何擴張必須是另一個明確核准 topic。
