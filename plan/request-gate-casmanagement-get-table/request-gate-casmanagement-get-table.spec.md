# request-gate-casmanagement-get-table - Behavior Spec

## Purpose

本 spec 凍結 `casManagement/dataSources/tables -> get_table` 的最小 request-shape contract。

本 spec 明確宣告：

- `tests-only / shape-only`
- direct identifiers only
- query blocked
- `list_tables` / `change_table_state` blocked

本 topic 只證明 request shape，不證明 runtime CAS behavior。

---

## Canonical request

### Allowed case

| Case ID | Method | Path | Query | Body |
| --- | --- | --- | --- | --- |
| `direct_identifiers` | `GET` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables/{tableName}` | `{}` | `null` |

### Required input

- `caslib`
  - required
  - non-empty string
- `tableName`
  - required
  - non-empty string
- query params
  - blocked
- body
  - blocked

### Request-shape focus

本 topic 只驗證：

- method
- path
- query absence
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
| non-string `tableName` | `123` | fast-fail |
| blank `tableName` | `"   "` | fast-fail |
| any query params | `extra_query={"state":"loaded"}` | fast-fail |
| request body present | `body={"x":1}` | fast-fail |
| drift to `list_tables` | `endpoint_variant="list_tables"` | fast-fail |
| drift to `change_table_state` | `endpoint_variant="change_table_state"` | fast-fail |

---

## Out-of-scope variants

- `list_tables`
- `change_table_state`
- response schema
- CAS load-state business semantics
- auth runtime wiring
- `src/**`
- creator / publish-in-progress 的 docs / version / workflow-doc 變更

---

## Fixture expectations

### Request-flow fixture

- file:
  `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.request-flow.json`
- cases:
  - `direct_identifiers`

### Mock-response fixture

- file:
  `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.mock-responses.json`
- response body:
  - minimal JSON object only
  - no response-schema assertion in this topic

---

## Test expectations

### Positive

- `get_table(caslib="CASUSER", table_name="SCORING_INPUT")` emits:
  - `GET /casManagement/dataSources/cas~fs~cas-shared-default~fs~CASUSER/tables/SCORING_INPUT`
  - query `{}`
  - `Authorization: Bearer <token>`
  - `Accept: application/json`
  - body `null`

### Negative

- non-string `caslib`
- blank `caslib`
- non-string `tableName`
- blank `tableName`
- any query params
- request body present
- drift to `list_tables`
- drift to `change_table_state`

### Guard

- any path drift causes failure
- any query params cause failure
- any request body causes failure
- any attempt to introduce a second outbound request is topic drift

### Edge

- reserved characters in `tableName` 必須被 percent-encoding

---

## Stable-library note

- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`
- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`

以上八者只在 final `release` 對齊，不在本 topic creator / publish-in-progress 落地。
