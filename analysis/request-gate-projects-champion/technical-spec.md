# Request-Gate Projects Champion Technical Spec

## Source requirements

本技術規格落實下列需求來源：

- `analysis/request-gate-projects-champion/requirements.md`

全域 workflow / planning guardrails 來自：

- `AGENTS.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`
- `analysis/api-client-porting-contract/technical-spec.md`

## Goal

把 `modelRepository/projects/champion` / `get_champion_model` 的 docs-suffice planning baseline 轉成可審查的
topic-local technical contract，並同步修正 reviewer 指出的 workflow state drift，明確凍結 endpoint inventory、
request contract draft、allowed write set、未來 implementation landing path、與 reviewer-first workflow
handoff，同時避免把 scope 擴到 `projects` family 其他 API。

## Current state summary

目前 repo-visible evidence 顯示：

- `docs/request-shape-priority-workflow/checklist.md`
  - queue order `06` 指向 `modelRepository/projects/champion` / `get_champion_model`
- `docs/request-shape-priority-workflow/standards.md`
  - surface queue 明確把 `modelRepository/projects/champion` 放在 `modelRepository/projects` 之後、`tables-link surface` 之前
- `docs/api-endpoints/swagger-spec/projects-spec.yaml`
  - 記錄 `GET /modelRepository/projects/{projectId}/champion`
  - 記錄 `Authorization` 與 `Accept` headers
  - 記錄使用場景為先取得 `projectId` 再查 champion model
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
  - 明確標示 `sasctl` 沒有直接取得 Champion Model 的方法，需保留 direct REST endpoint
- repo 目前找不到 `utils/_api/project.py` 或等價 legacy source file

因此本 topic 可以完成 planning，但 execution/TDD 仍缺少 source-level legacy evidence。

## Allowed file scope

### Allowed

- `analysis/request-gate-projects-champion/requirements.md`
- `analysis/request-gate-projects-champion/technical-spec.md`
- `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
- `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`

### Forbidden

- `src/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `docs/request-shape-priority-workflow/**`
- shared workflow contract
- `plan/request-gate-projects-champion/request-gate-projects-champion.spec.md`
- any other endpoint topic artifacts

## Endpoint inventory and precedent

| Item | Repo-visible evidence | Planning implication |
| --- | --- | --- |
| Queue slot | `docs/request-shape-priority-workflow/checklist.md` order `06` | 本 topic 是合法下一個 `projects` family endpoint |
| Surface order | `docs/request-shape-priority-workflow/standards.md` | 不得跳過 queue，也不得擴張到 tables-link surface |
| REST path | `GET /modelRepository/projects/{projectId}/champion` | 只規劃 direct champion endpoint |
| Upstream alignment | `sasctl` 無 direct champion getter | execution 不得假設有 upstream facade 可直接沿用 |
| Legacy source | docs 引用 `utils/_api/project.py::fetch_champion_model`，但 repo 無原始檔 | human 必須補件或明確 override，execution/TDD 才能前進 |

## Request contract draft

| Field | Draft |
| --- | --- |
| API | `get_champion_model` |
| Method | `GET` |
| Path | `/modelRepository/projects/{projectId}/champion` |
| Path input | `projectId` 為 required path parameter |
| Required headers | `Authorization`, `Accept` |
| Query semantics | 無 repo-visible required query params |
| Body shape | no body |
| Usage precondition | `projectId` 需由既有流程先取得；本 topic 不負責該流程 |
| Evidence status | docs-confirmed / source-not-confirmed |

### Excluded semantics in this topic

- `files` payload 驗證
- `inputVariables` / `outputVariables` payload 驗證
- `_get_model_type` 派生邏輯
- `project name -> list_projects -> projectId` 的多步序列
- response / error contract

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結 bounded endpoint、write set、reviewer-first workflow boundary、與 execution prerequisites |
| `technical-spec.md` | 把 baseline 映射成 endpoint inventory、request contract draft、landing path、與 stop rules |
| `request-gate-projects-champion.plan.md` | 作為 canonical topic-plan contract，供 downstream reviewer / planner 消費 |
| `request-gate-projects-champion.step.md` | 只追蹤本輪 creator-owned planning / rework 完成度，不承擔 reviewer、planner final gate、或 human-check 狀態 |

## Future implementation landing path

本 topic 不建立 tests，但已凍結 downstream landing rule：

- future execution topic 只能在 `tests/unit/request_contract/projects_request_gate/` 下新增 champion 專屬檔案
- permitted shape 僅限 new champion-only files，例如：
  - `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`
- forbidden：
  - 修改既有 `tests/unit/request_contract/projects_request_gate/conftest.py`
  - 修改既有 `list_projects` / `get_project` fixtures
  - 修改既有 `list_projects` / `get_project` request tests

若 execution 證明上述 forbidden set 無法維持，必須回到 human check，而不是在本 topic 內直接放寬。

## Workflow handoff sequence

本 topic 的 workflow handoff 固定為：

1. create managed worktree
2. 建立四個 topic-local planning artifacts
3. 建立 draft topic commit
4. 進入 reviewer flow
5. reviewer 若指出 workflow-state blocking issue，由 creator 在同 topic 內做 bounded fix
6. creator fix 完成後交由 planner final gate
7. planner final gate 完成後才進入 human check

`request-gate-projects-champion.step.md` 只覆蓋 creator-owned artifact authoring 與 bounded rework completion gate，不表示第 4-7 步的 workflow state。

## Planner-ready handoff

### Confirmed now

- endpoint surface 與 API 名稱
- queue precedence 與 bounded topic 位置
- method / path / required header subset
- `sasctl` 無 direct champion getter
- planning 可以 docs-suffice 完成

### Still unresolved

- `utils/_api/project.py::fetch_champion_model` 的 repo-visible原始實作
- URL helper `get_champion_model_url` 的完整 source context
- legacy source 是否含額外 header/query/body semantics
- execution 是否真的可在不碰既有 `projects_request_gate` harness 的前提下完成

## Validation

必要檢查：

1. 下列四個 topic-local files 存在：
   - `analysis/request-gate-projects-champion/requirements.md`
   - `analysis/request-gate-projects-champion/technical-spec.md`
   - `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
   - `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`
2. 四個 artifacts 一致宣告：
   - topic 只處理 `modelRepository/projects/champion` / `get_champion_model`
   - planning evidence 採 docs-suffice
   - execution/TDD 需 human 補齊 legacy source evidence 才可前進
   - reviewer flow 先於 planner final gate，且 planner final gate 先於 human check
   - 本輪不得修改 `src/**`、`tests/unit/request_contract/projects_request_gate/**`、`docs/request-shape-priority-workflow/**`
3. plan 的 `Artifact Paths` 僅列四個允許落地的 topic-local files。
4. step tracker 的 `## Implementation Steps` 只追蹤本輪 creator-owned planning / rework work，不混入 reviewer、planner final gate、human-check、或 implementation tasks。

## Stop conditions

若出現以下情況，必須停止並回到 human check：

- 需要修改 `src/**`
- 需要修改 `tests/unit/request_contract/projects_request_gate/**`
- 需要修改 `docs/request-shape-priority-workflow/**` 或 shared workflow contract
- 需要把 `modelRepository/projects/champion` 擴張成 `modelRepository/projects` family-level topic
- 需要建立或修改其他 endpoint 的 fixtures / topic artifacts
- 需要在缺少 legacy source evidence 的情況下直接 author execution/TDD files
- 需要調整既有 `projects_request_gate` harness / fixtures / tests 才能支援 champion endpoint
