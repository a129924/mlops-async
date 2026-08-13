---
topic: project-info
phase: publish-in-progress
status: publish-in-progress
---

# Project Info

## Analysis Routing

> **Semantic warning — optional analysis layer absent:** `analysis/project-info/requirements.md` 與 `analysis/project-info/technical-spec.md` 均不存在。本計畫依已獲 human 接受的 locked decisions 與已核對的 Projects request/OpenAPI evidence 撰寫；它們不屬於本 topic 的 File contract，不得在未重新規劃前新增或當作 implementation prerequisite。

## Goal / Outcome

### Goal

讓 `modelRepository/projects` 的 list 與 detail semantic value objects 一致公開 `created_by`、`modified_by`、`creation_timestamp`、`modified_timestamp`；每欄均為 `str | None`，default 為 `None`。

## Scope

### In-Scope

- 僅擴充 `ProjectSummary`、`ProjectDetail` 與其 list/detail parser 的四個 audit metadata fields。
- 對 `createdBy`、`modifiedBy`、`creationTimeStamp`、`modifiedTimeStamp` 使用完全相同的 mapping/validation；timestamps 保持 raw strings。
- 在既有 value-object/client unit tests 覆蓋 missing、有效字串、JSON `null`、非字串及 list/detail parity。

### Out-Of-Scope

- 不變更 `ProjectsClient` request shape/signatures、pagination、lookup、Champion、tables、request gate、exports 或 errors architecture。
- 不新增 datetime coercion、metadata model、schema/migration、live Viya E2E、retry/concurrency。
- 不變更 README、VERSION、OpenAPI、legacy evidence、analysis artifacts、release/tag/publish。

## Locked Decisions

- Endpoint family 固定為 `modelRepository/projects`；`ProjectSummary` 和 `ProjectDetail` 均需四欄 list/detail parity。
- Python fields 精確為 `created_by: str | None = None`、`modified_by: str | None = None`、`creation_timestamp: str | None = None`、`modified_timestamp: str | None = None`。
- JSON mappings 精確為 `createdBy` -> `created_by`、`modifiedBy` -> `modified_by`、`creationTimeStamp` -> `creation_timestamp`、`modifiedTimeStamp` -> `modified_timestamp`。
- key 缺失 -> `None`；key present 且 JSON `null` 或任何非 `str` JSON value -> `ProjectsResponseError`。空字串仍為 `str`，不得另加非空限制。
- timestamps 不 parse、normalize、timezone convert 或 format validate；`ProjectsResponseError`、unknown-field exclusion、frozen/slotted contract 與既有 request/JSON/transport propagation 不變。
- 這是 additive stable-library public value-object change，但 human 已鎖定 no release：不得改 stable metadata、版本或發布。

## Boundaries / Exclusions

### Non-Goal

不重新設計 Projects API，也不將 response evidence 擴張為 request contract。request gate 與 OpenAPI/legacy files 僅供唯讀 evidence；若需未列 production/test path、export、README/VERSION 或 release action，Creator 必須停止並 re-plan。

Planning actor 只寫 topic artifacts；Creator 只可變更 `Modify` 三檔；Reviewer 獨立給 verdict；Main Agent 擁有 worktree、routing、commit/push/PR 與後續流程。

## Status / Allowed Transitions

- **Current**: `publish-in-progress`。
- **Execution model**: 實作、implementation review 與 code review 均已完成並獲最終獨立 Reviewer 批准；下一步為 topic commit publisher 執行受控 commit/push/PR routing。topic merge 後結束，沒有 `merged` -> `released`。
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

Routing notes: Plan review 必須拒絕任何 list/detail parity 或 missing/null/non-string distinction 的漂移。此 artifact 不授權 implementation、commit、push、PR、merge 或 release。

## Artifact Paths

### ReadOnly

| Path | Owner | Role |
| --- | --- | --- |
| `src/mlops_async/clients/projects/client.py` | Creator | 確認既有 list/detail parsing integration，不修改 client |
| `src/mlops_async/clients/projects/__init__.py` | Creator | 確認既有 public exports 無變更 |
| `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py` | Creator | Frozen list request-shape gate |
| `tests/unit/request_contract/projects_request_gate/test_get_project_request_contract.py` | Creator | Frozen detail request-shape gate |
| `tests/unit/request_contract/projects_request_gate/test_get_champion_model_request_contract.py` | Creator | Family request-gate boundary |
| `docs/api-endpoints/swagger-spec/projects-spec.json` | Creator | 四個 exact JSON keys 的 OpenAPI string evidence |
| `docs/legacy-viya-outbound-endpoints/projects-champion.md` | Creator | Legacy Projects-family evidence |
| `README.md` | Main Agent | Stable metadata no-change evidence |
| `VERSION` | Main Agent | No-bump/no-release evidence |

### Written

| Path | Owner | Role |
| --- | --- | --- |
| `plan/project-info/project-info.plan.md` | Plan-Creator | Repo-visible execution contract |
| `plan/project-info/project-info.spec.md` | Plan-Creator | TDD 所需的 primary behavior contract |
| `plan/project-info/project-info.step.md` | Plan-Creator | Workflow/implementation tracker |
| `plan/project-info/project-info.tdd-test-authoring.yaml` | Tester | Machine-readable TDD verdict；僅於已核定的 TDD test-authoring gate 產生 |

### Deleted

None.

### Modify

| Path | Owner | Role |
| --- | --- | --- |
| `src/mlops_async/clients/projects/value_objects.py` | Creator | Add parity fields and strict missing-or-string parser rule |
| `tests/unit/clients/projects/test_value_objects.py` | Creator | VO shape/parser/error matrix |
| `tests/unit/clients/projects/test_client.py` | Creator | list/detail caller-observable parity |

These are exhaustive future change paths. Extra paths are plan-alignment blockers; `analysis/project-info/*` is intentionally absent from this File contract.

## Stable library metadata

- `README row`: no change.
- `VERSION bump`: no bump.
- `timing`: no promotion or release action in this topic.
- `rationale`: additive public fields do not authorize release; any release needs separate authorization and current-baseline verification.
- Release notes: no change.

## Implementation Steps

1. 在 `tests/unit/clients/projects/test_value_objects.py` 先寫 RED tests：兩 dataclass 的 frozen/slotted fields/defaults；list/detail 每一 exact key 的 missing -> `None`、string -> raw string、`null`/non-string -> `ProjectsResponseError`，保留 unknown-field exclusion。
2. 在 `tests/unit/clients/projects/test_client.py` 加 list/get response fixtures/assertions，驗證四個 raw values 的 parity 與 malformed values 的既有 `ProjectsResponseError` propagation，不改 request recording/path/params assertions。
3. 僅在 `src/mlops_async/clients/projects/value_objects.py` 擴充兩個 VOs/parsers，建立或重用 strict helper（missing -> `None`、present `str` -> `str`）；`null`/non-string 必須 raise，且不得改 Champion 已有 nullable rule。
4. 透過 WSL 執行 locked focused tests、Ruff format/check、Pyright、`git diff --check`；future diff 必須只有三個 `Modify` paths，否則停止並 re-plan。

## Validation / Acceptance Checks

### TestCase

- 兩 dataclass 都含 `id`/`name` 加四個 `str | None = None` fields，且仍 frozen/slotted。
- list `items[*]` 與 detail object 的四 key mapping 完全一致；missing 為 `None`、present strings 原樣保留（包括 raw timestamps）。
- 四 keys 任一 present `null` 或 `int`、`bool`、array、object 時，list/detail parser 都 raise `ProjectsResponseError`，不把 `null` 當 `None`。
- `ProjectsClient.list_projects`/`get_project` 露出相同有效 values，並維持 malformed-value propagation。
- request-gate、client public signatures、exports、README、VERSION 都無 diff。
- 在 WSL 執行：`uv run pytest tests/unit/clients/projects/test_value_objects.py tests/unit/clients/projects/test_client.py`；`uv run ruff format --check src/mlops_async/clients/projects/value_objects.py tests/unit/clients/projects/test_value_objects.py tests/unit/clients/projects/test_client.py`；`uv run ruff check src/mlops_async/clients/projects/value_objects.py tests/unit/clients/projects/test_value_objects.py tests/unit/clients/projects/test_client.py`；`uv run pyright src/mlops_async/clients/projects/value_objects.py tests/unit/clients/projects/test_value_objects.py tests/unit/clients/projects/test_client.py`；`uv run --frozen --no-sync tach check`；`git diff --check`。

本 planning pass 僅驗證 artifacts/git scope；不執行 Python implementation、tests、lint/type checks、commit、push、PR 或 release。

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

No release action is authorized. Merge does not authorize README/VERSION updates, version bump, tag, publication, or cleanup; each needs its own explicit workflow gate.

## Open Questions / Unresolved Items

None. Optional analysis layer absence is documented and non-blocking under locked human decisions.

## Workflow state

- current_step: `publish-in-progress`
- next_step: `topic commit publisher prepares the intentional topic commit`
- status: `COMPLETE`
