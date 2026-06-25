# Request-Gate Projects Champion

## Analysis Routing

- Analysis mode：strict
- Source of truth：`analysis/request-gate-projects-champion/technical-spec.md`
- Business guardrail：`analysis/request-gate-projects-champion/requirements.md`
- Human override：absent

## Goal / Outcome

為單一 bounded endpoint `modelRepository/projects/champion` / `get_champion_model` 維持可審查的 topic-local contract，包含 requirements、technical spec、plan、step tracker，與 PR 已提交的 champion-only request-contract test / fixture deliverables；並把 reviewer 指出的 workflow state drift 同步修正為 reviewer-first flow -> creator bounded fix -> planner final gate -> human check，同時凍結 request method、path shape、request construction chain，且不擴張到 `src/**`、response / error contract、或 `projects` family 其他 API。

## Scope

- **In scope**:
  - `analysis/request-gate-projects-champion/requirements.md`
  - `analysis/request-gate-projects-champion/technical-spec.md`
  - `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
  - `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`
  - 已提交的 champion-only request-contract deliverables：
    - `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
    - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
    - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`
  - endpoint inventory、docs-suffice evidence、legacy request evidence sync、bounded write set、stop conditions、reviewer-first workflow boundary

- **Out of scope**:
  - `src/**`
  - 本輪對任何 execution artifact content 的再修改
  - `docs/request-shape-priority-workflow/**`
  - shared workflow contract
  - `plan/request-gate-projects-champion/request-gate-projects-champion.spec.md`
  - `modelRepository/projects` 其他 API
  - response / error contract
  - execution / TDD
  - review、PR、release

## Locked Decisions

- 本 topic 只處理 `modelRepository/projects/champion` / `get_champion_model`，不得順手擴到 `list_projects`、`get_project`、或 `tables-link surface`
- planning evidence 採 **docs-suffice baseline**，並同步寫回 human-provided legacy request evidence
- human-provided legacy source evidence 已凍結 request contract 的 method / path / construction chain：`get_champion_model(...)` -> `get_project_by_name(...)` -> `get_champion_model_url(user_response.data)` -> `fetch_champion_model(...)`
- `get_champion_model_url(project_item)` 以 `project_item.id` 組出 `"{BASE_PROJECT_URL}/{project_item.id}/champion"`；`fetch_champion_model(...)` 以 `async_web_session.get(url=champion_model_url, headers=headers)` 發送 request
- 本 topic contract 必須與 PR 已提交的 champion-only request-contract artifacts 對齊；本輪 bounded fix 只允許更新四份 planning/analysis/step artifacts，既有 execution artifact 內容維持 frozen
- workflow 順序固定為：creator artifacts 完成 -> reviewer flow -> creator bounded fix（若 reviewer 要求）-> planner final gate -> human check
- Stable-library intent 明確為 **absent**：不修改 `src/**`、`README.md`、`VERSION`，不涉及 release timing
- 本 topic 已交付的 champion-only request-contract artifacts 固定為：
  - `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`
- 後續 forbidden modification set 固定為：既有 `projects_request_gate` shared artifacts、上述 champion-only artifacts 的內容、shared workflow docs、與其他 endpoint artifacts；若 execution 需要突破此集合，必須停止並交還 human check

## Boundaries / Exclusions

- Plan-Creator 本輪只能建立 topic-local planning artifacts，不得執行 reviewer、implementation、PR、或 release 工作
- Reviewer 必須獨立進行；creator 不得自行宣告 `approved`
- Main Agent / human 負責 reviewer routing、planner final gate routing、是否另開 execution topic、以及是否要求補充超出 frozen request evidence 的語意
- 本 topic 不得重開 queue order、surface naming、或 shared workflow contract
- 本 topic 不得把 `projectId` 取得流程、`files` payload 驗證、或 `_get_model_type` 邏輯混入 champion request-gate planning

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: 使用 canonical creator -> reviewer -> publish -> merge 流程；本 topic 的最新 creator bounded rework 已完成並形成最新版 draft，但這一版尚未取得新的 reviewer acceptance，因此當前 handoff state 是等待 reviewer 重新檢視；只有 reviewer 接受後，才可再依 topic-local routing 進入 planner final gate；human check 仍只能發生在 planner final gate 完成之後；不包含 release 動作，execution / TDD 仍不在本 topic scope
- **Step-tracker alignment**: `plan/request-gate-projects-champion/request-gate-projects-champion.step.md` 的 creator-owned planning / rework steps 已全部完成；step tracker 只表達 creator completion gate，因此當所有 creator steps 完成時，current state 應對齊為 `review-ready`，而不是直接宣告 reviewer acceptance
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

- 最新 reviewer blocker 已觸發同 topic 內的 bounded rework；本輪 creator fix 完成後，下一個外部 gate 是 reviewer 重新檢視，而不是 planner final gate
- 當前 `review-ready` 僅表達 creator 端已完成最新版 draft，並等待新的 reviewer acceptance；不得把它解讀成 `approved`、planner final gate 完成、或 human-check 完成
- 若 human 要求 execution/TDD，僅可沿用本輪已凍結的 request evidence；若需要超出該範圍的語意，必須另行停在 human check
- 若後續工作 drift 到 `src/**`、`tests/**`、或 shared workflow docs，必須先修正 topic routing，而不是在本 topic 內擴 scope

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-projects-champion/requirements.md` | Plan-Creator | 凍結 bounded endpoint、write set、與 reviewer-first business baseline |
| Topic technical spec | `analysis/request-gate-projects-champion/technical-spec.md` | Plan-Creator | 凍結 endpoint inventory、request contract draft、landing path、與 stop rules |
| Topic plan | `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md` | Plan-Creator | 本 topic 的 canonical execution contract 與 reviewer handoff contract |
| Step tracker | `plan/request-gate-projects-champion/request-gate-projects-champion.step.md` | Plan-Creator | 本輪 creator completion gate，需同時對齊四份 planning artifacts 與已提交 champion-only request-contract deliverables，但不承擔 reviewer、planner final gate、或 human-check 狀態 |

Artifact path notes:

- `src/**`：本 topic 不修改
- `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`：屬於本 topic 已提交 deliverable；本輪 bounded fix 不修改內容
- `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`：屬於本 topic 已提交 deliverable；本輪 bounded fix 不修改內容
- `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`：屬於本 topic 已提交 deliverable；本輪 bounded fix 不修改內容
- 其餘 `tests/unit/request_contract/projects_request_gate/**`：shared / existing artifacts，不在本 topic 修改範圍
- `docs/request-shape-priority-workflow/**`：本 topic 不修改
- `README.md` / `VERSION`：本 topic 不修改
- 若出現未列路徑的變更，視為 plan drift，必須停止並先回到 canonical reviewer / planner routing

## Implementation Steps

1. 對照 reviewer feedback、shared workflow contract、與 human-provided legacy source evidence，確認四個 topic-local artifacts 的 bounded update 範圍。
2. 更新 `analysis/request-gate-projects-champion/requirements.md`，把 request evidence 改寫成 legacy-source-confirmed，並移除 `legacy source evidence missing` gate。
3. 更新 `analysis/request-gate-projects-champion/technical-spec.md`，同步 method、path shape、request construction chain、transport call、與 schema presence。
4. 更新 `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`，把 current state、routing notes、與 locked decisions 對齊為 evidence-synced `review-ready` handoff state。
5. 更新 `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`，把 creator-owned completion gate 明確擴至四份 planning artifacts 與已提交 champion-only request-contract deliverables，不混入 planner final gate 或 human-check state。

## Validation / Acceptance Checks

- 四個 topic-local planning artifacts 都存在，且內容一致鎖定 `modelRepository/projects/champion` / `get_champion_model`
- `request-gate-projects-champion.plan.md` 使用 canonical required sections，且 `Reviewer Handoff` 為 machine-consumable JSON
- `Artifact Paths` 僅列四個允許落地的 topic-local files
- 四個 artifacts 一致宣告：
  - planning evidence 採 docs-suffice
  - human-provided legacy source evidence 已同步寫回 request method、path shape、request construction source、與 transport call
  - reviewer-first flow 存在，且本輪 post-rework 下一步為 reviewer acceptance；只有 reviewer 接受後才進入 planner final gate，planner final gate 再先於 human check
  - topic scope 已承認下列已提交 deliverables：
    - `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
    - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
    - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`
  - 本輪 bounded fix 不得修改任何 execution artifact content，且 downstream forbidden modification set 不得放寬為 shared artifact mutation
  - 不得修改 `src/**`、`docs/request-shape-priority-workflow/**`
- step tracker 的 `## Implementation Steps` 全部完成，且 creator completion gate 明確涵蓋已提交 champion-only request-contract deliverables，但不額外維護 planner final gate、或 human-check state

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

- 本 topic 不含 stable-library surface 變更，merge 後不需要 VERSION bump、README 更新、release notes、或 release timing 動作
- 本輪修正不啟動 publish / release routing；下一個外部 gate 是 reviewer acceptance；只有 reviewer 接受後，才可進入 planner final gate，之後才 wait human check
- `merged` 為 terminal；本 topic 無 `released` 狀態需求

## Open Questions / Unresolved Items

- [OPEN] `sas_viya_get_headers(...)` 的 shared helper 展開細節未在本 topic 追溯；本輪只凍結 docs-confirmed 的 required header subset `Authorization`、`Accept`
- [BLOCKED] 未來 champion request gate 是否能在完全不修改既有 `projects_request_gate` harness / fixtures / tests 的前提下完成，尚未有 repo-visible proof；若答案是否定，必須先回到 human check
