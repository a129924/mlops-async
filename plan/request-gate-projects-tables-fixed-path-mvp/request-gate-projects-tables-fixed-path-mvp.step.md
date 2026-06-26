# Request-Gate Projects Tables Fixed-Path MVP Workflow Steps

本 step tracker 只追蹤這個 topic 的 implementation completion gate。
目前 implementation 與 bounded validation 已完成，所以所有 steps 均標記為 `[X]`。

## Implementation Steps

- [X] 建立 `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py`。
- [X] 建立 `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py`。
- [X] 建立 `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`，只保留 `direct_project_identifier`。
- [X] 建立 `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`，只保留最小 JSON object scaffold。
- [X] 建立 `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py`。
- [X] 驗證 fixed-path request shape 為 `GET /modelRepository/projects/{project_id}/tables`，且 query/body 皆不存在。
- [X] 驗證 non-string、empty、blank `project_id` 都會 fast-fail。
- [X] 執行 bounded validation：`pytest`、`pyright`、`ruff`。
