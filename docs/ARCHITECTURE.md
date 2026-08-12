# Architecture

## Purpose

`mlops-async` is intended to become an async Python client library for selected
SAS Viya REST API endpoints, built on `httpx.AsyncClient` and Pydantic v2.

## Design principles

- Async-first I/O only
- Strict typing by default
- Import-safe modules with no side effects
- Clear separation between public API, endpoint transport, and data models

## Planned package shape

- `src/mlops_async/` as the public package root
- `tests/unit/` as isolated tests
- `tests/integration/` as live-environment tests

The blueprint currently names these future-facing public modules:

- `client.py`
- `models.py`
- `endpoints.py`

They are design targets, not implemented files yet.

## Client architecture and auth boundary

### Package-root facade (current)

`MlopsAsyncClient` is the current package-root facade. It owns exactly one
`HttpClient`, `PasswordTokenEndpointClient`, `InMemoryTokenStorage`,
`TokenManager`, `AuthProvider`, and raw `Requester`. The facade creates stable
`.auth`, `.models`, `.projects`, `.cas_tables`, and `.job_execution` clients;
all domain clients share the same raw requester, while `.auth` shares the
password-token collaborator. Constructor and context entry only compose
objects. Token acquisition remains lazy until an authenticated operation, and
`aclose()` / context exit close only the facade-owned HTTP client once.

The facade adds no retry, timeout, cancellation, transport injection, or
token-storage policy.

對 auth/request boundary topic，先讀
[`docs/standards/http-client-auth-boundary.md`](standards/http-client-auth-boundary.md)。
本節只保留 architecture overview；詳細 dependency diagram、component
responsibility、collision policy、lazy auth lifecycle 與 conflict-stop rule
以該文件為準。

### Public surface baseline

`MlopsAsyncClient` 是已實作且從 package root 匯出的 public facade。其穩定 namespace
contract 為 `.auth`、`.models`、`.projects`、`.cas_tables` 與 `.job_execution`；各 domain
namespace 共用 raw `Requester`，`.auth` 則共用 password-token collaborator。這些 namespace
不是額外的 package-root export。

`EndpointFamilyClient` 僅是架構分類，並非 base class、Protocol 或模組。`AuthClient` 接收
`TokenEndpointClientProtocol`，且 `get_access_token()` 只直接 await 一次
`fetch_access_token()`；它不負責 refresh、grant selection、cache、exception translation、
context、close 或 transport lifecycle。

### Public-to-internal dependency direction

對外的 family 入口是平行存在，但 runtime 依賴方向固定如下：

`Models/Projects/CAS Tables/Job Execution -> Requester -> HttpClient`

authenticated request 的內部 auth chain 固定如下：

`Requester -> AuthProvider -> TokenManager -> {TokenStorage, TokenEndpointClient -> HttpClient}`

顯式 auth 操作則走：

`AuthClient -> TokenEndpointClient -> HttpClient`

### Fixed boundary rules

- OtherFamilyEndpoint 不直接依賴 `AuthClient`。
- `ProjectsClient`、`ModelsClient`、`CasTablesClient`、`JobExecutionClient` 只持有 `Requester`。
- `Requester` 不自行處理 token acquisition、refresh、或 auth config 細節。
- `core/headers.py` 集中管理 JSON-domain request family 與 token-endpoint request family 的 shared request-header policy，避免多個 collaborator 重複複製預設 header 規則。
- `AuthProvider` 只把 token 轉成 `Authorization` headers。
- `TokenManager` 只負責 token lifecycle decision。
- `TokenEndpointClient` 才是真正掌握 `/SASLogon/oauth/token` contract 的 internal collaborator。

### Facade lifecycle

`MlopsAsyncClient.__init__` 是同步 constructor，因此只做 wiring，不預先取得真實 token。
它建立 auth-configured `Requester`，不是 token-resolved `Requester`。

authenticated token resolve 應在第一次需要 auth 的 request 時 lazy 發生：

1. `__init__`：建立 `HttpClient`、`TokenEndpointClient`、`TokenManager`、
   `AuthProvider`、`Requester` 與各 family clients。
2. `__aenter__`：進入 client lifecycle。
3. first authenticated request：若 `TokenStorage` 無有效 token，由
   `TokenManager` 透過 `TokenEndpointClient` lazy fetch / refresh。
4. `__aexit__` / `aclose`：只負責 transport/resource cleanup。

### Internal module placement

internal client contract 仍維持拆分：

- `src/mlops_async/core/`
  - protocol
  - value objects
  - request composition
  - auth lifecycle coordination
- `src/mlops_async/transport/`
  - concrete HTTP transport implementation

責任仍應保持 narrow：

- `core/client.py`：internal-only `Client` protocol
- `core/requester.py`：internal-only `Requester`
- `core/headers.py`：提供 JSON-domain requests 與 token-endpoint requests 共用的 request-header policy helpers
- `core/auth.py`：auth lifecycle 與 header adapter boundary
- `core/token_storage.py`：token state storage boundary
- `transport/http_client.py`：concrete transport-only `HttpClient`，可重用 shared JSON request-header helper，但不擁有 auth policy

後續調整 `MlopsAsyncClient` 或 token endpoint collaborator 時，必須維持上述 dependency
direction，而不是把 internal runtime auth chain 反向收斂成
`TokenManager -> AuthClient`。

## Skill map

This repository includes 35 project skills. They guide implementation rather
than replace normal source files.

### Async and API design

- `python-async-await`
- `python-api-signature`
- `python-error-handling`
- `python-serialization-boundaries`
- `python-type-hints-strict`

### Library structure

- `python-library-architecture`
- `python-module-boundaries`
- `python-package-layout`
- `python-class-design`
- `python-data-model-methods`
- `python-model-selection`
- `python-context-management`
- `python-docstrings`
- `python-naming`

### Testing and environment

- `python-testing-pytest`
- `sense-env-scaffold`
- `copilot-instructions-init`

### Planning and implementation workflow

- `api-client-porting-planner`
- `api-client-porting-implementer`
- `python-plan-authoring`
- `python-plan-review`
- `python-tdd-test-authoring`
- `plan-step-tracker`
- `python-implementation-review`
- `python-code-review`
- `python-async-planning`

### Git and release workflow

- `git-commit-convention`
- `git-branch-naming`
- `git-post-merge-workflow`
- `git-release-management`

## Composable resilient request execution

`Requester` is a raw `RequestExecutor`: it owns auth/header composition and
sends exactly once. Resilience is caller-owned wiring through
`PolicyRequestExecutor(raw, policies)`, with policies listed left-to-right from
outermost to innermost. The canonical authenticated composition is
`UnauthorizedRecoveryPolicy` outside `TransientRetryPolicy`.

The stable internal contracts live in `core.request_execution`; policy types
and the transport-backed failure classifier live in `mlops_async.resilience`.
They are intentionally not package-root exports and no default factory installs
them implicitly. `HttpClient` remains single-send and only attaches the
transport-neutral metadata consumed by the injected classifier. Raw
`TokenEndpointClient.request_json` stays outside every policy chain.

Only `GET` and `HEAD` are eligible: 401 recovery may conditionally refresh and
replay once, and transient retries cover connection, timeout, `429`, `502`,
`503`, and `504` failures with independent initial/replay budgets. `POST` and
all other methods receive neither retry nor replay without separate runtime
evidence and approval.

## Custom agents

This repository includes 1 custom workflow agent.

- `python-implementation-workflow` orchestrates plan review, TDD assessment,
  implementation gating, implementation review, and code review for one topic

## Control documents

- `README.md` as the human entry point
- `.github/CONTRIBUTING.md` as the development workflow
- `.github/copilot-instructions.md` as the AI control plane
- `docs/project-goal.md` as the project mission, success criteria, non-goals, and phase boundary
- `docs/project-guidelines.md` as the project execution rules, stop conditions, and topic git workflow
- `blueprint.md` as the initialization and acceptance contract
- `analysis/api-client-porting-contract/requirements.md` as the frozen API porting behavior requirements
- `analysis/api-client-porting-contract/technical-spec.md` as the technical mapping for API porting workflow artifacts
- `plan/api-client-porting-contract/api-client-porting-contract.plan.md` as the implementation contract for the porting workflow
- `docs/migration-map.md` as the centralized source-to-target migration map for endpoint families
- `docs/porting-ledger.md` as the evidence ledger for each ported source SDK API
