# Request-Gate CASManagement Change Table State Workflow Steps

此 step tracker 專注於 topic 的 creator implementation completion gate。
只有 in-scope artifacts 與 bounded validation 完成後，所有 steps 才能標記為 `[X]`。

## Implementation Steps

- [X] 建立 `analysis/request-gate-casmanagement-change-table-state/requirements.md`
- [X] 建立 `analysis/request-gate-casmanagement-change-table-state/technical-spec.md`
- [X] 建立 `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.plan.md`
- [X] 建立 `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.step.md`
- [X] 建立 `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.spec.md`
- [X] 建立 `tests/unit/request_contract/casmanagement_table_state_change_request_gate/__init__.py`
- [X] 建立 `tests/unit/request_contract/casmanagement_table_state_change_request_gate/conftest.py`
- [X] 建立 `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
- [X] 建立 `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json`
- [X] 建立 `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py`
- [X] 凍結 request shape、blocked variants、percent-encoding、與 topic-scoped harness regression
- [X] 完成 bounded validation：`pytest`、`ruff`、`pyright`
