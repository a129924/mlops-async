STRICT MODE

- execution-facing source of truth: `analysis/request-gate-jobexecution-get-job/technical-spec.md`
- business-intent guardrail: `analysis/request-gate-jobexecution-get-job/requirements.md`
- 本 plan 100% 對齊 analysis layer；未經 human `override` 不採用對話中的替代 scope

## Goal / Outcome

建立 `request-gate-jobexecution-get-job` 的四個 topic-local planning artifacts，凍結
`jobExecution/jobs / get_job` 的 bounded planning contract，並在 artifact authoring 完成後停在
`human-check`。

## Scope

- **In scope**:
  - `analysis/request-gate-jobexecution-get-job/requirements.md`
  - `analysis/request-gate-jobexecution-get-job/technical-spec.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`
  - `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`

- **Out of scope**:
  - `start_job`
  - `jobExecution/jobs/state`
  - polling / state gate
  - `src/**`
  - `tests/**`
  - `docs/request-shape-priority-workflow/**`
  - shared workflow board edits
  - commit / review / publish / PR / release

## Locked Decisions

- 本 topic 是 non-stable planning topic，不影響 stable-library surfaces。
- 本 topic 只處理 `jobExecution/jobs / get_job`；不得順手擴到 `start_job` 或
  `jobExecution/jobs/state / get_job_state`。
- `jobExecution/jobs/state / get_job_state` 只可作為 boundary reference，不屬於本 topic deliverable。
- bounded write set 固定為：
  - `analysis/request-gate-jobexecution-get-job/**`
  - `plan/request-gate-jobexecution-get-job/**`
- future implementation 測試目錄名稱固定為：
  - `tests/unit/request_contract/job_execution_jobs_request_gate/`
- future implementation 若要處理 `src/**` 或 `tests/**`，必須另開 implementation topic。

## Boundaries / Exclusions

- Planning actor 只負責撰寫 topic-local analysis / plan artifacts。
- Creator 只可在未來 implementation topic 內處理 bounded code / test work。
- Reviewer 只負責獨立審查 planning artifacts，不在本 pass 內修改內容。
- Main Agent 負責後續 phase routing、commit / publish / PR orchestration。
- shared workflow board 不得作為本 topic completion gate。
- 若後續工作漂移到未列 path，視為 plan drift，必須先回到 human decision。

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；本 topic 本輪只完成 planning artifacts，並在 human boundary 停止，不含 release。
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

- 本 topic 在四個 planning artifacts 建立完成後停在 `human-check`；不得自動進入 implementation。
- shared workflow spec-and-plan-finalization 的後續 phase 可包含 commit / review / final gate，但本文件不授權本 pass 跨越人工作業邊界。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical workflow lifecycle and status model reference |
| Shared topic-plan contract | `plan/topic-plan-contract.md` | Planning actor | Canonical required sections and contract-blocking baseline |
| Topic requirements | `analysis/request-gate-jobexecution-get-job/requirements.md` | Planning actor | Endpoint inventory, scope / non-goals, and boundary baseline |
| Topic technical spec | `analysis/request-gate-jobexecution-get-job/technical-spec.md` | Planning actor | Execution-facing planning contract and stop rules |
| Topic plan | `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md` | Planning actor | Repo-visible execution contract for this planning topic |
| Step tracker | `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md` | Planning actor | Topic-local completion gate for planning artifact authoring |

Artifact path notes:

- `README.md`：no change
- `VERSION`：no change
- `.github/copilot-instructions.md`：no change
- `docs/request-shape-priority-workflow/**`：no change
- `src/**`：no change
- `tests/**`：no change
- 若出現未列路徑的變更，視為 plan-alignment problem，必須先停止並回到 human-check。

## Implementation Steps

1. 建立 `analysis/request-gate-jobexecution-get-job/requirements.md`，完成 endpoint inventory、scope、non-goals、boundary、與 human-check 規則。
2. 建立 `analysis/request-gate-jobexecution-get-job/technical-spec.md`，完成 request contract draft、risk、stop flags、allowed file scope、與 deferred work。
3. 建立 `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.plan.md`，完成 canonical workflow contract、locked decisions、artifact paths、與 reviewer handoff JSON。
4. 建立 `plan/request-gate-jobexecution-get-job/request-gate-jobexecution-get-job.step.md`，並與本 plan 的 implementation steps 對齊。
5. 驗證四個 artifacts 只落在 bounded write set，且本 topic 明確停在 `human-check`。

## Validation / Acceptance Checks

- 四個 topic-local artifacts 全部存在。
- `requirements.md` 包含 endpoint inventory、bounded write set、與 `jobExecution/jobs/state` 邊界。
- `technical-spec.md` 包含 `GET /jobExecution/jobs/{jobId}` request contract draft、risk、stop flags、與 forbidden paths。
- `request-gate-jobexecution-get-job.plan.md` 使用 canonical required sections，且未加入 `Stable library metadata`。
- `request-gate-jobexecution-get-job.step.md` 只承擔 topic-local completion gate，不接管 shared workflow board。
- topic 內未建立 `spec.md`。
- topic 內未修改 `src/**`、`tests/**`、或 `docs/request-shape-priority-workflow/**`。

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

- 本 topic 不含 stable-library surface 變更，不需要 VERSION bump、README 更新、release notes、或 release timing 動作。
- 本 topic 的自動流程邊界停在 `human-check`；本 pass 不執行 commit、publish、PR、或 merge。

## Open Questions / Unresolved Items

- 若後續 implementation topic 要求 direct source file evidence 取代 swagger / markdown evidence，是否需先補 legacy `utils/_api/job_execution.py` 的 provenance，待 human reviewer 決定。
