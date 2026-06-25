# request-gate-jobexecution-start-job-execution — Step Tracking

## Implementation Steps

- [X] 重新讀取本 topic artifacts 與上游 planning baseline，確認 `start_job` request-only boundary、無 shared board edit、以及 `src/**` blocker rule。
- [X] 只在 `tests/unit/request_contract/job_requests_jobs_request_gate/**` 內建立或更新 `start_job` request-only gate 所需的 tests、fixtures、或 helpers。
- [X] 斷言僅限 `POST /jobExecution/jobRequests/{jobRequestId}/jobs` 的 `start_job` request semantics；不以 `timeout` 值、response status、payload、或 response-source fixture 作為 gate oracle，也不得擴到 `jobExecution/jobs`、`jobExecution/jobs/state`、polling、或 state gate。
- [X] 若 implementation 過程需要 `src/**`、shared workflow board、或其他未授權 surface，立刻停在 blocker 並要求 separate re-plan。
- [X] 完成本輪 creator rework 後，確認 topic-local artifacts 與 request-only gate 一致，且已移除 `timeout=180` hard gate/oracle，並以最窄 pytest 驗證通過後再移到 `review-ready`。
