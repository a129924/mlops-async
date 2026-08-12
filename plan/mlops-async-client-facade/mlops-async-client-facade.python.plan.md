---
topic: mlops-async-client-facade
phase: plan-authoring
status: approved
created: 2026-08-12
d1_verdict: non-trivial
branch: feat/andrew/mlops-async-client-facade
worktree: D:\code\python\mlops-async.worktrees\agent-20260812-mlops-async-client-facade
---

# MlopsAsyncClient Python implementation plan

## Authoritative completion update (2026-08-13)

The earlier rework record is retained as history but is no longer current.
Independent Python implementation review and independent Python code review
are approved. The authoritative final-validation route was an isolated
Linux-native ext4 detached checkout rebuilt from base
`e311e9e34c62979bb2ea5915e11c5d5fcbec07b2`, with six tracked diffs and eight
topic-untracked files hash-matched to the feature snapshot. `uv sync --frozen`,
full non-E2E pytest (`694 passed, 9 skipped, 1 deselected`, 94.38% coverage),
Ruff, Pyright, Tach, and `git diff --check` passed. Its retained transcript is
`/tmp/mlops-async-facade-validation-results-20260813-91d3b5e4.txt`
(SHA-256 `2b4d1be6dcf35fe78e44b5a6041a499c7ea2c8c452eab451368f57b35f8f0e83`);
the disposable checkout and bare cache were deleted.

Current status is `approved`; only `publish` remains pending. This plan update
does not perform or authorize a commit, push, pull request, merge, version
bump, tag, or release.

## Implementation-review rework record (2026-08-12)

The restored Python companion 的 independent plan approval 保持有效，`plan-review` 已完成；後續 implementation review 為 `needs-rework`，所以 companion workflow 現為 `needs-rework -> creator-in-progress`。不重開 Python plan review，除非發現 scope conflict。

> 本 companion plan 服從 `mlops-async-client-facade.plan.md` 的 strict analysis routing、scope、artifact ownership、workflow transition 與 stable-library metadata。rework 僅為鎖定的 Tach root order 與既定 facade tests；不改變任何 technical decision。

## Goal

保留既有 user-authorized provisional `MlopsAsyncClient` facade，僅以已授權的 exact Tach composition-root boundary 消除 cycle，並在 final validation 與獨立 review 後進入 publish gate。

## Non-goals

- 不新增 `.users`、API-key/other grants、transport injection、retry/timeout/cancellation API、facade-specific exception 或 token-storage policy。
- 不改變 existing family endpoint behavior、RequestExecutor migration、CAS Tables constructor，亦不改寫 `src/mlops_async/core/**`、`src/mlops_async/transport/**`、`src/mlops_async/clients/**`。
- 不修改 root seven-target / transport two-target lists 以外的 Tach block、target、global flag、exclude、interface 或 config content。
- 不執行 VERSION bump、tag、release、release notes 或 live Viya E2E。

## Current Context

`analysis/mlops-async-client-facade/requirements.md` 與 `technical-spec.md` 是 strict baseline。feature worktree 已有 facade、root export、tests、README 與 boundary docs，並有 scoped TDD/focused 及先前 full-validation evidence；它們是保留的 provisional/historical evidence，不是這次 Tach rework、new plan review 或後續 final gates 的完成證據。

Tach root facade composition 需直接依賴 family child boundaries；使用者已精確授權 root seven-target list，並要求 `mlops_async.transport` 維持僅依賴 `mlops_async.core` 與 `mlops_async.exceptions`。

## Requirements

1. `from mlops_async import MlopsAsyncClient` 保持可用；constructor 只接受五個 required keyword-only strings。
2. Facade 保持 shared `HttpClient`、password token endpoint、concrete `InMemoryTokenStorage()`、`TokenManager`、`AuthProvider` 與 raw `Requester`；五個 properties readonly、identity-stable。
3. Constructor、`__aenter__`、property access 不作 I/O；first authenticated operation 觸發既有 lazy token flow；Facade 是唯一 close owner，`aclose()`/context exit idempotent，errors/cancellation 原樣傳播。
4. `tach.toml` 的既有 root `mlops_async` list 恰為七 targets：`mlops_async.clients`、`mlops_async.core`、`mlops_async.transport`、`mlops_async.clients.cas_tables`、`mlops_async.clients.job_execution`、`mlops_async.clients.models`、`mlops_async.clients.projects`；既有 transport list 恰為 `mlops_async.core`、`mlops_async.exceptions`。
5. 精確 config diff/shape inspection、`tach check`、final full non-E2E pytest、Ruff、Pyright、`git diff --check`、independent implementation review、independent code review 都必須在這次 re-review approval 後完成。

## Decisions

- Async-planning status: triggered — facade 組合 shared async `HttpClient`，公開 `aclose()`/async context manager 並擁有 HTTP/auth runtime lifecycle；依 `analysis/mlops-async-client-facade/technical-spec.md` 的 Runtime Composition、Lifecycle and Error Contract、Async Baseline。
- Module/package placement: facade 位於 `src/mlops_async/mlops_async_client.py` 並由 `src/mlops_async/__init__.py` root re-export；Tach correction 僅在 `tach.toml` 的 two existing lists。
- New public API: 是；additive `MlopsAsyncClient`、five namespace properties、`aclose()`、async context manager，signature 依下方 Public Contract。
- Interface changes: 否；不改 family constructors、endpoint interfaces 或 core/transport/client source，僅 root export 為 additive public surface。
- Breaking changes allowed: 否；direct family imports/constructors 保持相容。
- New dependencies: 否；重用既有 HTTP/auth/client components。
- Error handling strategy: Facade 不包裝 blank/non-string credential、invalid URL、auth、transport、response 或 `asyncio.CancelledError` failures，沿用下層行為。
- Typing strategy: public constructor/properties/lifecycle methods 保持 strict typed；不新增 `Any`、Protocol 或 facade-specific exception。

### Async boundary decision

Facade 是 composition root；endpoint I/O 仍由 family clients 執行。async boundary 是 endpoint calls、`aclose()` 與 async context exit，不自行 delegate endpoint methods。

### Resource lifecycle decision

Facade 唯一擁有 shared `HttpClient`；`aclose()`/`__aexit__` 只關閉它。composed components/family clients 不增加 close path。constructor/context entry/property access 僅 validation/wiring。

### Concurrency model

不新增 background task、fan-out、queue、prefetch 或 facade-level parallel token flow；沿用 `TokenManager` 與 request/auth runtime 的既有行為。

### Failure model

OAuth、network、response parsing、closed-transport 和 cancellation failures 原樣傳播。close 後 properties 仍存在；後續 I/O 沿用下層 closed-transport error。

### Cancellation / timeout policy

Facade 不攔截 `asyncio.CancelledError`，不新增 timeout/retry API 或 policy；沿用 transport/request runtime。

### Validation plan

先完成精確 Tach config diff/shape acceptance：root exact seven targets、transport exact two targets、無其他 Tach drift，再執行 `tach check`。後續才執行 focused regression、full non-E2E pytest、Ruff、Pyright、`git diff --check`，並由獨立 implementation/code reviewers 審查。既有 provisional evidence 僅保留為歷史背景。

### Handoff notes for the implementer

在新 plan-review approval 前不得改 `tach.toml`。核准後，`tach.toml` 是唯一為 Tach correction 而變動的 production/config path，且只能改兩個既有 lists；root seven-target target names、transport exact two-target list 均不可自行替換、排序以外的擴張或縮減。不得觸及任何 other Tach block、flag、exclude、interface 或 production source。

## Public Contract / API Changes

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

Properties 無 setter，回傳 constructor 建立的同一 instance。此為 additive public contract；existing direct family imports/constructors 不變。

## Affected Files / Modules

Likely affected files:

- `tach.toml`：僅既有 root `mlops_async` 與 `mlops_async.transport` `depends_on` lists，且僅在 re-review approval 後。
- `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md`：本 companion rework artifact。

Retained provisional implementation evidence:

- `src/mlops_async/mlops_async_client.py`
- `src/mlops_async/__init__.py`
- `tests/unit/test_mlops_async_client.py`
- `tests/unit/clients/test_auth_client.py`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`

Read-only modules:

- `src/mlops_async/core/**`
- `src/mlops_async/transport/**`
- `src/mlops_async/clients/**`
- `VERSION`
- `pyproject.toml`
- `uv.lock`
- `.github/agents/**`
- `tach.toml` 除 two accepted lists 外的全部內容。

## Implementation Steps

1. 保留已完成的 independent Python plan-review approval；不重新送 plan review，除非發現 scope conflict。
2. Modify only `tach.toml` existing `mlops_async` `depends_on` to `["mlops_async.clients", "mlops_async.core", "mlops_async.transport", "mlops_async.clients.cas_tables", "mlops_async.clients.job_execution", "mlops_async.clients.models", "mlops_async.clients.projects"]`, and leave existing `mlops_async.transport` `depends_on` exactly `["mlops_async.core", "mlops_async.exceptions"]`; change nothing else for this correction.
3. In `tests/unit/test_mlops_async_client.py`, add the already-planned tests for post-close readable identity-stable properties, downstream existing closed-transport propagation, and first authenticated domain request lazy password-token flow through TokenManager/AuthProvider.
4. Inspect the `tach.toml` diff/shape to assert the exact two lists and no other Tach drift; run `tach check` and required WSL validations, recording the linked-worktree `.git` pointer guard as a pending full-validation environment exception.
5. Submit completed work to independent Python implementation review, then Python code review; both must verify retained provisional work did not expand scope.
5. After all gates, hand off to Main Agent for `publish-in-progress`, topic commit, push, draft PR and human review; do not perform release work.

## Test Plan

- Happy path: `tests/unit/test_mlops_async_client.py` covers root import, five namespaces, shared requester/storage wiring and `async with`; final full suite guards existing families.
- Invalid input: existing facade tests cover required credential string validation and invalid URL behavior without changing exception contracts.
- Edge case: repeated `aclose()`/context exit, readonly identity, property availability after close, and downstream closed-transport I/O behavior.
- Regression: existing facade/AuthClient tests preserve family non-ownership and CAS Tables concrete raw `Requester` compatibility.
- Backward compatibility: existing direct family imports/constructors and endpoint behavior remain unchanged; full non-E2E suite enforces regression coverage.
- Tach acceptance: config diff/shape inspection asserts root exactly seven named targets, transport exactly two named targets, no other Tach diff; `tach check` must pass without cycle.

## Validation Commands

透過 WSL 且在 feature worktree 使用 frozen environment；不可使用 Windows project-local `.venv`：

```powershell
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync pytest --no-cov tests/unit/test_mlops_async_client.py tests/unit/clients/test_auth_client.py'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync pytest --no-cov -m "not viya_e2e"'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync ruff check --no-fix .'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync pyright'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && uv run --frozen --no-sync tach check'
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/d/code/python/mlops-async.worktrees/agent-20260812-mlops-async-client-facade && git diff --check'
```

在執行 `tach check` 前，先以 `git diff -- tach.toml` 或等效 shape inspection 驗證 exact two-list delta；不以之前的 full-validation 結果替代此次 evidence。

## Risks

- Root facade 必須直接依賴四個 family child boundaries；遺漏/多出/錯名 target 會使 Tach fail 或違反 user authorization。
- 對已存在 provisional work 的任何不相關變更會造成 scope drift，且可把歷史 validation 誤當成新的 final gate。
- Password-grant values 不可出現在 README 實例、測試輸出或 logs。

## Rollback Plan

若 Tach correction 或 final validation 失敗，僅 revert `tach.toml` 的 two accepted list edits，保留 user-authorized provisional facade/root export/tests/docs 和 six artifacts；workflow 回到 `needs-rework -> creator-in-progress`，不得以修改 ReadOnly 路徑迴避 boundary。此 topic 的所有 permitted files 都可透過 Git path-limited revert 回復。

## Open Questions

無。使用者已明確指定 root seven targets、transport exact list、Tach config boundary與後續 review route。
