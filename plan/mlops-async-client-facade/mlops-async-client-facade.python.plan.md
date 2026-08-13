---
topic: mlops-async-client-facade
phase: plan-authoring
status: approved
created: 2026-08-12
d1_verdict: non-trivial
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# MlopsAsyncClient Python 實作計畫

## Goal

修正 facade owned `HttpClient` 的 close lifecycle，讓 concurrent/repeated close
single-flight、only-success-is-closed，且底層 close failure/cancellation 可重試；
同步 unit tests 與 HTTP/auth boundary doc。

## Non-goals

- 不改 public constructor、properties、endpoint APIs 或 exception classes。
- 不改 `core`、`clients`、`__init__.py` 或 AuthClient tests。
- 不修改 root seven-target / transport two-target lists 或任何其他 `tach.toml` content。
- 不做 version、release、tag、merge 或未指定 PR thread resolution。

## Current Context

PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d` 是已發布 baseline。
它不能證明目前 correction 已驗證；五條先前 action threads 已在 `9b51f95` 解決，兩條新
action threads 曾將本 companion 置於 `needs-rework -> creator-in-progress`。本輪 correction plan
已由獨立 Plan-Reviewer 批准，direct transport implementation review 亦已批准；isolated ext4
full-validation 是歷史 evidence，current full-validation、code review、correction push/readback 與
`PRRT_kwDOSTt_386Y0BD0` resolution 仍 pending。

目前 facade 已是 `HttpClient` 唯一 owner，且 Tach root exact seven targets 與 transport
exact two targets 已在 baseline；本輪只凍結並驗證那些 lists，不能調整它們。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagY` | transport doc | resolved history at `9b51f95`; no future resolve |

上述五條 thread 是已解決歷史，沒有 future resolve。本輪 pending correction 只新增
`PRRT_kwDOSTt_386YypkF`（concrete `HttpClient.aclose()` failure/cancellation 後的真實
cleanup retry，facade 不得信任 underlying no-op retry）與 `PRRT_kwDOSTt_386YypkJ`
（README/architecture facade 現況敘述為繁體中文）。

## 本輪 fresh evidence

focused facade/transport tests `80 passed`（`--no-cov`）；default assertions `80 passed`，
coverage `56.80%` 的唯一失敗為 fail-under。Ruff、Pyright、Tach、diff check 通過。isolated ext4
correction snapshot full non-E2E 為 `704 passed, 9 skipped, 1 deselected`、coverage `94.43%`；
base `9b51f95` 加十個 correction files 的 manifest SHA-256
`219b3593cb3213f035c728232d377eb2db55966b94ee967ba8532a3e755ce809` 相符。`uv sync --frozen`、
Ruff format/check、Pyright、Tach 與 diff check 通過；step 9 的 isolated ext4 full-validation
已完成，但僅為歷史 evidence，current full-validation 仍 pending。

## Requirements

1. `MlopsAsyncClient` 的 public contract、lazy auth 和 identity-stable properties 不變。
2. 第一次 close 建立唯一 private shared close task；所有 concurrent/repeated calls
   await 同一 task，底層 `HttpClient.aclose()` 最多執行一次。
3. shared task 成功才設 closed；成功後 later calls no-op。
4. 底層 close raise 或 cancellation 時，facade 保持可 close、清除 completed failed task，
   讓 later call retry；不吞掉 error/cancellation。
5. cancelled caller 不得取消 shared task 或使其他 caller 無法得到成功結果。
6. unit tests 與 `docs/standards/http-client-auth-boundary.md` 準確表達 requirements 2–5。
7. `HttpClient.aclose()` 的 concrete managed cleanup failure/cancellation 後必須保留真實
   retry；no-op 回傳不能使 facade 宣稱 success。對應測試只寫在
   `tests/unit/transport/test_http_client.py`。
8. README 與 `docs/ARCHITECTURE.md` 的新增 facade 現況敘述必須使用繁體中文；canonical
   headings、fixed labels、必要技術術語可保留原文。
9. Tach shape 必須保留 root `clients`, `core`, `transport`, `cas_tables`,
   `job_execution`, `models`, `projects` 順序，transport 必須只有 `core`,
   `exceptions`。

## Decisions

- Async-planning status: triggered — `aclose()`/async context manager 現在改變
  shared async lifecycle、concurrency、failure 與 cancellation behavior；依
  `analysis/mlops-async-client-facade/technical-spec.md` 的 Lifecycle and Error Contract。
- Module/package placement: facade private lifecycle code 在
  `src/mlops_async/mlops_async_client.py`；concrete retry code 在
  `src/mlops_async/transport/http_client.py`；tests 分別在
  `tests/unit/test_mlops_async_client.py` 與 `tests/unit/transport/test_http_client.py`；
  docs 在 `docs/standards/http-client-auth-boundary.md`、`README.md`、
  `docs/ARCHITECTURE.md`。
- New public API: 否；private fields/task 與既有 `aclose()` behavior correction。
- Interface changes: 否；family constructors、Requester、HttpClient interface 和
  Tach configuration 不變。
- Breaking changes allowed: 否。
- New dependencies: 否；使用 standard-library `asyncio` 與現有 runtime。
- Error handling strategy: 不包裝底層 error 或 `asyncio.CancelledError`；failed/cancelled
  close 只重設 private lifecycle state，並讓 concrete managed cleanup 真的可重試。
- Typing strategy: private state 使用 strict `asyncio.Task[None] | None`（或現有
  strict-compatible equivalent），不新增 `Any` 或 public Protocol。

### Async boundary decision

endpoint I/O 邊界不變；此修正只在 facade 的 close coordination 建立 single-flight task。

### Resource lifecycle decision

Facade 保持唯一 `HttpClient` owner。private task 是唯一 close-in-progress marker；
success 才 closed，failure/cancellation 可重試，properties 不因 close 消失。

### Concurrency model

第一個 caller 建 task，後續 callers await 同一 task。使用 shield 防止單一 waiter
cancellation 取消 operation；不引入 queue、fan-out、background service 或 parallel I/O。

### Failure model

底層 close raise/cancellation 原樣傳播；若 task 已結束且不成功，清除 in-progress state。
未成功前不得宣稱 closed；後續 caller 可建新 task retry。

### Cancellation / timeout policy

不新增 timeout/retry public policy。caller cancellation 只取消該 waiter；shared task
持續。底層 task 自身 cancellation 導致可重試而非 permanent closed。

### Validation plan

先跑 focused facade/transport tests，再跑 full non-E2E pytest、Ruff、Pyright、Tach、diff check；
每個結果都屬本輪 correction evidence，不能沿用 baseline 口述結論。最後依序
implementation review、code review、commit/push/readback/thread resolution。

### Handoff notes for the implementer

不要以 bool 在底層 close 開始前標示 closed；不要每個 caller 各自 close；不要在
`CancelledError` path 遺留 completed failed task；不要把 concrete transport cleanup 的 no-op
回傳當作成功。只改六個 authorized implementation
files，並保留 properties/Requester/auth composition。完成後不要自行 commit/push/reply/
resolve threads。

## Public Contract / API Changes

## Current direct-transport correction delta

`PRRT_kwDOSTt_386Y0BD0` 是唯一 current unresolved thread；`PRRT_kwDOSTt_386YypkF` 和
`PRRT_kwDOSTt_386YypkJ` 已在 `ea5732e` remote-head readback resolved，僅保留歷史 evidence。
本 delta 只授權 direct `HttpClient.aclose()` 的 private coordination，不修改 facade ownership、
`MlopsAsyncClient` public surface、Tach 或文件。

實作者必須讓第一個 direct caller 建立一個 shared managed-cleanup attempt，讓所有同時 direct
callers await 同一 attempt 並共同收到 success、原始 failure 或 `CancelledError`。waiter 自身的
cancellation 不得取消 shared attempt。attempt failure/cancellation 必須清除 in-progress marker，
而 non-success 不得設定 closed；下一個序列 caller 因此再次發起真實 managed cleanup，而不是接受
temporary `httpx` close state 的 no-op success。成功後才允許後續序列 no-op。

`tests/unit/transport/test_http_client.py` 要以 event/barrier fake 寫三組 deterministic tests：兩個
concurrent direct callers 的 success、failure、cleanup cancellation 都只產生一個底層 call；failure
與 cancellation 後各再做一次成功的序列 retry，累計 call count 為二。現有 facade tests 可回歸，
但不得以本 delta 取得或改寫 facade lifecycle ownership。

本輪已完成 independent Plan-Reviewer 與 implementation-review approval；remaining 順序是 current
full-validation → independent code review → `commit --no-verify` → push → GraphQL remote-head readback → 只 resolve
`PRRT_kwDOSTt_386Y0BD0` → GraphQL readback。此作者工作現在只更新 plan，不能 self-review。

無。`MlopsAsyncClient.aclose() -> None` 與 async context manager signature 不變；
本輪只修正其 concurrency/failure semantics。

## Affected Files / Modules

- `src/mlops_async/mlops_async_client.py`：private close lifecycle state/task。
- `tests/unit/test_mlops_async_client.py`：single-flight/failure/cancellation regression。
- `src/mlops_async/transport/http_client.py`：concrete managed cleanup retry state。
- `tests/unit/transport/test_http_client.py`：concrete failure/cancellation retry regression。
- `docs/standards/http-client-auth-boundary.md`：facade ownership、close semantics、
  frozen Tach boundary doc sync。
- `README.md`、`docs/ARCHITECTURE.md`：繁體中文 facade 現況敘述。
- six topic artifacts：workflow/evidence handoff。

## Implementation Steps

1. 在 `src/mlops_async/mlops_async_client.py` 加入或整理 strict-typed private closed 與
   in-progress task state；第一個 `aclose()` caller 僅建立一個底層 close task。
2. 在同檔讓 every caller shield-await 同一 task；success 後設定 closed，raise 或
   underlying cancellation 後清除 completed task 並保持可 retry；`__aexit__` 保持委派。
3. 在 `tests/unit/test_mlops_async_client.py` 寫 tests：single successful close + later
   idempotence、two concurrent callers one underlying close、raise then successful retry、
   underlying cancellation then retry、cancelled waiter 不取消 shared operation。
4. 在 `docs/standards/http-client-auth-boundary.md` 描述同一 ownership/lifecycle
   contract 和 frozen root/transport Tach dependency direction；不改 config。
5. 在 `src/mlops_async/transport/http_client.py` 實作 concrete managed cleanup retry；
   對 `tests/unit/transport/test_http_client.py` 寫 first close raise/cancellation、後續
   真實 retry、no-op 不得偽造 cleanup success 的 tests。
6. 在 `README.md` 與 `docs/ARCHITECTURE.md` 新增或修正繁體中文 facade 現況敘述。
7. 以 diff inspection 確認僅 authorized paths 且 Tach lists 不變，執行 validations，
   再交 independent implementation/code reviewers。

## Test Plan

- Happy path: first close success，later `aclose()` no-op；properties 仍 identity-stable。
- Invalid input: 既有 credential/URL validation tests 保持不變。
- Edge case: simultaneous `aclose()` callers share one operation；cancelled waiter isolation。
- Regression: failed 或 cancelled underlying close 後下一 call succeeds；domain closed-transport
  behavior 和 lazy password-token flow 保持既有 tests。
- Concrete cleanup: `HttpClient` first managed close failure/cancellation 後，retry 必須再次
  觸發 managed cleanup；underlying no-op 不得使 facade 視為 closed。
- Documentation: README 與 architecture 的新增 facade 現況文字為繁體中文。
- Backward compatibility: direct family constructors/imports 及 existing facade public
  contract 不變；full suite 監控。

## Validation Commands

透過 WSL，且不得執行 Windows project-local `.venv`：

```powershell
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync pytest --no-cov tests/unit/test_mlops_async_client.py tests/unit/transport/test_http_client.py tests/unit/clients/test_auth_client.py'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync pytest --no-cov -m "not viya_e2e"'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync ruff check --no-fix .'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync pyright'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync tach check'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && git diff --check'
```

## Risks

- 將 closed 提前設為 true 會使 close failure/cancellation 永久遺失 retry 路徑。
- 未 shield shared task 會讓單一 cancelled waiter 取消所有 callers 的 close。
- docs 若未同步既有 Tach composition boundary，會與已提交 config 和 lifecycle ownership
  契約漂移。

## Rollback Plan

若 correction 不通過，僅 revert 此 plan 列出的 source/test/doc 與六 artifacts 的
correction diff，回到 `ed29e837…` baseline；不動 ReadOnly paths、Tach lists、branch 或
remote state。

## Open Questions

無。行為、files、tests、frozen Tach lists 與 reviewer routing 均已鎖定。
