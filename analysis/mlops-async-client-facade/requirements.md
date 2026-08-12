---
topic: mlops-async-client-facade
status: approved
created: 2026-08-12
source_of_truth: locked human contract
---

# MlopsAsyncClient facade requirements

## Authoritative completion update (2026-08-13)

This update supersedes earlier provisional records that described full validation,
implementation review, or code review as pending. The locked scope and all
acceptance requirements remain unchanged. An isolated Linux-native ext4
validation rebuilt the current uncommitted topic snapshot from base
`e311e9e34c62979bb2ea5915e11c5d5fcbec07b2`: six tracked diffs and eight
topic-untracked files were hash-matched before validation. `uv sync --frozen`,
full non-E2E pytest (`694 passed, 9 skipped, 1 deselected`, 94.38% coverage),
Ruff, Pyright, Tach, and `git diff --check` passed. The disposable detached
checkout and bare cache were deleted after results were retained at
`/tmp/mlops-async-facade-validation-results-20260813-91d3b5e4.txt`
(`SHA-256 2b4d1be6dcf35fe78e44b5a6041a499c7ea2c8c452eab451368f57b35f8f0e83`).

Independent implementation review and independent code review are approved.
`publish` remains pending; no commit, push, pull request, merge, version bump,
tag, or release is implied by this evidence.

## Goal

新增 package-root `MlopsAsyncClient`，以 password-grant credentials 建立一個 shared async HTTP/auth runtime，提供既有 endpoint family 的 namespaced、identity-stable 存取與 idempotent async lifecycle。

## In-Scope

- keyword-only `MlopsAsyncClient(*, base_url, client_id, client_secret, username, password)`、package-root export 與 `.auth`、`.models`、`.projects`、`.cas_tables`、`.job_execution`。
- facade-owned `HttpClient`、`PasswordTokenEndpointClient`、concrete `InMemoryTokenStorage()`、`TokenManager`、`AuthProvider` 及一個 raw `Requester`；lazy token acquisition、idempotent lifecycle 與既有 error/cancellation propagation。
- 已存在且使用者授權保留的 facade implementation、root export、tests、README 與 architecture/boundary docs；其 scoped TDD/focused evidence 仍是 provisional/historical evidence。
- 僅修改 `tach.toml` 的既有 `mlops_async` 與 `mlops_async.transport` blocks 的 `depends_on` lists。
- 此次 six topic artifacts 的 material Tach rework 與 re-review routing。

## Out-Of-Scope

- `.users`、API-key/other grants、transport injection、retry/timeout/cancellation API、facade-specific exceptions、token-storage policy。
- 任一既有 endpoint 行為、RequestExecutor migration、CAS Tables constructor，或 `src/mlops_async/core/**`、`src/mlops_async/transport/**`、`src/mlops_async/clients/**` 的 production source。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`、tag、release、release notes、live Viya E2E。
- 除既有 `mlops_async` root seven-target list 與既有 `mlops_async.transport` exact two-target list 外的全部 `tach.toml` content、所有其他 Tach blocks、global flags、excludes 與 interfaces。

## ReadOnly

- `src/mlops_async/core/**`、`src/mlops_async/transport/**`、`src/mlops_async/clients/**`。
- `VERSION`、`pyproject.toml`、`uv.lock`、`.github/agents/**`。
- `tach.toml` 中除了既有 root seven-target list 與既有 transport exact two-target list 以外的所有內容。

## Written

- `src/mlops_async/mlops_async_client.py`
- `tests/unit/test_mlops_async_client.py`

## Modify

- `src/mlops_async/__init__.py`
- `tests/unit/clients/test_auth_client.py`
- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `tach.toml`：僅兩個既有 `depends_on` lists；此檔是 Modify，不是 Written。
- `analysis/mlops-async-client-facade/requirements.md`
- `analysis/mlops-async-client-facade/technical-spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.python.plan.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.spec.md`
- `plan/mlops-async-client-facade/mlops-async-client-facade.step.md`

## Deleted

- 無。

## Measurable Requirements

1. `from mlops_async import MlopsAsyncClient` 可用，constructor 只接受五個 required keyword-only strings。
2. Constructor、`__aenter__` 與 property access 不進行 I/O；首次 authenticated operation 才使用既有 lazy token flow。
3. Facade 是唯一 close owner；family clients 不取得 lifecycle ownership；`aclose()` 與 context exit idempotent。
4. 最終 `tach check` 無 cycle，且 config diff/shape inspection 驗證僅允許的 two-list delta。
5. 既有 scoped TDD/focused evidence 與 pending final full validation、independent implementation review、independent code review、publish 必須清楚區分。

## Tach correction acceptance

`tach.toml` 只可達成下列 shape：

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

Acceptance test 必須以 config diff/shape inspection 驗證 root 恰為上述 seven targets、transport 恰為上述 two targets，且沒有其他 Tach block、global flag、exclude 或 interface 差異；之後 `tach check` 必須無 cycle。

## Rework and Re-review Routing

### Implementation-review rework routing (2026-08-12)

Main workflow 與 restored Python companion 的 plan-review 先前均獲 `approved`，且 `plan-review` 維持完成的歷史事實；這不表示 implementation review 已通過。獨立 implementation reviewer 已作出 `needs-rework` verdict，workflow 現在依 canonical transition 位於 `needs-rework -> creator-in-progress`。

保留的 facade/root export/tests/docs、scoped TDD/focused evidence，以及 provisional Tach work 都是現況／歷史證據，不可誤標為本輪完成。Implementer 必須只在既有 scope 內完成下列 rework：root `mlops_async` list 依鎖定順序為 `clients`、`core`、`transport`、`cas_tables`、`job_execution`、`models`、`projects`；補齊既定 facade tests，驗證 close 後 properties 仍可讀且 identity 不變、close 後 domain requester I/O 原樣產生既有 closed-transport failure、以及首次 authenticated domain request 經 TokenManager/AuthProvider lazy 觸發 password token flow。完成後才可再次送 independent implementation review。

full non-E2E WSL command 因 linked-worktree `.git` Windows pointer policy guard 而 nonzero，故 full validation 仍是 pending 的 environment exception；不得以已完成 assertions 或 coverage 宣稱 full validation 完成。Tach correction（含 exact order）、independent implementation review、code review 與 publish 均 pending。
