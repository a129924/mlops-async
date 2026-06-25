# Request Gate Models Content Requirements

## Purpose

本文件凍結 `request-gate-models-content` 的需求基線，將本 topic 定義為
`modelRepository/models/content / get_model_content` 的 implement lane。
目前這一輪只把 implement lane 推進到 implement-plan workflow 的 `human-check` 前：
先完成 topic-local implement-plan artifacts、預留 draft-plan commit、進入 plan review、
支援 `needs-rework` fix loop、reviewer 通過後停在 `human-check`；本輪不落地
request-contract tests，也不擴張到其他 endpoint 或 shared workflow semantics。

## Scope

本 topic 涵蓋：

- `GET /modelRepository/models/{modelId}/contents/{fileId}/content`
- topic-local analysis / plan artifacts：
  - `analysis/request-gate-models-content/requirements.md`
  - `analysis/request-gate-models-content/technical-spec.md`
  - `plan/request-gate-models-content/request-gate-models-content.plan.md`
  - `plan/request-gate-models-content/request-gate-models-content.spec.md`
  - `plan/request-gate-models-content/request-gate-models-content.step.md`
- future primary implementation surface（本輪只凍結，不建立）：
  - `tests/unit/request_contract/models_content_request_gate/__init__.py`
  - `tests/unit/request_contract/models_content_request_gate/conftest.py`
  - `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py`
  - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json`
  - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json`

本 topic 不涵蓋：

- 任何其他 `modelRepository/models/**` endpoint
- `ModelRepository.get_model_contents()` 的 HATEOAS follow path
- file-type response semantics（`.json` / `.sas` / `.csv`）
- auth / CAS tables / `jobExecution` / champion / tables-link surface
- `docs/request-shape-priority-workflow/**`
- `src/**`
- `pyproject.toml`
- `uv.lock`
- `tests/unit/request_contract/models_request_gate/**`
- `tests/unit/request_contract/projects_request_gate/**`
- release / push / PR actions

## Actors and ownership

- Primary actor：後續 `Implementer`
- Secondary actor：後續 `Reviewer`
- Planning actor：本輪 topic-local analysis / plan artifact author
- Main Agent：後續 routing、review gate、publish、PR、merge orchestration

Ownership model：

- 本輪 write boundary 只限 topic-local analysis / plan artifacts
- 本輪 workflow boundary 只推進 implement lane 的 plan contract，不進 implementation
- future implementation write boundary 只限：
  `tests/unit/request_contract/models_content_request_gate/**`
- 任何超出上述 write set 的需求都必須先停下並回到 `blocked` 或 `needs-rework`

## Measurable requirements

1. **Endpoint boundary 必須完整凍結**
   - endpoint 固定為 `GET /modelRepository/models/{modelId}/contents/{fileId}/content`
   - queue 單位固定為 `modelRepository/models/content / get_model_content`
   - 不得擴到其他 endpoint 或 family

2. **Positive entry 必須凍結**
   - 第一輪只允許 direct path
   - 不得把 `ModelRepository.get_model_contents()` 當正向入口
   - 若後續 implementation 必須退回 `get_model_contents()` 或 HATEOAS follow，必須標記
     `blocked`

3. **Request contract 必須凍結**
   - 只驗證：
     - method = `GET`
     - path = `/modelRepository/models/{modelId}/contents/{fileId}/content`
     - query = `{}`
     - body = `None`
     - required header subset
   - required header subset 只允許：
     - `If-Range=""`
     - `Range=""`
     - `Access-Quarantine=""`
     - `Authorization: Bearer ...`
   - 明確要求單一 outbound request

4. **Non-goals 必須明確**
   - 不驗 response payload semantics
   - 不驗 host
   - 不驗 query order
   - 不驗 transport-generated headers
   - 不驗 timeout / auth proof / retries
   - 不驗 file-type behavior

5. **Implement plan write set 必須精確**
   - topic-local artifacts 需精確列出 exact paths
   - future implementation root 需凍結為
     `tests/unit/request_contract/models_content_request_gate/`
   - 不得把既有 `models_request_gate/**` 或 `projects_request_gate/**` 當成 edit target

6. **Evidence boundary 必須清楚**
   - repo-local swagger / markdown reference 可作為 direct path existence evidence
   - local `sasctl` source inventory 只證明 `/contents` list-follow pattern
   - `SASCTL_ALIGNMENT.md` 的完整對齊說法不得升格成 direct-path oracle

7. **Workflow boundary 必須清楚**
   - 本 topic 是 `non-stable`、`request-only`、`single-endpoint` 的 implement lane
   - `plan/agent-handoff-workflow.md` 與 `plan/topic-plan-contract.md` 維持 reusable shared
     workflow contract authority
   - shared board 與 shared workflow docs 只作為 queue/background authority
   - 本 topic 不修改 shared workflow files，也不重開 shared workflow semantics
   - 本輪節奏固定為：
     - 完成 implement-plan artifacts
     - draft-plan commit
     - plan review
     - `needs-rework` 時只在 topic-local plan artifacts 內修正
     - reviewer 通過後停在 `human-check`

## Endpoint inventory

### Swagger / OpenAPI inventory

- `docs/api-endpoints/swagger-spec/models-spec.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`

### Markdown reference inventory

- `docs/api-endpoints/markdown-reference/README.md`
- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
- `docs/api-endpoints/markdown-reference/SASCTL_MLOPS_OPERATIONS.md`

### Workflow / contract inventory

- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`

### Precedent inventory

- `tests/unit/request_contract/models_request_gate/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `tests/unit/request_contract/job_requests_jobs_request_gate/**`

### Local source inventory

- local `sasctl` source inventory for `ModelRepository`

## Contradictions surfaced and resolved

1. `SASCTL_ALIGNMENT.md` 把本 endpoint 對齊到 `ModelRepository.get_model_contents()`
   - Resolution：僅保留為 alignment summary；不得把它當成 direct-path positive oracle

2. 本機 `sasctl` source 沒有 direct `get_model_content()` 單步入口
   - Resolution：本 topic 採用 abstract repository evidence + future request-only gate，
     不以 `sasctl` direct invocation 作為成立前提

3. shared board injection hint 曾提到 file-type 後續判斷
   - Resolution：本 topic 以 locked decision 為準，直接排除 file-type response semantics

## Extreme-boundary checks

以下情況直接停止：

1. 要求把 `ModelRepository.get_model_contents()` 納為正向入口
2. 要求把 file-type response semantics 納回同 topic
3. 要求修改 `docs/request-shape-priority-workflow/**`
4. 要求修改 `src/**`
5. 要求修改 `pyproject.toml` 或 `uv.lock`
6. 要求回寫 `tests/unit/request_contract/models_request_gate/**`
7. 要求擴到 auth / CAS tables / `jobExecution` / champion / tables-link surface
8. 要求重開已凍結的 path / contract / architecture decision

## Assumptions

- topic 名稱固定為 `request-gate-models-content`
- shared board row `modelRepository/models/content / get_model_content` 目前為 `[ ]` / `03`
- endpoint 不屬於 `BLOCKED` 或 `OUT-OF-SCOPE`
- 本輪 deliverable 是 implement-plan artifacts 與 review-loop contract；
  request-contract test implementation 明確遞延到 `human-check` 之後

## Non-goals

- 不落地 `tests/unit/request_contract/models_content_request_gate/**`
- 不做 `src/**`
- 不做 shared workflow files
- 不做 `models_request_gate/**` 或 `projects_request_gate/**` 回寫
- 不做 file-type response contract
- 不做 release / push / PR

## Blockers

目前需求在 implement-plan workflow authoring 範圍內無 blocker。
若 draft-plan review loop 之外的工作企圖提前進 implementation，或後續 implementation 需要碰
write set 以外路徑，或 direct GET 不能獨立成立，必須升級為 `blocked`。

## Freeze status

Status: `FROZEN`

Current workflow state: reviewer 已通過 implement-plan re-review，topic 合法停在
`human-check`，等待下一輪明確授權才可進 implementation。
