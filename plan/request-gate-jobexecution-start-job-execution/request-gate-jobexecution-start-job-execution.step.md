# request-gate-jobexecution-start-job-execution — Step Tracking

## Implementation Steps

- [ ] 重新讀取本 topic artifacts 與上游 planning baseline，確認 `start_job` request-only boundary、無 shared board edit、以及 `src/**` blocker rule。
- [ ] 只在 `tests/unit/request_contract/job_requests_jobs_request_gate/**` 內建立或更新 `start_job` request-only gate 所需的 tests、fixtures、或 helpers。
- [ ] 僅為 `POST /jobExecution/jobRequests/{jobRequestId}/jobs` 的 `start_job` request semantics 建立 assertions，不得擴到 `jobExecution/jobs`、`jobExecution/jobs/state`、polling、或 state gate。
- [ ] 若 implementation 過程需要 `src/**`、shared workflow board、或其他未授權 surface，立刻停在 blocker 並要求 separate re-plan。
- [ ] 完成後確認 topic-local artifacts 與 bounded implementation 一致，再移到 `review-ready`。
