> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth:
>   `analysis/request-gate-casmanagement-list-tables/technical-spec.md`
> - Business-intent guardrail:
>   `analysis/request-gate-casmanagement-list-tables/requirements.md`

## Goal / Outcome

- 建立 `request-gate-casmanagement-list-tables` 的 repo-visible execution contract。
- 凍結 `casManagement/dataSources/tables -> list_tables` 的最小 request shape，讓後續 CAS implementation 不需要回頭重猜 list baseline。
- 讓 stable-library metadata 的 release-stage 對齊時機在 topic 內先被明確宣告，但不在 creator / publish-in-progress 當下落地。

## Scope

- **In scope**:
  - `analysis/request-gate-casmanagement-list-tables/requirements.md`
  - `analysis/request-gate-casmanagement-list-tables/technical-spec.md`
  - `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.plan.md`
  - `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.step.md`
  - `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.spec.md`
  - `tests/unit/request_contract/casmanagement_tables_list_request_gate/__init__.py`
  - `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py`
  - `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py`
  - `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json`
  - `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json`

- **Out of scope**:
  - `src/**`
  - `get_table`
  - `change_table_state`
  - bare `GET` baseline without query
  - pagination semantics beyond `limit=1000&start=0`
  - filter / sort / search query support
  - CAS load-state business semantics
  - auth runtime wiring
  - `docs/request-shape-priority-workflow/**`
  - creator / publish-in-progress 階段的 `README.md` / endpoint docs / version-source 變更

## Locked Decisions

- topic name 固定為 `request-gate-casmanagement-list-tables`
- implementation 前 branch 固定為 `feat/andrew/request-gate-casmanagement-list-tables`
- 本 topic classification: `tests-only / shape-only request gate`
- strict `limit=1000&start=0` 是唯一正向 query shape
- bare `GET` 不屬於正向 baseline
- `cas-shared-default` 是固定 path segment，不參數化
- 正向 fixture 只允許一個 case：`limit_1000_start_0`
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- stable-library intent present but deferred：
  `README.md`、`docs/api-endpoints/markdown-reference/README.md`、`VERSION`、
  `pyproject.toml`、`uv.lock` 只在 final `release` 執行
- 若未來要做 CAS runtime implementation，必須開新 topic，不能把 code-side work 回填到本 topic

## Boundaries / Exclusions

- creator work 僅能寫入 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/casmanagement_tables_list_request_gate/**`
- reviewer work 只審核這個 topic 的 contract 一致性與 bounded test surfaces
- Main Agent 不得把本 topic 擴張成 CAS runtime implementation、release、或 workflow doc 再修改
- 若需求漂移到 `get_table`、`change_table_state`、response schema、或 `src/**`，必須另開 topic

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path；本 topic creator phase 已完成，stable-library release work 延後到 final release 階段
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

- publish 階段不得提前修改 stable-library surfaces
- merge 後先停在 `merged`
- 只有 final release batch 才執行 `merged -> released`

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements | `analysis/request-gate-casmanagement-list-tables/requirements.md` | Plan-Creator | 凍結 tests-only boundary、goal、non-goals、與 release-stage alignment intent |
| Topic technical spec | `analysis/request-gate-casmanagement-list-tables/technical-spec.md` | Plan-Creator | 凍結 canonical request shape、fixture layout、與 harness rules |
| Topic plan | `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.plan.md` | Plan-Creator | Canonical execution contract |
| Topic step tracker | `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.step.md` | Plan-Creator | Implementation completion gate |
| Topic behavior spec | `plan/request-gate-casmanagement-list-tables/request-gate-casmanagement-list-tables.spec.md` | Plan-Creator | Request-shape acceptance scenarios |
| Request gate package marker | `tests/unit/request_contract/casmanagement_tables_list_request_gate/__init__.py` | Code-Implementer | Package anchor for isolated CAS list_tables request gate |
| Request gate harness | `tests/unit/request_contract/casmanagement_tables_list_request_gate/conftest.py` | Code-Implementer | Topic-local request capture / validation helper |
| Request gate test | `tests/unit/request_contract/casmanagement_tables_list_request_gate/test_list_tables_request_contract.py` | Code-Implementer | Positive / blocked / regression contract tests |
| Request-flow fixture | `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.request-flow.json` | Code-Implementer | Canonical source-observed request example |
| Mock-response fixture | `tests/unit/request_contract/casmanagement_tables_list_request_gate/fixtures/list_tables.mock-responses.json` | Code-Implementer | Minimal JSON response scaffold |

Artifact path notes:

- `README.md`: no change in creator / publish-in-progress
- `docs/api-endpoints/markdown-reference/README.md`: no change in creator / publish-in-progress
- `VERSION`: no change in creator / publish-in-progress
- `pyproject.toml`: no change in creator / publish-in-progress
- `uv.lock`: no change in creator / publish-in-progress
- listed paths are the full executable contract
- 若後續 work drift 到 listed paths 之外，必須視為 scope creep 並另開 topic

## Stable library metadata

- `README row`: final release 時補上或更新
  `casManagement/dataSources/tables -> list_tables` 的 request-gate status 描述
- `Docs alignment`: final release 時同步更新
  `docs/api-endpoints/markdown-reference/README.md` 的 endpoint inventory / status
- `VERSION bump`: only at final `release`；bump direction 由當次 release batch 決定
- `pyproject.toml` / `uv.lock`: only at final `release`
- `timing`: `release`
- `rationale`: 使用者要求 release-facing docs 與 version source 延後到 final release，一次對齊 topic merge truth
- `release-note expectations`: release note 需提到新增
  `casManagement/dataSources/tables -> list_tables` request-gate baseline 與 docs 對齊

## Implementation Steps

1. 建立 topic-local `requirements.md`，凍結 tests-only boundary、strict query baseline、blocked variants、與 release-stage docs / version alignment intent。
2. 建立 topic-local `technical-spec.md`，凍結 request shape、fixture layout、topic-local harness 規則、與不碰 `src/**` 的 execution boundary。
3. 建立 `.plan.md`、`.step.md`、`.spec.md`，使 topic 符合 repo workflow contract。
4. 新增 `tests/unit/request_contract/casmanagement_tables_list_request_gate/` isolated package。
5. 在 `conftest.py` 建立 topic-local harness，只允許單一步驟 observed flow。
6. 建立 `fixtures/list_tables.request-flow.json`，只保留 `limit_1000_start_0` case。
7. 建立 `fixtures/list_tables.mock-responses.json`，只提供最小 JSON object scaffold。
8. 建立 `test_list_tables_request_contract.py`，覆蓋正向 request shape、blocked variants、percent-encoding、與 topic-scoped harness regression。
9. 完成 bounded validation：
   - `pytest`
   - `ruff`
   - `pyright`

## Validation / Acceptance Checks

- topic-local 五個 analysis / plan artifacts 齊全且互相一致
- `tests/unit/request_contract/casmanagement_tables_list_request_gate/**` 是唯一 implementation surface
- 正向 case 只存在一個：`limit_1000_start_0`
- fixture query 固定為 `limit=1000&start=0`
- blocked variants 明確覆蓋 invalid `caslib`、query drift、body drift、與 endpoint drift
- 沒有任何 `src/**`、transport、或 core CAS module 被納入修改集合
- `Stable library metadata` 明確宣告 docs / version timing 為 `release`
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

- merge 後先停在 `merged`，不立即實作 stable-library surfaces
- final release 階段才執行：
  - 對齊 `README.md`
  - 對齊 `docs/api-endpoints/markdown-reference/README.md`
  - 更新 `VERSION`
  - 同步 `pyproject.toml`
  - 同步 `uv.lock`
  - 補 release note
- 因本 topic 宣告了實際 release action，狀態轉移需補上 `merged -> released`

## Open Questions / Unresolved Items

- None
