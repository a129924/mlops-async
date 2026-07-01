# request-gate-casmanagement-change-table-state - Behavior Spec

## Purpose

本 spec 用來固定 `casManagement/caslibs/tables/state -> change_table_state`
的 request-shape contract。

本 spec 明確限定：

- `tests-only / shape-only`
- `loaded` baseline only
- query `value=loaded`
- body required and must match path identifiers
- `list_tables` / `get_table` blocked

本 topic 只關心 request shape，不宣告 runtime CAS state-transition semantics。

---

## Canonical request

### Allowed case

| Case ID | Method | Path | Query | Body |
| --- | --- | --- | --- | --- |
| `loaded_direct_identifiers` | `PUT` | `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state` | `{"value":"loaded"}` | `{"outputCaslibName":"<caslib>","outputTableName":"<tableName>"}` |

### Required input

- `caslib`
  - required
  - non-empty string
- `tableName`
  - required
  - non-empty string
- `value`
  - required
  - only `loaded`
- body
  - required
  - JSON object
  - `outputCaslibName` must equal `caslib`
  - `outputTableName` must equal `tableName`

### Request-shape focus

本 topic 只驗證：

- method
- path
- query shape
- body shape
- `Authorization`
- `Accept`
- `Content-Type`

本 topic 不驗證 response schema。

---

## Blocked variants

| Variant | Example | Expected result |
| --- | --- | --- |
| non-string `caslib` | `123` | fast-fail |
| blank `caslib` | `"   "` | fast-fail |
| non-string `tableName` | `123` | fast-fail |
| blank `tableName` | `"   "` | fast-fail |
| missing `value` | `include_state_query=False` | fast-fail |
| `value=unloaded` | `state="unloaded"` | fast-fail |
| non-string `value` | `state=1` | fast-fail |
| non-canonical `value` | `state="loading"` | fast-fail |
| extra query params | `extra_query={"x":"1"}` | fast-fail |
| missing body | `body_override=None` | fast-fail |
| non-object body | `body_override="x"` | fast-fail |
| `outputCaslibName` mismatch | `body_override={"outputCaslibName":"OTHER",...}` | fast-fail |
| `outputTableName` mismatch | `body_override={"outputTableName":"OTHER"}` | fast-fail |
| drift to `list_tables` | `endpoint_variant="list_tables"` | fast-fail |
| drift to `get_table` | `endpoint_variant="get_table"` | fast-fail |

---

## Out-of-scope variants

- `list_tables`
- `get_table`
- `value=unloaded` positive baseline
- response schema
- CAS load / unload business semantics
- runtime CAS wiring
- `src/**`
- creator / publish-in-progress 的 docs / version / workflow-doc 修改

---

## Fixture expectations

### Request-flow fixture

- file:
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
- cases:
  - `loaded_direct_identifiers`

### Mock-response fixture

- file:
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json`
- response body:
  - minimal JSON object only
  - no response-schema assertion in this topic

---

## Test expectations

### Positive

- `change_table_state(caslib="CASUSER", table_name="SCORING_INPUT")` emits:
  - `PUT /casManagement/servers/cas-shared-default/caslibs/CASUSER/tables/SCORING_INPUT/state`
  - query `{"value": "loaded"}`
  - body
    `{"outputCaslibName": "CASUSER", "outputTableName": "SCORING_INPUT"}`
  - `Authorization: Bearer <token>`
  - `Accept: application/json`
  - `Content-Type: application/json`

### Negative

- non-string `caslib`
- blank `caslib`
- non-string `tableName`
- blank `tableName`
- missing `value`
- `value=unloaded`
- non-string `value`
- non-canonical `value`
- extra query params
- missing body
- non-object body
- `outputCaslibName` mismatch
- `outputTableName` mismatch
- drift to `list_tables`
- drift to `get_table`

### Guard

- any path drift causes failure
- any query drift causes failure
- any body drift causes failure
- any attempt to introduce a second outbound request is topic drift

### Edge

- reserved characters in `caslib` / `tableName` 必須正確 percent-encode 到 path

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

以上只在 final `release` 對齊，不在本 topic creator / publish-in-progress 變更。
