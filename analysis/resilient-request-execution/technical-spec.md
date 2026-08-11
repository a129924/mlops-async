# Resilient Request Execution Technical Specification

## Goal

在 authenticated `Requester` 邊界實作私有、可驗證且有界的 request resilience：符合資格的 `GET`/`HEAD` 可處理指定暫時失敗、初始 401 的一次條件式 refresh，以及一次 replay；公開 API 與既有例外契約維持不變。

## Non-Goal

- 不變更任何公開 constructor、export、client family API、facade 或 DI。
- 不將 resilience 套用到非 `GET`/`HEAD`、raw token endpoint route、背景工作或 live E2E。
- 不在本 topic 加入 release metadata、版本變更或發布行為。

## In-Scope

### Internal failure model

- 新增未 export 的 `src/mlops_async/core/request_failure.py`。
- 定義 immutable `ResponseFailureMetadata(status_code, retry_after)`。
- 定義 `RequestFailure(kind, connection|timeout|response)`；其 `kind` 僅表達 `connection`、`timeout` 或 `response`。
- core 不得 import transport 或 `httpx`；failure carrier 必須能由 core 消費而不反向耦合 transport。

### Transport to core classification boundary

- `Client` 新增內部 `failure_for(exception) -> RequestFailure | None`，只作已知 transport failure 到 core carrier 的分類；未知例外仍遵循既有傳播契約。
- `HttpClient` 保持 single-send 語意。它不得自行重試、refresh 或 replay。
- `HttpClient` 對既有例外保留同一 exception identity、message、context 與 properties，並加上 failure metadata 供 `Client.failure_for` 使用。

### Requester resilience state machine

- 在 `Requester` 加入私有 `_RequesterResilienceDecorator`，只包住既有的 primitive/canonical request 執行點。
- method eligibility 必須使用 Python `match`/`case`，且精確採用：

  ```python
  match method:
      case HttpMethod.GET | HttpMethod.HEAD:
          ...
      case _:
          ...
  ```

  不得使用 membership check 或 string comparison。
- eligible temporary failure 僅為 connection、timeout 與 HTTP `429`、`502`、`503`、`504`。
- 初始 attempt 與 replay 各自最多 3 次 send（含第一次 send）。
- sleep 使用 base `0.25`、exponential backoff、cap `2` 的 jitter。`Retry-After` 支援 delta-seconds 與 HTTP-date；結果 clamp 為 `0..30`，invalid value 回退至一般 jitter/backoff。
- 每一次 send 都沿用 per-send timeout；重試不得把多次 send 合併為一個較大的總 timeout。

### 401 refresh and replay

- `401` 最終失敗保持 generic，不創造新的公開例外。
- 只有 initial request 可作一次 `TokenManager.refresh_if_current`；replay 或其 retry 後的 401 絕不再 refresh。
- 若 storage token 已被其他協作者改變，跳過本次 refresh 並以 current token replay。
- 若 storage 已清除，禁止 fetch/refresh；保留既有失敗路徑。
- refresh failure 或 `asyncio.CancelledError` 必須保持 storage 狀態；cancel 不可轉譯或吞掉。
- replay 僅一次、有自己的三-send budget，且無第二次 refresh。
- raw `TokenEndpointClient.request_json` 明確 bypass 此 decorator。

## Out-Of-Scope

- 非 `GET`/`HEAD` retry/replay，包括 `POST`。
- token endpoint retry、公開 API/facade/DI、背景工作、live E2E、release 工作與穩定函式庫 metadata。

## ReadOnly

- 公開 family constructors、exports、raw `TokenEndpointClient.request_json` route。
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/*`。

## Written

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

## TestCase

- `test_request_failure.py`: immutable carrier、`kind`、response metadata 與 core 不反向 import transport/httpx 的 boundary。
- `test_request_resilience.py`: `GET`、`HEAD`、`POST` match/case branches；eligible classification；每一 initial/replay 3-send budget；jitter base/exponential/cap；`Retry-After` delta/date/clamp/invalid fallback；per-send timeout。
- `test_requester_auth_boundary.py` 與 `test_token_manager.py`: concurrent 401 的 existing-lock refresh、changed token skip/current replay、cleared storage no fetch、一次 replay、無第二次 refresh、refresh failure 與 cancellation storage preservation、raw token bypass。
- transport tests: metadata attachment，以及原 exception identity/message/context/properties preservation。

## Evidence and Risk Boundary

本 spec 為明確的人類核准聊天 contract 的執行面轉錄；它不是 live Viya evidence，也不把 request-contract shape 當作 runtime 行為證明。除非另有 endpoint runtime proof 與人類核准，禁止對 `POST` 或其他非 `GET`/`HEAD` 新增 retry/replay。
