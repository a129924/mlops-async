---
topic: mlops-async-client-facade
status: approved
created: 2026-08-12
requirements_source: analysis/mlops-async-client-facade/requirements.md
---

# MlopsAsyncClient facade technical specification

## Authoritative validation and review completion (2026-08-13)

This section supersedes earlier provisional records that left final validation
or the two independent reviews pending. The current uncommitted snapshot was
reconstructed in an isolated Linux-native ext4 detached checkout from base
`e311e9e34c62979bb2ea5915e11c5d5fcbec07b2`; its six tracked diffs and eight
topic-untracked files were hash-matched. `uv sync --frozen` passed, followed
by full non-E2E pytest (`694 passed, 9 skipped, 1 deselected`; 94.38% coverage),
Ruff, Pyright, Tach, and `git diff --check`, all passing. The evidence
transcript is retained at
`/tmp/mlops-async-facade-validation-results-20260813-91d3b5e4.txt`
with SHA-256 `2b4d1be6dcf35fe78e44b5a6041a499c7ea2c8c452eab451368f57b35f8f0e83`.
The temporary checkout and bare cache have been deleted.

Independent implementation review and code review are approved. The only
remaining workflow stage is `publish`; this completion does not authorize or
perform any Git publication action.

## Goal

`src/mlops_async/mlops_async_client.py` 是 additive composition root，組合既有 HTTP/auth/client components，而不改變 endpoint behavior 或 runtime policy。

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

Properties 沒有 setter，且回傳 constructor 建立的同一 instance。

## Runtime Composition

1. 建立 `HttpClient(base_url)`。
2. 以 password-grant values 建立 `PasswordTokenEndpointClient`。
3. 建立 concrete `InMemoryTokenStorage()`、`TokenManager(storage, fetcher)` 與 `AuthProvider(token_manager)`。
4. 建立 `Requester(http_client, auth_provider=auth_provider)`。
5. 將同一 raw requester 注入 Models、Projects、CAS Tables、Job Execution；AuthClient 使用 token-endpoint collaborator。

## Lifecycle and Error Contract

- Facade 是 `HttpClient` 唯一 close owner；composed components 與 family clients 不新增 close path。
- Constructor、context entry、property access 只做 validation/wiring；首次 authenticated request 才 lazy token acquisition。
- `aclose()` 與 `__aexit__` idempotent，不 suppress context exception。
- validation/auth/transport/response failures 與 `asyncio.CancelledError` 原樣傳播。

## Tach Composition-root Boundary

只允許下列兩個既有 blocks 的 `depends_on` lists 變更；`tach.toml` 是 Modify，不是 Written：

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

Root seven-target composition allowance 與 transport exact two-target list 必須同時存在，以避免 `mlops_async -> mlops_async.transport -> mlops_async` cycle。不得修改其他 Tach block、target、global flag、exclude 或 interface。

## File Contract

### Written

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`

### Modify

- `src/mlops_async/__init__.py`
- `tests/unit/clients/test_auth_client.py`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `tach.toml` 的既有 root seven-target list 與 transport exact two-target list
- six topic artifacts

### ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/transport/**`、`src/mlops_async/clients/**`
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`
- 除上述兩個既有 lists 外的 `tach.toml` content，以及所有其他 Tach blocks、global flags、excludes 與 interfaces

### Deleted

- 無。

## Test and Documentation Mapping

- Facade tests 覆蓋 constructor、shared requester/storage、readonly identities、lazy auth、error propagation、idempotent lifecycle。
- `tests/unit/clients/test_auth_client.py` 保留 AuthClient behavior assertions；不新增 family lifecycle ownership。
- README 與 architecture docs 說明 one facade-owned transport、one requester、one concrete storage、lazy password grant。
- Tach acceptance test 以 config diff/shape inspection 驗證 root exact seven targets、transport exact two targets、沒有其他 config drift，並執行 `tach check`。

## Async Baseline

- Async boundary 是 endpoint calls、`aclose()` 與 async context exit；不引入 background tasks、fan-out、queue、facade-level retry、timeout 或 cancellation policy。
- Facade 不重新定義 `TokenManager` refresh coordination，沿用既有 request/auth concurrency behavior。

## Re-review Routing

### Implementation-review rework routing (2026-08-12)

Independent main-workflow 和 Python-companion plan reviews 的 `approved` verdict 仍是歷史有效證據，`plan-review` 已完成；其後的獨立 implementation review 則為 `needs-rework`。本 spec 現處於 `needs-rework -> creator-in-progress`，不是 `review-ready`，且不需要新的 plan review，除非發現 scope conflict。

rework 不改變本 spec 的 public contract、scope、exact target lists 或順序：Implementer 必須使 root list 的順序精確為 `mlops_async.clients`、`mlops_async.core`、`mlops_async.transport`、`mlops_async.clients.cas_tables`、`mlops_async.clients.job_execution`、`mlops_async.clients.models`、`mlops_async.clients.projects`，並補足既定 tests：close 後 properties 可讀且 identity 不變、close 後 domain requester call 原樣產生既有 closed-transport failure、第一個 authenticated domain request 經 TokenManager/AuthProvider lazy 取得 password token。

provisional facade/Tach work 仍存在，但 Tach correction（含 exact order）未完成。full non-E2E WSL validation 因 linked-worktree `.git` Windows pointer policy guard 而 nonzero，故 full validation 保持 pending/environment exception；implementation review 需重做，code review 和 publish 也保持 pending。
