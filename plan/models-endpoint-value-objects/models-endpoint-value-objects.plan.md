# Models Endpoint ValueObject Plan

> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth: `analysis/models-endpoint-value-objects/technical-spec.md`
> - Business guardrail: `analysis/models-endpoint-value-objects/requirements.md`
> - 本計畫百分之百對應 technical spec；沒有 human `override`。

## Goal / Outcome

- Goal: 交付一個以 `Requester` 注入的 `ModelsClient`、其 Models list/get 的語意 response Value Objects，以及可獨立驗證 request、response、error 與取消契約的單元測試。

## Scope

- In-Scope:
  - `GET /modelRepository/models`，支援 `start`、`limit` 與 `project_id` 轉譯為 `filter=in(projectId,"...")` 的單一頁 request。
  - `GET /modelRepository/models/{model_id}` 的 direct get。
  - `ModelsClient`、`ModelSummary`、`ModelsPage`、`ModelDetail` 與 `ModelsResponseError`。
  - injected `Requester`、safe `EndpointPath`、primitive `Requester.request(method, path, params=...)`、semantic response parsing、精確 error propagation。
  - topic-local unit tests。

- Out-Of-Scope:
  - 自動 pagination、next-link follow、dataUris、files、variables、links、內容下載或 upload。
  - Models 以外 endpoint family、package-root facade/export、auth/transport lifecycle、timeout、retry、cache 或 concurrency policy。
  - README、VERSION、release、dependency、migration-map、porting-ledger 與 request-gate artifact 變更。

## Locked Decisions

- Non-Goal: 這不是 stable-library 或 release topic；沒有 README/VERSION/release metadata，merge 後也不產生 release action。
- `ModelsClient` 的 canonical module import 是 `mlops_async.clients.models_client.ModelsClient`，不修改 package-root 或 `clients` package export。
- client 建構時只接受 `Requester`；client 不自行建立、關閉或 context-manage 任何 async resource，也不得接收 `BaseUrl`、檢視 `Requester` private state 或新增/修改 Requester API。
- client 以 `EndpointPath` 建構靜態與動態 path，且每個 endpoint call 只直接 await 一次 `Requester.request(method, path, params=...)`；不得構造 `HttpRequest`。
- `list_models` 固定為 `start: int = 0`、`limit: int = 20`、`project_id: str | None = None`，只做單一 request；`project_id` 的唯一 filter 是 `in(projectId,"<project_id>")`。
- `get_model` 只接受非空 `model_id`，並使用 `EndpointPath.from_segments()`；不可手工串接未編碼 path。
- response VOs 只公開 models 的列舉語意；`dataUris`、`files`、variables、links 及未知 raw payload 永不暴露。
- Error policy: HTTP non-2xx 直接傳播 `HTTPStatusException`，transport failure 直接傳播 `HttpTransportException`，無效 JSON 直接傳播 `InvalidJSONResponseException`，成功 JSON 的語意形狀不合法 raise `ModelsResponseError`，取消直接傳播 `asyncio.CancelledError`。
- Async-planning status: triggered -- cite trigger evidence: `Requester.request()` 為 async、ModelsClient 新增公開 async endpoint methods，且 resource ownership、failure 與 cancellation 必須在 coding 前固定。

### Async boundary decision

- `ModelsClient.list_models()` 與 `ModelsClient.get_model()` 是唯一 async I/O boundary；Value Object construction、input validation、query rendering 與 response semantic parsing 保持同步。

### Resource lifecycle decision

- caller 建立並持有 `Requester` 與其下游 transport/auth resources；`ModelsClient` 僅保留引用，不提供 close 或 async context manager。

### Concurrency model

- 每個方法只直接 await 一次 `Requester.request()`；不做 page fan-out、task creation、gather、semaphore、streaming 或 background worker。

### Failure model

- 直接保留既有 transport exceptions 的 instance；僅成功 response 的語意 mismatch 由 `ModelsResponseError` 表示，並且不攜帶完整 payload。

### Cancellation / timeout policy

- 不攔截 `asyncio.CancelledError`，不 cleanup caller-owned resources，不加入 timeout 或 retry；既有 transport/request options 是本 topic 的 ReadOnly 行為。

### Validation plan

- fake `Requester` 檢查單一 await 的 method/path/params call、raw response parsing、各種 exception identity 與 cancellation；不進行 live I/O。

### Handoff notes for the implementer

- 先做 pure VO/parser tests，再完成單一請求 client method。若需要改動任一 ReadOnly 路徑、改變 error policy，或加入 pagination/files/dataUris，立即停止並回報 `BLOCKED`。

### Async contradiction log

| Contradiction | Source A | Source B | Risk impact | Decision owner / next action | Classification |
| --- | --- | --- | --- | --- | --- |
| 無 | 無 | 無 | 無 | 不適用 | non-blocking |

## Boundaries / Exclusions

- ReadOnly: `AGENTS.md`、Models evidence、core request/transport modules、現有 request-gate tests、所有 README/version/config/release/ledger surfaces。
- Written: 本 planning pass 僅寫入 `analysis/models-endpoint-value-objects/requirements.md`、`analysis/models-endpoint-value-objects/technical-spec.md`、本 plan、spec 與 step；在 canonical `approved` -> `creator-in-progress` 的 Tester-owned pass 中，Tester 必須於 post-approval/pre-production timing 寫入 `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`；其後 Creator 僅能新增 technical spec 列出的四個 source/test 檔案。
- Modify: `tach.toml` 是唯一可修改的既有檔案，且只限 `src/mlops_async/models.py` 與 `src/mlops_async/clients/models_client.py` 所需的 dependency edges。任何其他既有檔案或 Tach policy 修改均屬 scope drift，不能自行擴張。
- Deleted: 無。
- Creator 只執行本 plan 的 Implementation Steps；reviewer 僅給 verdict；Main Agent 處理後續 publish/PR routing。任何 review verdict 不授權擴張 endpoint scope。

## Status / Allowed Transitions

- Current: `publish-in-progress`
- Current status transition: all Implementation Steps and both independent review evidence gates are complete with `approved`; the topic may proceed to topic commit, push, and draft PR.
- Execution model: canonical creator -> reviewer -> publish -> merge；本 topic 為 non-stable、no-release，`merged` 是 terminal。
- Allowed transitions:
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

- Canonical `approved` -> `creator-in-progress` 開始 Tester-owned TDD pass；Tester 必須在任何 production implementation 前執行 `python-tdd-test-authoring`，建立 `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`。
- YAML 的 `red-tests-ready` 只是 verdict gate，允許 Creator 在同一 canonical `creator-in-progress` status flow 執行後續 implementation steps，並非 workflow status 或 transition；`needs-rework`、`insufficient-context` 或 `BLOCKED` 必須依其 issues 回到 workflow rework/blocker，不能寫 production code。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements | `analysis/models-endpoint-value-objects/requirements.md` | Planning actor | Frozen business boundary, file labels, and measurable outcome |
| Technical spec | `analysis/models-endpoint-value-objects/technical-spec.md` | Planning actor | Execution-facing source of truth for request/VO/error/async contract |
| Topic plan | `plan/models-endpoint-value-objects/models-endpoint-value-objects.plan.md` | Planning actor | Workflow contract and implementation handoff |
| Topic specification | `plan/models-endpoint-value-objects/models-endpoint-value-objects.spec.md` | Planning actor | Acceptance and behavioral contract for non-trivial topic |
| Step tracker | `plan/models-endpoint-value-objects/models-endpoint-value-objects.step.md` | Planning actor then creator | Pending implementation checkpoint source |
| TDD authoring verdict | `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml` | Tester | Post-approval machine-readable D1/test-mapping verdict that gates production implementation |
| Implementation review evidence | `review-log/models-endpoint-value-objects/implementation-review.yaml` | Reviewer | Required pre-commit implementation alignment verdict with traceability, scope, contract, and TestCase checks |
| Code review evidence | `review-log/models-endpoint-value-objects/code-review.yaml` | Reviewer | Required pre-commit Python quality verdict with tooling and categorized findings |
| Dependency guardrail | `tach.toml` | Creator | Only the required dependency edges for `src/mlops_async/models.py` and `src/mlops_async/clients/models_client.py` |
| Value Objects | `src/mlops_async/models.py` | Creator | New immutable semantic Models response types and parsing boundary |
| Models facade | `src/mlops_async/clients/models_client.py` | Creator | New injected `Requester` list/get client |
| VO tests | `tests/unit/test_models_value_objects.py` | Creator | Unit coverage for semantic fields and invalid response shape |
| Client tests | `tests/unit/clients/test_models_client.py` | Creator | Unit coverage for request construction, response mapping, errors and cancellation |

Artifact path notes:

- `README.md`: no change.
- `VERSION`: no change.
- `pyproject.toml` and `uv.lock`: no change.
- `tach.toml`: only the required dependency edges for the two listed Models modules; Tach validation is mandatory.
- No file may be created, changed or deleted outside the listed paths. Stop as `BLOCKED` if that becomes necessary.

## Implementation Steps

1. Tester：在 reviewer `approved` 後、production code 尚未變更時，執行 `python-tdd-test-authoring`，建立 RED tests `tests/unit/test_models_value_objects.py`、`tests/unit/clients/test_models_client.py` 與 `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`；YAML 必須以 `red-tests-ready` verdict 明確允許 implementation。
2. Creator：建立 `src/mlops_async/models.py`；實作 frozen、slots Value Objects `ModelSummary`、`ModelsPage`、`ModelDetail` 與 module-public `ModelsResponseError`，以及 private parsers，使 step 1 的語意 response tests 轉為綠色，同時不暴露 `dataUris` 或 `files`。
3. Creator：建立 `src/mlops_async/clients/models_client.py`；實作 injected `ModelsClient` 的 `list_models()` 與 `get_model()`，以 `EndpointPath` 構造安全靜態/動態 path，並在每次 invocation 以一個 `Requester.request(method, path, params=...)` 呼叫實現 canonical query、local input validation、JSON decoding 與 frozen error/cancellation policy；不得構造 `HttpRequest`、接收 `BaseUrl`、檢視 Requester private state 或變更 Requester API，使 step 1 的 client tests 轉為綠色。
4. Creator：在 WSL 執行 topic-local test、lint、type 與 Tach commands；檢查 TDD YAML verdict、RED-to-green evidence 與 diff，確認只存在兩個 planned source、兩個 test files 與僅限必要 Models dependency edges 的 `tach.toml`，且沒有 pagination、data/file、release 或 ReadOnly drift。

## Validation / Acceptance Checks

- TestCase: list default and project-filter requests have the exact method/path/query/body contract, and get encodes its dynamic model identifier through `EndpointPath.from_segments()`.
- TestCase: every client call produces exactly one `Requester.request()` await with the expected method/path/params; no follow-up request occurs even when `count` exceeds returned `items` length.
- TestCase: VOs expose only frozen semantic fields and exclude `dataUris`/`files`.
- TestCase: invalid inputs fail before I/O; schema mismatch yields `ModelsResponseError`; non-2xx, invalid JSON, transport errors and cancellation preserve the exact defined exception behavior.
- TestCase: reviewer approved 後的 Tester YAML verdict 含完整 D1 verdict、test mapping、validation checks、issues 與 next step，並在 `red-tests-ready` 前禁止 production implementation。
- Validate with existing project configuration through WSL:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 pytest --override-ini addopts='' tests/unit/test_models_value_objects.py tests/unit/clients/test_models_client.py -q
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 ruff check src/mlops_async/models.py src/mlops_async/clients/models_client.py tests/unit/test_models_value_objects.py tests/unit/clients/test_models_client.py
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 pyright
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 tach check
```

- Reviewer must verify strict analysis routing, exact artifact paths, non-stable/no-release decision, the limited `tach.toml` edges and Tach validation, all five planning labels, step mirroring, and the single JSON Reviewer Handoff shape.

## Reviewer Handoff

The independent Reviewers write their own evidence artifacts before the matching Workflow Stage is marked complete. Either `needs-rework` verdict blocks commit and returns the topic to `creator-in-progress`.

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

- 無。此 topic 為 non-stable、no-release；不得因這個 Models implementation 變更 README、VERSION、tag 或 release notes。

## Open Questions / Unresolved Items

- None.

## Workflow state

- current_step: `publish-in-progress`
- next_step: `commit by topic, push, and open draft PR`
- status: `IN_PROGRESS`
