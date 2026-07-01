# Request-Gate CASManagement List Tables Workflow Steps

本 step tracker 用來標記本 topic 的 creator implementation completion gate。
所有本輪 in-scope 產物與 bounded validation 完成後，對應 steps 必須標成 `[X]`。

## Implementation Steps

- [X] 建立 `analysis/request-gate-casmanagement-list-tables/requirements.md`
- [X] 建立 `analysis/request-gate-casmanagement-list-tables/technical-spec.md`
- [X] 建立 `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.plan.md`
- [X] 建立 `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.step.md`
- [X] 建立 `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.spec.md`
- [X] 建立 `tests/unit/request_contract/casmanagement_tables_list_request_gate/__init__.py`
- [X] 建立 `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py`
- [X] 建立 `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
- [X] 建立 `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json`
- [X] 建立 `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`
- [X] 覆蓋正向 request shape、blocked variants、percent-encoding、與 topic-scoped harness regression
- [X] 完成 bounded validation：`pytest`、`ruff`、`pyright`
