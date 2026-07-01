# request-gate-casmanagement-list-tables technical specification

## Status

- `FROZEN`

## Source Baseline Summary

- 本 technical spec 以
  `analysis/request-gate-casmanagement-list-tables/requirements.md`
  為 execution-facing baseline。
- 本 topic 為 `tests-only / shape-only` request gate。
- 實作邊界固定在
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/**`，不得修改
  `src/**`。

## Request Contract

### Canonical positive case

- case id: `limit_1000_start_0`
- method: `GET`
- path:
  `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables`
- query:
  - `limit=1000`
  - `start=0`
- required headers:
  - `Authorization: Bearer <token>`
  - `Accept: application/json`
- body: `null`

### Required inputs

- `caslib`
  - required
  - non-empty string
- `limit`
  - only `1000`
- `start`
  - only `0`
- extra query params
  - blocked in this topic
- request body
  - blocked in this topic
- endpoint family
  - only `list_tables`

## Fixture Layout

### Request-flow fixture

- path:
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
- exactly one case:
  - `limit_1000_start_0`
- exactly one observed step:
  - purpose: `target-api`
  - request:
    - method `GET`
    - path `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables`
    - query `{"limit": "1000", "start": "0"}`
    - body `null`

### Mock-response fixture

- path:
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json`
- exactly one case:
  - `limit_1000_start_0`
- response body:
  - minimal JSON object scaffold only
  - no response-schema assertion in this topic

## Topic-local Harness Rules

- harness 必須攔截單一 outbound request，並在第二個 outbound request 時立即失敗
- harness 必須將 prepared request 正規化成 semantic shape：
  - `method`
  - `path`
  - `query`
  - `body`
  - `headers`
- harness 必須驗證：
  - method 完全一致
  - path 完全一致
  - query 必須為 `{"limit": "1000", "start": "0"}`
  - body 必須為 `null`
  - `Authorization` / `Accept` 必須存在且前綴一致
- harness 必須保留 topic fixture root fallback，不可跳出
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures`

## Blocked Variants

- non-string `caslib` -> fast-fail
- blank `caslib` -> fast-fail
- bare `GET` without query -> fast-fail
- `limit != 1000` -> fast-fail
- `start != 0` -> fast-fail
- any extra query param -> fast-fail
- request body present -> fast-fail
- `get_table` drift -> fast-fail
- `change_table_state` drift -> fast-fail

## Test Expectations

### Positive

- `list_tables(caslib="CASUSER")` emits:
  - `GET /casManagement/dataSources/cas~fs~cas-shared-default~fs~CASUSER/tables`
  - query `{"limit": "1000", "start": "0"}`
  - `Authorization: Bearer <token>`
  - `Accept: application/json`
  - body `null`

### Negative

- non-string `caslib`
- blank `caslib`
- bare `GET` without query
- `limit != 1000`
- `start != 0`
- any extra query param
- request body present
- drift to `get_table`
- drift to `change_table_state`

### Edge / regression

- reserved characters in `caslib` 必須 percent-encoding
- topic-local harness 只允許單一步驟 observed flow
- topic-scoped pytest run detection 必須只在本 package target 時放寬 coverage gate

## Stable Library Metadata Intent

- `README.md`、`docs/api-endpoints/markdown-reference/README.md`、`VERSION`、
  `pyproject.toml`、`uv.lock` 僅在 final `release` 對齊。
- 本 topic creator / publish-in-progress implementation 不得落地 stable-library changes。

## Validation Commands

```bash
uv run pytest tests/unit/request_contract/casmanagement_tables_list_request_gate -v
uv run ruff check tests/unit/request_contract/casmanagement_tables_list_request_gate
uv run pyright tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py
```
