> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-shape-priority-workflow/technical-spec.md`
> - Business guardrail:
>   `analysis/request-shape-priority-workflow/requirements.md`
> - This plan maps 100% to the technical spec and does not reopen queue, entry hierarchy,
>   role boundary, or blocked-family decisions.

## Goal / Outcome

- 建立 `request-shape-priority-workflow` 的 repo-visible execution contract，使新 session 可以從
  docs-first session-entry surface 進場，並在不回溯歷史對話的前提下，恢復 request-shape
  family queue、Observer / Dispatcher 邊界、blocked-family policy 與 cross-family dispatch
  board。
- Topic 完成時，repo 應同時具備：
  - `docs/request-shape-priority-workflow/README.md`
  - `docs/request-shape-priority-workflow/standards.md`
  - `docs/request-shape-priority-workflow/checklist.md`
  - `analysis/request-shape-priority-workflow/requirements.md`
  - `analysis/request-shape-priority-workflow/technical-spec.md`
  - `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
  - `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`

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
  - `tables` family 解鎖
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
- `checklist.md` 是跨 family dispatch board，不與任何單一 topic 的 `*.step.md` 混用。
- family queue 鎖定為：
  1. `models`
  2. `projects`
  3. `tables` = `BLOCKED`
- Observer / Dispatcher 只負責 state check、phase decision、dispatch、triage；不得直接實作、改檔、commit、push、開 PR、或 release。
- request-shape 主測試面固定為 `tests/unit/request_contract/**`；`tests/contracts` 只保留 policy / guard surface 角色。

## Boundaries / Exclusions

- Planning actor 只負責本 topic 的 docs / analysis / plan artifacts。
- Creator 只可修改本 plan 列出的精確路徑；若工作漂移到 `src/**`、`tests/**` 或 stable-library surfaces，必須停止並回到 `human-check`。
- Reviewer 只審查 docs-first hierarchy、queue / blocked policy、role boundary、與 artifact-path exactness；不得在 review 中重開 queue 或 architecture decision。
- Main Agent 負責 draft commit、review routing、fix routing、final gate routing、與 wait-human-check 停點。
- 本 topic 不處理任何 family 的 request-shape implementation 細節，也不處理 publish / merge / release 執行。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops at human check after plan finalization and does not enter implementation or release.
- **Step-tracker alignment**:
  `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`
  已建立且 `## Implementation Steps` 已全部完成，因此本輪 creator gate 已完成，可進入獨立 review。
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

- 本 topic 的實際執行 workflow 為：
  - create worktree
  - create-analysis
  - create-agent-plan
  - draft plan commit by topic
  - independent plan review
  - plan-creator fix/update when needed
  - planner final gate
  - wait human check
- `wait human check` 是本輪 plan finalization 的停點，不是新的 canonical workflow status。
- 本 topic 不建立 `review-log`；reviewer verdict 可直接透過 canonical `Reviewer Handoff` JSON 回傳。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical workflow status model, transitions, and reviewer handoff contract |
| Shared topic-plan contract | `plan/topic-plan-contract.md` | Planning actor | Shared authority for canonical topic-plan sections and blocking semantics |
| Session-entry README | `docs/request-shape-priority-workflow/README.md` | Creator | First entry for new sessions; defines read order and artifact hierarchy |
| Session-entry standards | `docs/request-shape-priority-workflow/standards.md` | Creator | Formal Observer / Dispatcher workflow contract |
| Cross-family dispatch board | `docs/request-shape-priority-workflow/checklist.md` | Creator | Queue / phase / blocked / next-dispatch board for cross-family workflow |
| Requirements baseline | `analysis/request-shape-priority-workflow/requirements.md` | Planning actor | Frozen business baseline for docs-first queue workflow |
| Technical spec | `analysis/request-shape-priority-workflow/technical-spec.md` | Planning actor | Execution-facing source of truth for artifact roles and queue rules |
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

1. 建立 `analysis/request-shape-priority-workflow/requirements.md`，凍結 docs-first session-entry、queue、blocked policy、Observer / Dispatcher 邊界、與 request-shape 主測試面定位。
2. 建立 `analysis/request-shape-priority-workflow/technical-spec.md`，將需求轉成 exact artifact responsibilities、entry precedence、queue contract、dispatch board / step tracker 分工、與 stop rules。
3. 建立 `docs/request-shape-priority-workflow/README.md`，使其成為新 session 第一入口，明確宣告三份 session-entry docs、固定讀取順序、與 workflow artifact hierarchy。
4. 建立 `docs/request-shape-priority-workflow/standards.md`，把 Observer / Dispatcher 的 allowed roles、禁止事項、phase / gate、dispatch rules、queue law、與 stop conditions 寫成 repo-visible contract。
5. 建立 `docs/request-shape-priority-workflow/checklist.md`，使其只承擔跨 family queue / phase / blocked / next dispatch / resume checks，不混用 topic-local completion gate。
6. 建立 `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`，使用 canonical topic-plan sections，並把本 topic workflow 停點明確寫成 review 後 wait-human-check。
7. 建立 `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`，只追蹤本 topic artifact 建立與 review readiness；不得把 cross-family dispatch board 抄進 step tracker。

## Validation / Acceptance Checks

- `docs/request-shape-priority-workflow/README.md`、`standards.md`、`checklist.md` 全部存在，且 `README.md` 被明確宣告為 required first entry。
- docs trio 一致記錄固定讀取順序：
  1. `README.md`
  2. `standards.md`
  3. `checklist.md`
- docs trio、requirements、technical-spec、plan 一致宣告 `analysis/**` / `plan/**` 是 workflow artifacts，不是新 session 的 primary entry。
- `checklist.md` 僅記錄 queue / phase / blocked / next dispatch / resume checks，不作為任何單一 topic 的 completion gate。
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md` 存在，且只承擔本 topic 自己的 completion gate。
- family queue 在 docs / analysis / plan 中一致為：
  - `models`
  - `projects`
  - `tables` = `BLOCKED`
- `standards.md` 明確限制 allowed subAgent roles 為：
  - `Planner`
  - `Explorer`
  - `Plan-Creator`
  - `Plan-Reviewer`
  - `Code-Implementer`
  - `Code-Reviewer`
- `standards.md` 明確禁止 Observer / Dispatcher 直接實作、改檔、commit、push、開 PR、或 release。
- `technical-spec.md` 與 `standards.md` 明確把 `tests/unit/request_contract/**` 定位為主 request-shape surface，並把 `tests/contracts` 定位為 policy / guard surface。
- `Reviewer Handoff` 維持單一 machine-consumable JSON 物件。

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
- 本 topic 完成 plan finalization 與 planner final gate 後，停在 wait-human-check；後續是否進 implementation 由 human 決定。
- 若未來 human 決定進 implementation，應另依 docs-first session-entry 重新進場。

## Open Questions / Unresolved Items

- None.
