# request-gate-casmanagement-change-table-state technical specification

## Status

- `FROZEN`

## Source Baseline Summary

- technical spec 以
  `analysis/request-gate-casmanagement-change-table-state/requirements.md`
  為 execution-facing baseline。
- 本 topic 是 `tests-only / shape-only` request gate。
- 實作面只允許：
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/**`
  不碰 `src/**`。

## Request Contract

### Canonical positive case

- case id: `loaded_direct_identifiers`
- method: `PUT`
- path:
  `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
- query:
  - `value=loaded`
- required headers:
  - `Authorization: Bearer <token>`
  - `Accept: application/json`
  - `Content-Type: application/json`
- body:
  - `outputCaslibName = <caslib>`
  - `outputTableName = <tableName>`

### Required inputs

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
- endpoint family
  - only `change_table_state`

## Fixture Layout

### Request-flow fixture

- path:
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
- exactly one case:
  - `loaded_direct_identifiers`
- exactly one observed step:
  - purpose: `target-api`
  - request:
    - method `PUT`
    - path
      `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
    - query
      - `value = loaded`
    - body
      - `outputCaslibName = <caslib>`
      - `outputTableName = <tableName>`

### Mock-response fixture

- path:
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json`
- exactly one case:
  - `loaded_direct_identifiers`
- response body:
  - minimal JSON object scaffold only
  - no response-schema assertion in this topic

## Topic-local Harness Rules

- harness 只允許單一步 outbound request；第二個 outbound request 必須 fail fast
- harness capture prepared request 的 semantic shape：
  - `method`
  - `path`
  - `query`
  - `body`
  - `headers`
- JSON request body 必須在 capture 後正規化成 JSON object，再與 expected body 比對
- harness fixture locator 只允許 topic fixture root：
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures`
- source-observed drift check 至少比對：
  - `method`
  - `path`
  - `query`
  - `body`
  - `required_header_subset`

## Blocked Variants

- non-string `caslib` -> fast-fail
- blank `caslib` -> fast-fail
- non-string `tableName` -> fast-fail
- blank `tableName` -> fast-fail
- missing state query -> fast-fail
- `value=unloaded` -> fast-fail
- any non-string state -> fast-fail
- any state other than `loaded` -> fast-fail
- extra query params -> fast-fail
- missing body -> fast-fail
- non-object body -> fast-fail
- mismatched `outputCaslibName` -> fast-fail
- mismatched `outputTableName` -> fast-fail
- `list_tables` drift -> fast-fail
- `get_table` drift -> fast-fail

## Test Expectations

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
- any non-string state
- any non-canonical state
- extra query params
- missing body
- non-object body
- `outputCaslibName` mismatch
- `outputTableName` mismatch
- drift to `list_tables`
- drift to `get_table`

### Edge / regression

- reserved characters in `caslib` / `tableName` 必須 percent-encode 到 path
- topic-local harness 只允許一個 observed flow
- topic-scoped pytest run detection 只對這個 package 放寬 coverage gate
- explicit `#case` locator 也不得繞過單一-case topic rule

## Stable Library Metadata Intent

- `README.md` / `docs/api-endpoints/markdown-reference/README.md` /
  `VERSION` / `pyproject.toml` / `uv.lock` 只在 final `release` 對齊
- `docs/request-shape-priority-workflow/**` 只在 final `release` 同步 current truth
- 本 topic creator / publish-in-progress implementation 不做 stable-library changes

## Validation Commands

```bash
uv run pytest tests/unit/request_contract/casmanagement_table_state_change_request_gate -v
uv run ruff check tests/unit/request_contract/casmanagement_table_state_change_request_gate
uv run pyright tests/unit/request_contract/casmanagement_table_state_change_request_gate/conftest.py tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py
```
