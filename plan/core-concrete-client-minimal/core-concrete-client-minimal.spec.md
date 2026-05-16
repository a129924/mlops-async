# Core Concrete Client Minimal Specification

## Acceptance Criteria

1. `src/mlops_async/transport/http_client.py` 是唯一允許的 concrete HttpClient module path；若 `src/mlops_async/core/http_client.py` 存在，implementation 完成時必須刪除，且不得留下 alias、transition layer、或 duplicate residual code。
2. 本 topic 不新增 `src/mlops_async/__init__.py` re-export，也不新增 public facade；concrete client 仍是 internal-only substrate。
3. concrete client constructor surface 鎖定為：必要 `base_url`（接受字串或 URL 物件）、constructor-level `RequestTimeouts`、`verify`、optional low-level transport injection、optional `default_headers`；不得接受完整 `httpx.AsyncClient` injection，也不得加入 client-level default params 或 client-level default options。
4. concrete client 若自行建立 `httpx.AsyncClient`，必須在 `aclose()` / async context manager 結束時關閉其生命週期；若使用 injected low-level transport，生命週期由 caller 擁有，client 不得主動關閉它。
5. `request()` 只在 HTTP 2xx 時回傳 `RawClientResponse`，且成功結果必須保留 `status_code`、`headers`、`content`、`method`、`url`；non-2xx response 不得被當成成功 raw 值回傳。
6. `request_json()` 只在 HTTP 2xx 且 body 可解析為 JSON 時回傳 `JSONValue`；它不得繞過或放寬 `request()` 的 success-only boundary。
7. `src/mlops_async/exceptions.py` 在 implementation 完成後只保留 `MlopsAsyncBaseException`；`src/mlops_async/transport/exceptions.py` 必須定義 `HttpErrorContext`、`HttpTransportException`、`HTTPStatusException`、`InvalidJSONResponseException`。
8. exception hierarchy 必須為 `MlopsAsyncBaseException` -> `HttpTransportException` -> `HTTPStatusException` / `InvalidJSONResponseException`；`HTTPStatusException` 與 `InvalidJSONResponseException` 不得直接繼承 `MlopsAsyncBaseException`。
9. transport failure（例如 timeout、network、TLS verify、底層 request 建立失敗）必須映射為 `HttpTransportException`；2xx 但 non-JSON success body 必須映射為 `InvalidJSONResponseException`。
10. default header policy 僅允許最小 content negotiation：預設 `Accept: application/json`、僅在 request 有 JSON body 時補 `Content-Type: application/json`、per-request 同名 header 覆蓋 constructor-level default header、不得偷偷加入 auth/state/observability semantics。
11. auth / retry 不得被納入本 topic；`request()` / `request_json()` failure boundary 不得被重新設計。
12. 測試契約至少涵蓋：sole transport path、constructor surface、owned vs injected transport lifecycle、header merge、禁止 client-level params / options merge、`request()` 成功與失敗邊界、`request_json()` 成功與失敗邊界、concrete client 對 `Client` Protocol 的符合性、以及無 root re-export / alias 的 exception placement。

## Behavioral Scenarios

### Scenario 1: Owned client 以 JSON request 成功回傳解析結果
- **Given**: 一個以 `base_url` 建立、由 client 自行擁有底層 `httpx.AsyncClient` 的 concrete HttpClient，且 implementation 只存在於 `src/mlops_async/transport/http_client.py`
- **When**: 呼叫 `request_json()` 並收到 HTTP 2xx 且 body 為合法 JSON
- **Then**: 呼叫結果回傳 `JSONValue`，request 帶有 `Accept: application/json` 與必要時的 `Content-Type: application/json`，且不需要任何 package-root re-export 或 public facade

### Scenario 2: Per-request header 覆蓋 constructor-level default header
- **Given**: concrete client constructor 設有 minimal `default_headers`，且某次 request 額外提供同名 header
- **When**: 呼叫 `request()` 或 `request_json()`
- **Then**: per-request 同名 header 取代 constructor-level 預設值，其餘 default headers 仍依薄層 content negotiation 規則保留

### Scenario 3: Raw path 在 non-2xx 時直接失敗
- **Given**: concrete client 送出 request 並收到 non-2xx response
- **When**: 呼叫 `request()`
- **Then**: 呼叫以 `HTTPStatusException` 結束，且不回傳 `RawClientResponse`

### Scenario 4: JSON path 在 success body 非 JSON 時拒絕假成功
- **Given**: concrete client 送出 request 並收到 HTTP 2xx，但 body 為空或不是合法 JSON
- **When**: 呼叫 `request_json()`
- **Then**: 呼叫以 `InvalidJSONResponseException` 結束，而不是把 body 當成文字、位元組、`None`，或其他假成功結果回傳

### Scenario 5: Root/base 與 transport-local exceptions 嚴格分家
- **Given**: implementation 已完成 exception placement 對齊
- **When**: 檢查 `src/mlops_async/exceptions.py`、`src/mlops_async/transport/exceptions.py` 與舊的 `src/mlops_async/core/http_client.py` 路徑
- **Then**: root `exceptions.py` 只保留 `MlopsAsyncBaseException`，transport-local file 承接全部 transport concrete exceptions，且 old path 不存在也不以 alias 形式殘留

## Error / Edge Cases

- timeout、DNS/connection failure、TLS verify failure、或其他底層 transport/request 失敗，都必須轉為 `HttpTransportException`，不得回傳半套 raw 結果。
- HTTP 2xx 但空 body 的情境不可被 `request_json()` 視為 JSON success；若需要此類 raw success，只能走 `request()` 路徑。
- request 未提供 JSON body 時，不得自動加入 `Content-Type: application/json`。
- 任何保留 `src/mlops_async/core/http_client.py`、root re-export、或 alias / transition layer 的 implementation 都屬 contract failure，而非可接受的相容策略。
- `HTTPStatusException` 與 `InvalidJSONResponseException` 若直接繼承 `MlopsAsyncBaseException`，屬 hierarchy drift，必須視為失敗。
- 本 topic 不允許 client-level default params，也不允許 constructor-level `ClientRequestOptions`；相關能力若被需求拉入，屬於 plan/spec 衝突而非可在 implementation 內自行擴張。
- auth、retry、public facade、或 deeper exception package 若被一併加入，屬於超出 topic 範圍。
