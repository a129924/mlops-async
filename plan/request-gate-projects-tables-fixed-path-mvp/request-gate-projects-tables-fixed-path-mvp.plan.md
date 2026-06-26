> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-gate-projects-tables-fixed-path-mvp/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-gate-projects-tables-fixed-path-mvp/requirements.md`

## Goal / Outcome

- 建立 `request-gate-projects-tables-fixed-path-mvp` 的 repo-visible execution contract。
- 凍結 `list_tables(project_id)` 的 fixed-path MVP request shape，供未來
  implementation 與 request-contract tests 使用。
- 明確標記本 topic 的 divergence choice 為 `intentionally_changed`。

## Scope

- **In scope**:
  - `analysis/request-gate-projects-tables-fixed-path-mvp/requirements.md`
  - `analysis/request-gate-projects-tables-fixed-path-mvp/technical-spec.md`
  - `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.plan.md`
  - `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.step.md`
  - `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.spec.md`
  - future implementation landing path:
    - `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py`
    - `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py`
    - `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py`
    - `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`
    - `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`

- **Out of scope**:
  - `src/**`
  - `docs/request-shape-priority-workflow/**`
  - `tests/contracts/**`
  - `tests/unit/request_contract/projects_request_gate/**`
  - `casManagement/dataSources/tables`
  - response / error contract
  - HATEOAS link parsing
  - project pre-fetch + `links[].href` follow-up
  - polling / state-machine / orchestration
  - release / push / PR

## Locked Decisions

- canonical managed worktree path:
  `../mlops-async.worktrees/agent-20260626-request-gate-projects-tables-fixed-path-mvp`
- branch:
  `feat/andrew/request-gate-projects-tables-fixed-path-mvp`
- topic classification: `fixed-path MVP`
- contract status: `implementation-facing draft`
- divergence label: `intentionally_changed`
- canonical method/path:
  - `GET /modelRepository/projects/{project_id}/tables`
- canonical input shape:
  - required path parameter `project_id`
  - `project_id` 必須是 non-empty string
- canonical request shape:
  - query `{}` only
  - body `null` / absent
- no HATEOAS parsing
- no pre-step project fetch
- no `casManagement/.../tables`
- 若未來要恢復 HATEOAS-faithful contract，必須另開新 topic
- stable-library intent 明確 absent；本 topic 不碰 `README.md`、`VERSION`、或 release timing

## Boundaries / Exclusions

- Plan-Creator 只負責 analysis / plan artifacts，不能在本 topic 內直接做 implementation。
- Plan-Reviewer 只做 topic-plan contract review，不代寫 plan。
- Main Agent 只負責 workflow routing 與 human-check 前的 gate，不能把本 topic 擴成 code implementation。
- Future Code-Implementer 只能在 `tests/unit/request_contract/projects_tables_link_request_gate/**`
  內落地 request-contract artifacts；不得回寫 shared workflow docs 或其他 endpoint topic。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; 本輪只完成 plan finalization / review / fix / final gate，等待 human check 後才可 dispatch implementation。
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

- 本輪的 plan workflow 已走完：
  `create worktree -> plan-finalization -> plan-review -> plan-fix -> final-gate`
- 下一個允許的 execution transition 是 human approval 之後的
  `approved -> creator-in-progress`
- 若後續工作 drift 到 `src/**`、HATEOAS、CAS concrete tables、或 response contract，必須停止並另開 topic

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-projects-tables-fixed-path-mvp/requirements.md` | Plan-Creator | 凍結 topic purpose、scope、non-goals、與 implementation-facing assumptions |
| Topic technical spec | `analysis/request-gate-projects-tables-fixed-path-mvp/technical-spec.md` | Plan-Creator | 凍結 fixed-path MVP request contract draft 與 future implementation landing path |
| Topic plan | `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.plan.md` | Plan-Creator | Canonical execution contract |
| Topic step tracker | `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.step.md` | Plan-Creator | Future implementation completion gate |
| Topic behavior spec | `plan/request-gate-projects-tables-fixed-path-mvp/request-gate-projects-tables-fixed-path-mvp.spec.md` | Plan-Creator | Fixed-path MVP request-shape acceptance scenarios |
| Request gate package marker | `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py` | Code-Implementer | Package anchor for isolated tables-link request gate |
| Request gate harness | `tests/unit/request_contract/projects_tables_link_request_gate/conftest.py` | Code-Implementer | Fixed-path MVP request capture / validation helper |
| Request gate test | `tests/unit/request_contract/projects_tables_link_request_gate/test_list_tables_request_contract.py` | Code-Implementer | Positive / negative request-contract tests |
| Request-flow fixture | `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json` | Code-Implementer | Canonical fixed-path request example |
| Mock-response fixture | `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json` | Code-Implementer | Minimal harness scaffold |

Artifact path notes:

- `README.md`: no change
- `VERSION`: no change
- `.github/copilot-instructions.md`: no change
- `docs/request-shape-priority-workflow/**`: no change
- listed paths are the full executable contract
- 若後續工作需要超出 listed paths，視為 plan drift，必須先停下再重新定義 topic

## Implementation Steps

1. 建立 `tests/unit/request_contract/projects_tables_link_request_gate/__init__.py` 作為 isolated package marker。
2. 建立 `fixtures/list_tables.request-flow.json`，只保留 `direct_project_identifier` case。
3. 建立 `fixtures/list_tables.mock-responses.json`，只提供最小 JSON object scaffold。
4. 建立 `conftest.py`，實作 fixed-path MVP 的 request capture helper：
   `list_tables(project_id)` -> `GET /modelRepository/projects/{project_id}/tables`。
5. 建立 `test_list_tables_request_contract.py`，覆蓋：
   - direct identifier positive case
   - non-string `project_id`
   - blank `project_id`
   - path/query/body drift guards
6. 執行 bounded validation：
   - `pytest`
   - `pyright`
   - `ruff`
7. 保持 `intentionally_changed` 邊界，不把 implementation 擴回 HATEOAS 或 CAS concrete tables。

## Validation / Acceptance Checks

- plan 檔案包含 canonical required sections，且 section 名稱正確。
- stable-library intent 明確 absent。
- `Reviewer Handoff` 是單一 JSON object。
- technical spec 明確標記：
  - `fixed-path MVP`
  - `implementation-facing draft`
  - `intentionally_changed`
- future implementation path 精確限定在
  `tests/unit/request_contract/projects_tables_link_request_gate/**`
- implementation acceptance 需能驗證：
  - method `GET`
  - path `/modelRepository/projects/{project_id}/tables`
  - no query
  - no body
  - invalid `project_id` fast-fail

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

- 本 topic 無 stable-library release action。
- merge 後如需整理 worktree，使用 `worktree-manager` 走 release/remove 分離流程。
- 本 topic 不要求 `merged -> released` transition。

## Open Questions / Unresolved Items

- None
