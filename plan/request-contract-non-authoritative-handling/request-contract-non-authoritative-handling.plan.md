# request-contract-non-authoritative-handling

> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-contract-non-authoritative-handling/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-contract-non-authoritative-handling/requirements.md`
> - 本 topic 是 implementation workflow lane，且所有 topic 變更只可落在
>   `feat/andrew/request-contract-non-authoritative-handling` managed worktree。

## Goal / Outcome

- 對齊 `tests/unit/request_contract/**` 中 non-authoritative surfaces 的 current truth，
  讓後續 implementer 不會再從歷史 artifact、internal wrapper、或 custom client
  的 request gates 推導 upstream endpoint truth。
- 讓 `projects_tables_link_request_gate` 明確退回 historical superseded surface，
  同時保留仍有 repo-local shape 價值的 request gates。

## Scope

- **In scope**:
  - `analysis/request-contract-non-authoritative-handling/requirements.md`
  - `analysis/request-contract-non-authoritative-handling/technical-spec.md`
  - `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.plan.md`
  - `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.spec.md`
  - `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.step.md`
  - `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md`
  - `docs/request-shape-priority-workflow/request-contract-non-authoritative-ledger.md`
  - bounded request-contract topics:
    - `tests/unit/request_contract/projects_tables_link_request_gate/**`
    - `tests/unit/request_contract/job_execution_jobs_request_gate/**`
    - `tests/unit/request_contract/job_execution_jobs_state_request_gate/**`
    - `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
    - `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.request-flow.json`
    - `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
    - `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.request-flow.json`
    - `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json`

- **Out of scope**:
  - `src/mlops_async/**`
  - `docs/api-endpoints/swagger-spec/upstream/*.yml`
  - `docs/api-endpoints/swagger-spec/*.yaml`
  - old fixed-path MVP worktree cleanup
  - direct deletion of tests / plans
  - release / commit / push / PR / merge

## Locked Decisions

- branch: `feat/andrew/request-contract-non-authoritative-handling`
- managed worktree:
  `../mlops-async.worktrees/agent-20260709-request-contract-non-authoritative-handling`
- 本 topic 是 **implementation lane with no stable-library surfaces**；
  不包含 `README.md`、`VERSION`、release notes、或 release timing。
- authority vocabulary 固定為：
  - `upstream-aligned`
  - `non-authoritative-shape-only`
  - `historical-superseded`
  - `pseudo-endpoint-or-contract`
- allowed-use vocabulary 固定為：
  - `implementation-truth`
  - `keep-as-shape-baseline`
  - `keep-as-historical-only`
  - `delete-candidate`
- `projects_tables_link_request_gate` 固定為
  `historical-superseded + keep-as-historical-only`
- `job_execution_jobs_request_gate`、`job_execution_jobs_state_request_gate`、
  `casmanagement_*`、`saslogon_*` 在本 topic 內固定視為
  `non-authoritative-shape-only + keep-as-shape-baseline`
- 本 topic 不新增 pytest markers；只用 docs、fixture metadata、docstring、
  collection guard 來表達 boundary。

## Boundaries / Exclusions

- Creator work 只可修改 `Artifact Paths` 列出的精確路徑。
- Reviewer work 只負責驗證 scope drift、contract drift、workflow drift，不負責
  代作者修檔。
- Main Agent 只負責 workflow routing 與 human-check 停止點，不在本 topic 內做
  publish / merge。
- 任何超出 listed write set 的 endpoint、spec、runtime 或 release surface 改動，
  都視為 `blocked` 並需另開 topic。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic uses
  `create worktree -> plan-finalization -> plan-review -> plan-fix -> final-gate -> implementation -> independent review -> human check`
  and stops at `human-check`
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

- create-worktree gate 已完成；後續所有 topic 變更只可發生在這個 managed worktree。
- plan-review / plan-fix / final-gate 只允許修正 topic-local planning artifacts。
- implementation 完成後必須做獨立 review，之後停在 `human-check`，不進 publish。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-contract-non-authoritative-handling/requirements.md` | Planning actor | Business guardrail for this topic |
| Topic technical spec | `analysis/request-contract-non-authoritative-handling/technical-spec.md` | Planning actor | Execution-facing source of truth |
| Topic plan | `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.plan.md` | Planning actor | Repo-visible execution contract |
| Topic spec | `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.spec.md` | Planning actor | Acceptance scenarios and stop boundary |
| Topic step tracker | `plan/request-contract-non-authoritative-handling/request-contract-non-authoritative-handling.step.md` | Planning actor | Workflow stage and implementation completion gate |
| Evidence matrix | `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md` | Creator | Current-truth authority mapping |
| Non-authoritative ledger | `docs/request-shape-priority-workflow/request-contract-non-authoritative-ledger.md` | Creator | Central handling policy and allowed-use table |
| Historical package marker | `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py` | Creator | Historical-only package anchor |
| Historical harness | `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py` | Creator | Historical-only collection guard and metadata |
| Historical request-contract test | `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py` | Creator | Historical-only request gate surface |
| Historical request-flow fixture | `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json` | Creator | Historical-only fixture metadata |
| Historical mock-response fixture | `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json` | Creator | Historical-only fixture companion |
| Wrapper package marker | `tests/unit/request_contract/job_execution_jobs_request_gate/__init__.py` | Creator | Wrapper shape-only package anchor |
| Wrapper harness | `tests/unit/request_contract/job_execution_jobs_request_gate/conftest.py` | Creator | Wrapper shape-only metadata |
| Wrapper request-contract test | `tests/unit/request_contract/job_execution_jobs_request_gate/test_get_job_request_contract.py` | Creator | Wrapper shape-only request gate surface |
| Wrapper request-flow fixture | `tests/unit/request_contract/job_execution_jobs_request_gate/fixtures/get_job.request-flow.json` | Creator | Wrapper shape-only fixture metadata |
| Wrapper state package marker | `tests/unit/request_contract/job_execution_jobs_state_request_gate/__init__.py` | Creator | Wrapper state shape-only package anchor |
| Wrapper state harness | `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py` | Creator | Wrapper state shape-only metadata |
| Wrapper state request-contract test | `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py` | Creator | Wrapper state shape-only request gate surface |
| Wrapper state request-flow fixture | `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.request-flow.json` | Creator | Wrapper state shape-only fixture metadata |
| Custom-client list fixture | `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json` | Creator | Non-authoritative fixture metadata |
| Custom-client get fixture | `tests/unit/request_contract/casmanagement_table_get_request_gate/fixtures/get_table.request-flow.json` | Creator | Non-authoritative fixture metadata |
| Custom-client state fixture | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json` | Creator | Non-authoritative fixture metadata |
| Auth token fixture | `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.request-flow.json` | Creator | Non-authoritative fixture metadata |
| Auth refresh fixture | `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json` | Creator | Non-authoritative fixture metadata |

Artifact path notes:

- `README.md`: no change
- `VERSION`: no change
- `.github/copilot-instructions.md`: no change
- `src/mlops_async/**`: no change
- `docs/api-endpoints/swagger-spec/**`: no change
- 若 implementation drift 到 listed paths 之外，topic 必須視為 `blocked`

## Implementation Steps

1. 建立並凍結 topic-local planning artifacts，讓 authority vocabulary、allowed-use
   vocabulary、write set、與 human-check stop boundary 都是 repo-visible contract。
2. 更新 `request-contract-evidence-matrix.md`，把 non-authoritative topics 的 current
   truth、allowed use、與禁止用途寫清楚。
3. 新增 `request-contract-non-authoritative-ledger.md`，集中列出每個 affected topic 的
   authority class、allowed use、與 implementation consumption boundary。
4. 在 `projects_tables_link_request_gate` 落地 historical-only metadata 與
   non-topic-scoped collection guard，避免它再被當成一般 request gate。
5. 在 wrapper / custom-client shape-only topics 的 tests 或 fixtures 中同步
   non-authoritative metadata，保留 shape baseline 但禁止 upstream truth 解讀。
6. 針對被修改 topics 執行最小 scoped pytest，並執行 repo-required `ruff check` 與
   `pyright` 驗證。

## Validation / Acceptance Checks

- planning artifacts 只落在 new topic 的 `analysis/` 與 `plan/` 路徑
- `request-contract-evidence-matrix.md` 必須能讓 implementer 區分：
  - current truth
  - keep-as-shape-baseline
  - keep-as-historical-only
  - delete-candidate
- `projects_tables_link_request_gate` 在 docs 與 tests surfaces 都不可再被描述成
  current truth
- wrapper / custom-client shape-only topics 仍可保留 shape baseline，但 repo-visible
  metadata 必須明示禁止把它們讀成 upstream truth
- scoped pytest、`ruff check`、`pyright` 結果必須被記錄；若有 unrelated failure，
  必須明確區分
- implementation 完成後必須有獨立 review verdict，之後停止於 `human-check`

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

- 本 topic 不含 repository release action。
- 本 topic 在 `human-check` 停止，不進 publish / PR / merge。

## Open Questions / Unresolved Items

- None at plan finalization time.
