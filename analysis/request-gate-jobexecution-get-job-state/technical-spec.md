# Request Gate JobExecution Get Job State Technical Spec

## Source requirements

本技術規格對應下列需求來源：

- `analysis/request-gate-jobexecution-get-job-state/requirements.md`

repo-local governance 約束：

- `AGENTS.md`

## Goal

把 `GET /jobExecution/jobs/{jobId}/state` 的 bounded baseline 收斂成獨立的
`request-shape / shape-only` contract，只授權
`tests/unit/request_contract/job_execution_jobs_state_request_gate/**` 作為 primary
implementation surface；不重開 `src/*`、typed-response tests、`get_job`、`start_job`、
或 polling/state gate。

## Active contract basis

本 topic 的 active contract basis 只包含：

- `analysis/request-gate-jobexecution-get-job-state/requirements.md`
- `analysis/request-gate-jobexecution-get-job-state/technical-spec.md`
- `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.plan.md`
- `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.step.md`
- `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.spec.md`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/**`

下列 shared / adjacent surfaces 只可作為背景參照，不得作為本 topic 的 active write set：

- `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- `docs/request-shape-priority-workflow/**`
- shared workflow 文件

## Allowed file scope

本 topic 的 creator-owned primary implementation surface 為：

- `tests/unit/request_contract/job_execution_jobs_state_request_gate/__init__.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.request-flow.json`
- `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.mock-responses.json`

本 topic 的 topic-local contract surface 為：

- `analysis/request-gate-jobexecution-get-job-state/requirements.md`
- `analysis/request-gate-jobexecution-get-job-state/technical-spec.md`
- `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.plan.md`
- `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.step.md`
- `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.spec.md`

下列路徑在本 topic 中不得修改或不得作為 primary surface：

- `src/**`
- `tests/unit/test_job_execution_jobs_api.py`
- `tests/contracts/**`
- `tests/unit/request_contract/job_execution_jobs_request_gate/**`
- `tests/unit/request_contract/job_requests_jobs_request_gate/**`
- shared workflow 文件

## Endpoint family map

- In scope family：`jobExecution/jobs/state / get_job_state`
- Adjacent family：`jobExecution/jobs / get_job`
- Adjacent family：`jobExecution/jobRequests/jobs / start_job`

Boundary rule：

- `get_job_state` 不得與 `get_job` 或 `start_job` 併批
- `polling / wait / timeout / state machine` 只可作為 boundary reference，不可在本 topic 內吸收

## Boundary references to preserve

- `analysis/request-gate-jobexecution-get-job/technical-spec.md:117`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md:121`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md:122`
- `analysis/request-gate-jobexecution-get-job/technical-spec.md:257`
- `docs/request-shape-priority-workflow/checklist.md:45`

## Request contract draft

- Method：`GET`
- Path：`/jobExecution/jobs/{jobId}/state`
- Path params：
  - `jobId`：required，string
- Query params：none
- Request body：none
- Required headers：
  - `Authorization: Bearer {token}`
  - `Accept: application/vnd.sas.job.execution.job+json, application/vnd.sas.job.execution.job.request+json, application/vnd.sas.error+json, application/json`
- Explicit negative shape constraints：
  - `Delegate-Domain` 不出現在 outbound request headers
  - `Content-Type` 不出現在 outbound request headers

## Response-handling boundary

- `get_job_state.mock-responses.json` 只需提供足夠資料讓 request-shape harness 完成呼叫
- mock response 最小 JSON body 只需 `state`
- 本 topic 不驗證 state transition matrix
- 本 topic 不建立 polling / wait / timeout oracle
- 最小 decoded-result 驗證只保留：
  - `result.state`

## Test contract

必要 cases：

1. `direct_identifier`
   - 單一步驟 source-observed flow
   - path 固定為 `/jobExecution/jobs/job-id-abc-123/state`
2. blocked variants：
   - non-string identifier
   - dict-like identifier
   - blank identifier
3. fast-fail variant：
   - unregistered request path 以 `Unexpected outbound request` 失敗

## Risk classification

- Classification：`medium`
- Reasons：
  - endpoint path 與 `get_job` 相鄰，易產生 boundary drift
  - swagger description 會自然引導到 polling 語意，需明確排除
  - 本 topic 同時需要 endpoint plan 與 Python request-contract implementation，必須避免 scope 漂移

## Stop flags

- `polling_scope_drift: true`
  - 理由：本 endpoint 容易被誤擴成 polling / wait topic
- `src_scope_reopen: true`
  - 理由：human scope 已明確把 `src/**` 排除
- `get_job_gate_reopen: true`
  - 理由：本 topic 建立獨立 package，不回收既有 `get_job` gate

## Validation

必要檢查：

1. `tests/unit/request_contract/job_execution_jobs_state_request_gate/` primary surface 存在：
   - `__init__.py`
   - `conftest.py`
   - `test_get_job_state_request_contract.py`
   - `fixtures/get_job_state.request-flow.json`
   - `fixtures/get_job_state.mock-responses.json`
2. topic-local artifacts 明確寫出：
   - `src/**` out of scope
   - `tests/unit/test_job_execution_jobs_api.py` out of scope
   - `tests/contracts/**` out of scope
   - `get_job` / `start_job` / polling / timeout 只作 boundary
3. request-contract 測試明確驗證：
   - method / path / query / body
   - `Authorization` / `Accept`
   - `Delegate-Domain` / `Content-Type` 不出現在 headers
   - non-string / dict-like / blank identifier 被阻擋
   - unregistered request path fast-fail
4. validation commands 固定為：
   - `uv run pytest tests/unit/request_contract/job_execution_jobs_state_request_gate -q`
   - `uv run pyright tests/unit/request_contract/job_execution_jobs_state_request_gate`
   - `uv run ruff check tests/unit/request_contract/job_execution_jobs_state_request_gate`

## Stop conditions

若出現以下情況，必須停止並回到 `human-check`：

- 要求擴到 polling / wait / timeout / state machine
- 要求擴到 `src/**`
- 要求擴到 `tests/unit/test_job_execution_jobs_api.py`
- 要求擴到 `tests/contracts/**`
- 要求把 `get_job` 或 `start_job` 回收進同 topic
- 要求修改 shared workflow 文件作為本 topic 的順手修補
