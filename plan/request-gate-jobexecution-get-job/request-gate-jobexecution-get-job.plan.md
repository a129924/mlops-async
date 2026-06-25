> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-gate-jobexecution-get-job/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-gate-jobexecution-get-job/requirements.md`
> - 本 plan 100% 對齊最新 shape-only analysis layer，不重開 `start_job`、
>   `jobExecution/jobs/state`、polling/state gate、shared workflow board、或 shared
>   workflow contract。
> - 最新 staged reality 已包含 request-contract test surface；本次 repair pass 只修補
>   topic-local artifacts，讓 repo-visible contract 與既有 staged shape-only work 對齊。
> - shared workflow / queue surfaces 只保留背景脈絡，不作為本 topic current scope、
>   status、或 completion gate 的 active authority。

## Goal / Outcome

- 讓 `request-gate-jobexecution-get-job` 回到可執行的 `request-shape / shape-only`
  topic contract
- 讓 creator 後續工作只聚焦於
  `tests/unit/request_contract/job_execution_jobs_request_gate/**`
- 讓 reviewer 可依本 plan 與 analysis artifacts 驗證：
  - scope 只涵蓋 `GET /jobExecution/jobs/{jobId}` 的 request shape
  - `src/**` 與 `tests/unit/test_job_execution_jobs_api.py` 明確維持 out of scope
  - `tests/contracts/**` 只維持 reference-only

## Scope

- **In scope**:
  - `analysis/request-gate-jobexecution-get-job/requirements.md`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json`

- **Out of scope**:
  - `src/**`
  - `tests/unit/test_job_execution_jobs_api.py`
  - 把 `tests/contracts/**` 當成 primary implementation surface
  - `start_job`
  - `jobExecution/jobs/state`
  - polling / state gate
  - `docs/request-shape-priority-workflow/**`
  - shared workflow board edits
  - shared workflow contract edits
  - package-root re-export
  - release / push / PR actions
  - 任何未列出的 `tests/**`

## Locked Decisions

- 本 topic 是 **request-shape / shape-only topic with no stable-library surfaces**；
  stable-library intent 明確 absent，不需要 `## Stable library metadata`
- primary implementation surface 鎖定為：
  - `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json`
- `tests/contracts/__init__.py` 與
  `tests/contracts/test_import_contract_http_client_module_path.py`
  只可作為 reference，不可升格為 primary gate
- `src/**` 與 `tests/unit/test_job_execution_jobs_api.py` 明確不屬於本 topic
- endpoint 邊界鎖定為 `jobExecution/jobs / get_job`；不得順手擴到 `start_job` 或
  `jobExecution/jobs/state / get_job_state`
- request contract 鎖定為：
  - method `GET`
  - path `/jobExecution/jobs/{jobId}`
  - no query params
  - no request body
  - required header subset only `Authorization` and `Accept`
- latest staged shape-only gate 另明確鎖定 outbound request headers：
  - `Delegate-Domain` 不出現
  - `Content-Type` 不出現
- `get_job.mock-responses.json` 只作為 request-shape harness fixture，不代表 typed-response
  gate
- latest staged request-contract test 只保留最小 decoded-result 驗證：
  - `result.id`
  - `result.state`
- staged request-contract 測試若為了讓 harness 可執行而讀取 mock response 欄位，也不代表
  本 topic 重新承擔 typed-response behavior validation
- shared workflow / queue surfaces 不作為本 topic active contract basis；topic contract
  只由 topic-local artifacts 與最新 staged request-contract surface 決定

## Boundaries / Exclusions

- Planning actor 在本次 pass 只負責 topic-local analysis / plan contract 修補
- Creator 的後續工作只限於本 plan `Scope` 與 `Artifact Paths` 列出的 request-contract
  surface
- Reviewer 只負責獨立驗證 request-shape 與 contract alignment，不得在審查期間重開 topic
  邊界
- Main Agent 負責後續 routing、publish、PR、merge orchestration
- shared workflow board 與 shared workflow contract 不得作為本 topic 的編輯目標，也不得
  被引用成 active topic-contract basis
- 若後續工作漂移到未列 path，視為 plan-alignment failure，必須先回到 `human-check`

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this
  topic stops at `merged` and does not declare a release action
- **Step-tracker alignment**:
  `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md` 的
  `## Implementation Steps` 對齊 shape-only request gate；latest staged request-contract
  surface 與本次 topic-local artifact repair 已完成，因此目前可再次送交 reviewer
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- `human-check` 只作為 topic 外部 stop boundary；它不是 workflow status，也不是 allowed
  transition
- 本次 repair pass 僅修補 4 個 topic-local artifacts；request-contract test surface 代表
  最新 staged implementation reality，但不屬於本次 edit boundary
- 本 topic 不建立 `review-log`；單輪 reviewer verdict 可直接透過 canonical
  `Reviewer Handoff` JSON 路由
- 本 topic 不宣告 round cap

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-jobexecution-get-job/requirements.md` | Planning actor | Business-intent guardrail and shape-only boundary baseline |
| Topic technical spec | `analysis/request-gate-jobexecution-get-job/technical-spec.md` | Planning actor | Execution-facing source of truth for this topic |
| Topic plan | `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md` | Planning actor | Repo-visible workflow contract for this topic |
| Topic step tracker | `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md` | Creator | Machine-readable completion gate for shape-only work |
| Request gate package marker | `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py` | Creator | Package anchor for the topic-local request-contract surface |
| Request gate harness | `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py` | Creator | Request capture and request-shape assertion harness |
| Request gate test | `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py` | Creator | Request-only gate for method, path, header subset, query, and body semantics |
| Request-flow evidence | `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json` | Creator | Source-observed request evidence for direct identifier `get_job` |
| Mock-response fixture | `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.mock-responses.json` | Creator | Harness fixture that supports request-shape execution without reopening typed-response scope |
| Reference-only contract package | `tests/contracts/__init__.py` | Creator | Reference-only contract surface; not a primary gate in this topic |
| Reference-only import contract | `tests/contracts/test_import_contract_http_client_module_path.py` | Creator | Reference-only precedent; not a primary gate in this topic |

Artifact path notes:

- `README.md`: no change in this topic
- `VERSION`: no change in this topic
- `.github/copilot-instructions.md`: no change in this topic
- `src/**`: out of scope for this topic
- `tests/unit/test_job_execution_jobs_api.py`: out of scope for this topic
- `docs/request-shape-priority-workflow/**`: no change in this topic
- 若出現未列路徑的變更，視為 plan-alignment problem，必須先停止並回到 `human-check`

## Implementation Steps

1. 將 `tests/unit/request_contract/job_execution_jobs_request_gate/` 維持為唯一 primary
   implementation surface，只驗證 `GET /jobExecution/jobs/{jobId}` 的 method、path、
   required header subset、query、與 body semantics，並保留 `Delegate-Domain` /
   `Content-Type` 不出現在 outbound request headers 的 negative shape constraints
2. 維持
   `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json`
   與 `get_job.mock-responses.json` 為 request-shape evidence / harness fixture；只保留
   `result.id` / `result.state` 的最小 decoded-result 驗證，不擴張為 typed-response gate
3. 維持 topic-local analysis / plan artifacts 與 shape-only scope 一致，明確把 `src/**`、
   `tests/unit/test_job_execution_jobs_api.py`、與 `tests/contracts/**` primary gate 排除在外
4. 驗證本 topic 未重開 `start_job`、`get_job_state`、polling/state gate、shared workflow
   board、shared workflow contract、或其他未列出的路徑

## Validation / Acceptance Checks

- `analysis/request-gate-jobexecution-get-job/requirements.md` 與
  `analysis/request-gate-jobexecution-get-job/technical-spec.md` 明確宣告 shape-only mode
- `request-gate-jobexecution-get-job.plan.md` 使用 canonical required sections，且未加入
  `Stable library metadata`
- `request-gate-jobexecution-get-job.step.md` 的 `## Implementation Steps` 與本 plan 一一對齊，
  且完成標記反映 latest staged shape-only reality，而非過時的 pending 狀態
- `tests/unit/request_contract/job_execution_jobs_request_gate/` 仍是唯一 primary
  implementation surface
- topic-local artifacts 明確寫出 latest staged gate 已包含：
  - `Delegate-Domain` / `Content-Type` 不出現在 outbound request headers
  - `result.id` / `result.state` 的最小 decoded-result 驗證
- `tests/contracts/__init__.py` 與
  `tests/contracts/test_import_contract_http_client_module_path.py`
  只被宣告為 reference-only
- `src/**` 與 `tests/unit/test_job_execution_jobs_api.py` 在所有 topic-local artifacts 中均為
  out of scope
- topic-local artifacts 明確寫出：本 topic 不以 typed-response behavior 作為驗收範圍或
  completion gate
- shared workflow / queue surfaces 未被用作本 topic 的 active acceptance basis
- topic 內未把 scope 擴到 `start_job`、`jobExecution/jobs/state`、polling/state gate、
  shared workflow board、shared workflow contract、或未列出的路徑

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- 本 topic merge 後不需要 README 更新、VERSION bump、release notes、或 repository
  release action
- push / PR / merge orchestration 仍屬 Main Agent 工作，不屬於本 topic-local repair pass
- 本 topic 在 `merged` 時即為 terminal

## Open Questions / Unresolved Items

- None
