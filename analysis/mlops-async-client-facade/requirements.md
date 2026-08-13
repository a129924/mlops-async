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

五條 actionable PR review threads 已使本 topic 依
`needs-rework -> creator-in-progress` 進入修正。現在只能宣稱規劃工作進行中：
本輪 source/tests/docs 修正與 focused/static evidence 已完成；完整 non-E2E validation
仍因 WSL environment exception pending，implementation review、code review、correction
commit/push 與 thread resolution 也仍 pending。不得把原始 PR baseline 或任何歷史
assertion 當成本輪完成 gate。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 lifecycle handoff |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 lifecycle handoff |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | 六份 topic artifacts 的 correction evidence |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | 六份 topic artifacts 的 workflow/evidence handoff |
| `PRRT_kwDOSTt_386YpagY` | transport doc | `docs/standards/http-client-auth-boundary.md` 的文件 handoff |

上述五條 threads 全部仍未 resolved；本表僅補正可追溯性，不改變技術契約、範圍或任何 pending gate。

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
  `docs/standards/http-client-auth-boundary.md` 及六份 topic artifacts；實作前
  先依本契約補齊 lifecycle tests。
- 保留已提交的 Tach shape：root exact seven-target list 與 transport exact
  two-target list；本輪不得再修改 `tach.toml`。

## 範圍外

- `.users`、API-key/other grants、transport injection、retry/timeout/cancellation
  API、facade-specific exceptions、token-storage policy。
- 任一既有 endpoint 行為、RequestExecutor migration、CAS Tables constructor，或
  `src/mlops_async/core/**`、`src/mlops_async/transport/**`、
  `src/mlops_async/clients/**` 的 production source。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`、tag、release、
  release notes、live Viya E2E。
- 所有其他 `tach.toml` content、Tach blocks、global flags、excludes 與 interfaces。

## ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/transport/**`、
  `src/mlops_async/clients/**`。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`。
- 全部 `tach.toml` content；尤其 root seven-target list 與 transport exact
  two-target list 均不可變更。

## Written

- 無。本輪只有 Modify，且不得新增 public API。

## Modify

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`
- `docs/standards/http-client-auth-boundary.md`
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
7. `docs/standards/http-client-auth-boundary.md` 必須在實作同一 commit 中同步說明：
   facade 是 shared `HttpClient` 唯一 owner、close 成功才 closed、失敗/cancellation
   可重試，以及 root composition boundary 使用下列 frozen Tach shape。
8. 本輪依序需通過 scoped/full validation、independent implementation review、
   independent code review、correction commit/push，才可由 Main Agent 在 readback 後
   resolve 三條明列 threads。

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
