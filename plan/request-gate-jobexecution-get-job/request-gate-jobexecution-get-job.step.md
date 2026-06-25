# Request Gate JobExecution Get Job Steps

## Implementation Steps

- [X] 1. `tests/unit/request_contract/job_execution_jobs_request_gate/` 已作為唯一 primary implementation surface 留在最新 staged reality，且 contract 只涵蓋 `GET /jobExecution/jobs/{jobId}` 的 method、path、required header subset、query、與 body semantics，並明確斷言 outbound request headers 不出現 `Delegate-Domain` 與 `Content-Type`。
- [X] 2. `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json` 與 `get_job.mock-responses.json` 已維持為 request-shape evidence / harness fixture；staged reality 只保留 `result.id` / `result.state` 的最小 decoded-result 驗證，任何對 mock response 欄位的最小讀取都不升格為 typed-response gate。
- [X] 3. topic-local analysis / plan artifacts 已與 shape-only scope 對齊，並明確把 `src/**`、`tests/unit/test_job_execution_jobs_api.py`、與 `tests/contracts/**` primary gate 排除在外；shared workflow / queue surfaces 只保留背景參照，不作為 active topic-contract basis。
- [X] 4. 已驗證本 topic 未重開 `start_job`、`get_job_state`、polling/state gate、shared workflow board、shared workflow contract、或其他未列出的路徑。
