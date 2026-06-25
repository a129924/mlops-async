## Analysis Layer Routing

- Strict mode 生效：本 plan 以
  `analysis/request-gate-jobexecution-start-job-execution/technical-spec.md`
  為 execution-facing source of truth，並以
  `analysis/request-gate-jobexecution-start-job-execution/requirements.md`
  作為 business guardrail。
- 上游 `request-gate-jobexecution-start-job` planning baseline 視為本 topic 的
  scope guard；本 plan 不得擴張到相鄰 job execution surfaces。
- human-locked decision：legacy baseline 只可表述為
  `human-confirmed external source evidence`；不得在 repo artifacts 內寫入 physical path、
  absolute path、或 local filesystem path。

## Goal / Outcome

建立 `request-gate-jobexecution-start-job-execution` 的 execution contract，使後續 creator
只能在 `tests/unit/request_contract/job_requests_jobs_request_gate/**` 內完成
`start_job` 的 request-only gate，並在任何 `src/**` 需求、scope drift、或證據不足時
主動停在 blocker，而不是自行擴 scope。

## Scope

- **In scope**:
  - 維護本 topic 的四個 execution artifacts：
    `analysis/request-gate-jobexecution-start-job-execution/requirements.md`
    `analysis/request-gate-jobexecution-start-job-execution/technical-spec.md`
    `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.plan.md`
    `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.step.md`
  - 在後續 implementation 中，只於
    `tests/unit/request_contract/job_requests_jobs_request_gate/**`
    建立 `start_job` request-only gate artifacts
  - 凍結 `src/**` touch => blocker 的 execution rule

- **Out of scope**:
  - `jobExecution/jobs`
  - `jobExecution/jobs/state`
  - polling
  - state gate
  - `docs/request-shape-priority-workflow/**` 修改
  - shared workflow board 修改
  - `src/**` 修改
  - `pyproject.toml`、`uv.lock`、commit state

## Locked Decisions

- 新 topic 只承接 `start_job` 的 request-only gate implementation
- 不得擴到 `jobExecution/jobs`、`jobExecution/jobs/state`、polling、state gate
- implementation write set 應優先集中在
  `tests/unit/request_contract/job_requests_jobs_request_gate/**`
- 若 implementation 需要碰 `src/**` 才能成立，必須標記 blocker 並 separate re-plan；
  不得自行擴 scope
- legacy baseline 已由人類確認，可作為 `human-confirmed external source evidence`
- 不得把任何 physical path、absolute path、或 local filesystem path 寫入 repo artifacts
- 本 topic 不修改 shared workflow board，不承接 release 或 stable-library surfaces

## Boundaries / Exclusions

- Planning actor 只負責本 topic execution artifacts；不在此輪實作 tests 或 production code
- 後續 creator 只可在 topic-local artifacts 與
  `tests/unit/request_contract/job_requests_jobs_request_gate/**` 內工作
- reviewer 只審查本 topic contract 與 bounded implementation；不負責重定義 scope
- 任何 `src/**`、shared workflow board、docs workflow surface、或相鄰 endpoint family
  需求都屬新 topic 或 re-plan，不得回填到本 topic

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；
  本 topic 是 execution topic，但不包含 release action
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

- 本 topic 的 completion gate 只讀
  `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.step.md`
  的 `## Implementation Steps`
- shared workflow board 不在本 topic 可寫範圍內
- 若 implementation 觸發 `src/**` blocker，本 topic 必須停在 `creator-in-progress` 或
  `needs-rework`，直到 separate re-plan 完成

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements baseline | `analysis/request-gate-jobexecution-start-job-execution/requirements.md` | Planning actor | 凍結 execution topic 的 business baseline、allowed boundary、non-goals 與 completion gate |
| Technical spec | `analysis/request-gate-jobexecution-start-job-execution/technical-spec.md` | Planning actor | 凍結 exact write scope、evidence boundary、stop flags 與 acceptance gate |
| Topic plan | `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.plan.md` | Planning actor | 本 topic 的 canonical execution contract |
| Topic step tracker | `plan/request-gate-jobexecution-start-job-execution/request-gate-jobexecution-start-job-execution.step.md` | Planning actor | topic-local implementation completion gate |
| Implementation write root | `tests/unit/request_contract/job_requests_jobs_request_gate/` | Creator | `start_job` request-only gate 的唯一優先實作目錄 |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md`
- shared workflow board 不在 listed paths 內，因此任何 board edit 都是 scope drift
- 若後續工作需要 listed paths 以外的 surface，必須先停下並重新規劃

## Implementation Steps

1. 讀取本 topic 的 requirements、technical spec、plan、step artifacts，重新確認
   `start_job` request-only boundary、無 shared board edit、以及 `src/**` blocker rule。
2. 只在 `tests/unit/request_contract/job_requests_jobs_request_gate/**` 內建立或更新
   `start_job` request-only gate 所需的 tests、fixtures、或 helper artifacts。
3. 僅對 `POST /jobExecution/jobRequests/{jobRequestId}/jobs` 的 `start_job`
   request semantics 建立 assertions；不得延伸到 `jobExecution/jobs`、
   `jobExecution/jobs/state`、polling、或 state gate，也不得把 `timeout`
   值當成 hard gate 或 oracle。
4. 若 implementation 需要 `src/**` 變更、shared workflow board 修改、或超出既有抽象證據邊界，
   立即停止並標記 blocker，要求 separate re-plan。
5. 完成後確認 topic-local artifacts 與 implementation reality 一致，再移到 `review-ready`。

## Validation / Acceptance Checks

- 四個 topic-local artifacts 存在於 exact paths，且內容一致指向 `start_job` request-only gate
- `Artifact Paths` 明確把 implementation write root 限定為
  `tests/unit/request_contract/job_requests_jobs_request_gate/`
- `Locked Decisions`、`Scope`、`Boundaries / Exclusions` 沒有擴張到
  `jobExecution/jobs`、`jobExecution/jobs/state`、polling、state gate、或 shared board
- request-only gate 不以 `timeout` 值、response status、或 response payload
  作為 completion oracle
- `src/**` touch 明確被定義為 blocker，而非可接受例外
- `Reviewer Handoff` 是單一 machine-consumable JSON 物件

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

本 topic 沒有 release action。merge 後不修改 stable-library surfaces，也不回寫 shared
workflow board；若後續需要承接 `src/**` 或相鄰 surfaces，必須另開新 topic 或 re-plan。

## Open Questions / Unresolved Items

- 無新的 scope-level open question；唯一硬性停點是 `src/**` touch 需要 separate re-plan
