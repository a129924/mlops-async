# request-gate-jobexecution-start-job requirements

## Frozen Business Baseline

本 topic 的唯一目標是為 `jobExecution/jobRequests/jobs` 的 `start_job` 建立 future
request-only gate 的 planning handoff。完成條件是 topic-local planning artifacts
齊備，並把後續執行者必須遵守的 request-shape 邊界、證據來源、停止條件與 human-check
停點明確凍結；本 topic 本身不進入 implementation。

## Scope

- 只處理 `POST /jobExecution/jobRequests/{jobRequestId}/jobs`
- 只處理 `start_job` 的 request shape 與其 planning handoff
- 只建立以下 topic-local artifacts：
  - `analysis/request-gate-jobexecution-start-job/requirements.md`
  - `analysis/request-gate-jobexecution-start-job/technical-spec.md`
  - `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.plan.md`
  - `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.step.md`
- 凍結未來 request-contract test layout 名稱：
  `tests/unit/request_contract/job_requests_jobs_request_gate/`

## Non-goals

- 不做 `src/**` implementation
- 不做 `tests/**` implementation
- 不做 commit、review、publish、merge 或 release 動作
- 不修改 `docs/request-shape-priority-workflow/**`
- 不擴到 `GET /jobExecution/jobs/{jobId}`
- 不擴到 `GET /jobExecution/jobs/{jobId}/state`
- 不把 polling / state gate 納入本 topic
- 不修改 shared workflow board 或任何其他 topic artifacts

## Blocked / Out-of-Scope

- `jobExecution/jobs/state` 仍受 shared workflow 的 `BLOCKED` policy 約束；沒有新的人類決策前不得納入
- `jobExecution/jobs` detail surface 與本 topic 分離，必須保留給獨立 topic
- 任何超出四個 planning artifacts 的檔案變更都屬 plan-alignment drift，必須停止並回到 human-check
- legacy `job_execution.py` source file 不在 repo 內，不能把該檔案視為已驗證證據

## Human-check Boundary

- implementation 前必須由人類確認：repo-local swagger/reference 與
  `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md` 是否足以作為
  `start_job` request gate 的 surrogate evidence
- implementation 前必須由人類確認：缺失的 legacy `job_execution.py` 是否接受以
  repo-local swagger/reference 取代，且不要求補驗原始 source
- 本 topic 完成後固定停在 human-check；不得直接前進到 execution topic
