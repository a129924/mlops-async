---
topic: mlops-async-client-facade
phase: plan-authoring
status: creator-in-progress
created: 2026-08-12
d1_verdict: non-trivial
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# MlopsAsyncClient 規格

## 目前修正狀態

PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d` 是唯一已發布
baseline。五條 action threads 目前使 lifecycle/docs correction 處於
`creator-in-progress`；本輪 validation、reviews、commit/push 和 thread resolution
皆 pending，不能引用 baseline 作為完成證據。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 acceptance handoff |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 acceptance handoff |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | 六份 topic artifacts 的 correction evidence |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | 六份 topic artifacts 的 workflow/evidence handoff |
| `PRRT_kwDOSTt_386YpagY` | transport doc | `docs/standards/http-client-auth-boundary.md` 的文件 handoff |

上述五條 threads 全部仍未 resolved；本表僅補正可追溯性，不改變 acceptance criteria 或 correction validation/review/publish 的 pending 狀態。

## Acceptance Criteria

1. Package root 的 `MlopsAsyncClient`、五個 required keyword-only password-grant
   parameters、五個 readonly identity-stable namespace properties 和 lazy auth
   contract 保持不變。
2. Facade 仍是 shared `HttpClient` 唯一 close owner；family clients 不能 close transport。
3. 第一個 `aclose()` 建立唯一 private shared close task，且 simultaneous/repeated
   callers 均 await 這一 task，底層 `HttpClient.aclose()` 不重複執行。
4. shared close task success 才設 permanent closed；successful repeated close 是
   idempotent no-op。
5. 若底層 close raise 或被取消，facade 不設 closed、清除已結束的 failed task，並讓
   後續 `aclose()` retry；error/cancellation 原樣傳播。
6. caller cancellation 不可取消 shared task，其他 caller 仍可取得 close result。
7. `docs/standards/http-client-auth-boundary.md` 記錄 criteria 2–6，並同步 root exact
   Tach order `clients`, `core`, `transport`, `cas_tables`, `job_execution`, `models`,
   `projects` 和 transport exact `core`, `exceptions` boundary。
8. `tach.toml` 的上述 frozen lists 和所有 other config content 不得因 correction 改動；
   shape inspection、`tach check` 必須確認。
9. source/tests/docs rework 後才可執行 full validation、independent implementation
   review、independent code review、correction commit/push；push readback 後才可 resolve
    `PRRT_kwDOSTt_386YpZ_Q`、`PRRT_kwDOSTt_386Ypaf_`、
    `PRRT_kwDOSTt_386Ypaf3`、`PRRT_kwDOSTt_386YpagN`、`PRRT_kwDOSTt_386YpagY`。
10. 本輪不做 VERSION bump、tag、release、merge 或未指定的 thread resolution。

## Frozen Tach shape

```toml
# existing [[modules]] path = "mlops_async"
depends_on = [
    "mlops_async.clients",
    "mlops_async.core",
    "mlops_async.transport",
    "mlops_async.clients.cas_tables",
    "mlops_async.clients.job_execution",
    "mlops_async.clients.models",
    "mlops_async.clients.projects",
]

# existing [[modules]] path = "mlops_async.transport"
depends_on = ["mlops_async.core", "mlops_async.exceptions"]
```

## Behavioral Scenarios

### 成功與 concurrent close

Given 已建構的 facade，當兩個 callers 在 owned `HttpClient.aclose()` 完成前呼叫
`aclose()`，then 兩者都 await 同一 shared task，且底層 close 只呼叫一次。當它成功後，
後續 `aclose()` 不會再建立新的底層 close。

### 失敗與 cancellation retry

Given 底層 close raise 或被取消，當第一個 `aclose()` await 結束時，then facade 並未
permanently closed，且不保留已結束而失敗的 in-progress task。當後續 caller 呼叫
`aclose()` 時，then 它建立 retry 並可以成功。

### Cancelled waiter isolation

Given 一個 shared close task 與兩個 callers，當其中一個 caller 在 await 時被取消，then
其 cancellation 只傳播給該 caller；shared close task 繼續，另一 caller 可以觀察到
success 或 failure。

### 文件與 Tach boundary

Given correction diff，當檢查文件與 config 時，then boundary document 說明 facade-owned
close 和 frozen root/transport dependency shape，而 `tach.toml` 本身沒有變更。

## Error / Edge Cases

- 不得在 successful underlying close 前標記 closed。
- 不得將已結束的 failed/cancelled task 留為 permanent in-progress marker。
- 不得將既有 auth、transport、response、domain closed-transport errors 或
  `asyncio.CancelledError` 替換為 facade-specific errors。
- root order、transport targets 或其他 Tach config 的任一 drift 都阻擋 correction
  publication。
- current status 是 `creator-in-progress`；原 plan-review approval 與 PR baseline 是
  historical facts，不是本輪 validation/review/publish completion。
