# request-gate-projects-tables

## Goal / Outcome

為 `model-repository/projects` family 建立可審查的 request-only gate 測試（`list_projects`、`get_project_by_id`），並明確記錄 `model-repository/tables` family 因 HATEOAS conditional endpoint selection 觸發停止條件 §7，暫緩至人工決策後才可繼續。

**Projects** 已完成實作，本 topic 目標是確認實作符合 request-only 邊界，不含 response/error contract，並交付可審查的 plan 與實作產物。

**Tables** 在本 topic 內無任何可執行步驟，狀態為 `BLOCKED`，需人工明確授權後才可建立新 topic 繼續。

## Scope

- **In scope**:
  - `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md`
  - `plan/request-gate-projects-tables/request-gate-projects-tables.step.md`
  - `plan/request-gate-projects-tables/request-gate-projects-tables.spec.md`
  - `tests/unit/request_contract/projects_request_gate/**`（已實作；creator 負責確保通過 review gate）
    - `tests/unit/request_contract/projects_request_gate/__init__.py`
    - `tests/unit/request_contract/projects_request_gate/conftest.py`
    - `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py`
    - `tests/unit/request_contract/projects_request_gate/test_get_project_request_contract.py`
    - `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.request-flow.json`
    - `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.mock-responses.json`
    - `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.request-flow.json`
    - `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.mock-responses.json`

- **Out of scope**:
  - `src/mlops_async/**` production code（本 topic 不修改）
  - `docs/migration-map.md`（本 topic 不更新）
  - `docs/porting-ledger.md`（本 topic 不更新）
  - `pyproject.toml` 與 `uv.lock`（本 topic 不修改）
  - `README.md`、`VERSION`（本 topic 不修改）
  - response / error contract（本 topic 不包含）
  - `sasctl.ModelRepository.get_project` 的 champion endpoint / name / object branch（多步序列，超出本 topic）
  - `model-repository/tables` 所有 API（tables 整個 family 因 HATEOAS 停止，等待人工決策）
  - `analysis/request-gate-projects-tables/**`（本 topic 不建立 analysis artifacts）

## Locked Decisions

- 本 topic 為 **request-only gate**：projects 的 list 與 get 只做 request-contract 測試，不做 response/error contract。
- `get_project_by_id` 在本 topic 只允許 **direct identifier branch**（UUID 字串傳入），非 direct-request variants（champion、object、name）全部 blocked。
- `list_projects` 在本 topic 只允許 **bare GET** 與 **limit=1000** 兩個已確認 query semantics；其他 query fields 不得納入。
- `pyproject.toml` 與 `uv.lock` 不得在本 topic 修改，所有 mock/interception 只使用既有 repo dependencies。
- **Tables BLOCKED**：`model-repository/tables` 的所有端點因 HATEOAS conditional endpoint selection 觸發全域停止條件 §7，必須明確記錄為 `BLOCKED`，不得在本 topic 建立任何 tables 相關測試或 fixture。
- Stable-library intent 明確為 **absent**：本 topic 不修改 `src/mlops_async/**`，不需要 VERSION bump、README 改動或 release timing 動作。
- 已有實作代碼（`tests/unit/request_contract/projects_request_gate/**`）需通過 review gate，creator 不得在 review 前宣告 topic 完成。

## Boundaries / Exclusions

- Creator 的工作範圍限制在本 plan 的 `Scope` 章節所列路徑；若工作漂移至列外路徑，必須停止並先修正 plan。
- Reviewer 獨立裁決，不得在 review 過程中新增或修改 topic content。
- Main Agent 負責 worktree lifecycle、publish routing、PR flow、merge 後同步。
- Request-contract tests 只得比對 semantic request behavior：method、path、required header subset、query key/value semantics、body shape。不得比對 query order、host、content-length、connection headers、transport-generated headers。
- tables 的任何實作意圖（包含僅建立 fixture 或 spec）在取得人工授權前均為 out-of-scope。
- champion endpoint（需要多步序列 GET list → find by name → GET by id）超出本 topic；若後續 topic 需要，應另開 topic 並先進行 planner 分析。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: 使用 canonical creator -> reviewer -> publish -> merge 流程；本 topic 不含 release 動作。
- **Step-tracker alignment**: `plan/request-gate-projects-tables/request-gate-projects-tables.step.md` 的 `## Implementation Steps` 所有項目已完成（projects 實作已存在），因此本輪可由 `creator-in-progress` 前進到 `review-ready`。
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

- Tables BLOCKED 狀態屬於本 topic 的 `Open Questions / Unresolved Items`，不會阻擋 projects 部分進入 review/merge。
- 若 tables 取得人工授權，應另開獨立 topic（不在此 topic 內繼續）並從 planner 階段重新開始，以取得正確的 HATEOAS endpoint resolution 策略。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical status model and required topic-plan sections |
| Topic plan | `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md` | Planning actor | 本 topic 的執行契約與 handoff 規則 |
| Step tracker | `plan/request-gate-projects-tables/request-gate-projects-tables.step.md` | Creator | Implementation Steps completion gate（供 `plan-step-tracker` 讀取） |
| Behavior spec | `plan/request-gate-projects-tables/request-gate-projects-tables.spec.md` | Creator | request-only gate 行為規格與邊界 |
| Harness 與 conftest | `tests/unit/request_contract/projects_request_gate/conftest.py` | Creator | Layer 1 source-observed harness 實作 |
| list_projects 測試 | `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py` | Creator | list_projects bare GET 與 limit=1000 的 request-contract 測試 |
| get_project 測試 | `tests/unit/request_contract/projects_request_gate/test_get_project_request_contract.py` | Creator | get_project direct identifier branch 的 request-contract 測試 |
| list_projects request-flow | `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.request-flow.json` | Creator | list_projects Layer 1 source-observed raw flow fixture |
| list_projects mock-responses | `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.mock-responses.json` | Creator | list_projects mock answer set fixture |
| get_project_by_id request-flow | `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.request-flow.json` | Creator | get_project direct identifier Layer 1 source-observed raw flow fixture |
| get_project_by_id mock-responses | `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.mock-responses.json` | Creator | get_project direct identifier mock answer set fixture |

Artifact path notes:

- `analysis/request-gate-projects-tables/**`：本 topic 不建立 analysis artifacts，不需要此目錄。
- `docs/migration-map.md`：本 topic 不更新。
- `docs/porting-ledger.md`：本 topic 不更新。
- `src/mlops_async/**`：本 topic 不修改。
- `pyproject.toml` / `uv.lock`：本 topic 不修改。
- `README.md` / `VERSION`：本 topic 不修改。
- 若出現未列路徑的變更，視為 plan drift，必須先修正 plan 再繼續。

## Implementation Steps

1. 確認 `tests/unit/request_contract/projects_request_gate/conftest.py` 存在且符合 Layer 1 source-observed harness 規格；確認無 transport-noise 斷言、無 `pyproject.toml` / `uv.lock` 變更。
2. 確認 `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.request-flow.json` 存在，且只覆蓋 `bare_get` 與 `limit_1000` 兩個 case。
3. 確認 `tests/unit/request_contract/projects_request_gate/fixtures/list_projects.mock-responses.json` 存在，且 mock answer set 與 request-flow fixture 對應。
4. 確認 `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.request-flow.json` 存在，且只覆蓋 `direct_identifier` case。
5. 確認 `tests/unit/request_contract/projects_request_gate/fixtures/get_project_by_id.mock-responses.json` 存在，且 mock answer set 與 request-flow fixture 對應。
6. 確認 `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py` 通過測試，且所有 list_projects 測試只比對 semantic request behavior。
7. 確認 `tests/unit/request_contract/projects_request_gate/test_get_project_request_contract.py` 通過測試，且 get_project 只覆蓋 direct identifier branch；out-of-scope variants 觸發 `blocked_topic_scope_error`。
8. 建立 `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md`（本文件）。
9. 建立 `plan/request-gate-projects-tables/request-gate-projects-tables.step.md`。
10. 建立 `plan/request-gate-projects-tables/request-gate-projects-tables.spec.md`。

## Validation / Acceptance Checks

- `uv run --python 3.10.0 pytest tests/unit/request_contract/projects_request_gate -q` 全部通過，無 skip / xfail。
- `uv run --python 3.10.0 ruff check tests/unit/request_contract/projects_request_gate` 無 violations。
- `uv run --python 3.10.0 pyright` 無 strict mode errors（含 projects_request_gate 目錄）。
- `tests/unit/request_contract/projects_request_gate/**` 內無任何 `src/mlops_async/**`、`docs/migration-map.md`、或 `docs/porting-ledger.md` 的寫入或修改。
- Fixture 中不存在 tables 相關 endpoint（`/modelRepository/projects/{id}/tables` 或類似路徑）。
- `plan/request-gate-projects-tables/request-gate-projects-tables.step.md` 的 `## Implementation Steps` 所有項目均已標記為 `[X]`。
- `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md` 本文件存在，使用 canonical topic-plan sections，且 Reviewer Handoff 為合法 JSON。

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

- 本 topic 不含 stable-library surface 變更，merge 後不需要 VERSION bump、README 更新、release notes 或 release timing 動作。
- 本 topic 於 `merged` 狀態時即為 terminal。
- Tables BLOCKED 議題在 merge 後由人工另開 topic 處理，不屬於本 topic 的 post-merge action。

## Open Questions / Unresolved Items

### [BLOCKED] model-repository/tables — HATEOAS conditional endpoint selection（停止條件 §7）

**停止原因**: `model-repository/tables` family 的端點選擇依賴 HATEOAS link resolution。`sasctl.ModelRepository.list_tables` 透過先取得 project 的 `self` link、再從 project 的 `links` 陣列中找出對應的 tables href，才能決定最終 request path。此行為屬於全域停止條件 §7（conditional endpoint selection），無法從靜態 source 穩定推出單一 request contract。

**停止條件引用**:
- 停止條件 §7: conditional endpoint selection（來源：`analysis/api-client-porting-contract/technical-spec.md`）
- 行為描述：tables endpoint URL 由 project response 的 `links` 欄位動態決定，而非固定 path template；此屬 HATEOAS conditional routing，超出 Layer 1 source-observed request-shape gate 的可驗證範圍。

**後續人工決策點**:
1. 是否接受以固定 path template `/modelRepository/projects/{id}/tables` 替代 HATEOAS link resolution，並標記為 `intentionally_changed`？
2. 如接受 fixed path，由人工明確授權後，另開獨立 topic（不在此 topic 內繼續），從 planner 階段重新分析 `list_tables` 的 request contract。
3. 如不接受替代，tables 維持永久 BLOCKED 直到有對應的 HATEOAS resolution 策略被凍結在 analysis artifacts 中。

**本 topic 的 blocking 邊界**: tables BLOCKED 不影響 projects 部分的 review / merge 流程。
