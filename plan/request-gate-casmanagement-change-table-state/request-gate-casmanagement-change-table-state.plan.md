> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-gate-casmanagement-change-table-state/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-gate-casmanagement-change-table-state/requirements.md`

## Goal / Outcome

- 建立 `request-gate-casmanagement-change-table-state` 的 repo-visible execution contract
- 凍結 `casManagement/caslibs/tables/state -> change_table_state` 的 request shape，
  作為後續 CAS mutation implementation 的最小 baseline
- stable-library metadata 與
  `docs/request-shape-priority-workflow/**` 的 current-truth alignment
  延後到 final `release`

## Scope

- **In scope**:
  - `analysis/request-gate-casmanagement-change-table-state/requirements.md`
  - `analysis/request-gate-casmanagement-change-table-state/technical-spec.md`
  - `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.plan.md`
  - `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.step.md`
  - `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.spec.md`
  - `tests/unit/request_contract/casmanagement_table_state_change_request_gate/__init__.py`
  - `tests/unit/request_contract/casmanagement_table_state_change_request_gate/conftest.py`
  - `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py`
  - `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json`
  - `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json`

- **Out of scope**:
  - `src/**`
  - `list_tables`
  - `get_table`
  - `value=unloaded`
  - response schema semantics beyond minimal mock scaffold
  - CAS load / unload business rules
  - CAS memory lifecycle orchestration
  - creator / publish-in-progress 的 `README.md` / endpoint docs / version-source /
    `docs/request-shape-priority-workflow/**` 修改

## Locked Decisions

- topic name 固定為 `request-gate-casmanagement-change-table-state`
- implementation branch 固定為
  `feat/andrew/request-gate-casmanagement-change-table-state`
- 本 topic classification: `tests-only / shape-only request gate`
- 唯一正向 baseline 固定為 `loaded_direct_identifiers`
- method 固定為 `PUT`
- path 固定為
  `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
- query 固定為 `{"value": "loaded"}`
- body 固定為
  `{"outputCaslibName": "<caslib>", "outputTableName": "<tableName>"}`
- `cas-shared-default` 視為固定 path segment
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- stable-library intent present but deferred：
  `README.md` / `docs/api-endpoints/markdown-reference/README.md` / `VERSION` /
  `pyproject.toml` / `uv.lock` / `docs/request-shape-priority-workflow/**`
  只在 final `release` 對齊

## Boundaries / Exclusions

- creator work 只允許 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/casmanagement_table_state_change_request_gate/**`
- reviewer work 只審 topic contract 與 bounded test surfaces
- Main Agent 不在本 topic creator phase 推進 CAS runtime implementation 或 release
- 不把 `list_tables` / `get_table` / `unloaded` state 回填到這個 topic

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；
  topic creator phase 不做 stable-library / workflow-doc release work
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
  - `merged` -> `released`
  - `released` -> terminal

Routing notes:

- publish 不處理 stable-library surfaces 或 shared workflow docs
- merge 後先停在 `merged`
- final release batch 再做 `merged -> released`

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-casmanagement-change-table-state/requirements.md` | Plan-Creator | 凍結 tests-only boundary、goal、non-goals、release intent |
| Topic technical spec | `analysis/request-gate-casmanagement-change-table-state/technical-spec.md` | Plan-Creator | 凍結 canonical request shape、fixture layout、harness rules |
| Topic plan | `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.plan.md` | Plan-Creator | Canonical execution contract |
| Topic step tracker | `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.step.md` | Plan-Creator | Implementation completion gate |
| Topic behavior spec | `plan/request-gate-casmanagement-change-table-state/request-gate-casmanagement-change-table-state.spec.md` | Plan-Creator | Request-shape acceptance scenarios |
| Request gate package marker | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/__init__.py` | Code-Implementer | Package anchor for isolated CAS state-change request gate |
| Request gate harness | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/conftest.py` | Code-Implementer | Topic-local request capture / validation helper |
| Request gate test | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/test_change_table_state_request_contract.py` | Code-Implementer | Positive / blocked / regression contract tests |
| Request-flow fixture | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.request-flow.json` | Code-Implementer | Canonical source-observed request example |
| Mock-response fixture | `tests/unit/request_contract/casmanagement_table_state_change_request_gate/fixtures/change_table_state.mock-responses.json` | Code-Implementer | Minimal JSON response scaffold |

Artifact path notes:

- `README.md`: no change in creator / publish-in-progress
- `docs/api-endpoints/markdown-reference/README.md`: no change in creator / publish-in-progress
- `VERSION`: no change in creator / publish-in-progress
- `pyproject.toml`: no change in creator / publish-in-progress
- `uv.lock`: no change in creator / publish-in-progress
- `docs/request-shape-priority-workflow/README.md`: no change in creator / publish-in-progress
- `docs/request-shape-priority-workflow/standards.md`: no change in creator / publish-in-progress
- `docs/request-shape-priority-workflow/checklist.md`: no change in creator / publish-in-progress

## Stable library metadata

- `README row`: final release 時補上
  `casManagement/caslibs/tables/state -> change_table_state` 的 request-gate status
- `Docs alignment`: final release 時同步
  `docs/api-endpoints/markdown-reference/README.md` 的 endpoint inventory / status
- `Workflow-doc alignment`: final release 時同步
  `docs/request-shape-priority-workflow/README.md`、
  `docs/request-shape-priority-workflow/standards.md`、
  `docs/request-shape-priority-workflow/checklist.md`
  的 current truth
- `VERSION bump`: only at final `release`
- `pyproject.toml` / `uv.lock`: only at final `release`
- `timing`: `release`
- `rationale`: `change_table_state` 是 queue 外 boundary topic，release 時才讓 shared
  release surfaces 與 workflow docs 對齊 merged truth

## Implementation Steps

1. 建立 topic-local `requirements.md`，凍結 tests-only boundary、`loaded` baseline、
   blocked variants、與 release-stage docs / workflow-doc / version alignment intent。
2. 建立 topic-local `technical-spec.md`，凍結 `PUT + value=loaded + JSON body` request shape、
   fixture layout、topic-local harness 規則、與不碰 `src/**` 的 execution boundary。
3. 建立 `.plan.md`、`.step.md`、`.spec.md`，使 topic 符合 repo workflow contract。
4. 新增 `tests/unit/request_contract/casmanagement_table_state_change_request_gate/`
   isolated package。
5. 在 `conftest.py` 建立 topic-local harness：
   - 只允許單一步 observed flow
   - capture method / path / query / body / headers
   - JSON body 需正規化為 object 後比對
6. 建立 `fixtures/change_table_state.request-flow.json`，只保留
   `loaded_direct_identifiers` case。
7. 建立 `fixtures/change_table_state.mock-responses.json`，只提供最小 JSON object scaffold。
8. 建立 `test_change_table_state_request_contract.py`，覆蓋正向 request shape、
   blocked variants、percent-encoding、與 topic-scoped harness regression。
9. 跑 bounded validation：
   - `pytest`
   - `ruff`
   - `pyright`

## Validation / Acceptance Checks

- topic-local analysis / plan artifacts 齊全且一致
- `tests/unit/request_contract/casmanagement_table_state_change_request_gate/**`
  是唯一 implementation surface
- 正向 case 只存在一個：`loaded_direct_identifiers`
- fixture path 固定為
  `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state`
- blocked variants 明確覆蓋 invalid identifiers、state drift、body drift、query drift、
  endpoint drift
- 沒有任何 `src/**`、transport、或 core CAS module 被納入修改集合
- `Stable library metadata` 明確宣告 docs / workflow-doc / version timing 為 `release`
- `Post-merge / release actions` 明確要求 `merged -> released`

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

- merge 後先停在 `merged`，不立即修改 stable-library surfaces
- final release 階段才執行：
  - 對齊 `README.md`
  - 對齊 `docs/api-endpoints/markdown-reference/README.md`
  - 更新 `VERSION`
  - 更新 `pyproject.toml`
  - 更新 `uv.lock`
  - 對齊 `docs/request-shape-priority-workflow/README.md`
  - 對齊 `docs/request-shape-priority-workflow/standards.md`
  - 對齊 `docs/request-shape-priority-workflow/checklist.md`
  - 補 release note

## Open Questions / Unresolved Items

- None
