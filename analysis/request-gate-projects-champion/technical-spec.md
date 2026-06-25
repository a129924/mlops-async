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

把 `modelRepository/projects/champion` / `get_champion_model` 的 docs-suffice planning baseline 與新增 legacy request
evidence 轉成可審查的 topic-local technical contract，並同步修正 reviewer 指出的 workflow state drift，明確凍結
endpoint inventory、request contract draft、allowed write set、未來 implementation landing path、與 reviewer-first
workflow handoff，同時避免把 scope 擴到 `projects` family 其他 API。

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
- human-provided legacy source：`sas-api/src/sas_api/utils/_api/project.py`
  - `get_champion_model_url`（line 76-77）回傳 `f"{BASE_PROJECT_URL}/{project_item.id}/champion"`
  - `fetch_champion_model`（line 80-92）執行 `async_web_session.get(url=champion_model_url, headers=headers)`
- human-provided legacy source：`sas-api/src/sas_api/api/sas/project/api.py`
  - `get_champion_model`（line 169-184）先呼叫 `get_project_by_name(...)`
  - 再以 `get_champion_model_url(user_response.data)` 組出 champion endpoint
  - 接著呼叫 `fetch_champion_model(...)`
- human-provided legacy source：`sas-api/src/sas_api/schema/sas_viya/project/champion.py`
  - 存在 champion response 相關模型，證明上游 schema surface 已 materialize

因此本 topic 的 request evidence 已可凍結到 legacy-source-confirmed；同一個 PR 也已提交 champion-only request-contract test / fixture artifacts。這份 technical spec 只把該 deliverable set 與後續 forbidden modification set 寫清楚，不把 scope 擴張到 `src/**`、response / error contract、或 `projects` family 其他 API。

## Allowed file scope

### Allowed

- `analysis/request-gate-projects-champion/requirements.md`
- `analysis/request-gate-projects-champion/technical-spec.md`
- `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
- `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`
- topic 已提交的 champion-only request-contract artifacts：
  - `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`

### Forbidden

- `src/**`
- 對任何既有 request-contract artifact 的內容修改，包含：
  - `tests/unit/request_contract/projects_request_gate/conftest.py`
  - `tests/unit/request_contract/projects_request_gate/__init__.py`
  - 既有 `list_projects` / `get_project` request tests 與 fixtures
  - 上述已提交的 champion-only request-contract artifacts（本輪 bounded fix 內視為 frozen）
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
| Legacy URL helper | `get_champion_model_url(project_item)` 回傳 `"{BASE_PROJECT_URL}/{project_item.id}/champion"` | path shape 與 `project_item.id` 來源已 source-confirmed |
| Legacy transport | `fetch_champion_model(...)` 執行 `async_web_session.get(url=champion_model_url, headers=headers)` | method 為 `GET`，且 request body 為空 |
| Legacy call chain | `get_champion_model(...)` -> `get_project_by_name(...)` -> `get_champion_model_url(user_response.data)` -> `fetch_champion_model(...)` | `projectId` 前提與 request construction chain 已 source-confirmed |
| Legacy schema surface | `schema/sas_viya/project/champion.py` 存在 champion response 相關模型 | 上游存在對應 response schema，但本 topic 不擴張 response contract |

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
| Request construction source | `get_champion_model(...)` -> `get_project_by_name(...)` -> `get_champion_model_url(user_response.data)` -> `fetch_champion_model(...)` |
| Transport call | `async_web_session.get(url=champion_model_url, headers=headers)` |
| Usage precondition | `projectId` 需由既有流程先取得；本 topic 只凍結此前提，不負責該流程 |
| Evidence status | docs-confirmed / legacy-source-confirmed |

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

本 topic 已新增並交付下列 champion-only request-contract artifacts：

- `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
- `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
- `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`

後續 frozen rule：

- 本次 bounded fix 只允許更新四份 planning artifacts；上述 champion-only files 在本輪不再修改
- downstream forbidden modification set 固定包含：
  - `tests/unit/request_contract/projects_request_gate/conftest.py`
  - `tests/unit/request_contract/projects_request_gate/__init__.py`
  - 既有 `list_projects` / `get_project` fixtures
  - 既有 `list_projects` / `get_project` request tests
  - 上述已交付 champion-only request-contract artifacts，除非 human 另開新 topic 明確放行

若 execution 證明上述 forbidden set 無法維持，必須回到 human check，而不是在本 topic 內直接放寬。

## Workflow handoff sequence

本 topic 的 workflow handoff 固定為：

1. create managed worktree
2. 建立四個 topic-local planning artifacts
3. 建立 draft topic commit
4. 進入 reviewer flow
5. reviewer 若指出 workflow-state blocking issue，由 creator 在同 topic 內做 bounded fix
6. creator fix 完成後回到 reviewer acceptance
7. reviewer 接受後才交由 planner final gate
8. planner final gate 完成後才進入 human check

`request-gate-projects-champion.step.md` 只覆蓋 creator-owned artifact authoring 與 bounded rework completion gate，不表示 reviewer acceptance，也不表示第 4-8 步的 workflow state。

## Planner-ready handoff

### Confirmed now

- endpoint surface 與 API 名稱
- queue precedence 與 bounded topic 位置
- method / path / required header subset
- `project_item.id` 經 `get_champion_model_url(...)` 組成 `/modelRepository/projects/{projectId}/champion`
- 上層 request construction chain：`get_champion_model(...)` -> `get_project_by_name(...)` -> `get_champion_model_url(user_response.data)` -> `fetch_champion_model(...)`
- transport call：`async_web_session.get(url=champion_model_url, headers=headers)`
- `sasctl` 無 direct champion getter
- champion response schema surface 已在 legacy source materialize
- planning 可以完成 evidence sync，且 request evidence 已 frozen

### Still unresolved

- `sas_viya_get_headers(...)` 展開後是否還含 `Authorization` / `Accept` 之外的 shared header semantics，不在本 topic 內追溯
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
   - planning evidence 已同步 docs surfaces 與 human-provided legacy request evidence
   - request evidence 至少凍結 method、path shape、request construction source、與 transport call
   - 本輪 creator rework 完成後先回到 reviewer acceptance；只有 reviewer 接受後才進入 planner final gate，且 planner final gate 先於 human check
   - 本輪不得修改 `src/**`、任何 `tests/unit/request_contract/projects_request_gate/**` execution artifact content、或 `docs/request-shape-priority-workflow/**`
3. plan 的 `Artifact Paths` 僅列四個允許落地的 topic-local files。
4. step tracker 的 `## Implementation Steps` 只追蹤本輪 creator-owned completion gate，不混入 reviewer、planner final gate、human-check、或新的 implementation tasks；但必須明確承認已提交 champion-only request-contract artifacts 也是本 PR deliverables。

## Stop conditions

若出現以下情況，必須停止並回到 human check：

- 需要修改 `src/**`
- 需要修改任何 `tests/unit/request_contract/projects_request_gate/**` execution artifact
- 需要修改 `docs/request-shape-priority-workflow/**` 或 shared workflow contract
- 需要把 `modelRepository/projects/champion` 擴張成 `modelRepository/projects` family-level topic
- 需要建立或修改其他 endpoint 的 fixtures / topic artifacts
- 需要擴寫超出本輪 frozen request evidence 的 semantics，例如追 header helper 細節、response contract、或 error contract
- 需要調整既有 `projects_request_gate` harness / fixtures / tests 才能支援 champion endpoint
