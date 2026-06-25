# Request Gate Models Content Technical Spec

## Source requirements

本技術規格對應下列需求來源：

- `analysis/request-gate-models-content/requirements.md`

repo-local governance 約束：

- `AGENTS.md`

## Goal

把 `request-gate-models-content` author 成 implement lane 的 execution contract，
使本輪工作只在 topic-local plan artifacts 內完成 implement-plan workflow，並使後續工作只能在
frozen write set 內落地
`GET /modelRepository/models/{modelId}/contents/{fileId}/content` 的 request-only gate，
而不擴張到 `sasctl` HATEOAS path、shared workflow semantics、或相鄰 endpoint family。

## Active contract basis

本 topic 的 active contract basis 只包含：

- `analysis/request-gate-models-content/requirements.md`
- `analysis/request-gate-models-content/technical-spec.md`
- `plan/request-gate-models-content/request-gate-models-content.plan.md`
- `plan/request-gate-models-content/request-gate-models-content.spec.md`
- `plan/request-gate-models-content/request-gate-models-content.step.md`
- future implementation root：
  `tests/unit/request_contract/models_content_request_gate/**`

下列 shared surfaces 只可作為背景參照，不得作為 current scope、status、或 completion gate
的 active authority：

- `docs/request-shape-priority-workflow/**`
- shared workflow board
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`

## Current state summary

目前 repo / worktree 已有：

- `modelRepository/models/content / get_model_content` 位於 shared board order `03`
- repo-local swagger / markdown reference 已列出 direct path
- `tests/unit/request_contract/models_request_gate/**`、
  `tests/unit/request_contract/projects_request_gate/**`、
  `tests/unit/request_contract/job_requests_jobs_request_gate/**` 作為 precedent
- local `sasctl` source inventory 證明 `ModelRepository.get_model_contents()` 走 `/contents`
  list-follow path，而非 direct content GET
- implement lane 已有 topic-local implement-plan artifacts 初稿，但尚未進 draft-plan commit /
  reviewer gate

目前 repo / worktree 尚未有：

- `tests/unit/request_contract/models_content_request_gate/**`

## Allowed file scope

本輪 planning actor 的 write boundary 僅限：

- `analysis/request-gate-models-content/requirements.md`
- `analysis/request-gate-models-content/technical-spec.md`
- `plan/request-gate-models-content/request-gate-models-content.plan.md`
- `plan/request-gate-models-content/request-gate-models-content.spec.md`
- `plan/request-gate-models-content/request-gate-models-content.step.md`

後續 `Implementer` 的 planned write boundary 僅限：

- `tests/unit/request_contract/models_content_request_gate/__init__.py`
- `tests/unit/request_contract/models_content_request_gate/conftest.py`
- `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py`
- `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json`
- `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json`

下列路徑在本 topic 中不得修改或不得作為 primary surface：

- `docs/request-shape-priority-workflow/**`
- `src/**`
- `pyproject.toml`
- `uv.lock`
- `tests/unit/request_contract/models_request_gate/**`
- `tests/unit/request_contract/projects_request_gate/**`
- 其他 `tests/unit/request_contract/**` surface
- 其他 topic 的 `analysis/**` 或 `plan/**`

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結 business baseline、single-endpoint scope、locked request shape、non-goals、stop rules |
| `technical-spec.md` | 把需求映射為 implement lane 的 workflow contract、allowed scope、evidence boundary、risk、stop flags |
| `plan.md` | 提供 canonical execution workflow contract、review loop、與 exact artifact paths |
| `spec.md` | 凍結 implement-plan workflow acceptance criteria、behavioral scenarios、error / edge handling boundaries |
| `step.md` | 提供 implement-plan workflow 與後續 implementation handoff 的 topic-local completion gate |

## Evidence inventory

可用且應優先使用的 direct path evidence：

- `docs/api-endpoints/swagger-spec/models-spec.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `docs/api-endpoints/markdown-reference/README.md`
- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`

可用但不得升格成 direct-path positive oracle 的 evidence：

- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
- `docs/api-endpoints/markdown-reference/SASCTL_MLOPS_OPERATIONS.md`
- local `sasctl` source inventory for `ModelRepository`

precedent-only evidence：

- `tests/unit/request_contract/models_request_gate/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `tests/unit/request_contract/job_requests_jobs_request_gate/**`

## Endpoint family map

- In scope family：`modelRepository/models/content / get_model_content`
- Adjacent family：`modelRepository/models / list_models`
- Adjacent family：`modelRepository/models / get_model`
- Explicitly excluded family：`modelRepository/projects/**`
- Explicitly excluded family：`jobExecution/**`
- Explicitly excluded family：`casManagement/**`

Boundary rule：

- 本 topic 不得與 `modelRepository/models` 其他 API 併批
- `modelRepository/models/content` 只處理 direct content GET，不吸收 list-follow 或
  HATEOAS resolution topic

## Request contract draft

- Method：`GET`
- Path：`/modelRepository/models/{modelId}/contents/{fileId}/content`
- Path params：
  - `modelId`：required，string
  - `fileId`：required，string
- Query params：`{}`
- Request body：`None`
- Required header subset：
  - `If-Range: ""`
  - `Range: ""`
  - `Access-Quarantine: ""`
  - `Authorization: Bearer {token}`
- Explicit execution rule：
  - exactly one outbound request

## Response-handling boundary

- 後續 request-contract gate 不驗 response payload semantics
- 不驗 `.json` / `.sas` / `.csv` file-type behavior
- 不驗 host、query order、transport-generated headers、timeout、auth proof、retries
- `get_model_content.mock-responses.json` 只作為 harness 執行輔助，不升格為 response contract

## Implementation strategy for the future Implementer

後續 `Implementer` 應採用：

- `abstract repository evidence`
- `request-only`
- `single outbound request`
- `new isolated topic-local test directory`

不允許採用：

- `ModelRepository.get_model_contents()` positive invocation
- `src/**` fallback implementation
- 回寫既有 `models_request_gate/**`

## Risk classification

- Classification：`medium`
- Reasons：
  - direct path 存在於 swagger / markdown，但 `sasctl` 無 direct positive entry
  - `SASCTL_ALIGNMENT.md` 與 local source 之間存在 oracle 邊界，需要明寫不混用
  - adjacent `models_request_gate/**` precedent 容易被誤當成可修改 surface

## Stop flags

- `hateful_follow_required: true`
  - 理由：若 direct GET 不能單獨成立，topic 必須 `blocked`
- `write_scope_drift: true`
  - 理由：任何超出 write set 的需求都不允許自動擴張
- `shared_workflow_reopen: true`
  - 理由：不得重開 shared workflow semantics
- `response_semantics_scope_drift: true`
  - 理由：不得把 file-type / payload behavior 混入本 topic
- `precedent_surface_edit: true`
  - 理由：既有 `models_request_gate/**`、`projects_request_gate/**` 只可參考

## Human-review notes

- `SASCTL_ALIGNMENT.md` 的完整對齊說法只可視為 alignment summary，不是 direct-path oracle
- local `sasctl` source inventory 的證據只用來排除 `get_model_contents()` positive entry
- shared board 的 file-type hint 不適用於本 topic；以 locked decision exclusion 為準

## Requirement-to-technical mapping

| Requirement | Technical realization |
| --- | --- |
| Endpoint boundary 凍結 | `requirements.md` scope、inventory、extreme-boundary checks |
| Positive entry 凍結 | `technical-spec.md` evidence boundary 與 stop flags |
| Request contract 凍結 | `spec.md` acceptance criteria + `plan.md` implementation steps |
| Non-goals 清楚 | `requirements.md` non-goals + `technical-spec.md` response boundary |
| Write set 精確 | `plan.md` artifact paths + `technical-spec.md` allowed file scope |
| Workflow boundary 清楚 | `plan.md` locked decisions + status / allowed transitions |

## Required technical tasks

1. author `analysis/request-gate-models-content/requirements.md`，凍結 single-endpoint scope、
   direct-path-only rule、required header subset、non-goals、與 stop rules
2. author `analysis/request-gate-models-content/technical-spec.md`，凍結 evidence boundary、
   allowed file scope、future implementation strategy、risk、與 stop flags
3. author `plan/request-gate-models-content/request-gate-models-content.plan.md`，以 canonical
   required sections 凍結 implement lane、artifact paths、draft-plan commit、review routing、
   `needs-rework` fix loop、與 reviewer handoff
4. author `plan/request-gate-models-content/request-gate-models-content.spec.md`，凍結
   implement-plan workflow 的 acceptance criteria、behavioral scenarios、與 edge-case boundaries
5. author `plan/request-gate-models-content/request-gate-models-content.step.md`，建立後續
   implement-plan workflow 的 pending completion gate，並在 reviewer 通過後停在
   `human-check`

## Deferred prerequisites and explicit non-work

以下事項在本 topic 明確 defer：

- `tests/unit/request_contract/models_content_request_gate/**` 的實際建立
- draft-plan commit 之後的 request-contract implementation
- `src/**`
- shared workflow board edits
- shared workflow contract edits
- file-type response contract
- 相鄰 endpoint family

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo language default | compatible | analysis / plan 以繁體中文撰寫 |
| Shared-authority isolation | compatible | shared workflow docs 只保留背景 authority，不作 active topic-contract basis |
| Production boundary | compatible | `src/**` 明確 out of scope |
| Topic isolation | compatible | 單一 endpoint、單一 future implementation root |

## Validation

必要檢查：

1. 五個 topic-local artifacts 存在於 exact paths：
   - `analysis/request-gate-models-content/requirements.md`
   - `analysis/request-gate-models-content/technical-spec.md`
   - `plan/request-gate-models-content/request-gate-models-content.plan.md`
   - `plan/request-gate-models-content/request-gate-models-content.spec.md`
   - `plan/request-gate-models-content/request-gate-models-content.step.md`
2. `plan.md` 使用 canonical required sections，且不加入 `Stable library metadata`
3. `spec.md` 只定義 request-only acceptance，不混入 response payload semantics
4. `step.md` 的 `## Implementation Steps` 與 `plan.md` 一一對齊，且初始化為 pending
5. 所有 artifacts 都明確寫出：
   - 不得把 `ModelRepository.get_model_contents()` 當正向入口
   - future implementation root 只限
     `tests/unit/request_contract/models_content_request_gate/**`
   - `docs/request-shape-priority-workflow/**`、`src/**`、`pyproject.toml`、`uv.lock`、
     `models_request_gate/**`、`projects_request_gate/**` 均不在可寫範圍內
6. `step.md` 明確表達：
   - `plan-authoring`
   - `draft-plan-commit`
   - `plan-review`
   - `plan-review-fix-loop`
   - `human-check`
7. `plan.md`、`spec.md`、`requirements.md`、`technical-spec.md` 對 review fix loop 的語意一致

## Stop conditions

若出現以下情況，必須停止並回到 `blocked` 或 `needs-rework`：

- direct GET 無法獨立成立，必須退回 HATEOAS follow
- implement-plan artifacts 完成前被要求進 implementation
- implementation 需要碰 write set 以外檔案
- reviewer 指出 scope drift / contract drift / workflow drift
- 有人要求把 shared workflow semantics 納回可寫範圍
