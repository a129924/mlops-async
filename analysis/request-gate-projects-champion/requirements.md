# Request-Gate Projects Champion Requirements

## Purpose

本文件凍結 `request-gate-projects-champion` 的 planning baseline，讓後續 workflow 只針對單一 bounded endpoint
`modelRepository/projects/champion` / `get_champion_model` 建立 topic-local planning artifacts，並把 reviewer 指出的
workflow state drift 收斂為 reviewer-first flow、creator bounded fix、planner final gate、最後才 wait human check；
本輪不得直接把 creator commit 視為 human-check 終點，也不得擴張到 implementation、TDD、或
`modelRepository/projects` 其他 API。

## Scope

本 topic 的需求只涵蓋：

- endpoint inventory 與 precedent 盤點
- docs-suffice planning evidence 凍結
- topic-local analysis artifacts：
  - `analysis/request-gate-projects-champion/requirements.md`
  - `analysis/request-gate-projects-champion/technical-spec.md`
- topic-local plan artifacts：
  - `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
  - `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`
- bounded write set、stop conditions、reviewer-first workflow、與未來 implementation landing path 凍結

本 topic 不涵蓋：

- `src/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `docs/request-shape-priority-workflow/**`
- shared workflow contract 或 shared board 改寫
- `modelRepository/projects` 其他 API
- response / error contract
- execution / TDD 實作
- release、PR、或 reviewer / planner final gate 執行

## Actors and ownership

- Primary actor：Plan-Creator
- Downstream actor：Plan-Reviewer
- Human owner：human check / legacy evidence 補件決策者

Ownership model：

- docs-suffice planning with reviewer-first flow；若 reviewer 要求修正，creator 在同 topic 內完成 bounded fix，之後才交 planner final gate 與 human check

## Measurable requirements

1. **Bounded endpoint freeze**
   - Actor: Plan-Creator
   - Condition: 建立 topic-local planning artifacts 時
   - Required outcome: scope 只允許 `modelRepository/projects/champion` / `get_champion_model`
   - Metric / decision rule: 若 artifact 提到 `list_projects`、`get_project`、`tables`、或其他 `projects` family API 的實作延伸，視為超出基線
   - Evidence signal: requirements、technical-spec、plan、step 四份文件都只描述 champion endpoint
   - Failure meaning: topic 會從 bounded endpoint 漂移成 family-level work

2. **Docs-suffice planning evidence**
   - Actor: Plan-Creator
   - Condition: 本 topic author planning contract 時
   - Required outcome: planning evidence 只依賴 repo-visible docs surfaces，不要求先修改 code 或 tests
   - Metric / decision rule: 至少凍結下列 evidence：
     - `docs/request-shape-priority-workflow/checklist.md`
     - `docs/request-shape-priority-workflow/standards.md`
     - `docs/api-endpoints/swagger-spec/projects-spec.yaml`
     - `docs/api-endpoints/swagger-spec/openapi-complete.yaml`
     - `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md`
   - Evidence signal: technical-spec 內有 endpoint inventory、request contract draft、precedent 與 gap 說明
   - Failure meaning: 若 planning 仍需依賴口頭記憶或未落地 evidence，後續 reviewer 無法判斷 contract 是否完整

3. **Bounded write set freeze**
   - Actor: Plan-Creator
   - Condition: 本 topic 落地 planning artifacts 時
   - Required outcome: 只允許四個 topic-local files 被建立或修改
   - Metric / decision rule: 允許寫入只限：
     - `analysis/request-gate-projects-champion/requirements.md`
     - `analysis/request-gate-projects-champion/technical-spec.md`
     - `plan/request-gate-projects-champion/request-gate-projects-champion.plan.md`
     - `plan/request-gate-projects-champion/request-gate-projects-champion.step.md`
   - Evidence signal: `git status` 只出現上述四檔
   - Failure meaning: 若變更漂移到其他檔案，topic contract 已失真

4. **Execution boundary freeze**
   - Actor: Human reviewer / downstream planner
   - Condition: 未來想把本 topic 推進到 execution/TDD 時
   - Required outcome: 必須先由 human 補齊或明確放行 legacy source evidence，才可進入 tests-side authoring
   - Metric / decision rule: 若 repo 仍無 `utils/_api/project.py::fetch_champion_model` 的 repo-visible source evidence，execution/TDD 一律不得自動前進
   - Evidence signal: plan 與 technical-spec 一致把 `legacy source evidence missing` 列為 stop condition
   - Failure meaning: 若直接依 docs 推進測試實作，request gate 會混入未驗證的 legacy semantics

5. **Future implementation landing path freeze**
   - Actor: future Code-Implementer
   - Condition: human 之後放行 execution topic 時
   - Required outcome: 實作只能新增 `tests/unit/request_contract/projects_request_gate/` 下的 champion 專屬檔案
   - Metric / decision rule: 不得修改既有 `projects_request_gate` artifacts；若需要修改既有 `conftest.py`、fixtures、或 tests，必須重新停在 human check
   - Evidence signal: plan 與 technical-spec 一致列出 new champion-only landing path 與 forbidden modification rule
   - Failure meaning: 若後續 topic 直接改既有 artifacts，bounded endpoint 會被 shared harness drift 汙染

6. **Reviewer-first workflow boundary**
   - Actor: workflow router / downstream planner
   - Condition: 本輪 planning artifacts 建立或 bounded rework commit 完成後
   - Required outcome: 先以 reviewer flow 作為外部前置 gate；若 reviewer 提出 blocking feedback，creator 在同 topic 內完成 bounded fix，之後由 planner final gate 決定是否交 human check
   - Metric / decision rule: step tracker 只表達 creator-owned completion gate，不承擔 reviewer、planner final gate、或 human-check 狀態
   - Evidence signal: requirements、technical-spec、plan、step 一致宣告 reviewer-first flow；本輪 creator rework 完成後的下一個外部 gate 是 planner final gate；且 `step.md` 只保留 creator completion gate
   - Failure meaning: 若 artifacts 仍把本輪 creator rework commit 直接視為 human-check 終點，workflow phase 會與實際路由衝突

## Contradictions surfaced and resolved

1. `swagger docs 已有 champion endpoint 描述` vs `execution/TDD 需要 source-level legacy evidence`
   - Resolution: planning 採 docs-suffice；execution/TDD 則必須等 human 補齊 legacy source evidence 才能前進

2. `champion endpoint 使用場景依賴 list_projects 先找 projectId` vs `本 topic 只允許單一 bounded endpoint`
   - Resolution: planning 只把 `projectId` 視為既有前提，不把 `list_projects` 取回流程納入本 topic

3. `未來可能需要新增 tests` vs `本輪不得修改 tests/**`
   - Resolution: 只在 planning artifacts 凍結 future landing path；本輪不建立任何 test files

4. `projects_request_gate 可能需要 shared harness 支援` vs `不得修改既有 artifacts`
   - Resolution: 一律先視為 forbidden；若 execution 發現必須調整 shared harness，立即回到 human check

## Extreme-boundary checks

1. **Branch / worktree drift**
   - 若 planning artifacts 不是落在外部 managed worktree，而是直接落在 `dev`，視為違反本 topic 前提

2. **Scope drift**
   - 若 topic 開始觸碰 `src/**`、`tests/**`、或 shared workflow docs，立即停止

3. **Surface drift**
   - 若文件開始把 `modelRepository/projects/champion` 擴成 `modelRepository/projects` family，立即停止

4. **Evidence drift**
   - 若後續要求用缺失的 legacy source 細節直接推斷 request contract，立即停止並交 human

5. **Shared-artifact drift**
   - 若後續 implementation 需要修改既有 `projects_request_gate` artifacts、shared workflow board、或 shared contract，立即停止並另開決策

## Assumptions

- `docs/request-shape-priority-workflow/checklist.md` 將 `modelRepository/projects/champion / get_champion_model` 排在 queue order `06`
- `docs/api-endpoints/swagger-spec/projects-spec.yaml` 與 `openapi-complete.yaml` 已提供 `GET /modelRepository/projects/{projectId}/champion` 的 repo-visible request evidence
- `docs/api-endpoints/markdown-reference/SASCTL_ALIGNMENT.md` 已確認 `sasctl` 無直接取得 Champion Model 的方法
- repo 目前沒有可直接讀取的 `utils/_api/project.py` legacy source file，因此 execution/TDD 仍需 human 補件或明確 override

## Non-goals

- 不在此 topic 中修改 `src/**`
- 不在此 topic 中修改 `tests/unit/request_contract/projects_request_gate/**`
- 不在此 topic 中修改 `docs/request-shape-priority-workflow/**`
- 不在此 topic 中建立 `spec.md`
- 不在此 topic 中建立 request-flow fixture、mock-response fixture、或 request tests
- 不在此 topic 中處理 response / error contract
- 不在此 topic 中重排 shared queue 或解鎖其他 blocked surface

## Blockers

- `legacy source evidence missing`：repo-visible docs 雖足以支撐 planning，但不足以自動放行 execution/TDD；human 必須先補齊或明確放行 `utils/_api/project.py::fetch_champion_model` 與相關 URL / branch semantics evidence
- `shared-artifact mutation forbidden`：若未來 execution 需要修改既有 `projects_request_gate` artifacts、shared workflow docs、或其他 endpoint topic artifacts，必須先停在 human check

## Freeze status

Status: `FROZEN`
