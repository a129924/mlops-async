---
topic: mlops-async-client-facade
phase: plan-authoring
status: creator-in-progress
created: 2026-08-12
d1_verdict: non-trivial
branch: feat/andrew/mlops-async-client-facade
worktree: D:\code\python\mlops-async.worktrees\agent-20260812-mlops-async-client-facade
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# MlopsAsyncClient facade 實作計畫

> **Analysis-layer routing: strict mode.**
> `analysis/mlops-async-client-facade/technical-spec.md` 是 execution-facing
> source of truth；`requirements.md` 是 business-intent guardrail。本次只處理
> 五條 PR review threads 所要求的 lifecycle/docs rework，不重新定義原先 facade
> contract、scope 或 frozen Tach shape。

## Goal / Outcome

在不擴張 public API 或 Tach authorization 的前提下，修正 `MlopsAsyncClient` 的
`aclose()` single-flight lifecycle，補足 test coverage，並同步 HTTP/auth boundary
文件，使 PR #70 可針對指定 threads 提交、推送與 resolve。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 implementation handoff |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 implementation handoff |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | 六份 topic artifacts 的 correction evidence |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | 六份 topic artifacts 的 workflow/evidence handoff |
| `PRRT_kwDOSTt_386YpagY` | transport doc | `docs/standards/http-client-auth-boundary.md` 的文件 handoff |

上述五條 threads 全部仍未 resolved；本表僅補正可追溯性，不改變技術契約、範圍或 correction validation/review/publish 的 pending 狀態。

## Scope

### In-Scope

- PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d` 所代表的已發布
  facade baseline；其既有 source/tests/docs/Tach 是歷史基線，不等於本輪完成。
- `src/mlops_async/mlops_async_client.py` 的 private close coordination。
- `tests/unit/test_mlops_async_client.py` 的 lifecycle race/failure/cancellation
  tests。
- `docs/standards/http-client-auth-boundary.md` 對 facade ownership/lifecycle 和
  frozen Tach composition boundary 的同步說明。
- six topic artifacts 的 current/historical evidence 修正與 implementer handoff。

### Out-Of-Scope

- `.users`、other grants、transport injection、retry/timeout/cancellation public API、
  facade-specific exception、RequestExecutor/CAS migration。
- `core`、`transport`、`clients` production source、endpoint behavior、root export、
  AuthClient tests、README、architecture doc、VERSION/tag/release/release notes/live E2E。
- 任一 `tach.toml` content；root seven-target 和 transport exact two-target lists
  都只可驗證、不可修改。

## Locked Decisions

- Constructor 的五個 required keyword-only `str` arguments、five readonly
  identity-stable namespace properties、lazy auth/runtime composition 保持不變。
- Facade 是唯一 `HttpClient` close owner；family clients 不取得 lifecycle ownership。
- `aclose()` 維護 private shared in-progress `asyncio.Task[None]`（或等價 private
  state）。若尚未 closed，第一個 caller 建立唯一底層 close task；所有 concurrent 或
  repeated callers await 該 task，不能重複呼叫 `HttpClient.aclose()`。
- await shared task 必須 shield；一個 waiter 的 cancellation 不可取消 shared close。
  底層 task 成功後才標記 permanent closed。底層 task raise 或被取消時，清除已結束
  in-progress state、不可標 closed、讓後續 caller 重試；failure 和 cancellation 原樣傳播。
- `__aexit__` 使用同一 `aclose()` lifecycle 且不 suppress context exception。
- frozen Tach root list 的順序必為 `mlops_async.clients`、`mlops_async.core`、
  `mlops_async.transport`、`mlops_async.clients.cas_tables`、
  `mlops_async.clients.job_execution`、`mlops_async.clients.models`、
  `mlops_async.clients.projects`；transport list 必須且僅為
  `mlops_async.core`、`mlops_async.exceptions`。兩 lists 均 ReadOnly。
- 此為 stable-library-affecting additive public API，但本 topic 不 bump VERSION、
  不建立 tag/release；本輪 correction 也不改 public API。

## Boundaries / Exclusions

### Written

- 無。

### Modify

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`
- `docs/standards/http-client-auth-boundary.md`
- `analysis/mlops-async-client-facade/requirements.md`
- `analysis/mlops-async-client-facade/technical-spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.step.md`

### ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/transport/**`、
  `src/mlops_async/clients/**`、`src/mlops_async/__init__.py`。
- `tests/unit/clients/test_auth_client.py`、`README.md`、`docs/ARCHITECTURE.md`、
  `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`。
- `tach.toml` 的 root exact seven-target list、transport exact two-target list，
  以及其他全部 blocks、global flags、excludes、interfaces 與 content。

### Deleted

- 無。

## Status / Allowed Transitions

**Current:** `creator-in-progress`。PR #70 published baseline 是
`ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d`；original plan-review approval 是
完成的歷史 gate。五條 action threads 使本輪 correction 採
`needs-rework -> creator-in-progress`。

本輪 source/tests/docs rework 與 focused/static evidence 已完成；完整 non-E2E
validation 仍因 WSL environment exception pending，implementation review、code review、
correction commit/push 與 thread resolution 也仍 pending。這些 current states 與既有
baseline 不得混寫為 current completion。

Allowed transitions: `planned -> creator-in-progress -> review-ready ->
reviewer-in-progress -> approved|needs-rework`; `needs-rework ->
creator-in-progress`; `approved -> creator-in-progress|publish-in-progress`;
`publish-in-progress -> pr-open|merged`; `pr-open -> needs-rework|merged`;
`merged -> terminal`。

## Artifact Paths

| Artifact | Path | Owner | Purpose |
| --- | --- | --- | --- |
| Requirements | `analysis/mlops-async-client-facade/requirements.md` | Plan-Creator | 範圍、frozen Tach、lifecycle requirements |
| Technical spec | `analysis/mlops-async-client-facade/technical-spec.md` | Plan-Creator | single-flight close execution contract |
| Topic plan | `plan/mlops-async-client-facade/mlops-async-client-facade.plan.md` | Plan-Creator | workflow routing |
| Python companion | `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md` | Plan-Creator | Python implementer handoff |
| Specification | `plan/mlops-async-client-facade/mlops-async-client-facade.spec.md` | Plan-Creator | acceptance scenarios |
| Step tracker | `plan/mlops-async-client-facade/mlops-async-client-facade.step.md` | Plan-Creator | current pending gates |
| Source | `src/mlops_async/mlops_async_client.py` | Python implementer | private lifecycle correction |
| Tests | `tests/unit/test_mlops_async_client.py` | Python implementer | lifecycle regression tests |
| Boundary doc | `docs/standards/http-client-auth-boundary.md` | Python implementer | ownership/Tach documentation sync |

## Stable library metadata

- `stable_library`: yes; additive API already exists in the PR baseline.
- `README action`: none in this correction; `README.md` is ReadOnly.
- `VERSION bump`: no.
- `release timing`: no version/tag/release in this topic or correction.
- `publish timing`: only after correction validation and both independent reviews;
  it means a topic correction commit/push to the existing PR, not merge/release.

## Implementation Steps

1. 在 `src/mlops_async/mlops_async_client.py` 檢視 current `aclose()` state，新增或
   調整 private closed/in-progress fields，確保僅成功後 closed、失敗/cancellation 可重試。
2. 在同檔以 single shared close task 與 shield 實作 concurrent/repeated close；
   `__aexit__` 保持委派同一 `aclose()`，不改 public contract 或 other source modules。
3. 在 `tests/unit/test_mlops_async_client.py` 新增成功 idempotence、concurrent/repeated
   close 單一底層 call、failure retry、underlying-close cancellation retry、cancelled
   waiter 不取消 shared close 的 tests；保留既有 identity/lazy-auth/closed-transport tests。
4. 在 `docs/standards/http-client-auth-boundary.md` 同步 facade 的唯一 ownership、
   successful-close-only state、failure/cancellation retry 與 frozen root/transport Tach
   boundary；不得改 `tach.toml` 或 docs 以外 scope。
5. 檢查本輪 diff，確認 frozen Tach lists 完全未改、沒有 ReadOnly drift；再執行計畫
   指定 validations，將結果標為本輪 evidence。
6. 將完成的 correction 送 independent implementation review，通過後送 independent
   code review。兩者 approved 後交 Main Agent commit、push、GraphQL/readback，最後只
    resolve `PRRT_kwDOSTt_386YpZ_Q`、`PRRT_kwDOSTt_386Ypaf_`、
    `PRRT_kwDOSTt_386Ypaf3`、`PRRT_kwDOSTt_386YpagN`、
    `PRRT_kwDOSTt_386YpagY`。

## Validation / Acceptance Checks

- focused facade tests、full non-E2E pytest、Ruff、Pyright、Tach、`git diff --check`
  全部是本輪 pending validation，須在 source/tests/docs rework 後重跑。
- tests 證明單一 shared close task、成功後才 closed、failure/cancellation 後可重試，
  與 caller cancellation isolation。
- shape inspection 證明 root exact seven-target 和 transport exact two-target list
  未變，且無其他 Tach drift。
- doc review 證明 HTTP/auth boundary 文本與實作/現有 Tach boundary 一致。

## Reviewer Handoff

```json
{
  "verdict": "needs-rework|approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [
      "PRRT_kwDOSTt_386YpZ_Q",
      "PRRT_kwDOSTt_386Ypaf_",
      "PRRT_kwDOSTt_386Ypaf3",
      "PRRT_kwDOSTt_386YpagN",
      "PRRT_kwDOSTt_386YpagY"
    ],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

Re-reviewer 必須確認本輪 evidence，而非引用 `ed29e837…` 的歷史 baseline；
`approved` 不可預填。thread resolution 只屬於 Main Agent，且必須在 correction
commit/push/readback 後。

## Post-merge / release actions

無。不得由 correction commit/push 推論 merge、VERSION bump、tag 或 release。

## Open Questions / Unresolved Items

無。lifecycle retry、shared task、frozen Tach lists、docs target 和 thread IDs 均已明確。
