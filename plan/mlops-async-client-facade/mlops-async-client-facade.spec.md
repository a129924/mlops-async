---
topic: mlops-async-client-facade
phase: plan-authoring
status: approved
created: 2026-08-12
d1_verdict: non-trivial
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# MlopsAsyncClient 規格

## 目前修正狀態

PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d` 是唯一已發布
baseline。五條先前 action threads 已在 correction commit `9b51f95` 解決；兩條新 action
threads 曾使 lifecycle/docs correction 處於 `creator-in-progress`。本輪 correction plan 已由獨立
Plan-Reviewer 批准，direct transport implementation review 亦已批准；isolated ext4 full-validation
是歷史 evidence，current full-validation、code review、commit/push/readback 和新 thread resolution
仍 pending，不能引用 baseline 作為完成證據。

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
cleanup retry，facade 不得接受 underlying no-op retry 作為成功）與
`PRRT_kwDOSTt_386YypkJ`（README/architecture facade 現況敘述為繁體中文）。

## 本輪 fresh evidence

focused facade/transport tests `80 passed`（`--no-cov`）；default assertions `80 passed`，
coverage `56.80%` 的唯一失敗為 fail-under；Ruff、Pyright、Tach、diff check 通過。full non-E2E
isolated ext4 correction snapshot 得到 `704 passed, 9 skipped, 1 deselected`、coverage `94.43%`；
base `9b51f95` 加十個 correction files 的 manifest SHA-256
`219b3593cb3213f035c728232d377eb2db55966b94ee967ba8532a3e755ce809` 相符。`uv sync --frozen`、Ruff
format/check、Pyright、Tach 與 diff check 全部通過，故 isolated ext4 full-validation 已完成；
它僅為歷史 evidence，current full-validation 仍 pending。

## Acceptance Criteria

### Current direct transport concurrency correction

此節 supersede 舊的 pending-thread 描述：`PRRT_kwDOSTt_386YypkF` 與
`PRRT_kwDOSTt_386YypkJ` 是 `ea5732e` 的 resolved history；僅
`PRRT_kwDOSTt_386Y0BD0` 為 current unresolved。

12. direct `HttpClient.aclose()` 第一個 caller 建立唯一 shared managed-cleanup attempt；所有在其
    結束前加入的 direct callers 必須 await 同一 attempt，且底層 managed close count 為 `1`。
13. shared attempt success 時所有 joiners 正常完成；shared attempt raise 時所有 joiners re-raise
    failure；shared attempt cancellation 時所有 joiners 收到 `asyncio.CancelledError`。waiter 自身
    cancellation 不得取消 shared attempt。
14. shared attempt failure/cancellation 後不得設定 closed，且必須清除 in-progress state；下一個
    序列 direct caller 必須啟動真正的第二次 managed cleanup，不能把 temporary `httpx` no-op 當成功。
15. success/failure/cancellation 以 deterministic event/barrier fakes 測試；failure/cancellation 的
    序列 retry 成功後 cumulative managed-close count 為 `2`。不得改變 facade ownership、public API、
    Tach 或 README/architecture。
16. current full-validation 與 independent code review 完成後，才可 `commit --no-verify`、push、
    GraphQL remote-head readback、只 resolve `PRRT_kwDOSTt_386Y0BD0`、再 GraphQL readback。

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
7. concrete `HttpClient.aclose()` 只有在 managed cleanup 真正成功後才可使 facade close
   成功；managed cleanup first failure/cancellation 後，retry 必須再次執行真實 cleanup，
   不能以 underlying no-op 回傳偽造成功。
8. `docs/standards/http-client-auth-boundary.md` 記錄 criteria 2–7，並同步 root exact
   Tach order `clients`, `core`, `transport`, `cas_tables`, `job_execution`, `models`,
   `projects` 和 transport exact `core`, `exceptions` boundary。
9. `tach.toml` 的上述 frozen lists 和所有 other config content 不得因 correction 改動；
   shape inspection、`tach check` 必須確認。
10. README 與 `docs/ARCHITECTURE.md` 的新增 facade 現況敘述必須為繁體中文；canonical
    headings、fixed labels、必要技術術語可保留原文。
11. source/tests/docs rework 的 isolated ext4 full-validation 是歷史 evidence；本輪 correction plan 與
    direct transport implementation review 已取得獨立 approval。current full-validation、independent
    code review、correction commit/push/readback 後，才可 resolve `PRRT_kwDOSTt_386Y0BD0`；先前
    threads 為 resolved history，不得再次 resolve 或重新分類。
12. 本輪不做 VERSION bump、tag、release、merge 或未指定的 thread resolution。

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

### Concrete cleanup retry

Given `HttpClient` 的 managed cleanup first attempt raise 或被取消，when later
`HttpClient.aclose()` 執行，then 它必須再次觸發真實 managed cleanup；不得因 underlying
client 已呈現 no-op 而讓 `MlopsAsyncClient` 將 cleanup 標為成功。

### 文件與 Tach boundary

Given correction diff，當檢查文件與 config 時，then boundary document 說明 facade-owned
close 和 frozen root/transport dependency shape，而 `tach.toml` 本身沒有變更。
README 與 `docs/ARCHITECTURE.md` 的新增 facade 現況敘述必須為繁體中文。

## Error / Edge Cases

- 不得在 successful underlying close 前標記 closed。
- 不得將已結束的 failed/cancelled task 留為 permanent in-progress marker。
- 不得將既有 auth、transport、response、domain closed-transport errors 或
  `asyncio.CancelledError` 替換為 facade-specific errors。
- root order、transport targets 或其他 Tach config 的任一 drift 都阻擋 correction
  publication。
- current status 是 `approved`；本輪 correction plan 與 direct transport implementation review
  已分別取得獨立 approval。isolated ext4 full-validation 是歷史 evidence，不是 current
  full-validation、code review 或 publish completion。
