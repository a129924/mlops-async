# Request Gate JobExecution Get Job State Requirements

## Purpose

本文件凍結 `request-gate-jobexecution-get-job-state` 的需求基線，將本 topic 明確定義成
`GET /jobExecution/jobs/{jobId}/state` 的 `request-shape / shape-only` topic。

本輪工作已先完成 canonical managed worktree creation，後續 topic-local analysis / plan 與
request-contract implementation 一律只在此 worktree 內落地。

## Current state summary

目前 worktree / branch 基線為：

- worktree：`../mlops-async.worktrees/agent-20260626-request-gate-jobexecution-get-job-state`
- branch：`feat/andrew/request-gate-jobexecution-get-job-state`
- base：`dev`

本 topic 的相鄰 repo-visible evidence 已存在：

- `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- `docs/request-shape-priority-workflow/checklist.md`
- `docs/api-endpoints/swagger-spec/jobs-spec.yaml`
- `docs/api-endpoints/swagger-spec/jobs-spec.json`
- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`

## Scope

本 topic 涵蓋：

- `GET /jobExecution/jobs/{jobId}/state` 的 endpoint inventory 與 direct evidence
- topic-local analysis / plan artifacts：
  - `analysis/request-gate-jobexecution-get-job-state/requirements.md`
  - `analysis/request-gate-jobexecution-get-job-state/technical-spec.md`
  - `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.plan.md`
  - `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.step.md`
  - `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.spec.md`
- primary implementation surface：
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/__init__.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.request-flow.json`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.mock-responses.json`

本 topic 不涵蓋：

- `src/**`
- `tests/unit/test_job_execution_jobs_api.py`
- `tests/contracts/**`
- 既有 `tests/unit/request_contract/job_execution_jobs_request_gate/**`
- `start_job`
- polling / wait loop / timeout policy / state machine
- shared workflow 文件的修改
- release / push / PR 動作

## Actors and ownership

- `Plan-Creator`
  - 建立本 topic 的 requirements / technical-spec / plan / step / spec artifacts
- `Code-Implementer`
  - 建立本 topic 的 request-contract harness、tests、與 fixtures
- `Code-Reviewer`
  - 審 request-contract implementation 與 code quality
- `Code-Tester`
  - 執行 pytest / pyright / ruff evidence collection
- `Main Agent`
  - 管理 worktree / publish / merge routing

## Measurable requirements

1. **Request contract 必須鎖定**
   - method 固定為 `GET`
   - path 固定為 `/jobExecution/jobs/{jobId}/state`
   - query 固定為 none
   - request body 固定為 none
   - required header subset 固定至少包含：
     - `Authorization: Bearer {token}`
     - `Accept: application/vnd.sas.job.execution.job+json, application/vnd.sas.job.execution.job.request+json, application/vnd.sas.error+json, application/json`

2. **Negative header constraints 必須明確**
   - `Delegate-Domain` 不得作為 required emitted header
   - `Content-Type` 不得作為 required emitted header

3. **Positive / negative cases 必須 bounded**
   - 正向 case 只允許 `direct_identifier`
   - `full_observed_flow` 長度固定為 `1`
   - 必須阻擋：
     - non-string identifier
     - dict-like identifier
     - blank identifier
     - unregistered request path
   - 不得新增 polling / wait / timeout variants

4. **Fixture boundary 必須最小化**
   - `get_job_state.request-flow.json` 只包含 `direct_identifier`
   - `get_job_state.mock-responses.json` 只作 harness scaffold
   - mock response JSON body 只需最小 `state`
   - 不建立 state transition matrix

5. **Boundary references 必須清楚**
   - topic-local plan 必須保留下列 boundary 引用：
     - `analysis/request-gate-jobexecution-get-job/technical-spec.md:117`
     - `analysis/request-gate-jobexecution-get-job/technical-spec.md:121`
     - `analysis/request-gate-jobexecution-get-job/technical-spec.md:122`
     - `analysis/request-gate-jobexecution-get-job/technical-spec.md:257`
     - `docs/request-shape-priority-workflow/checklist.md:45`

## Contradictions surfaced and resolved

1. `jobExecution/jobs/state` 很容易被誤擴成 polling / state machine topic
   - Resolution：本 topic 只保留單次 `GET /state` request shape；不建立 polling / wait / timeout 語意

2. `get_job` 與 `get_job_state` path 相鄰，容易被誤合併
   - Resolution：沿用 `get_job` technical spec 已凍結的 boundary 引用，不修改既有 `get_job` gate

3. 本輪 workflow 已要求 create worktree 先於任何檔案落地
   - Resolution：topic-local artifacts 與 request-contract tests 只在本 managed worktree 內建立

## Assumptions

- topic 名稱固定為 `request-gate-jobexecution-get-job-state`
- 沿用 `tests/unit/request_contract/job_execution_jobs_request_gate/` 的 harness pattern，但建立獨立 package `job_execution_jobs_state_request_gate/`
- 最小 decoded-result 驗證只需 `state`

## Non-goals

- 不做 `src/**`
- 不做 `tests/unit/test_job_execution_jobs_api.py`
- 不做 `tests/contracts/**`
- 不做 `get_job` 或 `start_job` 回收
- 不做 polling / wait / timeout / state machine
- 不做 shared workflow 文件的順手修補
- 不做 release / push / PR

## Blockers

本 topic 在目前範圍內無 execution blocker；若後續要求擴回 polling、`src/**`、
`tests/contracts/**`、或 shared workflow files，即立即升級為 `human-check`。

## Freeze status

Status: `FROZEN`
