---
topic: mlops-async-client-facade
status: creator-in-progress
created: 2026-08-12
source_of_truth: locked human contract
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# MlopsAsyncClient facade 需求

## PR #70 修正狀態（2026-08-13）

已發布的唯一基線是 PR #70 head
`ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d`。此 baseline 已含先前已授權的
facade、Tach lists、tests 與文件；它不是本輪修正已完成的證據。

先前五條 actionable PR review threads 已在 correction commit `9b51f95` 解決，僅保留為
歷史紀錄，不得重新列為 current pending 或 future resolve。兩條新 action threads 使本 topic
依 `needs-rework -> creator-in-progress` 進入本輪修正。transport retry implementation/tests 與
README/architecture 繁中敘述已 materially 完成。isolated ext4 correction snapshot validation 已完成：以
base `9b51f95` 加上精確十個 correction files 重建，manifest SHA-256
`219b3593cb3213f035c728232d377eb2db55966b94ee967ba8532a3e755ce809` 相符；`uv sync --frozen`、
full non-E2E、Ruff format/check、Pyright、Tach 與 diff check 均通過。full-validation 已完成；
independent reviews、correction commit/push/readback 與新 thread resolution 仍 pending。不得把原始
baseline 或任何歷史 assertion 當成本輪完成 gate。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagY` | transport doc | resolved history at `9b51f95`; no future resolve |

上述五條 thread 是已解決歷史，並非本輪待處理項目。本輪 pending correction 僅為
`PRRT_kwDOSTt_386YypkF`：concrete `HttpClient.aclose()` 在 failure/cancellation 後必須
保留真實 cleanup retry，facade 不得把 underlying no-op 的第二次 close 視為成功；以及
`PRRT_kwDOSTt_386YypkJ`：README 與 architecture 的 facade 現況敘述必須使用繁體中文。

## 本輪 fresh evidence

- focused facade/transport tests：`80 passed`（`--no-cov`）。
- default assertions：`80 passed`；coverage `56.80%`，唯一失敗為 repository-wide
  coverage fail-under。
- Ruff、Pyright、Tach 與 diff check：通過。
- full non-E2E：`704 passed, 9 skipped, 1 deselected`、coverage `94.43%`；isolated ext4
  snapshot 的完整 command 已通過。transcript 為
  `/tmp/mlops-async-pr70-correction-validation-20260813-001.validation.transcript.log`，SHA-256
  `49487b86e22b2f31a189d9f8215d2c63e051acde6b7ec43603fc25e170c9a972`；temporary path 已刪除。

## 目標

維持 additive package-root `MlopsAsyncClient`：它以 password-grant credentials
建立 shared async HTTP/auth runtime，提供既有 endpoint family 的 namespaced、
identity-stable 存取及正確的 async lifecycle。

## 範圍內

- keyword-only `MlopsAsyncClient(*, base_url, client_id, client_secret, username,
  password)`、package-root export 與 `.auth`、`.models`、`.projects`、
  `.cas_tables`、`.job_execution` 的既有 public contract。
- facade-owned `HttpClient`、`PasswordTokenEndpointClient`、concrete
  `InMemoryTokenStorage()`、`TokenManager`、`AuthProvider` 及一個 raw
  `Requester`；lazy token acquisition 與既有 error/cancellation propagation。
- PR 修正只可變動 `src/mlops_async/mlops_async_client.py`、
  `tests/unit/test_mlops_async_client.py`、
  `src/mlops_async/transport/http_client.py`、`tests/unit/transport/test_http_client.py`、
  `docs/standards/http-client-auth-boundary.md`、`README.md`、`docs/ARCHITECTURE.md`
  及六份 topic artifacts；實作前先依本契約補齊 facade 與 concrete transport lifecycle tests。
- 保留已提交的 Tach shape：root exact seven-target list 與 transport exact
  two-target list；本輪不得再修改 `tach.toml`。

## 範圍外

- `.users`、API-key/other grants、transport injection、retry/timeout/cancellation
  API、facade-specific exceptions、token-storage policy。
- 任一既有 endpoint 行為、RequestExecutor migration、CAS Tables constructor，或
  `src/mlops_async/core/**`、`src/mlops_async/clients/**` 的 production source。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`、tag、release、
  release notes、live Viya E2E。
- 所有其他 `tach.toml` content、Tach blocks、global flags、excludes 與 interfaces。

## ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/clients/**`。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`。
- 全部 `tach.toml` content；尤其 root seven-target list 與 transport exact
  two-target list 均不可變更。

## Written

- 無。本輪只有 Modify，且不得新增 public API。

## Modify

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/transport/test_http_client.py`
- `docs/standards/http-client-auth-boundary.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- `analysis/mlops-async-client-facade/requirements.md`
- `analysis/mlops-async-client-facade/technical-spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.step.md`

## Deleted

- 無。

## 可驗證需求

1. `from mlops_async import MlopsAsyncClient`、五個 required keyword-only strings
   與 readonly identity-stable namespace properties 的既有 public contract 不變。
2. Constructor、`__aenter__`、property access 不做 I/O；首個 authenticated domain
   request 才經既有 `TokenManager`/`AuthProvider` password-token flow lazy 取得 token。
3. Facade 仍是 `HttpClient` 唯一 close owner；family clients 不取得 lifecycle ownership。
4. `aclose()` 以 private in-progress shared task 協調 close：同時或重複呼叫只能
   使用同一 close operation；只有底層 close 成功後才永久標為 closed。
5. 底層 close raise 或 cancellation 時，facade 不得永久 closed，必須清除已結束的
   in-progress state，讓後續 `aclose()` 可重試；取消單一 waiter 不得取消 shared close
   operation。既有 domain/auth/transport failures 與 `asyncio.CancelledError` 不包裝。
6. tests 必須覆蓋成功後 idempotence、concurrent/repeated close 單一底層 call、
   close failure retry、underlying-close cancellation retry，以及 cancelled waiter 不使
   其他 waiter 的 shared close 失敗。
7. `HttpClient.aclose()` 必須只在 managed cleanup 真正成功時完成 concrete close state；
   first cleanup failure/cancellation 後，下一次呼叫必須真的再次呼叫 managed cleanup，而不以
   underlying no-op 回傳宣稱成功。`tests/unit/transport/test_http_client.py` 必須覆蓋 raise
   與 cancellation 的 retry。
8. `docs/standards/http-client-auth-boundary.md` 必須在實作同一 commit 中同步說明：
   facade 是 shared `HttpClient` 唯一 owner、close 成功才 closed、失敗/cancellation
   可重試，以及 root composition boundary 使用下列 frozen Tach shape。
9. `README.md` 與 `docs/ARCHITECTURE.md` 的新增 facade 現況敘述必須是繁體中文；
   canonical headings、fixed labels 與必要技術術語可保留原文。
10. 本輪依序需通過 scoped/full validation、independent implementation review、
   independent code review、correction commit/push，才可由 Main Agent 在 readback 後
   resolve `PRRT_kwDOSTt_386YypkF` 與 `PRRT_kwDOSTt_386YypkJ`；先前 thread 不因本輪
   correction 重新分類或 resolve。

## Frozen Tach shape

`tach.toml` 在 PR baseline 已具有、且本輪必須保留的 shape：

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

shape inspection 必須確認此 root exact seven targets 與 transport exact two targets
未被本輪修正改動；不得有其他 Tach drift。

## 工作流與歷史證據

原本 main workflow 和 Python companion 的 plan-review `approved` 是歷史事實，
但不等於本輪 implementation review 已通過。`ed29e837…` 是已推送並已開 PR 的
歷史 baseline；它與 pending correction evidence 不得同時被標為 current completion。
目前唯一 current status 是 `creator-in-progress`。修正完成後，必須重新取得
independent implementation review，再取得 code review；publish 指的是本輪 correction
commit/push，不是 version/tag/release，也不授權 merge。
