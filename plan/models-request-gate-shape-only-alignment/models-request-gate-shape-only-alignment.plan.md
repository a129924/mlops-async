> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/models-request-gate-shape-only-alignment/technical-spec.md`
>   (`sha256: 9cfea55f07db4ea93f0c98295f362a57be1dd71b4269b80f7c4af1b457cd0410`)
> - Business guardrail:
>   `analysis/models-request-gate-shape-only-alignment/requirements.md`
>   (`sha256: 9c1c43467cd1570a0251d6e38bb57599b562516a0484cf2897c83bc554a8ea89`)
> - This plan maps 100% to the technical spec and does not reopen architecture, scope, or
>   contract decisions.
> - No human `override` instruction changes that priority rule for this topic.

## Goal / Outcome

- 建立 `models-request-gate-shape-only-alignment` 的 repo-visible execution contract，讓後續
  creator 只在授權的 `models_request_gate` 測試檔與 mock-response fixtures 內，把
  `list_models` 與 `get_model` 收斂成純 request-only / shape-only 測試。
- Topic 完成時，reviewer 應能直接依本 plan 與既有 analysis artifacts 判斷：
  - `GET /modelRepository/models` 只保留 bare GET 與既有
    `filter=in(projectId,"proj-uuid")` semantics
  - `GET /modelRepository/models/{modelId}` 只保留 direct identifier branch
  - 測試 oracle 不再依賴 response payload、response header、fixture equality、或 returned
    object assertions

## Scope

- **In scope**:
  - `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.plan.md`
  - `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.step.md`
  - `tests/unit/request_contract/models_request_gate/conftest.py`
  - `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
  - `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
  - `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json`
  - `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json`

- **Out of scope**:
  - `src/**`
  - `pyproject.toml`
  - `uv.lock`
  - `docs/**`
  - `analysis/**` 既有檔案改寫
  - 其他 topic 的 `plan/**`
  - `tests/unit/request_contract/projects_request_gate/**`
  - `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json`
  - `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json`
  - 第三個 endpoint、額外 HTTP method、額外 query semantics、response / error contract work

## Locked Decisions

- 本 topic 是 **test-only implementation topic with no stable-library surfaces**；stable-library
  intent 明確 absent，不需要 `## Stable library metadata`。
- Endpoint 邊界已鎖定為：
  - `GET /modelRepository/models`
  - `GET /modelRepository/models/{modelId}`
- `list_models` 只允許：
  - bare GET
  - 既有 `filter=in(projectId,"proj-uuid")`
- `get_model` 只允許 direct identifier branch。
- 非 direct identifier 的 `get_model` variants、額外 `list_models` query semantics、與任何
  response-oriented assertion 都不得在本 topic 內重新打開。
- `*.request-flow.json` 是 source-observed request evidence，於本 topic 維持唯讀。
- `*.mock-responses.json` 只扮演 execution scaffolding，不是 correctness oracle。
- 後續 creator 若需要修改未授權檔案、重寫 request-flow evidence、或重開 architecture /
  contract decision，必須停止並回到 `human-check`，不得在本 topic 內自行擴 scope。

## Boundaries / Exclusions

- Planning actor 只負責本 topic 的 planning artifacts。
- Creator 只可在本 plan `Scope` 與 `Artifact Paths` 列出的授權檔案內實作，不得把 reviewer
  或 Main Agent 的工作混入 `Implementation Steps`。
- Reviewer 負責獨立評估 request-only / shape-only 邊界是否成立，不得在審查過程中重寫 topic
  scope。
- Main Agent 負責 publish routing、PR flow、merge 後同步與任何人工作業協調。
- 本 topic 不處理 `projects_request_gate`、不處理產品碼、不處理依賴調整，也不重開本 topic 的
  requirements / technical-spec。
- 若後續工作需要動到 `tests/unit/request_contract/models_request_gate/__init__.py` 或其他未列
  路徑，視為 plan-alignment failure，而不是 implementation 細節。

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this
  topic stops at `merged` and does not declare a release action.
- **Step-tracker alignment**:
  `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.step.md`
  已建立且 `## Implementation Steps` 全部維持 `[ ]`，因此目前仍停留在 `planned`，待 creator
  開始執行後才可進入 `creator-in-progress`。
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

- 本 topic 不建立 `review-log`；單輪 reviewer verdict 可直接透過 canonical `Reviewer Handoff`
  JSON 路由。
- 本 topic 不宣告 round cap。
- 任一 drift 若超出 strict-mode analysis、精確 artifact paths、或鎖定 query / branch
  semantics，應停止並回到 `human-check`，而不是在 creator pass 內修補 topic 定義。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical workflow status model, transitions, and reviewer handoff contract |
| Shared topic-plan contract | `plan/topic-plan-contract.md` | Planning actor | Shared authority for canonical topic-plan sections and blocking semantics |
| Requirements baseline | `analysis/models-request-gate-shape-only-alignment/requirements.md` | Planning actor | Read-only business guardrail for request-only / shape-only scope |
| Technical spec | `analysis/models-request-gate-shape-only-alignment/technical-spec.md` | Planning actor | Read-only execution-facing source of truth for future creator work |
| Topic plan | `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.step.md` | Creator | Machine-readable completion gate that mirrors `## Implementation Steps` |
| Harness alignment | `tests/unit/request_contract/models_request_gate/conftest.py` | Creator | Remove response-equality oracle while keeping intercepted request capture and request-shape checks |
| list_models test | `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py` | Creator | Enforce shape-only assertions for bare GET, project filter, and blocked out-of-scope filter semantics |
| get_model test | `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py` | Creator | Enforce shape-only assertions for direct identifier and blocked non-direct variants |
| list_models mock scaffolding | `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json` | Creator | Minimal mock response stub that lets `list_models` invocation complete without becoming a response oracle |
| get_model mock scaffolding | `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json` | Creator | Minimal mock response stub that lets direct-identifier `get_model` invocation complete without becoming a response oracle |
| list_models request evidence | `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json` | Creator | Read-only source-observed request evidence for list-models request shape |
| get_model request evidence | `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json` | Creator | Read-only source-observed request evidence for direct-identifier get-model request shape |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: no change in this topic.
- `src/**`: no change in this topic.
- `pyproject.toml`: no change in this topic.
- `uv.lock`: no change in this topic.
- `docs/**`: no change in this topic.
- `analysis/**`: existing artifacts are read-only inputs in this topic.
- 若後續工作出現在未列出的路徑，必須先回到 planner / human-check 修正合約，不能視為可接受的
  implementation 漂移。

## Implementation Steps

1. 更新 `tests/unit/request_contract/models_request_gate/conftest.py`，移除把
   `FakeResponse` 或 source-observed response fixture 當成 equality oracle 的流程，同時保留
   intercepted request capture、request-shape 對齊、required header subset 驗證與單一
   outbound request gate。
2. 收窄
   `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json`
   與
   `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json`，
   只保留讓 invocation 成功完成所需的最小 mock scaffolding；不得讓 response payload、
   response headers、或 fixture equality 再次成為測試 oracle。
3. 重寫
   `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`，
   使正向 case 只覆蓋 bare GET 與既有
   `filter=in(projectId,"proj-uuid")`，並僅斷言 request method、path、required header
   subset、query semantics 與 body shape；unsupported filter semantics 只作為 blocked gate
   保留。
4. 重寫
   `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`，
   使正向 case 只覆蓋 direct identifier branch，且只斷言 request method、path、
   required header subset、query/body shape；非 UUID 字串、dict-like item、`refresh=True`
   等既有 blocked variants 維持為 out-of-scope gate。
5. 執行並通過下列驗證，不得為了通過而修改授權範圍外檔案：
   - `uv run --python 3.10.0 pytest tests/unit/request_contract/models_request_gate -q`
   - `uv run --python 3.10.0 ruff check tests/unit/request_contract/models_request_gate`
   - `uv run --python 3.10.0 pyright`
6. 確認最終 diff 只落在本 plan 授權的六個 implementation 檔案，且：
   - `*.request-flow.json` 維持未改動
   - `projects_request_gate` 未改動
   - 測試中不再以 returned object、response payload、response header、或 fixture equality
     作為成功 oracle

## Validation / Acceptance Checks

- `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.plan.md`
  存在，且使用 canonical topic-plan sections 與 canonical order。
- 本 plan 明確記錄 strict-mode analysis routing、兩份 analysis input 的引用路徑與
  `sha256`。
- `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.step.md`
  存在，且 `## Implementation Steps` 與本 plan 一一對齊。
- Stable-library intent 在本 plan 中被明確宣告為 absent，且沒有 `README.md`、`VERSION`、
  release timing、或 release notes 的隱含工作。
- Creator 完成後，`test_list_models_request_contract.py` 只保留：
  - bare GET 正向 case
  - `filter=in(projectId,"proj-uuid")` 正向 case
  - 已鎖定的 out-of-scope filter semantics gate
- Creator 完成後，`test_get_model_request_contract.py` 只保留：
  - direct identifier 正向 case
  - 已鎖定的 blocked variants gate
- Creator 完成後，`conftest.py` 不再把 response equality 納入 oracle，但仍保留 request
  capture 與 request-shape 檢查。
- `list_models.request-flow.json` 與 `get_model_by_id.request-flow.json` 於本 topic 維持唯讀。
- 最終 diff 若出現 `src/**`、`pyproject.toml`、`uv.lock`、`docs/**`、`analysis/**`、
  其他 topic 的 `plan/**`、或 `tests/unit/request_contract/projects_request_gate/**`，視為
  blocking drift。
- `Reviewer Handoff` 必須維持單一 machine-consumable JSON 物件。

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

- 本 topic merge 後不需要 README 更新、VERSION bump、release notes、或 repository
  release action。
- Main Agent 如需進行本地同步，應依一般 merge 後流程處理，但不屬於本 topic 的 creator /
  reviewer 工作。
- 本 topic 在 `merged` 時即為 terminal。

## Open Questions / Unresolved Items

- None.
