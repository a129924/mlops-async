# request-gate-jobexecution-start-job-execution requirements

## Frozen Business Baseline

本 execution topic 只承接 `start_job` 的 request-only gate implementation contract。
它授權後續 creator 在受限測試面建立 request-contract artifacts，驗證
`POST /jobExecution/jobRequests/{jobRequestId}/jobs` 的 `start_job` request shape，
但不授權擴張到其他 job execution surfaces，也不授權以 implementation convenience
為理由修改 production code。

## Request-only Scope

- 只處理 `POST /jobExecution/jobRequests/{jobRequestId}/jobs`
- 只處理 `start_job` 的 request semantics
- 只允許 request-only gate；不納入 response contract、polling、state gate、或後續 job detail surfaces
- implementation write set 優先且應集中在
  `tests/unit/request_contract/job_requests_jobs_request_gate/**`

## Allowed Implementation Boundary

- topic-local 分析與計畫 artifacts 可維持同步更新：
  - `analysis/request-gate-jobexecution-start-job-execution/requirements.md`
  - `analysis/request-gate-jobexecution-start-job-execution/technical-spec.md`
  - `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.plan.md`
  - `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.step.md`
- request-contract fixtures、helpers、tests 只可建立或修改於
  `tests/unit/request_contract/job_requests_jobs_request_gate/**`
- 若 implementation 需要碰 `src/**` 才能成立，必須立刻標記為 blocker，停止 topic，
  並要求 separate re-plan；不得自行擴 scope

## Non-goals

- 不擴到 `jobExecution/jobs`
- 不擴到 `jobExecution/jobs/state`
- 不納入 polling 或 state gate
- 不修改 `docs/request-shape-priority-workflow/**`
- 不修改 shared workflow board
- 不修改 `pyproject.toml` 或 `uv.lock`
- 不做 commit、publish、merge、release

## Evidence Boundary

- legacy baseline 已由人類確認，可視為 `human-confirmed external source evidence`
- repo artifacts 只能保留上述抽象結論，不得寫入任何 physical path、absolute path、
  或 local filesystem path
- 若後續 implementation 需要超出既有抽象證據邊界的新 source interpretation，
  必須先停下來請求人類確認

## Completion Gate

只有在下列條件同時成立時，本 topic 才可宣告 implementation completion：

- 完成物只覆蓋 `start_job` 的 request-only gate
- 寫入面仍受限於 topic-local artifacts 與
  `tests/unit/request_contract/job_requests_jobs_request_gate/**`
- 沒有任何 `src/**` 變更
- 沒有任何 `jobExecution/jobs`、`jobExecution/jobs/state`、polling、state gate、
  shared workflow board 或 docs workflow surface 的 scope expansion

若上述任一條件不成立，topic 狀態必須維持 `BLOCKED` 或回到 re-plan，
不得以部分完成宣告結案。
