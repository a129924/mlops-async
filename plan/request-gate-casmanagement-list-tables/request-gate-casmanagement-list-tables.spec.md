# request-gate-casmanagement-list-tables - Behavior Spec

## Purpose

本 spec 凍結 `casManagement/dataSources/tables -> list_tables` 的最小 request-shape contract。

本 spec 明確宣告：

- `tests-only / shape-only`
- strict `limit=1000&start=0` only
- bare `GET` blocked
- `get_table` / `change_table_state` blocked

本 topic 只證明 request shape，不證明 runtime CAS behavior。

---

## Canonical request

### Allowed case

| Case ID | Method | Path | Query | Body |
| --- | --- | --- | --- | --- |
| `limit_1000_start_0` | `GET` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables` | `{"limit": "1000", "start": "0"}` | `null` |

### Required input

- `caslib`
  - required
  - non-empty string
- `limit`
  - only `1000`
- `start`
  - only `0`
- extra query params
  - blocked
- body
  - blocked

### Request-shape focus

本 topic 只驗證：

- method
- path
- query exactness
- body absence
- `Authorization`
- `Accept`

本 topic 不驗證 response schema。

---

## Blocked variants

| Variant | Example | Expected result |
| --- | --- | --- |
| non-string `caslib` | `123` | fast-fail |
| blank `caslib` | `"   "` | fast-fail |
| bare `GET` without query | `include_default_query=False` | fast-fail |
| `limit != 1000` | `limit=500` | fast-fail |
| `start != 0` | `start=10` | fast-fail |
| any extra query param | `extra_query={"filter":"x"}` | fast-fail |
| request body present | `body={"x":1}` | fast-fail |
| drift to `get_table` | `endpoint_variant="get_table"` | fast-fail |
| drift to `change_table_state` | `endpoint_variant="change_table_state"` | fast-fail |

---

## Out-of-scope variants

- `get_table`
- `change_table_state`
- response schema
- pagination behavior beyond strict `limit=1000&start=0`
- filter / sort / search
- auth runtime wiring
- `src/**`
- creator / publish-in-progress 的 docs / version 變更

---

## Fixture expectations

### Request-flow fixture

- file:
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
- cases:
  - `limit_1000_start_0`

### Mock-response fixture

- file:
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json`
- response body:
  - minimal JSON object only
  - no response-schema assertion in this topic

---

## Test expectations

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

### Guard

- any path drift causes failure
- any query drift causes failure
- any request body causes failure
- any attempt to introduce a second outbound request is topic drift

### Edge

- reserved characters in `caslib` 必須被 percent-encoding

---

## Stable-library note

- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

以上五者只在 final `release` 對齊，不在本 topic creator / publish-in-progress 落地。
