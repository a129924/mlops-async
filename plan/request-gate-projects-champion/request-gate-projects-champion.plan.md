# Request-Gate Projects Champion

## Analysis Routing

- Analysis mode：strict
- Source of truth：`analysis/request-gate-projects-champion/technical-spec.md`
- Business guardrail：`analysis/request-gate-projects-champion/requirements.md`
- Human override：absent

## Workflow State Contract

- current_step: draft topic-local planning artifacts
- next_step: human check
- status: COMPLETE

## Goal / Outcome

為單一 bounded endpoint `modelRepository/projects/champion` / `get_champion_model` 建立可審查的 topic-local planning contract，包含 requirements、technical spec、plan、與 step tracker，並把 execution / TDD gate 明確停在 human 補齊 legacy source evidence 之後。

## Scope

- **In scope**:
  - `analysis/request-gate-projects-champion/requirements.md`
  - `analysis/request-gate-projects-champion/technical-spec.md`
  - `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
  - `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`
  - endpoint inventory、docs-suffice evidence、bounded write set、stop conditions、human-check boundary

- **Out of scope**:
  - `src/**`
  - `tests/unit/request_contract/projects_request_gate/**`
  - `docs/request-shape-priority-workflow/**`
  - shared workflow contract
  - `plan/request-gate-projects-champion/request-gate-projects-champion.spec.md`
  - `modelRepository/projects` 其他 API
  - response / error contract
  - execution / TDD
  - review、PR、release

## Locked Decisions

- 本 topic 只處理 `modelRepository/projects/champion` / `get_champion_model`，不得順手擴到 `list_projects`、`get_project`、或 `tables-link surface`
- planning evidence 採 **docs-suffice**
- `utils/_api/project.py::fetch_champion_model` 的 repo-visible source evidence 目前缺失；execution/TDD 必須等 human 補件或明確 override 才可前進
- 本 topic 為 **planning-only** topic；不建立 `spec.md`，不建立 tests-side artifacts
- Stable-library intent 明確為 **absent**：不修改 `src/**`、`README.md`、`VERSION`，不涉及 release timing
- 未來 implementation landing path 只允許在 `tests/unit/request_contract/projects_request_gate/` 下新增 champion 專屬檔案，例如：
  - `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.request-flow.json`
  - `tests/unit/request_contract/projects_request_gate/fixtures/get_champion_model.mock-responses.json`
- 若未來 execution 需要修改既有 `projects_request_gate` artifacts、shared workflow docs、或其他 endpoint artifacts，必須停止並交還 human check

## Boundaries / Exclusions

- Plan-Creator 本輪只能建立 topic-local planning artifacts，不得執行 reviewer、implementation、PR、或 release 工作
- Reviewer 必須獨立進行；本輪不得自行進入 `reviewer-in-progress`
- Main Agent / human 才能決定是否派 reviewer、是否放行 execution、以及是否接受 legacy source evidence gap 的補件方式
- 本 topic 不得重開 queue order、surface naming、或 shared workflow contract
- 本 topic 不得把 `projectId` 取得流程、`files` payload 驗證、或 `_get_model_type` 邏輯混入 champion request-gate planning

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: 使用 canonical creator -> reviewer -> publish -> merge 流程；但本 topic 在本輪 commit 後停在 human check，不自動派 reviewer，也不包含 release 動作
- **Step-tracker alignment**: `plan/request-gate-projects-champion/request-gate-projects-champion.step.md` 的 creator-owned planning steps 已完成；independent review 尚未開始
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

- 本輪停在 human check；只有在 human 明確 dispatch reviewer 後，才可進入 `reviewer-in-progress`
- 若 human 要求 execution/TDD，必須先補齊或明確放行 legacy source evidence gap，且另由下游角色處理
- 若後續工作 drift 到 `src/**`、`tests/**`、或 shared workflow docs，必須先修正 topic routing，而不是在本 topic 內擴 scope

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-projects-champion/requirements.md` | Plan-Creator | 凍結 bounded endpoint、write set、與 human-check business baseline |
| Topic technical spec | `analysis/request-gate-projects-champion/technical-spec.md` | Plan-Creator | 凍結 endpoint inventory、request contract draft、landing path、與 stop rules |
| Topic plan | `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md` | Plan-Creator | 本 topic 的 canonical execution contract 與 reviewer handoff contract |
| Step tracker | `plan/request-gate-projects-champion/request-gate-projects-champion.step.md` | Plan-Creator | 本輪 planning creator steps completion gate 與 human-check stop marker |

Artifact path notes:

- `src/**`：本 topic 不修改
- `tests/unit/request_contract/projects_request_gate/**`：本 topic 不修改
- `docs/request-shape-priority-workflow/**`：本 topic 不修改
- `README.md` / `VERSION`：本 topic 不修改
- 若出現未列路徑的變更，視為 plan drift，必須停止並先回到 human check

## Implementation Steps

1. 盤點 `modelRepository/projects/champion` / `get_champion_model` 的 repo-visible surface、queue precedence、與 precedent，且不擴張到其他 `projects` APIs。
2. 建立 `analysis/request-gate-projects-champion/requirements.md`，凍結 bounded write set、execution prerequisite、landing path、與 human-check boundary。
3. 建立 `analysis/request-gate-projects-champion/technical-spec.md`，凍結 endpoint inventory、request contract draft、evidence gap、與 stop conditions。
4. 建立 `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`，使用 canonical plan contract 與 reviewer handoff JSON。
5. 建立 `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`，只追蹤本輪 planning creator work。
6. 以 topic 名稱提交 draft plan commit，然後停在 human check，不進 reviewer、execution、PR、或 release。

## Validation / Acceptance Checks

- 四個 topic-local planning artifacts 都存在，且內容一致鎖定 `modelRepository/projects/champion` / `get_champion_model`
- `request-gate-projects-champion.plan.md` 使用 canonical required sections，且 `Reviewer Handoff` 為 machine-consumable JSON
- `Artifact Paths` 僅列四個允許落地的 topic-local files
- 四個 artifacts 一致宣告：
  - planning evidence 採 docs-suffice
  - execution/TDD 需 human 補齊 legacy source evidence 才可前進
  - 未來 implementation 只能新增 `tests/unit/request_contract/projects_request_gate/` 下的 champion 專屬檔案
  - 不得修改既有 `projects_request_gate` artifacts
  - 不得修改 `src/**`、`tests/unit/request_contract/projects_request_gate/**`、`docs/request-shape-priority-workflow/**`
- step tracker 的 `## Implementation Steps` 全部完成，且 `Workflow Stages` 仍保留未開始的 independent review / human dispatch 停點

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
- 本 topic 的自動流程在本輪 draft plan commit 後即停止；後續 reviewer / publish routing 由 human 另行決定
- `merged` 為 terminal；本 topic 無 `released` 狀態需求

## Open Questions / Unresolved Items

- [BLOCKED] `utils/_api/project.py::fetch_champion_model` 與 `get_champion_model_url` 的 repo-visible legacy source evidence 仍缺失；human 需決定補件來源或明確 override，execution/TDD 才可前進
- [BLOCKED] 未來 champion request gate 是否能在完全不修改既有 `projects_request_gate` harness / fixtures / tests 的前提下完成，尚未有 repo-visible proof；若答案是否定，必須先回到 human check
