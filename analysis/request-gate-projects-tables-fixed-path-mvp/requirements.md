# Request-Gate Projects Tables Fixed-Path MVP Requirements

> Status: `SUPERSEDED`
>
> 這份 artifact 只保留 fixed-path MVP 的歷史決策痕跡。
> `/modelRepository/projects/{project_id}/tables` 不得再被當成 current truth，
> 也不得再被描述成 upstream `sasctl` 對應端點。
## Purpose

本 topic 的目的，是為 `modelRepository/projects -> tables-link surface` 的
`list_tables` 凍結一個 **最小可行、可實作、明確承認 intentional divergence**
的 request-shape contract。

此 contract 的用途只限於：

- 作為未來 implementation 的最小 request-shape 依據
- 作為未來 request-contract tests 的固定範例
- 明確宣告此 topic 採 fixed-path MVP，而不是 upstream 的 HATEOAS 單一真相

## Scope

本 topic 只處理：

- `list_tables(project_id)` 的 fixed-path MVP request shape
- topic-local analysis artifacts
  - `analysis/request-gate-projects-tables-fixed-path-mvp/requirements.md`
  - `analysis/request-gate-projects-tables-fixed-path-mvp/technical-spec.md`
- topic-local plan artifacts
  - `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.plan.md`
  - `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.step.md`
  - `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.spec.md`
- future implementation landing path
  - `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py`
  - `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py`
  - `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py`
  - `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`
  - `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`

本 topic 不處理：

- `src/**`
- `docs/request-shape-priority-workflow/**`
- `casManagement/dataSources/tables`
- response / error contract
- polling / state-machine / orchestration
- multi-step flow

## Actors and ownership

- Primary actor: Plan-Creator
- Downstream review actor: Plan-Reviewer
- Future execution actor: Code-Implementer
- Human owner: human check 後決定是否 dispatch implementation

## Measurable requirements

1. **Fixed-path MVP freeze**
   - `list_tables` 必須凍結為固定路徑：
     `/modelRepository/projects/{project_id}/tables`
   - 不允許同 topic 內再引回 HATEOAS path discovery

2. **Implementation-facing draft**
   - contract status 必須明確標示為 `implementation-facing draft`
   - 不得把本 contract 描述成 source-observed single truth

3. **Intentional divergence freeze**
   - divergence label 必須明確標示為 `intentionally_changed`
   - 必須清楚說明這是 implementation-friendly 的 fixed-path MVP 選擇

4. **Single-step request shape**
   - canonical request 只允許單一步驟 `GET`
   - required input 只允許 `project_id`
   - query 必須為空
   - request body 必須不存在

5. **Surface boundary freeze**
   - topic 只處理 `modelRepository/projects -> tables-link surface`
   - 不得擴成 `casManagement/dataSources/tables`
   - 不得擴成 broader tables family orchestration

6. **Future implementation landing path freeze**
   - future request-contract implementation 只能落在
     `tests/unit/request_contract/projects_tables_link_request_gate/**`
   - 不得要求修改 shared workflow docs 或其他 endpoint topic artifacts

## Assumptions

- `project_id` 在本 topic 中只視為必要 path parameter
- `project_id` 不額外承擔 UUID、名稱、object branch、或 lookup semantics
- future mock response 只需提供最小 JSON object 讓 harness 完成呼叫
- 若未來要恢復 HATEOAS-faithful contract，必須另開新 topic

## Non-goals

- 不做 HATEOAS link parsing
- 不做先取 project 再 follow `links[].href`
- 不做 `casManagement/dataSources/tables`
- 不做 response schema
- 不做 pagination / filter / search / sort / limit / offset
- 不做 release / push / PR
- 不做 implementation code

## Freeze status

Status: `FROZEN`
