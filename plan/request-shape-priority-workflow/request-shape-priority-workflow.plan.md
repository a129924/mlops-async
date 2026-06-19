> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-shape-priority-workflow/technical-spec.md`
> - Business guardrail:
>   `analysis/request-shape-priority-workflow/requirements.md`
> - This plan maps 100% to the technical spec and does not reopen queue, entry hierarchy,
>   blocked-surface decisions, or request-shape scope.

## Goal / Outcome

- 修正 `request-shape-priority-workflow` 的 repo-visible docs / analysis / plan contract，使新
  session 能從 docs-first session-entry surface 進場，並正確恢復：
  - template-only session resume checklist
  - global surface/API implementation board
  - implementation-focused standards
  - `checklist.md` 與 `*.step.md` 的責任分界
- Topic 完成時，repo 應同時具備：
  - `docs/request-shape-priority-workflow/README.md`
  - `docs/request-shape-priority-workflow/standards.md`
  - `docs/request-shape-priority-workflow/checklist.md`
  - `analysis/request-shape-priority-workflow/requirements.md`
  - `analysis/request-shape-priority-workflow/technical-spec.md`
  - `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
  - `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`
  並且這些文件對 `checklist.md` 與 `standards.md` 的角色描述完全一致。

## Scope

- **In scope**:
  - `docs/request-shape-priority-workflow/README.md`
  - `docs/request-shape-priority-workflow/standards.md`
  - `docs/request-shape-priority-workflow/checklist.md`
  - `analysis/request-shape-priority-workflow/requirements.md`
  - `analysis/request-shape-priority-workflow/technical-spec.md`
  - `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
  - `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`

- **Out of scope**:
  - `src/**`
  - `tests/**`
  - `pyproject.toml`
  - `uv.lock`
  - `README.md`
  - `VERSION`
  - request-contract tests 內容改寫
  - blocked surface 解鎖
  - release / publish automation

## Locked Decisions

- 本 topic 是 **workflow-governance topic with no stable-library surfaces**；stable-library intent 明確 absent，不需要 `## Stable library metadata`。
- canonical session-entry artifacts 固定為：
  - `docs/request-shape-priority-workflow/README.md`
  - `docs/request-shape-priority-workflow/standards.md`
  - `docs/request-shape-priority-workflow/checklist.md`
- `README.md` 是必需 artifact，不是選配。
- 新 session 進場順序固定為：
  1. `docs/request-shape-priority-workflow/README.md`
  2. `docs/request-shape-priority-workflow/standards.md`
  3. `docs/request-shape-priority-workflow/checklist.md`
- `analysis/**` 與 `plan/**` 是 workflow artifacts，不是新 session 的 primary entry。
- `checklist.md` 只承擔兩種共享用途：
  - session resume checklist template
  - global surface/API implementation board
- 共享 `checklist.md` 中的 resume checklist 不得直接打勾；需先複製到 session-local artifact。
- queue 單位固定為明確 `surface + API`，不得使用抽象 family 名稱。
- 共享 board 至少涵蓋：
  - `modelRepository/models`
  - `modelRepository/models/content`
  - `modelRepository/projects`
  - `modelRepository/projects/champion`
  - `modelRepository/projects -> tables-link surface`
  - `jobExecution/jobRequests/jobs`
  - `jobExecution/jobs`
  - `jobExecution/jobs/state`
- `modelRepository/projects -> tables-link surface` 與 `jobExecution/jobs/state` 維持 `BLOCKED`。
- `casManagement/.../tables` 與 `SASLogon/oauth/token` 保持 `OUT-OF-SCOPE`，但需在 board 中明確列出。
- `standards.md` 只承擔 implementation standards，不得寫成 workflow handoff prompt。
- request-shape 主測試面固定為 `tests/unit/request_contract/**`；`tests/contracts` 只保留 policy / guard surface 角色。

## Boundaries / Exclusions

- Planning actor 只負責本 topic 的 docs / analysis / plan artifacts。
- Creator 只可修改本 plan 列出的精確路徑；若工作漂移到 `src/**`、`tests/**` 或 stable-library surfaces，必須停止並回到 `human-check`。
- Reviewer 只審查 docs-first hierarchy、template-only policy、surface board、implementation standards、與 artifact-path exactness；不得在 review 中重開 queue 或 architecture decision。
- Main Agent 負責 commit、review routing、final gate routing、與 human-check 停點。
- 本 topic 不處理任何 surface 的 request-shape implementation 細節，也不處理 publish / merge / release 執行。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this correction pass should stop at `review-ready` until a new independent review verdict exists.
- **Step-tracker alignment**:
  `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`
  會在本輪 correction 完成後把 `## Implementation Steps` 全部標記為 `[X]`，但 `Independent review`
  應回到未完成，等待新的獨立 review。
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

- 本輪 correction 不建立 `review-log`；reviewer verdict 可直接透過 canonical `Reviewer Handoff` JSON 回傳。
- 本輪 correction 完成後，應由新的獨立 reviewer 重新審查；不可沿用先前針對舊文件形狀的 review 結果。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical workflow status model, transitions, and reviewer handoff contract |
| Shared topic-plan contract | `plan/topic-plan-contract.md` | Planning actor | Shared authority for canonical topic-plan sections and blocking semantics |
| Session-entry README | `docs/request-shape-priority-workflow/README.md` | Creator | First entry for new sessions; defines read order, artifact hierarchy, and shared-file warning |
| Implementation standards | `docs/request-shape-priority-workflow/standards.md` | Creator | Surface/API sequencing rules, blocked policy, board/step boundary, and request-shape scope |
| Shared checklist and API board | `docs/request-shape-priority-workflow/checklist.md` | Creator | Session resume checklist template plus global surface/API implementation board |
| Requirements baseline | `analysis/request-shape-priority-workflow/requirements.md` | Planning actor | Frozen business baseline for docs-first queue workflow |
| Technical spec | `analysis/request-shape-priority-workflow/technical-spec.md` | Planning actor | Execution-facing source of truth for artifact roles, board schema, and correction rules |
| Topic plan | `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md` | Creator | Machine-readable completion gate for this topic only |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: no change in this topic.
- `src/**`: no change in this topic.
- `tests/**`: no change in this topic.
- `pyproject.toml`: no change in this topic.
- `uv.lock`: no change in this topic.
- 若後續工作出現在未列路徑，必須先回到 planner / human-check 修正 topic contract，不得視為可接受 drift。

## Implementation Steps

1. 更新 `analysis/request-shape-priority-workflow/requirements.md`，把 `checklist.md` 的需求改成：
   - template-only session resume checklist
   - global surface/API implementation board
   - implementation-focused `standards.md`
2. 更新 `analysis/request-shape-priority-workflow/technical-spec.md`，把 drift 重點、artifact responsibilities、board schema、與 correction rules 對齊到新需求，並明寫 `surface + API` 命名規則。
3. 更新 `docs/request-shape-priority-workflow/README.md`，把 `standards.md` 描述改成 implementation standards，把 `checklist.md` 描述改成 template + board，並補上共享勾選污染警告與 surface-based queue 說明。
4. 更新 `docs/request-shape-priority-workflow/standards.md`，移除 prompt / persona / allowed-subAgent / output-preference 內容，只保留 implementation sequencing、surface naming、artifact precedence、board / step 邊界、blocked policy、與 request-shape scope。
5. 更新 `docs/request-shape-priority-workflow/checklist.md`，使其同時承擔：
   - session resume checklist template
   - global surface/API implementation board
   並明寫共享 resume checklist 不可直接勾選、`tables` 不可作為抽象 queue 單位。
6. 更新 `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`，把 locked decisions、artifact roles、implementation steps、validation wording 對齊 correction 後的文件形狀。
7. 更新 `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`，使本輪 correction 的 implementation steps 與新 plan 一致，並把 `Independent review` 留為未完成。

## Validation / Acceptance Checks

- `docs/request-shape-priority-workflow/README.md`、`standards.md`、`checklist.md` 全部存在，且 `README.md` 被明確宣告為 required first entry。
- docs trio 一致記錄固定讀取順序：
  1. `README.md`
  2. `standards.md`
  3. `checklist.md`
- docs trio、requirements、technical-spec、plan 一致宣告 `analysis/**` / `plan/**` 是 workflow artifacts，不是新 session 的 primary entry。
- `checklist.md` 明確分成：
  - session resume checklist template
  - global surface/API implementation board
- `checklist.md` 沒有共享可直接勾選的 resume checklist。
- implementation board 至少包含：
  - `modelRepository/models / list_models`
  - `modelRepository/models / get_model`
  - `modelRepository/models/content / get_model_content`
  - `modelRepository/projects / list_projects`
  - `modelRepository/projects / get_project`
  - `modelRepository/projects/champion / get_champion_model`
  - blocked `modelRepository/projects -> tables-link surface / list_tables`
  - `jobExecution/jobRequests/jobs / start_job`
  - `jobExecution/jobs / get_job`
  - blocked `jobExecution/jobs/state / get_job_state`
  - out-of-scope `casManagement/.../tables` 列
  - out-of-scope `SASLogon/oauth/token` 列
- implementation board 的欄位固定為 `State`、`Surface`、`API`、`Order`、`Injection hint`、`Notes`。
- docs trio、requirements、technical-spec、plan 一致記錄 `tables` 不得再作為抽象 queue 單位。
- `standards.md` 不再包含 persona、allowed subAgent roles、或 output-preference prompt wording。
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md` 存在，且只承擔本 topic 自己的 completion gate。
- `technical-spec.md` 與 `standards.md` 明確把 `tests/unit/request_contract/**` 定位為主 request-shape surface，並把 `tests/contracts` 定位為 policy / guard surface。
- 本輪 correction 完成後，`step.md` 的 `Independent review` 應為未完成，等待新 reviewer lane。

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

- 本 topic 不需要 README 更新、VERSION bump、release notes、或 repository release action。
- 本輪 correction 完成後應停在 `review-ready`，等待新的獨立 review。
- 若未來 human 決定進下一步 implementation，應另依 docs-first session-entry 重新進場。

## Open Questions / Unresolved Items

- None.
