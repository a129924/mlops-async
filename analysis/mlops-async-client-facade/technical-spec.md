---
topic: mlops-async-client-facade
status: creator-in-progress
created: 2026-08-12
requirements_source: analysis/mlops-async-client-facade/requirements.md
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# MlopsAsyncClient facade 技術規格

## Current correction state

PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d` 是已發布 baseline。
五條先前 action threads 已在 correction commit `9b51f95` 解決，僅為 historical record；
兩條新 action threads 使 lifecycle/docs rework 目前為 `creator-in-progress`。本規格不將
baseline validation、review 或 publication 作為本輪修正的完成證據。isolated ext4 snapshot 的
full-validation 已完成；independent reviews、commit/push/readback 與新 thread resolution 仍 pending。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagY` | transport doc | resolved history at `9b51f95`; no future resolve |

上述五條 thread 為已解決歷史，沒有 future resolve。本輪只為
`PRRT_kwDOSTt_386YypkF` 與 `PRRT_kwDOSTt_386YypkJ` 進入 pending correction：前者要求
concrete `HttpClient.aclose()` failure/cancellation 後可執行真實 cleanup retry，並防止
facade 將 underlying no-op retry 誤判成功；後者要求 README/architecture facade 現況敘述為
繁體中文。

## 本輪 fresh evidence

focused facade/transport tests `80 passed`（`--no-cov`）；default assertions `80 passed`，
coverage `56.80%` 且唯一失敗為 coverage fail-under。Ruff、Pyright、Tach、diff check 均通過。
isolated ext4 correction snapshot 的 full non-E2E 為 `704 passed, 9 skipped, 1 deselected`、
coverage `94.43%`；以 base `9b51f95` 加十個 correction files 的 manifest SHA-256
`219b3593cb3213f035c728232d377eb2db55966b94ee967ba8532a3e755ce809` 驗證相符。`uv sync --frozen`、
Ruff format/check、Pyright、Tach 與 diff check 皆通過；transcript SHA-256 為
`49487b86e22b2f31a189d9f8215d2c63e051acde6b7ec43603fc25e170c9a972`，temporary path 已刪除。

## 目標

`src/mlops_async/mlops_async_client.py` 維持 additive composition root，組合既有
HTTP/auth/client components，不改變 endpoint behavior 或 runtime policy，並以可重試的
single-flight close lifecycle 管理其唯一擁有的 HTTP transport。

## Public Contract

```python
class MlopsAsyncClient:
    def __init__(
        self,
        *,
        base_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
    ) -> None: ...

    @property
    def auth(self) -> AuthClient: ...
    @property
    def models(self) -> ModelsClient: ...
    @property
    def projects(self) -> ProjectsClient: ...
    @property
    def cas_tables(self) -> CasTablesClient: ...
    @property
    def job_execution(self) -> JobExecutionClient: ...

    async def aclose(self) -> None: ...
    async def __aenter__(self) -> MlopsAsyncClient: ...
    async def __aexit__(self, exc_type, exc, traceback) -> None: ...
```

Properties 沒有 setter，且回傳 constructor 建立的同一 instance；本輪不新增 public
method、argument 或 exception。

## Runtime Composition

1. 建立 `HttpClient(base_url)`。
2. 以 password-grant values 建立 `PasswordTokenEndpointClient`。
3. 建立 concrete `InMemoryTokenStorage()`、`TokenManager(storage, fetcher)` 與
   `AuthProvider(token_manager)`。
4. 建立 `Requester(http_client, auth_provider=auth_provider)`。
5. 將同一 raw requester 注入 Models、Projects、CAS Tables、Job Execution；
   `AuthClient` 使用 token-endpoint collaborator。

## Lifecycle and Error Contract

- Facade 是 `HttpClient` 唯一 close owner；composed components 與 family clients
  不新增 close path。
- Constructor、context entry、property access 只做 validation/wiring；首個
  authenticated request 才 lazy token acquisition。
- `aclose()` 使用 private shared `asyncio.Task[None]`（或語意等同的 private
  in-progress state）代表唯一進行中的底層 `HttpClient.aclose()`。同時或重複 callers
  必須 await 同一 task，不能啟動第二次 close。
- callers await shared task 時必須 shield 它；一個 caller 的 cancellation 不得取消
  shared close。若底層 task raise 或被取消，清除已結束的 in-progress state 並保持
  facade 可再次 close；只有 task 成功後才設定 permanent closed state。成功後的
  repeated `aclose()` 是 no-op/idempotent。
- `__aexit__` 使用同一 lifecycle，且不 suppress context exception。validation/auth/
  transport/response failures 與 `asyncio.CancelledError` 原樣傳播，沒有 facade wrapper。
- `HttpClient` 的 concrete close state 也必須以 managed `httpx.AsyncClient.aclose()` 的
  真實成功為準。若 managed cleanup raise 或被取消，下一次 concrete close 必須再次嘗試
  managed cleanup；它不能把 underlying client 已變成 no-op 的回傳當作 cleanup 成功，否則
  facade 不得被標記 permanently closed。
- 此 retry 僅為 cleanup lifecycle 的再次嘗試；不得新增 dependency、network request retry
  behavior、timeout、background task 或 public API。

## Tach Composition-root Boundary

以下是 PR baseline 的 frozen shape；本輪只檢查、不得改它：

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

Root seven-target composition allowance 與 transport exact two-target list 避免
`mlops_async -> mlops_async.transport -> mlops_async` cycle。不得修改其他 Tach block、
target、global flag、exclude 或 interface。

## File Contract

### Written

- 無。

### Modify

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/transport/test_http_client.py`
- `docs/standards/http-client-auth-boundary.md`
- `README.md`
- `docs/ARCHITECTURE.md`
- six topic artifacts

### ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/clients/**`。
- `src/mlops_async/__init__.py`、`tests/unit/clients/test_auth_client.py`、`VERSION`、
  `pyproject.toml`、`uv.lock`、`.github/agents/**`。
- 全部 `tach.toml` content，包括 root exact seven-target list 與 transport exact
  two-target list，以及所有其他 Tach blocks、global flags、excludes 與 interfaces。

### Deleted

- 無。

## Test and Documentation Mapping

- `tests/unit/test_mlops_async_client.py` 要覆蓋 existing constructor/identity/lazy-auth
  behavior，並新增 single-flight close、successful-close idempotence、close failure retry、
  underlying-close cancellation retry 與 cancelled waiter isolation。
- `tests/unit/transport/test_http_client.py` 要以可觀察的 managed cleanup fake/mocking
  覆蓋 first close raise、first close cancellation、後續 real retry，並驗證 no-op 回傳不能
  偽造成功的 concrete close state。
- docs update 必須同步 lifecycle semantics 和 frozen Tach composition boundary；只更新
  `docs/standards/http-client-auth-boundary.md`、`README.md` 與 `docs/ARCHITECTURE.md`；
  後兩者新增 facade 現況敘述必須為繁體中文，不得藉此修改 HTTP/auth implementation。
- shape inspection 和 `tach check` 確認 frozen lists 無 drift。

## Async Baseline

- Async boundary 是 endpoint calls、shared close task、`aclose()` 與 async context
  exit；不引入 queue、fan-out、prefetch、retry 或 facade-level timeout policy。
- single-flight close 是 lifecycle coordination，不是 background service；其 task 僅存活到
  close 完成、失敗或取消，且其 error/cancellation 依上述規則傳播。

## Rework Routing

main workflow 與 Python companion plan-review 的 `approved` 是已完成的歷史 gate。
PR action threads 不重開 plan-review；本次 lifecycle/docs correction 現在是
`needs-rework -> creator-in-progress`。Implementer 完成後依序送 independent
implementation review、code review、correction commit/push；Main Agent 只可在 push
readback 後 resolve `PRRT_kwDOSTt_386YypkF` 與 `PRRT_kwDOSTt_386YypkJ`。先前 thread
維持既有狀態。VERSION、tag、release、merge 均不在此 routing 中。
