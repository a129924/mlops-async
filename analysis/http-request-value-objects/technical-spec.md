# HTTP Request Value Objects Technical Specification

## Status and Authority

- **Topic**: `http-request-value-objects`
 - **Status**: `review-ready`; the rework planning constraints are complete and
  only the six HUMAN-selected PR #57 review threads below are execution
  constraints.
- 本檔是 execution-facing source of truth；`requirements.md` 是 business-intent guardrail。

## Technical Design

### Module ownership

- `src/mlops_async/core/types.py` 保留 `HttpMethod`、`JSONValue` 與 response-side types。
- `src/mlops_async/core/http_request.py` 擁有 `BaseUrl`、`EndpointPath`、`QueryParams`、
  `Headers`、`JsonBody`、`RawBody`、`HttpRequest` 及 JSON primitive adapter。
- `src/mlops_async/core/headers.py` 保留 merge precedence ownership；最終 request output
  canonicalize 為 lowercase。
- `src/mlops_async/core/requester.py` 是 immutable JSON-domain composition boundary。
- `src/mlops_async/transport/http_client.py` 是 canonical request execution-only boundary。

### Canonical request model

- value objects 為 frozen/slotted 或等效 immutable implementation，snapshot mutable input，
  不 import `httpx` 或進行 I/O。
- `BaseUrl` 只保存 origin；path-prefix、user-info、query、fragment 一律 `ValueError`。
- `EndpointPath.literal(path)` 保存 validated static path；`from_segments(*segments)` 對 raw
  dynamic values逐段 encode 一次，拒絕含預編碼 `%HH` 的 dynamic ID。
- `QueryParams` 保存 ordered pairs，允許 duplicate keys；空 key `ValueError`，empty string
  value 為 `key=`，None omit，bool 為 `true`/`false`，UTF-8 percent encode，space `%20`，
  不用 `+`、不 sort、不 double-encode。
- `Headers` 將 validated names canonicalize 為 lowercase；lookup case-insensitive，case-
  insensitive collision last wins，canonical storage/output 不含 duplicate name。merge
  precedence 不變，final merge output 的 names 必須 lowercase。
- `JsonBody` validation/snapshot only，沒有 serialization side effect。`RawBody` 只保存
  immutable `bytes`，不自動注入 `Content-Type`。
- `HttpRequest` 唯一 body construction field 是 `body: JsonBody | RawBody | None`。
  readonly `json_body`／`content` compatibility properties 只映射 body variant；它們不是
  constructor fields，且不存在 XOR/priority/default/override semantics。`url` 是唯一 final URL。

### Composition and execution

- `Requester` 對 `HttpRequest` 做 immutable JSON-domain auth/default/caller header
  composition，產生新 request；不得 mutate input，亦不得接管 token/form。
- `HttpClient.execute(HttpRequest, ...)` 只執行 canonical `HttpRequest.url` 與 body；不再
  base/path/query join，也不得讓 HTTP library 的 default/override 形成第二語意。
- primitive `request(...)`／`request_json(...)` 僅為 JSON-domain compatibility adapter，必須
  經同一 canonical construction delegate。其 cleanup 屬後續 topic。
- `<EndpointFamily>Endpoints` 僅是 future family 的 return-type contract，不新增 concrete
  catalog 或 port。

### Token/form boundary

- TokenEndpointClient、password token、token/form 保持既有 raw-content primitive path。
- 它們不得經 JSON-domain Requester 或本批 primitive adapter migration。
- token/form value-object migration 必須另立 topic。

## Selected review rework execution constraints

Only the following six HUMAN-selected PR #57 threads are in scope for this
rework. They refine the existing JSON-domain request contract and do not reopen
the locked architecture decisions.

1. `PRRT_kwDOSTt_386VAaWm` — `JsonBody(None)` remains a value-object snapshot
   of JSON `null`; it does not serialize itself. At the transport boundary,
   `HttpRequest.body` variant discrimination must pass the JSON value so the
   wire content is exactly `b"null"`, rather than treating the variant as no
   body.
2. `PRRT_kwDOSTt_386VAaWr` — public direct construction and named construction
   of `BaseUrl`, `EndpointPath`, `QueryParams`, and `Headers` must enforce the
   same validation and canonicalization. A caller must not bypass an invariant
   through a generated dataclass initializer or raw internal storage fields.
3. `PRRT_kwDOSTt_386VAaWs` — `EndpointPath.literal()` accepts only a canonical
   static absolute path. It must reject non-canonical whitespace, non-ASCII,
   and control-character input instead of delegating encoding or normalization
   to the HTTP library; already percent-encoded static literals remain the
   caller's canonical representation.
4. `PRRT_kwDOSTt_386VAaWw` — `BaseUrl` validates its authority/hostname at the
   construction boundary and raises `ValueError` for parser-permitted invalid
   host characters, including spaces, backslashes, and percent-encoded NUL.
5. `PRRT_kwDOSTt_386VAaWx` — canonical direct `HttpClient.execute()` requests
   must not acquire an implicit `accept: */*` from httpx. Hidden `Accept` is
   removed when absent from the canonical `Headers`; an explicit canonical
   `accept` is preserved.
6. `PRRT_kwDOSTt_386VAaW2` — the JSON-domain primitive compatibility adapter
   preserves an already embedded query in `path` for both `request()` and
   `request_json()`: it separates the path from query pairs before constructing
   `EndpointPath` and `QueryParams`, then delegates to the same canonical
   execution path. This is compatibility preservation, not primitive-surface
   cleanup.

## Compatibility and Error Strategy

- readonly `json_body`／`content` properties 只提供讀取相容，不提供 legacy construction。
- value-object invalid input 在 construction 時以 `ValueError` 拒絕；不新增 transport errors。
- 不變更現有 transport/error/auth/timeout semantics。

## Validation Baseline

- `uv run pytest tests/unit/core/test_http_request.py tests/unit/core/test_client_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_request_headers.py tests/unit/core/test_token_endpoint_client.py tests/unit/core/test_password_token_endpoint_client.py tests/unit/transport/test_http_client.py tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`
- 上述兩個 JSON-domain GET request-contract tests 必須斷言 `body is None` 時不存在
  `Content-Type`，並以 canonical lowercase `authorization`／`accept` lookup 驗證 headers。
- `uv run ruff check src tests`
- `uv run pyright`
- `uv run pytest --cov=src/mlops_async --cov-report=term-missing`
