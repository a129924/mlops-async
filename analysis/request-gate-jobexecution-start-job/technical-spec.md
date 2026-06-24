# request-gate-jobexecution-start-job technical spec

## Allowed File Scope

本 topic 的 bounded write set 僅限下列四個檔案：

- `analysis/request-gate-jobexecution-start-job/requirements.md`
- `analysis/request-gate-jobexecution-start-job/technical-spec.md`
- `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.plan.md`
- `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.step.md`

禁止修改：

- `docs/request-shape-priority-workflow/**`
- `src/**`
- `tests/**`
- 任何其他 topic 的 `analysis/**` 或 `plan/**`
- shared workflow board 與 commit state

## Artifact Responsibilities

- `requirements.md`
  - 凍結 business baseline、scope、non-goals、blocked/out-of-scope 與 human-check boundary
- `technical-spec.md`
  - 凍結允許寫入範圍、artifact responsibilities、evidence inventory、risk/stop flags、
    deferred future test layout 與 implementation 前的人類確認點
- `request-gate-jobexecution-start-job.plan.md`
  - 作為本 topic 的 canonical planning contract，明示 strict analysis routing、
    locked decisions、exact artifact paths、canonical transitions、reviewer handoff JSON
    與 post-merge 無 release action
- `request-gate-jobexecution-start-job.step.md`
  - 作為 topic-local completion gate；只用 `## Implementation Steps` 的核取方塊表示
    planning handoff 是否完成

## Evidence Inventory

本 topic 可使用且應優先使用的證據：

- `docs/api-endpoints/swagger-spec/jobs-spec.yaml`
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
- `docs/api-endpoints/markdown-reference/ENDPOINTS_EXTRACTED.md`
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`

證據解讀結論：

- shared workflow board 已將 `jobExecution/jobRequests/jobs` / `start_job` 排在 order `08`
- shared workflow board 已將 `jobExecution/jobs/state` 保持 `BLOCKED`
- swagger/reference 已把 `start_job` 固定為
  `POST /jobExecution/jobRequests/{jobRequestId}/jobs`
- swagger/reference 已記錄 request body 為空 JSON 物件 `{}`，並附帶必要 headers 與已知
  header bug 說明

## External Evidence Boundary

- 人類已確認 legacy `start_job` source exists，且足以作為 request-shape baseline；
  repo artifacts 只能將此事實記錄為 `human-confirmed external source evidence`
- 任何 physical legacy source path 或 local filesystem path 都不得寫入 repo artifacts
- 在目前可見證據下，只能把 `SASCTL_ALIGNMENT.md` 中對
  `ScoreExecution.create_score_execution(...)` /
  `poll_score_execution_state(...)` /
  `get_score_execution_results(...)` 的對齊說明視為 repo-local precedent 摘要

## Deferred Future Test Layout

未來若進入 implementation topic，request-contract tests 的目錄名稱固定為：

- `tests/unit/request_contract/job_requests_jobs_request_gate/`

本 topic 只凍結命名與存在義務，不建立任何測試檔案。

## Risk / Stop Flags

- 若後續工作企圖把 scope 擴到 `jobExecution/jobs` 或 `jobExecution/jobs/state`，必須停止
- 若後續工作企圖把 polling / state gate 一併納入，必須停止
- 若後續工作企圖修改 `docs/request-shape-priority-workflow/checklist.md` 的 shared board，
  必須停止
- 若後續工作企圖把 human-confirmed external source evidence 寫成實體路徑或 repo-local
  已驗證檔案，必須停止
- 若後續工作企圖以未記錄的人類確認擴張 request-shape baseline 以外的 source 依據驅動
  implementation，必須停止
- 若後續工作漂移到四個 planning artifacts 以外，必須停止

## Human-check Handoff Condition

本 topic 的 human-check 已完成記錄。legacy source 的 surrogate evidence acceptability
blocker 已解除；後續只能以 `human-confirmed external source evidence` 的抽象表述保留此結論，
不得把 physical path 帶入 repo artifacts。本 topic 因此可進入 planner final gate，但仍不進入
implementation。
