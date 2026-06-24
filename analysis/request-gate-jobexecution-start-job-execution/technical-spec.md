# request-gate-jobexecution-start-job-execution technical spec

## Allowed Write Scope

本 topic 的 implementation write scope 僅限下列 surfaces：

- `analysis/request-gate-jobexecution-start-job-execution/requirements.md`
- `analysis/request-gate-jobexecution-start-job-execution/technical-spec.md`
- `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.plan.md`
- `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.step.md`
- `tests/unit/request_contract/job_requests_jobs_request_gate/**`

implementation write priority：

1. `tests/unit/request_contract/job_requests_jobs_request_gate/**`
2. topic-local `analysis/` artifacts
3. topic-local `plan/` artifacts

除非另有獨立 re-plan，任何 `src/**` 觸碰都直接構成 blocker。

## Implementation Responsibilities

- 在 `tests/unit/request_contract/job_requests_jobs_request_gate/**` 內建立或更新
  `start_job` request-only gate 所需的 request-contract artifacts
- 只驗證 request semantics，例如 method、path、required header subset、body shape、
  與已確認的 request-side invariants
- 維持 topic-local analysis 與 plan artifacts 和實際執行邊界一致
- 不將 execution 成果解讀為 `jobExecution/jobs`、`jobExecution/jobs/state`、
  polling、或 state gate 的授權

## Evidence Inventory

本 topic 可依賴的證據只可用下列抽象類別表述：

- repository 內既有的 job execution swagger request definitions
- repository 內既有的 request-shape markdown alignment 與 endpoint reference 摘要
- 上游 planning topic 已凍結的 `start_job` request-only baseline
- human-confirmed external source evidence

證據使用限制：

- 不得在 repo artifacts 中記錄任何 physical path、absolute path、或 local filesystem path
- 若既有抽象證據不足以支持 implementation decision，必須停在 blocker，
  不得自行發明新的 request contract

## Stop Flags

- 若工作漂移到 `jobExecution/jobs`，停止
- 若工作漂移到 `jobExecution/jobs/state`，停止
- 若工作納入 polling 或 state gate，停止
- 若工作修改 `docs/request-shape-priority-workflow/**` 或 shared workflow board，停止
- 若工作需要 `src/**` 變更，停止並標記為 separate re-plan blocker
- 若工作需要 `pyproject.toml`、`uv.lock`、或其他非允許 surface，停止
- 若工作企圖把抽象外部證據具體化為 physical path 或 local filesystem reference，停止

## Acceptance Gate

implementation 只能在下列條件成立時進入 review-ready：

- request-only gate 完整限定在 `start_job`
- 實作寫入面以 `tests/unit/request_contract/job_requests_jobs_request_gate/**` 為中心，
  且沒有越界到未授權 surfaces
- topic-local artifacts 與 implementation boundary 保持一致
- 沒有任何 `src/**` 變更
- 沒有任何 scope expansion 到 `jobExecution/jobs`、`jobExecution/jobs/state`、
  polling、state gate、或 shared workflow board

若 acceptance gate 失敗，topic 必須停在 `BLOCKED` 或回到 re-plan，
不得以例外方式放行。
