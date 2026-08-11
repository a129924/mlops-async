---
topic: job-execution-family
type: correction-plan
parent_plan: plan/job-execution-family/job-execution-family.plan.md
parent_step: plan/job-execution-family/job-execution-family.step.md
created: 2026-08-10
status: approved
---

# Job Execution Family — Post-merge Correction Plan

> **Analysis-layer routing: incomplete**
>
> `analysis/job-execution-family/requirements.md` 與
> `analysis/job-execution-family/technical-spec.md` 均不存在。本 correction 僅依已合併
> parent plan、已鎖定 human decisions 與下列 review-thread 診斷；不得藉此重新探索
> endpoint、architecture 或 release scope。

## Goal / Outcome

在既有 `job-execution-family` topic 內完成一個最小 post-merge correction，使三項已鎖定
Job Execution 契約重新一致：

1. `get_job_state()` 發送完整 Legacy header set，且 `Accept: text/plain`。
2. `stateDetails` 不會在沒有合法 `JobState` 時形成 `Job(state=None, ...)`。
3. JSON success decoder 不遞迴驗證 raw nested containers，極深巢狀資料不會從該額外驗證
   路徑洩漏 `RecursionError`。

此 artifact 是 post-merge correction 的 historical decision record；它不覆寫或淡化已合併的
parent plan/step。

## Scope

- **In scope**:
  - `GET /jobExecution/jobs/{jobId}/state` 的 `Accept: text/plain`、Legacy internal
    headers、無 query、無 body 與一次 `Requester.request()` 契約。
  - `Job.state` / `stateDetails` 的已鎖定 conjunction：非 null `stateDetails` 必須伴隨
    已驗證的 `JobState`。
  - `start_job` / `get_job` JSON success decoder 的 syntax/encoding error boundary；保留
    modeled shallow fields 的 parser 驗證，取消對 raw nested containers 的全遞迴驗證。
  - 兩個 family-local unit-test modules，以及既有 state request gate 的 local harness、test
    與 mock-response fixture；gate 只可作 request-shape baseline，不得作 response oracle。

- **Out of scope**:
  - 其他 endpoint、public method signature、`JobState` 六個值、`Job` 欄位集合、Requester
    lifecycle、transport error/cancellation propagation。
  - polling、retry、timeout、wait-until-complete、background task、job orchestration。
  - shared request-contract harness、`tests/unit/request_contract/header_families.py`、core/
    transport、package-root 或 `mlops_async.clients` export。
  - README、VERSION、release metadata、tag、release、worktree/branch cleanup、PR closure
    或既有 feature branch/worktree 刪除。

## Locked Decisions

- 本 correction 屬同一已合併 `job-execution-family` topic；不可另開 topic，亦不可重寫
  parent plan/step 的歷史內容。
- `get_job_state(self, job_id: str) -> JobState` 維持不變；其 request 必須恆送
  `Delegate-Domain: ""`、`Content-Type: application/json` 與 `Accept: text/plain`，使用
  `params={}`、不送 body，且每次 public call 只 `await` 一次遠端 request。
- state response 僅以 UTF-8 解碼的完整 `text/plain` 建立 `JobState`；不得 strip、normalize、
  JSON decode 或回退為 `str`。未知值、非 UTF-8 或 enum conversion 失敗均 raise
  `JobExecutionResponseError`。
- `JobState` 的完整 wire set 仍只有 `pending`、`running`、`canceled`、`completed`、
  `failed`、`timedOut`；`Job.state` 仍使用同一 enum。
- `stateDetails` 為 non-null string 時，`state` 必須存在且先成功轉換為 `JobState`；缺失或
  null `state` 必須 raise `JobExecutionResponseError`，不得構造半一致 `Job`。
- JSON decoder 只翻譯 JSON syntax/UTF-8/decode failure 至 family-local response error；不對
  lists、dicts 或其子項作遞迴 JSONValue 驗證。`parse_job()` 仍只驗證 modeled top-level
  fields 與其既有 shallow shape，raw `error`、`jobRequest`、`links` nested content 不新增
  schema policy。
- 原先 human 已鎖定本 family 為 **non-stable, no-release**。本 correction 即使再次 merge，
  也不得 tag、release 或 cleanup；`merged` 為此 correction 的 terminal state。
- state request gate 的原 internal-wrapper JSON mock 無 response authority。它必須改為
  `text/plain` test fixture 與 `JobState` assertion，且不得以 JSON mock 或
  `{"state": ...}` 宣稱 endpoint runtime truth。

## Boundaries / Exclusions

- Planning actor 只可撰寫本 correction plan/step；Creator 才可改列出的 source/tests/gate；
  獨立 Reviewer 才可判斷 plan/implementation contract 與 scope drift；Main Agent 才可 route
  commit/push/PR/human review。
- `plan/job-execution-family/job-execution-family.plan.md` 與 `.step.md` 是已合併歷史；本
  correction 必須以新增 artifact 保留差異記錄，不得把它們回寫成未合併或目前 execution state。
- 現有 feature branch/worktree 是 correction 的保留工作區，不得在本 correction 中刪除、清理
  或重建。
- 若實作發現任一條修正需要改 shared harness、header family、Requester API、public API 或
  unlisted path，停止並交回 human-check；不得擴張本 correction。

### Bounded parent-sync closure

`plan/job-execution-family/job-execution-family.plan.md` 目前的 `Current:
creator-in-progress` 與已發生的 PR #64 merge 不一致。此 correction 的唯一 parent-sync
closure 是一項 **planning-only status backfill**，不是重新執行 parent topic：

- **Owner**: Planning actor；不得交由 Creator、Reviewer 或 Main Agent 代改。
- **Timing**: 本 correction plan 經獨立 Plan-Reviewer verdict `approved` 後、任何 source/test/gate
  implementation 開始前。
- **Exact path and edit**: 僅在
  `plan/job-execution-family/job-execution-family.plan.md` 的 `## Status / Allowed Transitions`
  將 `**Current**: creator-in-progress` 改為 `**Current**: merged`，並在同 section 的 Routing
  notes 加入 PR #64 merge SHA `7411c65dea56aaab3e07e647c5a671849a924b5d` 與本 retained
  correction artifact path 的 historical routing note。
- **Exclusions**: 不改 parent Goal/Scope/Locked Decisions/Artifact Paths/Implementation Steps/
  Validation/Reviewer Handoff/Post-merge actions，不改 parent step tracker，不回寫 code/tests，
  不做 release/tag/cleanup。
- **Closure evidence**: independent Reviewer 必須確認 parent diff 只含上述 status/routing-note
  backfill，且 parent current state 為 `merged`；否則本 correction 不得 publish。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: correction plan review -> independent creator implementation -> independent
  review -> bounded human-check -> approved -> publish/PR -> merge；不進入 release 或 cleanup。
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

- 獨立 Reviewer 的 implementation verdict 是 `approved-with-human-check`。唯一 human-check 是
  WSL 無法解析 Windows linked-worktree `.git` pointer 的 shared policy guard 環境例外；它不是
  Job Execution production/test/gate defect，且修 shared guard 屬本 correction scope 外。
- Human 已明確接受該 WSL linked-worktree environment exception。因此在不擴張 shared guard
  scope 的前提下，本 correction 由 `reviewer-in-progress` 進入 `approved`。
- 已保留的驗證證據為：511 passed、coverage 95.76%，Ruff format/lint、Pyright、Tach 與
  diff check 均通過。此 evidence 不代表已執行 commit、push、PR、merge、release 或 cleanup。
- `PRRT_kwDOSTt_386X3TAX` 是 ADDRESS：依既有 human-locked text/plain decision 修正，不重開
  DISCUSS。
- `PRRT_kwDOSTt_386X3TBC` 是 ADDRESS：補足 `stateDetails` conjunction。
- `PRRT_kwDOSTt_386X3TBl` 是 ADDRESS：收斂為 parent plan 的 raw-container boundary，而非
  擴大深層 JSON validation policy。
- 若任何三項 review diagnosis 與已鎖定契約有真實衝突，轉 `human-check`，不以 status
  transition 假裝解決。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Parent-status backfill | `plan/job-execution-family/job-execution-family.plan.md` | Planning actor | 僅於 approved 後寫入 bounded `creator-in-progress` -> `merged` closure |
| Historical parent step | `plan/job-execution-family/job-execution-family.step.md` | ReadOnly | 已合併 creator gate 記錄；不得回寫 |
| Correction plan | `plan/job-execution-family/job-execution-family.post-merge.correction-plan.md` | Planning actor | 本次 retained correction contract |
| Correction step tracker | `plan/job-execution-family/job-execution-family.post-merge.correction-step.md` | Creator | correction creator completion gates |
| Client correction | `src/mlops_async/clients/job_execution/client.py` | Creator | state request headers 與 non-recursive JSON decoder boundary |
| Value-object correction | `src/mlops_async/clients/job_execution/value_objects.py` | Creator | state/stateDetails conjunction |
| Client unit tests | `tests/unit/clients/job_execution/test_job_execution_client.py` | Creator | exact state request headers and decoder regression tests |
| Value-object unit tests | `tests/unit/clients/job_execution/test_job_execution_value_objects.py` | Creator | stateDetails conjunction regression tests |
| State-gate local harness | `tests/unit/request_contract/job_execution_jobs_state_request_gate/conftest.py` | Creator | text/plain fixture parsing and local legacy-header expectation only |
| State-gate test | `tests/unit/request_contract/job_execution_jobs_state_request_gate/test_get_job_state_request_contract.py` | Creator | `JobState` assertion; no JSON response oracle |
| State-gate mock fixture | `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.mock-responses.json` | Creator | non-authoritative `200 text/plain` fixture |
| State-gate request-flow fixture | `tests/unit/request_contract/job_execution_jobs_state_request_gate/fixtures/get_job_state.request-flow.json` | ReadOnly | shape-only request evidence; no response authority |

Artifact path notes:

- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`tach.toml`、package exports、shared
  request-contract harness 與 `tests/unit/request_contract/header_families.py` 均不得修改。
- Parent-sync closure 以外的 parent plan 內容，以及完整 parent step tracker，均為 ReadOnly。
- 任一未列路徑的需求是 plan-alignment failure，必須 human-check。

## Implementation Steps

0. Planning actor 在 correction plan review `approved` 後、Creator 寫入 source/tests/gate 前，完成
   `Bounded parent-sync closure` 所列的唯一 parent-plan status/routing-note backfill，並交由獨立
   Reviewer 確認 diff scope；不符合時停止，不可進入 Step 1。

1. Creator 在 `client.py` 將 state endpoint 的 headers 固定為三個已鎖定值，保留
   `EndpointPath.from_segments()`、`params={}`、無 body 與單一 await；不得調整其他 endpoint。
2. Creator 在 `value_objects.py` 先取得已驗證 `JobState | None`，再處理 `stateDetails`；當
   `stateDetails` 為 non-null 而 state 非合法 enum 時 raise family-local response error。
3. Creator 在 `client.py` 移除對 decoded raw nested containers 的 recursive traversal；保留
   JSON decoding exceptions 的 family-local translation，讓 `parse_job()` 管理既有 modeled
   shallow semantic checks。
4. Creator 更新兩個 family-local unit-test modules：exact state headers、six-value plain text
   behavior、no strip/non-UTF-8/unknown state、stateDetails-without-state rejection，以及足夠深的
   JSON success payload 不因 client recursive validator 失敗且不新增 nested validation。
5. Creator 僅在 state request gate 的三個 listed local files 將 fixture/assertion 收斂至
   `200 text/plain` + `JobState`，保留 shape-only/non-authoritative 標示，並驗證 Legacy
   headers、無 query/body；不得修改 shared gate utilities。
6. Creator 依 correction step tracker 執行 WSL validation，確認 diff 僅在 listed writable
   paths，然後移交獨立 Reviewer。

## Validation / Acceptance Checks

- parent plan 的 `Current` 已為 `merged`，並只具 PR #64 merge SHA 與 correction artifact path
  的 historical routing note；parent step tracker 保持原樣，parent diff 無其他變更。
- `get_job_state("job id/slash")` 只發出一個 GET 到 encoded state path，headers 精確包含
  `Delegate-Domain: ""`、`Content-Type: application/json`、`Accept: text/plain`，query 是
  `{}`，body 是 `None`。
- `parse_job_state()` 與 client state method 對六個完整 text values 回傳對應 `JobState`；
  leading/trailing whitespace、JSON text、unknown value、非 UTF-8 均為
  `JobExecutionResponseError`。
- `parse_job({"stateDetails": "detail"})`、`parse_job({"state": null,
  "stateDetails": "detail"})` 必須失敗；合法 state + string detail 仍成功；null/absent
  stateDetails 維持 parent optional-field policy。
- 深巢狀 raw nested JSON success payload 不經 client recursive walk，並保留 parse_job 對
  modeled shallow fields 的既有 error contract；decode syntax/UTF-8 failures仍為
  `JobExecutionResponseError`。
- state request gate mock 使用 `Content-Type: text/plain` 與 text body，assert result 是
  `JobState`，不使用 `json_body`、`{"state": ...}` 或 JSON parser 當 oracle。
- WSL only commands:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --frozen python -m pytest --override-ini addopts='' tests/unit/clients/job_execution/test_job_execution_client.py tests/unit/clients/job_execution/test_job_execution_value_objects.py tests/unit/request_contract/job_execution_jobs_state_request_gate -q
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --frozen python -m ruff format --check src/mlops_async/clients/job_execution/client.py src/mlops_async/clients/job_execution/value_objects.py tests/unit/clients/job_execution/test_job_execution_client.py tests/unit/clients/job_execution/test_job_execution_value_objects.py tests/unit/request_contract/job_execution_jobs_state_request_gate
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --frozen python -m ruff check src/mlops_async/clients/job_execution/client.py src/mlops_async/clients/job_execution/value_objects.py tests/unit/clients/job_execution/test_job_execution_client.py tests/unit/clients/job_execution/test_job_execution_value_objects.py tests/unit/request_contract/job_execution_jobs_state_request_gate
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --frozen python -m pyright
powershell -ExecutionPolicy Bypass -File scripts/wsl-run.ps1 uv run --frozen tach check
```

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [
      "PRRT_kwDOSTt_386X3TAX",
      "PRRT_kwDOSTt_386X3TBC",
      "PRRT_kwDOSTt_386X3TBl"
    ],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

本 correction merge 後不做 README/VERSION 變更、tag、release、release note、worktree cleanup、
feature-branch deletion 或 post-merge cleanup。由 Main Agent 交還 human review；任何後續 release
必須另經 release gate，且不在本 correction scope。

## Open Questions / Unresolved Items

- 無 blocking question。三項 correction 的 source boundary 與 exact scope 已由 human-locked
  decisions、parent plan 與 review-thread diagnosis 凍結；後續 publish/PR 仍是獨立、尚未執行的
  workflow action。
