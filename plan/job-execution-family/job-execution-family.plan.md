> **Analysis-layer routing: incomplete**
>
> - `analysis/job-execution-family/requirements.md` 與
>   `analysis/job-execution-family/technical-spec.md` 目前都不存在。
> - 本計畫依人類已核准的正式 contract materialize；該 contract 是本 topic 的
>   execution-facing source of truth。若後續建立 analysis layer，必須先進行 plan
>   rework，不得由實作者自行改寫任何 locked decision。

## Goal / Outcome

交付一個 family-local 的 `JobExecutionClient`，以 caller-owned `Requester` 執行三個單次
async Job Execution 請求：`start_job(job_request_id) -> Job`、`get_job(job_id) -> Job`、
`get_job_state(job_id) -> JobState`。結果由語意 Value Objects 表示，且 response semantic
mismatch 一律以 `JobExecutionResponseError` 表示。

## Scope

- **In scope**:
  - `POST /jobExecution/jobRequests/{job_request_id}/jobs` 的 `start_job`。
  - `GET /jobExecution/jobs/{job_id}` 的 `get_job`。
  - `GET /jobExecution/jobs/{job_id}/state` 的 `get_job_state`。
  - `JobExecutionClient`、`Job`、`JobState`、`JobExecutionResponseError` 與 topic-local
    unit tests。
  - 僅為此 family 在 `tach.toml` 建立明確 dependency boundary。

- **Out of scope**:
  - polling、wait/state-machine、background task、retry、timeout、cache、pagination 或
    concurrency policy。
  - job request payload、submitter、query parameter、request body、`Requester` API 或
    caller-owned resource lifecycle 的修改。
  - README、VERSION、release note、release、package-root export、
    `mlops_async.clients` export、shared test harness、`conftest.py`、request-contract
    fixtures，及任何既有 request-gate artifact。

## Locked Decisions

- 本 topic 是 **non-stable, no-release** topic；不建立 `Stable library metadata`，且
  `README.md`、`VERSION`、release metadata 均不得變更。
- canonical public import 僅為 `mlops_async.clients.job_execution`；
  `src/mlops_async/clients/job_execution/__init__.py` 只 re-export 此 family 的 public
  symbols。不得新增 package-root 或 `mlops_async.clients` 的 re-export。
- `JobExecutionClient` 建構子只接受 `Requester`。caller 擁有 requester、transport、auth
  及任何 resource lifecycle；client 不建立、關閉或 context-manage resource。
- 三個 public methods 均為 async，且每次 invocation 只直接 await 一次
  `Requester.request(method, path, headers=..., params={})`。它們不得建立
  `HttpRequest`、讀取 `Requester` private state、重試、輪詢、加入 timeout，或發出第二個
  request。
- 所有三個 endpoint 都帶 Legacy internal headers：`Delegate-Domain: ""` 與
  `Content-Type: application/json`。`start_job` 與 `get_job` 的 `Accept` 必須精確為
  `application/vnd.sas.job.execution.job+json, application/vnd.sas.job.execution.job.request+json, application/vnd.sas.error+json, application/json`。
- 路徑必須以 `EndpointPath` 建構，dynamic identifiers 使用
  `EndpointPath.from_segments()`；每個 call 的 `params={}`。`start_job` 沒有 body、
  query 或 submitter；所有 endpoint 均不得加入未鎖定的 request data。
- `JobState` 是 `str, Enum`，且只有六個值：`pending`、`running`、`canceled`、
  `completed`、`failed`、`timedOut`。`Job.state` 的型別必須是此 enum。
- `Job` 是 `@dataclass(frozen=True, slots=True)`，只公開下列由官方
  `components.schemas.job` 逐一映射的 snake_case fields：
  `id: str | None`、`state: JobState | None`、`state_details: str | None`、
  `results: Mapping[str, str] | None`、`error: Mapping[str, JSONValue] | None`、
  `job_request: Mapping[str, JSONValue] | None`、`heartbeat_interval: int | None`、
  `heartbeat_timestamp: str | None`、`creation_timestamp: str | None`、
  `modified_timestamp: str | None`、`end_timestamp: str | None`、
  `elapsed_time: int | float | None`、`log_location: str | None`、
  `expiration_timestamp: str | None`、`created_by: str | None`、
  `modified_by: str | None`、`submitted_by_application: str | None`、
  `links: tuple[Mapping[str, JSONValue], ...] | None`、`version: int | None`。
  schema 沒有 `required` array，所以所有欄位均為 optional：缺席映射為 `None`，不是
  `JobExecutionResponseError`。wire keys 只能依序映射為
  `id`、`state`、`stateDetails`、`results`、`error`、`jobRequest`、
  `heartbeatInterval`、`heartbeatTimeStamp`、`creationTimeStamp`、
  `modifiedTimeStamp`、`endTimeStamp`、`elapsedTime`、`logLocation`、
  `expirationTimeStamp`、`createdBy`、`modifiedBy`、`submittedByApplication`、
  `links`、`version`；不得新增別名或 datetime coercion。
- `Job` parser 對存在的欄位採 schema type 檢查：string/date-time-format 保留為 `str`；
  `state` 轉為 `JobState`；`results` 是每個 value 均為 `str` 的 object；
  `heartbeatInterval`、`version` 是非 `bool` 的 `int`；`elapsedTime` 是非 `bool` 的
  `int | float`；`error`、`jobRequest` 是 object，`links` 是由 object 組成的 array。
  `stateDetails` 存在時必須同時存在有效的 `state`，遵守 schema 描述的 conjunction。
  這三個 referenced object/array fields 是 raw JSON containers：不建立 Error、
  JobRequest 或 Link public VO，也不遞迴驗證或正規化其內容；parser 以 defensive copy
  產生與 response payload 脫鉤的 containers。`job` schema 沒有
  `additionalProperties: false`，故未知 top-level keys 允許但忽略，不放進 `Job` 或
  raw response 屬性；`Job` 不保留原始 payload、headers、status 或 content bytes。
- `get_job_state` 將成功 response 的 `text/plain` UTF-8 完整文字直接傳給
  `JobState(...)`：不 `strip()`、不 JSON decode、也不正規化空白或大小寫。無效 UTF-8、
  空白/換行造成的不相符文字、或非 enum 值皆 raise `JobExecutionResponseError`。
- `start_job` / `get_job` 的 `JobExecutionResponseError` 只代表成功 response 的
  semantic decode 失敗：body 無法 JSON decode、JSON root 不是 object、已存在的上述
  modeled field 型別不符（包含 `bool` 冒充 integer/number）、`state` 不在六個 enum
  值中、`stateDetails` 未搭配有效 `state`、`results` 的 key/value shape 不符、
  `error`/`jobRequest` 不是 object，或 `links` 不是 object array。它不因任何 Job
  field 缺席、未知 top-level key、或 raw nested container 的未知/未遞迴驗證內容而 raise。
  既有 HTTP/transport exceptions 與 `asyncio.CancelledError` 保持原樣傳播，exception
  message 不包含完整 response payload。
- 測試 helper 必須留在各自 test module；不得新增共用 harness、`conftest.py`、fixture
  JSON、或修改既有 `tests/unit/request_contract/**`。
- `tach.toml` 只可新增本 family 三個 module entries：
  `mlops_async.clients.job_execution` 依賴 client/value_objects、value_objects 依賴
  core/exceptions、client 依賴 value_objects/core/transport；其他 dependency policy
  不得修改。
- Async-planning status: triggered — cite trigger evidence: three new public async methods
  await `Requester.request()` and the resource ownership, failure, cancellation, and
  no-retry/no-timeout contract must be frozen before implementation.

### Async boundary decision

三個 client methods 是唯一 async I/O boundary；identifier validation、path/header building、
UTF-8/plain-text state conversion 與 JSON Job semantic parsing 均保持同步。

### Resource lifecycle decision

caller 建立並持有 `Requester` 及其下游 resources；`JobExecutionClient` 只保留 reference，
沒有 `close()` 或 async context manager。

### Concurrency model

每個 public method 僅直接 await 一次 request；不建立 task、`gather`、semaphore、stream、
fan-out、polling 或 background work。

### Failure model

HTTP/transport failures 和 cancellation 原樣傳播；只有成功 response 不符合本 plan 的 Job 或
JobState semantic contract 時，raise `JobExecutionResponseError`，且不包含完整 response
payload。

### Cancellation / timeout policy

不攔截 `asyncio.CancelledError`，不 cleanup caller-owned resource，也不加 timeout 或 retry；
既有 request option/transport 行為是 ReadOnly。

### Validation plan

使用每個 test module 自有的 fake requester，驗證單一 await、精確 method/path/headers、
`params={}`、無 body/query/submitter、Job JSON parsing、text/plain state parsing、exception
identity 與 cancellation；不進行 live I/O。

### Handoff notes for the implementer

先完成 Value Object/parser tests，再實作單一 request client methods。任何需要新增 path、
shared harness、root export、response field 擴張、polling/retry/timeout 或修改 ReadOnly
surface 的需求，都必須停止並回報 `BLOCKED`。

## Boundaries / Exclusions

- ReadOnly：`AGENTS.md`、`README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、所有 core/
  transport modules、既有 request-contract gates、docs、release/ledger surfaces，以及
  `src/mlops_async/__init__.py`、`src/mlops_async/clients/__init__.py`。
- Written：只限 `Artifact Paths` 列出的 topic plan、三個 Job Execution source files、兩個
  topic-local test files及 `tach.toml`。
- Creator 只實作本 plan 的 Implementation Steps；Reviewer 只給 verdict；Main Agent 負責
  後續 publish/PR/merge routing。review verdict 不授權擴大 endpoint 或 artifact scope。
- 若任何必要變更不在 Artifact Paths，或 legacy/request-gate evidence 與 locked contract
  衝突，停止於 `human-check`；不得自行推論或擴張。

## Status / Allowed Transitions

- **Current**: `creator-in-progress`
- **Execution model**: canonical creator -> reviewer -> publish -> merge；本 topic 在
  `merged` 結束，沒有 release phase。
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

- `human-check` 是 scope/evidence conflict 的外部 stop boundary，不是 workflow status 或
  allowed transition。
- `plan/job-execution-family/job-execution-family.step.md` 是本 topic 唯一的 creator
  completion gate：creator 只能在完成對應 Implementation Step 的可驗證工作後將其改為
  `[X]`；任何 `[ ]`（或小寫 `[x]`）存在時維持 `creator-in-progress`，五項均為 `[X]`
  才能轉為 `review-ready`。
- 本 topic 不建立 `review-log`、不宣告 round cap，且不修改 shared workflow surfaces。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/job-execution-family/job-execution-family.plan.md` | Planning actor | Repo-visible family implementation contract |
| Creator step tracker | `plan/job-execution-family/job-execution-family.step.md` | Creator | Five creator completion gates consumed before `review-ready` |
| Family public surface | `src/mlops_async/clients/job_execution/__init__.py` | Creator | Family-local public re-exports only |
| Job Execution client | `src/mlops_async/clients/job_execution/client.py` | Creator | Injected `Requester` three-endpoint client |
| Job Execution Value Objects | `src/mlops_async/clients/job_execution/value_objects.py` | Creator | `Job`/`JobState` semantics and response errors |
| Client tests | `tests/unit/clients/job_execution/test_job_execution_client.py` | Creator | One-request, headers, path, parameter, errors, and cancellation tests |
| Value Object tests | `tests/unit/clients/job_execution/test_job_execution_value_objects.py` | Creator | Enum, Job semantic parse, exact plain-text state parse, and error tests |
| Dependency guardrail | `tach.toml` | Creator | Add only the three locked Job Execution family module entries |

Artifact path notes:

- `README.md`、`VERSION`、`.github/copilot-instructions.md`、package-root exports and
  `mlops_async.clients` exports: no change.
- 不建立或修改 `conftest.py`、shared harness、fixture JSON、request-contract tests 或 analysis/
  spec artifacts，亦不得改動未列檔案。Creator 必須維護同目錄的 step tracker；它不是
  source/test change。
- 任何未列 path 的需求都是 plan-alignment failure，必須先停止於 `human-check`。

## Implementation Steps

1. Creator：建立 `src/mlops_async/clients/job_execution/value_objects.py`，定義
   `JobExecutionResponseError`、六值 `JobState(str, Enum)` 與完整 locked `Job` public
   fields；實作 optional-field / exact-type / raw-container / unknown-key policy 及精確的
   semantic-error boundary，以及 `text/plain` bytes 的 UTF-8 exact-text-to-enum
   conversion；不得 `strip()` 或 JSON decode state。完成且驗證後才標記 step tracker 的
   Gate 1。
2. Creator：建立 `src/mlops_async/clients/job_execution/client.py` 與 family-local
   `__init__.py`。`JobExecutionClient` 只接受 injected `Requester`，實作
   `start_job(job_request_id) -> Job`、`get_job(job_id) -> Job`、
   `get_job_state(job_id) -> JobState`；每個方法只 direct await 一次，使用 locked
   `EndpointPath`、headers 與 `params={}`，且不傳 request body/query/submitter。完成且
   驗證後才標記 step tracker 的 Gate 2。
3. Creator：在 `tests/unit/clients/job_execution/test_job_execution_value_objects.py` 建立獨立 tests，
   覆蓋六個 enum values、完整 `Job` wire-to-public-field mapping、所有 optional-field
   缺席、存在欄位的 exact type、`stateDetails` conjunction、raw referenced containers、
   unknown top-level keys ignored、unknown state、invalid UTF-8 及任何空白/換行 text/plain
   state 都是 `JobExecutionResponseError`。完成且驗證後才標記 step tracker 的 Gate 3。
4. Creator：在 `tests/unit/clients/job_execution/test_job_execution_client.py` 建立獨立 fake requester
   與 tests，覆蓋三端點的 exactly-one await、encoded dynamic path、各 endpoint locked
   headers、`params={}`、`start_job` 無 body/query/submitter、error/cancellation identity，
   並確保不新增 shared harness。完成且驗證後才標記 step tracker 的 Gate 4。
5. Creator：只在 `tach.toml` 加入 locked Job Execution family entries，然後於 WSL 執行
   topic-local pytest、Ruff、Pyright 與 Tach；檢查 diff 僅包含 Artifact Paths，且沒有
   retry/polling/timeout/root export/shared harness drift。完成且驗證後才標記 step tracker
   的 Gate 5。

## Validation / Acceptance Checks

- `JobExecutionClient` 的三個 public signatures 與回傳型別精確為
  `start_job(job_request_id) -> Job`、`get_job(job_id) -> Job`、
  `get_job_state(job_id) -> JobState`，且只從 family-local package 匯出。
- `Job` 的 19 個 locked public fields、wire names、types 與 optional rules 完全符合
  official `job` schema：所有 fields 缺席為 `None`；日期時間不轉型；raw
  `error`/`jobRequest`/`links` containers 脫鉤但不遞迴建模；未知 top-level keys ignored。
- `JobState` 精確只含 `pending`、`running`、`canceled`、`completed`、`failed`、`timedOut`；
  `Job.state` 是 `JobState | None` 而不是 raw string，且 `stateDetails` 不得脫離有效
  `state`。
- 每個 call 恰好一次 `Requester.request()`，dynamic identifier 經 `EndpointPath`，
  `params={}`，沒有第二個 outbound request、body、query、submitter、retry、polling 或
  timeout。
- 三 endpoint 都含 `Delegate-Domain: ""` 與 `Content-Type: application/json`；
  `start_job` / `get_job` 使用 locked exact Legacy JSON Accept value。
- `get_job_state` 將 raw `text/plain` UTF-8 complete text 直接 enum；任何 JSON decode、
  `strip()` 或 whitespace normalization 都使實作不合格。
- semantic response failure 僅在 locked JSON/root/known-field/state/raw-container conditions
  下由 `JobExecutionResponseError` 表示；缺席 optional field、未知 top-level key 與未遞迴
  驗證的 raw nested content 不得觸發它。HTTP/transport exceptions 與
  `asyncio.CancelledError` 維持 identity，不得包裝。
- `tach.toml` 只含 locked 三項 addition，且 source/test/diff 未超出 Artifact Paths。
- 使用現有 project configuration 透過 WSL 驗證：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 pytest --override-ini addopts='' tests/unit/clients/job_execution/test_job_execution_value_objects.py tests/unit/clients/job_execution/test_job_execution_client.py -q
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 ruff check src/mlops_async/clients/job_execution/__init__.py src/mlops_async/clients/job_execution/client.py src/mlops_async/clients/job_execution/value_objects.py tests/unit/clients/job_execution/test_job_execution_value_objects.py tests/unit/clients/job_execution/test_job_execution_client.py
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 pyright
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --python 3.10.0 tach check
```

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

無。本 topic 為 non-stable、no-release；merge 不得觸發 README、VERSION、tag 或 release
note 變更。

## Open Questions / Unresolved Items

- 無。人類已核准的 formal contract 凍結 endpoint、header、response、error、async 與
  artifact-path decisions；與現有 historical shape-only gate 不同之處不授權實作者回推修改。
