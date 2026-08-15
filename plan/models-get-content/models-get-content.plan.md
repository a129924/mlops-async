# Models Content Download Topic Plan

## Goal

在 `ModelsClient` 新增 `get_model_content()`，以 encoded model/content identifiers 下載 raw bytes，回傳不可變 `ModelContent` 與必要 HTTP metadata。

## Non-goals

- 不實作其餘 66 個 Models operations、stream、multipart、mutation、polling 或 link-follow。
- 不修改 Auth、Requester、transport、Tach、README、VERSION、release/tag。
- 不改變既有 `list_models()`、`get_model()` public contract，也不改寫 legacy request-gate evidence。

## Current Context

既有 Models client 已有 list/get，core `Requester.request()` 已提供 async HTTP I/O 與 request-level headers。本 topic 是 Models content download 的最小 executable slice。

## Requirements

- 200/206 以 bytes 與 Content-Type、ETag、Content-Range 建立 `ModelContent`。
- caller 可指定 raw `Range`／`If-Range`；`if_range` 不可單獨使用。
- invalid input 必須於 requester I/O 前 `ValueError`；HTTP、transport、cancellation 語意維持不變。

## Decisions

- Async-planning status: triggered — cite trigger evidence: `ModelsClient` 透過 async `Requester.request()` 執行 HTTP I/O，且本 contract 凍結 cancellation propagation。
- Module/package placement: client、value object 與 export 都位於既有 `mlops_async.clients.models`。
- New public API: `ModelsClient.get_model_content()` 與 `ModelContent`。
- Interface changes: 新增一個 Models client method；既有 list/get signature 與行為不變。
- Breaking change: 不允許。
- Dependencies: 無新 dependency。
- Error strategy: invalid input `ValueError`；HTTP、transport、`CancelledError` 原樣傳播。
- Typing: Python 3.10 strict typing；不使用 `Any`；可缺失 metadata 為 `str | None`。

### Async boundary decision

validation、segment encoding、header composition、metadata extraction 與 value-object construction 同步進行；僅單次 `await requester.request(...)` 是 async boundary。

### Resource lifecycle decision

Requester 與 transport 由呼叫端持有；Models client 不建立、關閉、包裝 client 或 stream resource。

### Concurrency model

每次 invocation 只發送一個 request；無 fan-out、batch、background task、polling 或 retry。

### Failure model

200/206 mapping；non-2xx 與 transport failure 不 catch、不轉譯、不 parse binary payload。

### Cancellation / timeout policy

`CancelledError` 原樣傳播，沒有 retry 或 follow-up work；timeout 沿用 transport 現有 policy。

### Validation plan

先建立 async RED tests，覆蓋 success、headers、no-I/O validation、error/cancellation 與 list/get regression；所有 Python quality gates 僅透過 WSL 執行。

### Handoff notes for the implementer

Authorization 由 `Requester` 管理；public parameter 名稱固定為 `range_header`。未指定時不得送出 `Range`、`If-Range` 或 `Access-Quarantine`；request-gate 僅是 request-shape evidence。

## Public Contract / API Changes

```python
@dataclass(frozen=True, slots=True)
class ModelContent:
    content: bytes
    content_type: str | None
    etag: str | None
    content_range: str | None


async def get_model_content(
    self,
    model_id: str,
    content_id: str,
    *,
    range_header: str | None = None,
    if_range: str | None = None,
) -> ModelContent: ...
```

`ModelContent` 僅自 `mlops_async.clients.models` 匯出；無 breaking change。

## Affected Files / Modules

所有允許與禁止檔案，以及 owner/role，列於後方 Artifact Paths table。runtime scope 僅限 Models client family。

## Implementation Steps

1. 在 `tests/unit/clients/models/test_client.py` 擴充 fake requester 與 RED tests，涵蓋 encoded path、success response、conditional headers、所有 `model_id`/`content_id`/`range_header`/`if_range` 非字串輸入的 pre-I/O `ValueError`，以及 exception propagation。
2. 在 `src/mlops_async/clients/models/value_objects.py` 新增 frozen/slotted `ModelContent`；在 `src/mlops_async/clients/models/__init__.py` 新增 family-local export；在 `tests/unit/clients/models/test_value_objects.py` 驗證 immutable/slotted fields。
3. 在 `src/mlops_async/clients/models/client.py` 實作 `get_model_content()` 的 non-empty validation、encoded segments、`Range`／`If-Range` composition、200/206 bytes/metadata mapping。
4. 在 `tests/unit/clients/models/test_client.py` 完成 416/non-2xx、transport failure、`CancelledError`、metadata casing 與 list/get regression assertions。

## Test Plan

### TestCase

- 200 full download：回傳相同 bytes、Content-Type 與 ETag。
- 206 partial download：精確傳送 Range、可選 If-Range，並讀取 Content-Range。
- 預設呼叫不送 Range、If-Range、Access-Quarantine。
- empty/blank identifier、blank supplied header、孤立 `if_range` 都在 I/O 前 `ValueError`。
- `model_id`、`content_id`、`range_header`、`if_range` 的任何 non-str input 都在 requester I/O 前 `ValueError`。
- dynamic identifiers percent-encode；416/other HTTP、transport failure、`CancelledError` 原樣傳播。
- 缺少 Content-Type 時 `content_type is None`；缺少 ETag 時 `etag is None`；缺少 Content-Range 時 `content_range is None`。
- metadata header case-insensitive lookup；`ModelContent` frozen/slotted。
- backwards compatibility：確認 `list_models()` 與 `get_model()` signatures 未變，且既有 behavior regression tests 維持通過。

## Validation Commands

```powershell
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest tests/unit/clients/models'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff check src/mlops_async/clients/models tests/unit/clients/models'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pyright src/mlops_async/clients/models'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync tach check'
```

## Risks

legacy empty conditional headers 與新 public policy 可能不同；metadata headers 可能缺失；任何 upstream/current/evidence 實質矛盾必須停止 human-check。

## Rollback Plan

回復本 topic 的 five Written artifacts 與 five Modify files；不改 `dev`、其他 worktree 或 ReadOnly evidence。

## Open Questions

無。若 OpenAPI、legacy evidence、request gate 與 current client 的 method/path/header contract 有實質衝突，停止並交 human-check。

## Goal / Outcome

完成一個可驗證、可審查、可獨立發布候選的 Models content-download slice；不在本 topic merge 或 release。

## Scope

範圍僅限 `get_model_content()`、`ModelContent`、Models family-local export、允許的 Models tests 及 five planning artifacts。

## Locked Decisions

Python implementation decisions、async boundary 與 public contract 以上方 13 Python sections 為準，均已凍結。

## Boundaries / Exclusions

不進行 JSON/text decode、client-owned resource、retry、timeout override、其他 endpoint、core transport 改動或 legacy request-gate rewrite。legacy snapshot/OpenAPI/request-contract matrix 僅為 request-shape evidence，不是 runtime response truth。

## Status / Allowed Transitions

Current=`review-ready`。

- `planned->creator-in-progress`
- `creator-in-progress->review-ready`
- `review-ready->reviewer-in-progress`
- `reviewer-in-progress->approved`
- `reviewer-in-progress->needs-rework`
- `needs-rework->creator-in-progress`
- `approved->creator-in-progress`
- `approved->publish-in-progress`
- `publish-in-progress->pr-open`
- `publish-in-progress->merged`
- `pr-open->needs-rework`
- `pr-open->merged`
- `merged->terminal`

Draft PR human review 使用 `publish-in-progress->pr-open`；merge/release 不在本 topic scope。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Written | `analysis/models-get-content/requirements.md` | Plan Creator | requirements baseline |
| Written | `analysis/models-get-content/technical-spec.md` | Plan Creator | technical contract |
| Written | `plan/models-get-content/models-get-content.plan.md` | Plan Creator | executable plan |
| Written | `plan/models-get-content/models-get-content.spec.md` | Plan Creator | acceptance specification |
| Written | `plan/models-get-content/models-get-content.step.md` | Plan Creator | workflow tracker |
| Modify | `src/mlops_async/clients/models/client.py` | Implementer | client API and response mapping |
| Modify | `src/mlops_async/clients/models/value_objects.py` | Implementer | ModelContent value object |
| Modify | `src/mlops_async/clients/models/__init__.py` | Implementer | family-local export |
| Modify | `tests/unit/clients/models/test_client.py` | Implementer | client contract tests |
| Modify | `tests/unit/clients/models/test_value_objects.py` | Implementer | value-object tests |
| ReadOnly | `reference/legacy_code/長庚備份程式/10_48_11_146/sas-docker-api/utils/_api/get_model.py` | Evidence Reader | legacy request evidence |
| ReadOnly | `docs/api-endpoints/swagger-spec/upstream/modelRepository-openapi.yml` | Evidence Reader | upstream API evidence |
| ReadOnly | `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md` | Evidence Reader | evidence priority |
| ReadOnly | `tests/unit/request_contract/models_content_request_gate/test_get_model_content_request_contract.py` | Evidence Reader | request-shape gate |
| ReadOnly | `tests/unit/request_contract/models_content_request_gate/conftest.py` | Evidence Reader | gate fixture setup |
| ReadOnly | `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.request-flow.json` | Evidence Reader | request flow fixture |
| ReadOnly | `tests/unit/request_contract/models_content_request_gate/fixtures/get_model_content.mock-responses.json` | Evidence Reader | response fixture evidence |
| ReadOnly | `src/mlops_async/core/requester.py` | Evidence Reader | requester boundary |
| ReadOnly | `src/mlops_async/core/types.py` | Evidence Reader | response type boundary |
| ReadOnly | `tach.toml` | Evidence Reader | architecture gate |
| Deleted | — | — | none |

## Stable library metadata

- README row: no change。
- VERSION: no bump。
- timing: deferred to separately authorized per-slice release gate。
- rationale: this is a new public API but topic stops before release。
- release notes: no change。

## Implementation Steps

以上方 Python `## Implementation Steps` 為唯一 implementation contract；不得加入 review、push、PR 或 human-role action。

## Validation / Acceptance Checks

以上方 Python `## Test Plan` 與 `## Validation Commands` 為唯一 acceptance/validation contract。

## Reviewer Handoff

{ "verdict": "approved|needs-rework", "blocking_issues": [], "copilot_feedback_triage": { "ADDRESS": [], "DISCUSS": [], "SKIP": [] } }

## Post-merge / release actions

本 topic 通過 validation/reviewer approval 後，可由 `approved->publish-in-progress->pr-open` 建立 Draft PR，然後停止 human review。不得 merge、release、tag 或 cleanup。

## Open Questions / Unresolved Items

無；任何 evidence/current-contract conflict 皆交 human-check。
