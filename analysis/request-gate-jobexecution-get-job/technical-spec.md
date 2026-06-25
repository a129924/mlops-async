# Request Gate JobExecution Get Job Technical Spec

## Source requirements

本技術規格對應下列需求來源：

- `analysis/request-gate-jobexecution-get-job/requirements.md`

repo-local governance 約束：

- `AGENTS.md`

## Goal

把 `GET /jobExecution/jobs/{jobId}` 的 bounded baseline 收斂回 `request-shape / shape-only`
contract，只授權 `tests/unit/request_contract/job_execution_jobs_request_gate/**` 作為 primary
implementation surface；不重開 `src/*`、typed-response tests、`start_job`、
`jobExecution/jobs/state`、或 polling/state gate。

## Active contract basis

本 topic 的 active contract basis 只包含：

- `analysis/request-gate-jobexecution-get-job/requirements.md`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`
- 最新 staged 的
  `tests/unit/request_contract/job_execution_jobs_request_gate/**` request-contract surface

下列 shared surfaces 只可作為背景參照，不得作為 current scope、status、或 completion
gate 的 active authority：

- `docs/request-shape-priority-workflow/**`
- shared workflow board
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`

## Current state summary

目前 repo / worktree 已有：

- `jobExecution/jobs` 與 `jobExecution/jobs/state` 的 swagger / markdown surfaces
- `tests/unit/request_contract/models_request_gate/**` 與
  `tests/unit/request_contract/projects_request_gate/**` 作為 request-gate precedent
- 已 materialize 的 request-shape surface：
  - `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json`
- 最新 staged reality 同時包含：
  - 上述 5 個 request-contract files
  - `analysis/request-gate-jobexecution-get-job/requirements.md`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`

active repo 另有但不屬於本 topic：

- `src/mlops_async/_api/job_execution_jobs.py`
- `tests/unit/test_job_execution_jobs_api.py`
- `tests/contracts/__init__.py`
- `tests/contracts/test_import_contract_http_client_module_path.py`

## Allowed file scope

本 topic 的 creator-owned primary implementation surface 為：

- `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
- `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
- `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json`

本 topic 的 topic-local contract surface 為：

- `analysis/request-gate-jobexecution-get-job/requirements.md`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`

本次 repair pass 的實際 write boundary 僅限下列 4 個 topic-local artifacts；這是
repair boundary，不是 latest staged reality 的完整檔案集合：

- `analysis/request-gate-jobexecution-get-job/requirements.md`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
- `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`

下列路徑在本 topic 中不得修改或不得作為 primary surface：

- `src/**`
- `tests/unit/test_job_execution_jobs_api.py`
- `tests/contracts/__init__.py`
- `tests/contracts/test_import_contract_http_client_module_path.py`
- `docs/request-shape-priority-workflow/**`
- shared workflow board / shared workflow contract
- 其他 `jobExecution` future topic artifacts

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結 endpoint inventory、shape-only boundary、與 human-check stop rules |
| `technical-spec.md` | 把需求映射成 shape-only execution contract、allowed scope、risk、與 stop rules |
| `plan.md` | 提供本 topic 的 canonical workflow contract |
| `step.md` | 提供本 topic 唯一的 topic-local shape-only completion gate |
| request-contract files | 鎖定 method、path、required header subset、query、與 body 的 request-only gate |
| `tests/contracts/__init__.py` | reference-only contract baseline，不是 creator-owned implementation surface |
| `tests/contracts/test_import_contract_http_client_module_path.py` | reference-only import precedent，不是 creator-owned implementation surface |

## Endpoint family map

- In scope family：`jobExecution/jobs / get_job`
- Adjacent family：`jobExecution/jobRequests/jobs / start_job`
- Boundary-only family：`jobExecution/jobs/state / get_job_state`

Boundary rule：

- `get_job` 不得與 `start_job` 或 `get_job_state` 併批
- `jobExecution/jobs/state` 只可作為 boundary reference，不可在本 topic 內吸收 polling、
  state gate、或 stop condition implementation

## Request contract draft

- Method：`GET`
- Path：`/jobExecution/jobs/{jobId}`
- Path params：
  - `jobId`：required，string
- Query params：none
- Request body：none
- Required headers：
  - `Authorization: Bearer {token}`
  - `Accept: application/vnd.sas.job.execution.job+json, application/vnd.sas.job.execution.job.request+json, application/vnd.sas.error+json, application/json`
- Explicit negative shape constraints in latest staged gate：
  - `Delegate-Domain` 不出現在 outbound request headers
  - `Content-Type` 不出現在 outbound request headers，因本 endpoint 無 request body
- Source-doc-present but not promoted：
  - `Delegate-Domain`
    - source-doc-present，但本 shape-only topic 不把它升格為 required 或 emitted header
- Auth behavior：Bearer token required

## Response-handling boundary

- `get_job.mock-responses.json` 只需提供足夠資料讓 request-shape harness 完成呼叫
- 本 topic 不驗證 typed job document decoding
- latest staged request-contract test 只保留最小 decoded-result 驗證：
  - `result.id`
  - `result.state`
- 上述最小 decoded-result 驗證只用來確認 harness 可完成既有 decode path，不構成
  typed-response behavior acceptance contract
- staged request-contract 測試若出現對 mock response 欄位的最小讀取，只視為 harness
  執行輔助，不構成 typed-response behavior acceptance contract
- 本 topic 不建立 invalid JSON、non-object success payload、或 missing-required-fields
  的 typed-response rejection matrix
- `tests/unit/test_job_execution_jobs_api.py` 維持 adjacent but out-of-scope

## Risk classification

- Classification：`medium`
- Reasons：
  - method / path / path param 在 swagger 中清楚
  - `jobExecution/jobs` 與 `jobExecution/jobs/state` 相鄰，需強化 boundary 防漂移
  - active repo 已有 `src/*` 與 typed-response tests，需明確避免 topic 回擴

## Stop flags

- `polling_job_wait: true`
  - 理由：本 endpoint 容易被誤擴成 polling/state topic
- `state_topic_scope_drift: true`
  - 理由：`jobExecution/jobs/state` 只保留 adjacent boundary，不得回收進本 topic
- `src_scope_reopen: true`
  - 理由：human re-scope 已把 `src/*` 排除在 topic 外
- `typed_response_scope_reopen: true`
  - 理由：`tests/unit/test_job_execution_jobs_api.py` 已被明確移出 topic
- `reference_surface_promotion: true`
  - 理由：`tests/contracts/**` 只可參考，不可升格為 primary gate
- `shared_authority_reactivation: true`
  - 理由：shared workflow / queue surfaces 不得重新成為 active topic-contract basis

## Human-review notes

- `sasctl.ScoreExecution.get_score_execution_results()` 只能作為 adjacent precedent，不得當作
  direct source authority
- `src/mlops_async/_api/job_execution_jobs.py` 與 `tests/unit/test_job_execution_jobs_api.py`
  雖存在於 active repo，但不屬於本 topic 的 shape-only contract
- `Delegate-Domain` 對 GET detail endpoint 的 requiredness 只保留 source-doc wording，不自行擴張
- shared workflow / queue surfaces 若仍被提及，只代表背景脈絡，不代表本 topic 的 active
  contract authority

## Requirement-to-technical mapping

| Requirement | Technical realization |
| --- | --- |
| Endpoint inventory 完整 | `requirements.md` 的 inventory 與 contradiction sections |
| Primary implementation surface 精確 | `technical-spec.md` 的 allowed file scope 與 `plan.md` artifact paths |
| Queue / boundary freeze | `technical-spec.md` 的 family map、risk、stop flags、validation |
| Request contract 鎖定 | `tests/unit/request_contract/job_execution_jobs_request_gate/**` |
| Response handling 維持 shape-only | `technical-spec.md` 的 response boundary 與 `plan.md` exclusions |
| Reference-only boundary 清楚 | `technical-spec.md` 的 out-of-scope / reference-only declarations |
| Completion gate 對齊 shape-only pass | `plan.md` 的 workflow status 與 `step.md` 的 `## Implementation Steps` |

## Required technical tasks

1. 維持 `tests/unit/request_contract/job_execution_jobs_request_gate/` 為 request-only gate，
   只驗證 method、path、required header subset、query、與 body semantics，並保留
   `Delegate-Domain` / `Content-Type` 不出現在 outbound request headers 的 negative shape
   constraints
2. 維持
   `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
   與 `get_job.mock-responses.json` 為 request-shape evidence / harness fixture，且只允許
   `result.id` / `result.state` 的最小 decoded-result 驗證，而非 typed-response gate
3. 維持 topic-local analysis / plan artifacts 與上述 request-shape surface 的 scope、
   status、與 step-tracker alignment 一致
4. 維持 `tests/contracts/**` 為 reference-only，且不把 `src/*` 或
   `tests/unit/test_job_execution_jobs_api.py` 納回本 topic

## Deferred prerequisites and explicit non-work

以下事項在本 topic 明確 defer：

- `src/**`
- `tests/unit/test_job_execution_jobs_api.py`
- `start_job`
- `get_job_state`
- polling / state gate contract
- 其他 `jobExecution/**` client / wrapper implementation
- shared workflow board / queue artifact changes
- shared workflow contract changes

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo language default | compatible | analysis / plan 以繁體中文撰寫 |
| Shared-authority isolation | compatible | topic contract 由 topic-local artifacts 與 staged request gate 驅動，不由 shared queue/workflow surfaces 決定 |
| Production boundary | compatible | `src/*` 不在本 topic primary surface 內 |
| Topic isolation | compatible | 只保留 request-contract surface 與 topic-local artifacts |

## Validation

必要檢查：

1. `tests/unit/request_contract/job_execution_jobs_request_gate/` primary surface 存在：
   - `__init__.py`
   - `conftest.py`
   - `test_get_job_request_contract.py`
   - `fixtures/get_job.request-flow.json`
   - `fixtures/get_job.mock-responses.json`
2. topic-local artifacts 明確寫出：
   - `src/**` out of scope
   - `tests/unit/test_job_execution_jobs_api.py` out of scope
   - `tests/contracts/__init__.py` 與
     `tests/contracts/test_import_contract_http_client_module_path.py`
     是 reference-only
   - `jobExecution/jobs/state` 是 boundary，不是 in-scope deliverable
3. `plan.md` 使用 canonical required sections，且 `Reviewer Handoff` 是單一 JSON object
4. `step.md` 的 `## Implementation Steps` 對齊 shape-only pass，而不是 `src/*` 或
   typed-response implementation pass
5. topic-local artifacts 明確寫出 latest staged gate 已包含：
   - `Delegate-Domain` / `Content-Type` 不出現在 outbound request headers
   - `result.id` / `result.state` 的最小 decoded-result 驗證
6. topic 內未建立 `spec.md`
7. 本次 repair pass 未編輯 `src/**` 或 `tests/**`
8. 最新 staged reality 明確包含 request-contract test surface；本次 repair pass 只同步
   4 個 topic-local artifacts 與該 reality 對齊，不得把 typed-response behavior 重新納入
   completion gate
9. shared workflow / queue surfaces 未被宣告為本 topic 的 active authority

## Stop conditions

若出現以下情況，必須停止並回到 `human-check`：

- 要求擴到 `src/**`
- 要求擴到 `tests/unit/test_job_execution_jobs_api.py`
- 要求把 `tests/contracts/**` 升格成 primary gate
- 要求擴到 `start_job`
- 要求擴到 `jobExecution/jobs/state`
- 要求把 polling / state gate 混入本 topic
- 要求把 shared workflow / queue surfaces 重新拉回 active topic-contract basis
- 要求修改 shared queue / workflow board
- 要求修改 shared workflow contract
