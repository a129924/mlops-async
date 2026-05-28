# Request-Gate Projects-Tables Workflow Steps

## Implementation Steps

- [X] 確認 `tests/unit/request_contract/projects_request_gate/conftest.py` 存在且符合 Layer 1 source-observed harness 規格；確認無 transport-noise 斷言、無 `pyproject.toml` / `uv.lock` 變更。
- [X] 確認 `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.request-flow.json` 存在，且只覆蓋 `bare_get` 與 `limit_1000` 兩個 case。
- [X] 確認 `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.mock-responses.json` 存在，且 mock answer set 與 request-flow fixture 對應。
- [X] 確認 `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.request-flow.json` 存在，且只覆蓋 `direct_identifier` case。
- [X] 確認 `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.mock-responses.json` 存在，且 mock answer set 與 request-flow fixture 對應。
- [X] 確認 `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py` 通過測試，且所有 list_projects 測試只比對 semantic request behavior。
- [X] 確認 `tests/unit/request_contract/projects_request_gate/test_get_project_request_contract.py` 通過測試，且 get_project 只覆蓋 direct identifier branch；out-of-scope variants 觸發 `blocked_topic_scope_error`。
- [X] 建立 `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md`。
- [X] 建立 `plan/request-gate-projects-tables/request-gate-projects-tables.step.md`。
- [X] 建立 `plan/request-gate-projects-tables/request-gate-projects-tables.spec.md`。

## Workflow Stages

這些 stage markers 僅供參考。Completion gate 只讀取 `## Implementation Steps`。

- [X] Projects request-flow fixture 建立（bare_get、limit_1000、direct_identifier）
- [X] Projects mock-responses fixture 建立
- [X] Projects harness / conftest 實作
- [X] Projects request-contract tests 實作（list_projects、get_project）
- [X] Plan artifacts 建立
- [ ] Independent review
- [ ] Tables BLOCKED 人工決策（此 stage 屬於 open question，不屬於本 topic completion gate）
