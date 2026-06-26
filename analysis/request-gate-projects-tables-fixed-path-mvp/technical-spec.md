# Request-Gate Projects Tables Fixed-Path MVP Technical Spec

## Source requirements

- `analysis/request-gate-projects-tables-fixed-path-mvp/requirements.md`

## Workflow guardrails

- `AGENTS.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`
- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`

## Goal

把 `modelRepository/projects -> tables-link surface / list_tables` 從原本的
`BLOCKED` HATEOAS 決策點，凍結成一個可直接實作的 fixed-path MVP request-shape
baseline，供未來 implementation topic 使用。

## Current state summary

- `docs/request-shape-priority-workflow/checklist.md`
  - queue order `07` 為 `modelRepository/projects -> tables-link surface / list_tables`
  - board 目前仍標成 `BLOCKED`
- `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md`
  - 舊 topic 將 tables surface 記錄為 HATEOAS conditional endpoint selection
  - 本 topic 明確取代該 open decision，改採 fixed-path MVP
- 本 topic 不回寫 shared workflow docs；它只建立 implementation-facing draft

## Allowed file scope

### Allowed now

- `analysis/request-gate-projects-tables-fixed-path-mvp/requirements.md`
- `analysis/request-gate-projects-tables-fixed-path-mvp/technical-spec.md`
- `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.plan.md`
- `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.step.md`
- `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.spec.md`

### Allowed later in implementation

- `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`
- `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`

### Forbidden

- `src/**`
- `docs/request-shape-priority-workflow/**`
- `tests/contracts/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `casManagement/dataSources/tables`
- any response / error contract artifact

## Request contract draft

| Field | Draft |
| --- | --- |
| API | `list_tables` |
| Classification | `fixed-path MVP` |
| Contract status | `implementation-facing draft` |
| Divergence label | `intentionally_changed` |
| Method | `GET` |
| Path | `/modelRepository/projects/{project_id}/tables` |
| Required input | `project_id` |
| Query | none |
| Body | none |
| Flow shape | single-step direct request |
| Evidence posture | implementation-facing, not source-observed single truth |

### Canonical invocation

- `list_tables(project_id="project-id-abc-123")`

### Allowed input shape

- `project_id` 必須是 non-empty string
- 本 topic 不額外限制 `project_id` 的格式語意

### Blocked variants

- `project_id` 不是字串
- `project_id` 是空字串
- `project_id` 只含空白
- 任何 query parameters
- 任何 request body

### Explicitly excluded semantics

- HATEOAS link parsing
- project fetch pre-step
- `links[].href` follow-up
- `casManagement/.../tables` remap
- response contract
- pagination / filter / search / sort / limit / offset

## Fixture proposal

### Request-flow fixture

- path:
  `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`
- single case:
  - `direct_project_identifier`
- minimal shape:
  - method `GET`
  - path `/modelRepository/projects/project-id-abc-123/tables`
  - query `{}`
  - body `null`

### Mock-response fixture

- path:
  `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`
- minimal body:
  - one JSON object only
  - just enough for harness completion

## Future implementation landing path

未來 implementation 只應建立一個 isolated request-contract package：

- `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py`
- `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`
- `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`

## Workflow handoff sequence

1. create managed worktree
2. finalize topic-local analysis / plan artifacts
3. independent plan review
4. bounded plan fix if needed
5. final gate re-review
6. wait for human check before dispatching implementation

## Validation

規格完成時，至少要能明確回答：

- canonical path 是否固定為 `/modelRepository/projects/{project_id}/tables`
- `project_id` 是否為唯一必要輸入
- query / body 是否明確禁止
- divergence label 是否明確為 `intentionally_changed`
- future implementation path 是否精確且 bounded
- future HATEOAS restoration 是否被明確切到新 topic

## Stop conditions

以下任何一項都視為 drift：

- 把本 topic 改回 HATEOAS 討論
- 擴到 `casManagement/dataSources/tables`
- 擴到 response / error contract
- 擴到 multi-step flow
- 擴到 polling / orchestration
