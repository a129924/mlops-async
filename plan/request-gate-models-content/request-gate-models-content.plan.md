> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-gate-models-content/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-gate-models-content/requirements.md`
> - 本 plan 100% 對齊 single-endpoint / request-only analysis layer。
> - shared workflow docs 與 shared board 只保留 queue / background authority，不重開
>   shared workflow semantics。
> - 本 topic 仍是 implement lane；只是本輪 workflow 只推進 implement-plan artifacts、
>   draft-plan commit、plan review、`needs-rework` fix loop、reviewer 通過後的
>   `human-check`。
> - future request-contract implementation 仍需由後續 `Implementer` 在 frozen write set 內
>   執行。

## Goal / Outcome

- 建立 `request-gate-models-content` 的 implement lane plan，使後續 `Implementer` 可在不猜測的
  前提下，於 `tests/unit/request_contract/models_content_request_gate/**` 內落地
  `get_model_content` request-only gate
- 讓本輪 workflow 只在 topic-local plan artifacts 內完成：
  - implement-plan artifacts authoring
  - draft-plan commit 準備
  - plan review
  - `needs-rework` fix loop
  - reviewer 通過後停在 `human-check`
- 讓 reviewer 可依本 plan 與 analysis artifacts 驗證：
  - scope 只涵蓋 `GET /modelRepository/models/{modelId}/contents/{fileId}/content`
  - `ModelRepository.get_model_contents()` 不得作為正向入口
  - response payload / file-type semantics 不屬於本 topic

## Scope

- **In scope**:
  - `analysis/request-gate-models-content/requirements.md`
  - `analysis/request-gate-models-content/technical-spec.md`
  - `plan/request-gate-models-content/request-gate-models-content.plan.md`
  - `plan/request-gate-models-content/request-gate-models-content.spec.md`
  - `plan/request-gate-models-content/request-gate-models-content.step.md`
  - implement-plan workflow state：
    - draft-plan commit
    - plan review
    - `needs-rework` fix loop
    - reviewer 通過後的 `human-check`
  - future implementation files：
    - `tests/unit/request_contract/models_content_request_gate/__init__.py`
    - `tests/unit/request_contract/models_content_request_gate/conftest.py`
    - `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py`
    - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json`
    - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json`

- **Out of scope**:
  - `docs/request-shape-priority-workflow/**`
  - `src/**`
  - `pyproject.toml`
  - `uv.lock`
  - `tests/unit/request_contract/models_request_gate/**`
  - `tests/unit/request_contract/projects_request_gate/**`
  - 任何其他 endpoint
  - `ModelRepository.get_model_contents()` HATEOAS follow path
  - response payload semantics
  - file-type behavior
  - auth / CAS tables / `jobExecution` / champion / tables-link surface
  - release / push / PR actions

## Locked Decisions

- 本 topic 是 **request-only / single-endpoint / non-stable topic**；
  stable-library intent 明確 absent，不需要 `## Stable library metadata`
- queue 單位固定為 `modelRepository/models/content / get_model_content`
- endpoint 固定為 `GET /modelRepository/models/{modelId}/contents/{fileId}/content`
- 第一輪只允許 direct path；不得把 `ModelRepository.get_model_contents()` 當正向入口
- request contract 只驗證：
  - method `GET`
  - path `/modelRepository/models/{modelId}/contents/{fileId}/content`
  - query `{}`
  - body `None`
  - required header subset
- required header subset 只允許：
  - `If-Range=""`
  - `Range=""`
  - `Access-Quarantine=""`
  - `Authorization: Bearer ...`
- future implementation 明確要求單一 outbound request
- future implementation 不驗：
  - response payload semantics
  - `.json` / `.sas` / `.csv` file-type behavior
  - host
  - query order
  - transport-generated headers
  - timeout / auth proof / retries
- future implementation write set 只限：
  - `tests/unit/request_contract/models_content_request_gate/__init__.py`
  - `tests/unit/request_contract/models_content_request_gate/conftest.py`
  - `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py`
  - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json`
  - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json`
- 既有 `models_request_gate/**`、`projects_request_gate/**` 只可作 precedent，不得回寫

## Boundaries / Exclusions

- Planning actor 在本輪只負責 topic-local implement-plan authoring
- 本輪只推進 implement lane 的 plan workflow，不進 implementation
- 後續 `Implementer` 只可在本 plan `Artifact Paths` 列出的 future implementation files 工作
- `Reviewer` 只負責 bounded scope / contract drift / workflow drift 驗證
- Main Agent 負責後續 routing、review gate、publish、PR、merge orchestration
- shared workflow board 與 shared workflow contract 不得作為本 topic 的 edit target
- 若後續工作漂移到未列路徑，視為 plan-alignment failure，必須先回到 `blocked` 或
  `needs-rework`

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this
  topic is an implement lane, but the current pass stops at `human-check` before implementation
- **Step-tracker alignment**:
  `plan/request-gate-models-content/request-gate-models-content.step.md` 的
  `## Implementation Steps` 只表達 creator-owned implement-plan completion gate；
  `draft-plan-commit`、`plan-review`、`plan-review-fix-loop`、與 `human-check`
  由同檔的 `## Workflow Stages` 表達，不得混入 completion gate
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

- `human-check` 是本 topic 的外部 stop boundary，不是 workflow status
- draft-plan commit 是本 topic 在進 reviewer gate 前的必要 workflow step，但本輪不自動 commit
- `plan-review-fix-loop` 發生時，只允許在 topic-local plan artifacts 內修正
- reviewer 通過後，本 topic 停在 `human-check`，不自動進 implementation
- 本輪 draft-plan commit 已完成，且第一輪 reviewer 已回 `needs-rework`
- 最新 bounded fix 已限制在這 5 個 topic-local artifacts 內，且 reviewer re-entry 已通過
- 當前 topic 已合法停在 `human-check`，不自動建立
  `tests/unit/request_contract/models_content_request_gate/**`
- 若 future implementation 需要碰 write set 以外路徑，topic 必須停在 `blocked`
- 若 reviewer 指出 scope drift / contract drift / workflow drift，topic 必須回到
  `needs-rework`

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-models-content/requirements.md` | Planning actor | Business-intent guardrail and frozen scope baseline |
| Topic technical spec | `analysis/request-gate-models-content/technical-spec.md` | Planning actor | Execution-facing source of truth for the implement lane |
| Topic plan | `plan/request-gate-models-content/request-gate-models-content.plan.md` | Planning actor | Repo-visible canonical workflow contract for the implement-plan pass |
| Topic spec | `plan/request-gate-models-content/request-gate-models-content.spec.md` | Planning actor | Acceptance and scenario contract for the implement-plan workflow |
| Topic step tracker | `plan/request-gate-models-content/request-gate-models-content.step.md` | Creator | Machine-readable completion gate for implement-plan workflow and handoff |
| Future package marker | `tests/unit/request_contract/models_content_request_gate/__init__.py` | Creator | 新 request-contract surface 的 package anchor |
| Future harness | `tests/unit/request_contract/models_content_request_gate/conftest.py` | Creator | 單一 outbound request capture 與 request-only assertion harness |
| Future request-contract test | `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py` | Creator | `get_model_content` 的 request-only gate |
| Future request-flow evidence | `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json` | Creator | direct path request-flow evidence |
| Future mock-response fixture | `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json` | Creator | harness 執行輔助 fixture |

Artifact path notes:

- `README.md`: no change in this topic
- `VERSION`: no change in this topic
- `.github/copilot-instructions.md`: no change in this topic
- `docs/request-shape-priority-workflow/**`: no change in this topic
- `src/**`: out of scope
- `pyproject.toml`: out of scope
- `uv.lock`: out of scope
- `tests/unit/request_contract/models_request_gate/**`: reference-only precedent
- `tests/unit/request_contract/projects_request_gate/**`: reference-only precedent
- 若出現未列路徑的變更，視為 `blocked`

## Implementation Steps

1. 完成 topic-local implement-plan artifacts：
   `requirements.md`、`technical-spec.md`、`plan.md`、`spec.md`、`step.md`，並使其對
   implement lane、frozen write set、direct-path-only rule、與 shared workflow contract
   authority 的語意一致
2. 完成 draft-plan commit 前的 creator-owned artifact freeze，確保這 5 個 topic-local files
   已可作為 reviewer gate 的 bounded review target
3. 若 reviewer 回 `needs-rework`，只允許在這 5 個 topic-local plan artifacts 內修正，
   不得提前進 implementation，也不得擴到 shared workflow files、`src/**`、或 future
   implementation files
4. 完成 review fix loop 後，將最新版 topic-local artifacts 重新對齊為可再次進 reviewer gate
   的 `review-ready` draft

## Validation / Acceptance Checks

- 五個 topic-local artifacts 存在於 exact paths，且內容一致指向 single-endpoint
  request-only implementation lane
- `request-gate-models-content.plan.md` 使用 canonical required sections，且未加入
  `Stable library metadata`
- `request-gate-models-content.spec.md` 只定義 request-only acceptance，不混入 response
  payload semantics
- `request-gate-models-content.step.md` 的 `## Implementation Steps` 與本 plan 一一對齊，且在
  reviewer 通過前只表達 creator-owned implement-plan completion gate，而不是 reviewer /
  human-check state
- 所有 artifacts 都明確寫出：
  - `ModelRepository.get_model_contents()` 不得作為正向入口
  - future implementation files 只限：
    - `tests/unit/request_contract/models_content_request_gate/__init__.py`
    - `tests/unit/request_contract/models_content_request_gate/conftest.py`
    - `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py`
    - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json`
    - `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json`
  - `docs/request-shape-priority-workflow/**`、`src/**`、`pyproject.toml`、`uv.lock`、
    `models_request_gate/**`、`projects_request_gate/**` 不在可寫範圍內
- topic 未把 scope 擴到其他 endpoint、shared workflow semantics、或 file-type behavior
- `step.md` 明確表達：
  - `plan-authoring`
  - `draft-plan-commit`
  - `plan-review`
  - `plan-review-fix-loop`
  - `human-check`
- reviewer 通過後的正確停點是 `human-check` 前，不是 implementation

## Reviewer Handoff

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- 本 topic merge 後不需要 README 更新、VERSION bump、release notes、或 repository release
  action
- push / PR / merge orchestration 仍屬 Main Agent 工作，不屬於本 topic-local authoring pass
- 本輪 implement-plan workflow 已在 reviewer 通過後停在 `human-check`；是否繼續進
  implementation 由後續明確授權決定

## Open Questions / Unresolved Items

- None
