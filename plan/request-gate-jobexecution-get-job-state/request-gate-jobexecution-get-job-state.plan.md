> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-gate-jobexecution-get-job-state/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-gate-jobexecution-get-job-state/requirements.md`

## Goal / Outcome

- 讓 `request-gate-jobexecution-get-job-state` 成為獨立、可審查、可驗證的 request-shape topic。
- 交付本 topic 的 endpoint plan artifacts，以及獨立的
  `tests/unit/request_contract/job_execution_jobs_state_request_gate/**` Python request-contract surface。

## Scope

- **In scope**:
  - `analysis/request-gate-jobexecution-get-job-state/requirements.md`
  - `analysis/request-gate-jobexecution-get-job-state/technical-spec.md`
  - `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.plan.md`
  - `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.step.md`
  - `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.spec.md`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/__init__.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.request-flow.json`
  - `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.mock-responses.json`

- **Out of scope**:
  - `src/**`
  - `tests/unit/test_job_execution_jobs_api.py`
  - `tests/contracts/**`
  - `tests/unit/request_contract/job_execution_jobs_request_gate/**`
  - `tests/unit/request_contract/job_requests_jobs_request_gate/**`
  - polling / wait / timeout / state machine
  - shared workflow 文件
  - release / push / PR

## Locked Decisions

- canonical managed worktree 路徑固定為：
  `../mlops-async.worktrees/agent-20260626-request-gate-jobexecution-get-job-state`
- branch 固定為：
  `feat/andrew/request-gate-jobexecution-get-job-state`
- 沿用 `tests/unit/request_contract/job_execution_jobs_request_gate/` 的 harness pattern，但建立獨立 package `job_execution_jobs_state_request_gate/`。
- 不修改既有 `get_job` gate，也不與其共用 topic plan。
- request contract 固定為：
  - method `GET`
  - path `/jobExecution/jobs/{jobId}/state`
  - query `{}`
  - body `None`
  - required headers：`Authorization`、`Accept`
- negative header constraints 固定為：
  - `Delegate-Domain` 不得作為 required emitted header
  - `Content-Type` 不得作為 required emitted header
- fixture boundary 固定為：
  - `get_job_state.request-flow.json` 只含 `direct_identifier`
  - `full_observed_flow` 長度固定為 `1`
  - `get_job_state.mock-responses.json` 最小 body 只含 `state`
- 必須保留的 boundary references：
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md:117`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md:121`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md:122`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md:257`
  - `docs/request-shape-priority-workflow/checklist.md:45`

## Boundaries / Exclusions

- 不把 `jobExecution/jobs/state` 擴成 polling / wait / timeout topic。
- 不把 `get_job` 或 `start_job` 回收進同 topic。
- 不修改 shared workflow 文件作為順手修補。
- `Main Agent` 保留 publish / merge routing；本 topic 只處理 endpoint plan 與 Python request-contract implementation。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；本 topic 已完成 endpoint plan artifacts 與 request-contract surface，下一個外部 gate 是 reviewer 與 validation consumption；不含 release action。
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

- create worktree step 已完成；後續任何本 topic rework 仍只可在此 managed worktree 內進行。
- `human-check` 只作為外部 stop boundary，不是 workflow status。
- 若後續工作 drift 到 shared workflow 文件、`src/**`、或 polling semantics，必須先回到 `human-check`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-jobexecution-get-job-state/requirements.md` | Plan-Creator | 凍結 bounded endpoint、scope、與 stop conditions |
| Topic technical spec | `analysis/request-gate-jobexecution-get-job-state/technical-spec.md` | Plan-Creator | 凍結 request contract draft、allowed write set、與 validation |
| Topic plan | `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.plan.md` | Plan-Creator | canonical execution contract |
| Topic step tracker | `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.step.md` | Plan-Creator | creator-owned completion gate |
| Topic spec | `plan/request-gate-jobexecution-get-job-state/request-gate-jobexecution-get-job-state.spec.md` | Plan-Creator | acceptance criteria、behavioral scenarios、error cases |
| Request gate package marker | `tests/unit/request_contract/job_execution_jobs_state_request_gate/__init__.py` | Code-Implementer | package anchor |
| Request gate harness | `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py` | Code-Implementer | request capture、fallback client、與 bounded validation helper |
| Request gate test | `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py` | Code-Implementer | positive / negative request-contract tests |
| Request-flow evidence | `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.request-flow.json` | Code-Implementer | source-observed request evidence |
| Mock-response fixture | `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.mock-responses.json` | Code-Implementer | minimal harness scaffold |

Artifact path notes:

- `README.md`: no change
- `VERSION`: no change
- shared workflow 文件：no change
- 若出現未列路徑的變更，視為 plan drift，必須停止並先回到 `human-check`

## Implementation Steps

1. 確認 managed worktree `../mlops-async.worktrees/agent-20260626-request-gate-jobexecution-get-job-state` 與 branch `feat/andrew/request-gate-jobexecution-get-job-state` 為唯一落地位置。
2. 建立 `analysis/request-gate-jobexecution-get-job-state/requirements.md` 與 `technical-spec.md`，凍結 bounded endpoint、boundary references、與 validation rules。
3. 建立 `plan/request-gate-jobexecution-get-job-state/` 下的 `plan.md`、`step.md`、`spec.md`，把 endpoint plan 寫成 repo-visible contract。
4. 建立 `tests/unit/request_contract/job_execution_jobs_state_request_gate/` package、harness、fixtures、與 request-contract tests，並維持與 `get_job` gate 分離。
5. 執行 `pytest`、`pyright`、`ruff` 驗證，確認 direct identifier、blocked variants、與 fast-fail variant 全部符合 bounded contract。

## Validation / Acceptance Checks

- `tests/unit/request_contract/job_execution_jobs_state_request_gate/` primary surface 完整存在。
- 正向測試明確驗證 method / path / query / body / required headers。
- `Delegate-Domain` 與 `Content-Type` 不出現在 outbound request headers。
- non-string、dict-like、blank identifier 會被阻擋。
- unregistered request path 以 `Unexpected outbound request` fast-fail。
- `plan.md` 使用 canonical required sections，`Reviewer Handoff` 為單一 JSON object。
- `spec.md` 明確收錄 acceptance criteria、behavioral scenarios、與 error / edge cases。

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

- 本 topic 無 release action。
- merge 後若要做 worktree cleanup，應走 `worktree-manager` 的 release / remove semantics；本 topic 不自動處理該 lifecycle。

## Open Questions / Unresolved Items

- None
