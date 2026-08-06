# Job execution handoff

## Legacy observation

- Legacy 可 `POST /jobExecution/jobRequests/{id}/jobs` start，並有
  `GET /jobExecution/jobs/{id}` 與 `GET .../state` detail/state observations。

## Upstream/evidence

- repo 已納入 `docs/api-endpoints/swagger-spec/upstream/jobExecution-openapi.yml` 的
  official upstream OpenAPI evidence；repo-local mapping 為
  `docs/api-endpoints/swagger-spec/jobs-spec.yaml`。
- start gate 是 `repo-helper-direct-path` / `upstream-aligned`；detail/state gates 是
  `internal-wrapper-shape-only`，不能當 implementation truth。

## Current repo evidence

- `tests/unit/request_contract/job_requests_jobs_request_gate/` 有 start request gate。
- `job_execution_jobs_request_gate/` 與 `job_execution_jobs_state_request_gate/` 只有
  internal-wrapper shape baseline；沒有 runtime client。

## Difference

- start 的 request baseline 不能推導 polling、wait、state machine、timeout 或 response
  handling；detail/state 尚未有可實作的 authority。

## Disposition

- job start、detail/state 可進入 contract planning；這不授權 runtime implementation，
  compatibility、response 與 runtime contract 仍未決。

## Human decision required

- 是否需要 start 的 response/error contract；以及 detail/state 的可接受 source evidence。

## Target mapping
