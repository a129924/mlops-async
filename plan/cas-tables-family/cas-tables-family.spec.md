# CAS Tables Endpoint Family Specification

## Public Contract

- `mlops_async.clients.cas_tables` re-exports `CasTablesClient`,
  `CasTablesResponseError`, `TableDetail`, `TableState`, and `TablesPage`.
- `TableState` is `TableState(str, Enum)` with only `LOADED = "loaded"`.
- `TableDetail` is a frozen, slotted dataclass with `name: str`, `caslib: str`,
  and `state: TableState`.
- `TablesPage` is a frozen, slotted dataclass with
  `items: tuple[TableDetail, ...]`.
- `list_tables(data_source_id: str, *, start: int = 0, limit: int = 20) -> TablesPage`.
- `get_table(data_source_id: str, table_name: str) -> TableDetail`.
- `change_table_state(server: str, caslib: str, table_name: str, state: str) -> TableDetail`.
  The public `state` is validated and converted to `TableState` before I/O.

## Acceptance Criteria

1. List uses `GET /casManagement/dataSources/{data_source_id}/tables` with explicit
   `start` and `limit` query values, issues exactly one request, and returns `TablesPage`.
2. Get uses `GET /casManagement/dataSources/{data_source_id}/tables/{table_name}` and
   returns a strict `TableDetail`.
3. State change uses
   `PUT /casManagement/servers/{server}/caslibs/{caslib}/tables/{table_name}/state`,
   sends `value=<TableState.value>` as query, sends no JSON body, and returns a strict
   `TableDetail`.
4. All names/caslib fields are strict non-empty strings, `state` is a supported enum
   value, and table-detail parser rejects missing, null, wrong-type, unknown-state, or
   extra detail fields with `CasTablesResponseError`.
5. Blank/non-string identifiers, bool/non-integer/negative `start`, bool/non-integer/
   non-positive `limit`, and blank/non-string/unknown public `state` raise `ValueError`
   before requester I/O.
6. Dynamic identifiers are percent-encoded; transport failures and
   `asyncio.CancelledError` propagate as the exact original instance.
7. The only unit-test paths are
   `tests/unit/clients/cas_tables/test_cas_tables_client.py` and
   `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py`; no root clients shortcut export,
   lifecycle helper, retry, or release artifact is introduced.

## Behavioral Scenarios

### Scenario 1: list one explicit page

- **Given** `data_source_id`, `start=0`, `limit=20`, and a JSON `items` array.
- **When** the caller awaits `list_tables`.
- **Then** one list request is sent, its query has `start` and `limit`, and the result is
  `TablesPage(items=(TableDetail(...),))`.

### Scenario 2: get a strict table detail

- **Given** a detail response `{"name":"INPUT","caslib":"CASUSER","state":"loaded"}`.
- **When** the caller awaits `get_table`.
- **Then** the result is `TableDetail(name="INPUT", caslib="CASUSER",
  state=TableState.LOADED)`.

### Scenario 3: change state from a public string

- **Given** explicit `server`, `caslib`, `table_name`, and `state="loaded"`.
- **When** the caller awaits `change_table_state`.
- **Then** state converts before I/O, the request is a no-body PUT with `value=loaded`,
  and the result is `TableDetail`.

### Scenario 4: preserve caller-owned failures

- **Given** requester raises a transport exception or `asyncio.CancelledError`.
- **When** any CAS Tables operation is awaited.
- **Then** the exact exception instance propagates without retry, cleanup, or translation.

## Test Plan

- `test_cas_tables_value_objects.py`: enum shape, frozen/slotted dataclasses, tuple page items,
  successful detail/list parsing, and semantic parser rejection cases.
- `test_cas_tables_client.py`: three endpoint shapes and result types, string-to-enum state conversion,
  all pre-I/O validation groups, dynamic path encoding, semantic JSON errors, exact failure
  propagation, and public-surface/lifecycle exclusions.
- Validation evidence 已記錄於 topic plan：以已驗證的 feature `GIT_DIR`、
  `GIT_WORK_TREE` 與 feature `PYTHONPATH` 執行 approved paired target pytest
  command，兩個 renamed test files 與 `--override-ini addopts=""` 一併執行後為
  `49 passed in 7.05s`；在 `--no-sync` 下，保留的 main Python 3.10.20 環境與要求的
  Python 3.10.0 不相容，uv 因而輸出 warning。保留的較早 scoped Ruff、Pyright、Tach
  evidence 均為 exit 0。retained latest default full pytest evidence 精確為
  `603 passed, 10 skipped`、95.54% coverage。八個 untracked topic paths 逐檔以
  `git diff --no-index --check -- /dev/null <path>` 檢查，均未輸出 whitespace
  diagnostic；這是 untracked-content evidence，不是普通 `git diff --check`。
  這些結果不授權 publication、PR、merge 或 release。
