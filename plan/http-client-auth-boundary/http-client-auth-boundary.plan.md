Analysis-layer routing: **strict mode** — both `analysis/http-client-auth-boundary/requirements.md` and `analysis/http-client-auth-boundary/technical-spec.md` exist. This plan treats `analysis/http-client-auth-boundary/technical-spec.md` as the execution-facing source of truth and uses `analysis/http-client-auth-boundary/requirements.md` as the business guardrail. Chat-time context is used only where it does not conflict with the analysis layer.

## Goal / Outcome

建立一個 repo-visible execution contract，讓後續 creator 可以在不擴張 scope 的前提下，實作 `HttpClient` / `Requester` / `AuthProvider` / `TokenManager` / `TokenStorage` / `TokenFetcher` 的 internal 邊界、測試與文件。

Topic 完成時，repo 內應明確存在 auth/request composition 所需的 internal contracts、request composition boundary、transport regression coverage、以及對應的 architecture documentation。

## Scope

- **In scope**:
  - `analysis/http-client-auth-boundary/requirements.md`
  - `analysis/http-client-auth-boundary/technical-spec.md`
  - `plan/http-client-auth-boundary/http-client-auth-boundary.plan.md`
  - `plan/http-client-auth-boundary/http-client-auth-boundary.spec.md`
  - `plan/http-client-auth-boundary/http-client-auth-boundary.step.md`
  - `docs/ARCHITECTURE.md`
  - `src/mlops_async/core/auth.py`
  - `src/mlops_async/core/token_storage.py`
  - `src/mlops_async/core/requester.py`
  - `src/mlops_async/transport/http_client.py`
  - `tests/unit/core/test_token_manager.py`
  - `tests/unit/core/test_token_storage.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_auth_contract.py`
  - `tests/unit/core/test_requester_auth_boundary.py`
  - `tests/unit/transport/test_http_client.py`

- **Out of scope**:
  - Public stable `MlopsAsyncClient` surface
  - Full OAuth flow
  - Credential persistence or cross-process token cache
  - 401 auto refresh/retry
  - upload/download/streaming
  - README/VERSION/release-note changes

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**.
- `HttpClient` remains pure transport. It may transmit a final `Authorization` header already present in request headers, but must not generate, validate, refresh, override, or persist it.
- `Requester` is the only request composition layer for domain calls. It may apply safe request defaults, obtain auth headers from `AuthProvider`, check `Authorization` conflicts case-insensitively, merge defaults/auth/caller headers, and then call `HttpClient`.
- If `AuthProvider` is configured, caller-provided `Authorization` must be rejected before the domain request transport executes.
- `AuthProvider` stays thin and depends only on `TokenManager`.
- `TokenManager` owns token lifecycle, expiry check, refresh decision, `asyncio.Lock`, and double-check locking; it depends only on `TokenStorage` and `TokenFetcher`.
- `TokenStorage` is dumb storage only; it does not validate, refresh, or call HTTP.
- `TokenFetcher` is the token endpoint collaborator. It may depend on raw `HttpClient`, but must not depend on `Requester` or `AuthProvider`.
- `AccessToken` expiry uses configurable skew defaulting to 60 seconds, and `now + skew >= expires_at` means expired.
- Refresh/fetch success is the only state-change point for `TokenStorage`; failure or cancellation must preserve previous token state.
- Concurrency validation must prove that at least 10 concurrent coroutines sharing one `TokenManager` trigger at most one refresh/fetch.
- No correction/delta artifact path is used in this topic.
- No `review-log` artifact is required because routing does not depend on multi-round reviewer-controlled rework.
- No round cap is declared for this topic.

## Boundaries / Exclusions

- Planning actor creates and updates the repo-visible analysis/plan artifacts only; creator implementation begins later.
- Creator must not expand this topic into public facade stabilization, distributed locking, or retry orchestration.
- Reviewer evaluates this topic against the locked decisions, exact artifact paths, and analysis-layer traceability; reviewer must not re-scope the topic by inference.
- If later work needs OAuth grant semantics, cross-process coordination, or 401 retry, that belongs to a separate topic.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops before release and does not declare stable-library promotion.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- Analysis-layer strict mode applies for this topic.
- Shared-file coordination warning: `analysis/`, `plan/`, and `docs/ARCHITECTURE.md` are planner/governance surfaces that can conflict across worktrees; any drift outside listed paths must be treated as a plan-alignment issue.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic requirements baseline | `analysis/http-client-auth-boundary/requirements.md` | Planning actor | Business baseline and business guardrail for this topic |
| Topic technical specification | `analysis/http-client-auth-boundary/technical-spec.md` | Planning actor | Execution-facing technical baseline mapped from requirements |
| Topic plan | `plan/http-client-auth-boundary/http-client-auth-boundary.plan.md` | Planning actor | Repo-visible execution contract for creator/reviewer workflow |
| Topic specification | `plan/http-client-auth-boundary/http-client-auth-boundary.spec.md` | Planning actor | Python workflow behavior contract for non-trivial TDD assessment |
| Topic step tracker | `plan/http-client-auth-boundary/http-client-auth-boundary.step.md` | Planning actor | Repo-visible step tracker mirroring `## Implementation Steps` for completion gates |
| Architecture contract update | `docs/ARCHITECTURE.md` | Creator | Documents final dependency direction and boundary split |
| Auth contracts | `src/mlops_async/core/auth.py` | Creator | Internal `AuthProvider` / `TokenManager` / `TokenFetcher` contracts and minimal implementations allowed by scope |
| Token state and storage | `src/mlops_async/core/token_storage.py` | Creator | Internal `AccessToken`, `TokenStorage`, and minimal in-memory storage |
| Request composition boundary | `src/mlops_async/core/requester.py` | Creator | Single request composition layer for domain calls |
| Transport boundary preservation | `src/mlops_async/transport/http_client.py` | Creator | Transport-only implementation with auth-agnostic behavior preserved |
| Token manager tests | `tests/unit/core/test_token_manager.py` | Creator | Proves lifecycle, concurrency, failure, and state-preservation behavior |
| Token storage tests | `tests/unit/core/test_token_storage.py` | Creator | Proves dumb storage semantics |
| Auth provider tests | `tests/unit/core/test_auth_provider.py` | Creator | Proves thin token-to-header behavior |
| Auth contract tests | `tests/unit/core/test_auth_contract.py` | Creator | Proves internal contract surface and shape |
| Requester boundary tests | `tests/unit/core/test_requester_auth_boundary.py` | Creator | Proves defaults/auth/caller merge, conflict rejection, and transport gating |
| Transport regression tests | `tests/unit/transport/test_http_client.py` | Creator | Preserves transport-only scope and forbidden default-header rules |

Artifact path notes:

- This topic does **not** modify `README.md`, `VERSION`, or `.github/copilot-instructions.md`.
- Listed paths are an executable contract; later work outside these paths requires plan alignment before implementation continues.
- No correction or delta artifact family is used here.
- No `review-log` path is listed because reviewer feedback does not control routing across multiple mandatory rework rounds in this topic.

## Implementation Steps

1. Update `docs/ARCHITECTURE.md` so it states that `HttpClient` is transport-only, `Requester` is the only request composition layer, and dependency direction is Domain client -> `Requester` -> `HttpClient` with optional `AuthProvider`.
2. Add `src/mlops_async/core/token_storage.py` with internal `AccessToken`, `TokenStorage`, and `InMemoryTokenStorage`, including configurable expiry skew defaulting to 60 seconds.
3. Add or update `src/mlops_async/core/auth.py` with internal `AuthProvider`, `TokenManager`, and `TokenFetcher` contracts and minimal topic-scoped implementations allowed by the technical spec.
4. Implement `TokenManager` lifecycle behavior so `get_access_token()` uses `asyncio.Lock` plus double-check locking, writes new token state only after successful fetch/refresh, and preserves previous token state on failure or cancellation.
5. Add `src/mlops_async/core/requester.py` so it may apply safe request defaults, obtains auth headers from `AuthProvider`, rejects caller-supplied `Authorization` when `AuthProvider` is configured, merges defaults/auth/caller headers, and delegates final request data to `HttpClient`.
6. Preserve transport-only scope in `src/mlops_async/transport/http_client.py`; only make changes required to clarify or preserve the locked transport contract.
7. Add `tests/unit/core/test_token_manager.py` covering at least 10 concurrent coroutines, single refresh/fetch behavior, non-expired bypass behavior, auth-layer failure surfacing, skew behavior, and previous-token preservation on failure/cancellation.
8. Add `tests/unit/core/test_token_storage.py`, `tests/unit/core/test_auth_provider.py`, and `tests/unit/core/test_auth_contract.py` covering dumb storage, thin auth header generation, and internal contract shape.
9. Add `tests/unit/core/test_requester_auth_boundary.py` covering safe defaults, conflict rejection, auth-optional caller `Authorization`, merge ordering, and transport gating.
10. Preserve and extend `tests/unit/transport/test_http_client.py` so auth-specific scope creep remains blocked by regression tests.

## Validation / Acceptance Checks

- `analysis/http-client-auth-boundary/requirements.md` and `analysis/http-client-auth-boundary/technical-spec.md` both exist and match this plan's scope.
- Every implementation step maps back to `analysis/http-client-auth-boundary/technical-spec.md` without extra feature work.
- `HttpClient` remains auth-agnostic and transport-only after creator work.
- `Requester` is the only domain request composition layer.
- `AuthProvider` depends only on `TokenManager`.
- `TokenManager` depends only on `TokenStorage` and `TokenFetcher`.
- `TokenFetcher` depends only on raw `HttpClient`, never on `Requester` / `AuthProvider`.
- Concurrency tests prove that at least 10 concurrent coroutines sharing one `TokenManager` trigger at most one refresh/fetch.
- Failure/cancellation tests prove previous token state is preserved and no domain request transport call occurs after auth-layer failure.
- Validation commands remain:
  - `uv run pytest tests/unit/transport/test_http_client.py tests/unit/core/test_auth_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_manager.py tests/unit/core/test_token_storage.py tests/unit/core/test_auth_provider.py`
  - `uv run ruff check src tests`
  - `uv run pyright`
  - `uv run tach check`
  - `uv run pytest`

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- After merge, no repository release action is required for this topic.
- No README row, VERSION bump, or release-note action is expected.

## Open Questions / Unresolved Items

- None.

## Goal

建立 internal auth/request composition boundary，使後續 creator 可以在不擴張 scope 的前提下，實作 `HttpClient` / `Requester` / `AuthProvider` / `TokenManager` / `TokenStorage` / `TokenFetcher`，並讓 Python implementation workflow 在 plan review 與 TDD gate 都有足夠的 repo-visible contract 可依循。

## Non-goals

1. 不建立 public stable `MlopsAsyncClient` surface。
2. 不實作完整 OAuth flow。
3. 不實作 credential persistence 或 cross-process token cache。
4. 不實作 401 auto refresh/retry。
5. 不修改 README、VERSION、release notes。

## Current Context

1. `src/mlops_async/transport/http_client.py` 已存在，並被既有測試鎖定為 transport-only concrete client。
2. `analysis/http-client-auth-boundary/requirements.md` 與 `analysis/http-client-auth-boundary/technical-spec.md` 已存在，分別凍結 business baseline 與 execution-facing technical baseline。
3. 目前 repo-visible topic plan 已符合 `plan/agent-handoff-workflow.md` 與 `plan-reviewer` contract，但 implement-agent feedback 指出 Python workflow 仍缺 `plan/http-client-auth-boundary/http-client-auth-boundary.spec.md`，且 `.plan.md` 需要 exact Python-plan sections 才能被 `python-plan-review` / `python-tdd-test-authoring` 正常消費。
4. `plan/http-client-auth-boundary/http-client-auth-boundary.step.md` 已存在，並已鏡射 `## Implementation Steps`。

## Requirements

1. `HttpClient` 必須維持 pure transport：只接收 final request data，不產生、驗證、刷新、覆寫或持久化 `Authorization`。
2. `Requester` 必須是唯一 request composition layer，並在 configured `AuthProvider` 存在時拒絕 caller-supplied `Authorization`。
3. `AuthProvider` 必須保持薄，只把 `TokenManager` 產出的 token 轉成 auth headers。
4. `TokenManager` 必須擁有 token lifecycle、expiry check、refresh decision、`asyncio.Lock` 與 double-check locking。
5. `TokenStorage` 必須是 dumb storage；refresh 成功前不得覆寫既有 token state。
6. `TokenFetcher` failure 必須 surface 成 auth-layer exception，且 failure path 不得繼續呼叫 domain request transport。
7. `AccessToken` expiry 判斷必須支援 configurable skew，預設 60 秒。
8. 測試必須證明至少 10 個 concurrent coroutines 共用一個 `TokenManager` 時，最多只會 refresh/fetch 一次。

## Decisions

- Async-planning status: triggered — cite trigger evidence: `src/mlops_async/transport/http_client.py` 使用 `httpx.AsyncClient`，topic 需要決定 `Requester` request composition、`TokenManager` 的 `asyncio.Lock` / double-check locking、refresh failure/cancellation state handling、與 auth-layer timeout/cancellation boundary。
- Module/package placement: `src/mlops_async/core/auth.py` 放 internal `AuthProvider` / `TokenManager` / `TokenFetcher` contracts；`src/mlops_async/core/token_storage.py` 放 `AccessToken` / `TokenStorage` / `InMemoryTokenStorage`；`src/mlops_async/core/requester.py` 放 `Requester`；`src/mlops_async/transport/http_client.py` 保持 transport-only。
- New public API: no — 本 topic 不新增 public stable API，也不更新 `src/mlops_async/__init__.py` 對外匯出。
- Interface changes: yes — 新增 internal `AuthProvider` / `TokenManager` / `TokenFetcher` / `TokenStorage` / `Requester` contracts 或最小實作；既有 `HttpClient` public/internal transport semantics 不變。
- Breaking changes allowed: no — 必須保留既有 `HttpClient` forbidden default-header 與 transport regression semantics。
- New dependencies: no — 不新增 runtime dependency；只使用 stdlib 與既有專案依賴。
- Error handling strategy: `HttpClient` 只 raise transport/status/invalid JSON exceptions；token fetch/refresh failure 與 `Authorization` conflict 必須 surface 成 auth/request boundary exception，不翻譯成 transport exception。
- Typing strategy: fully typed internal contracts；以 `Protocol` 表示可替換 collaborators；不使用未約束的 `Any`。

### Async boundary decision

`HttpClient` 只承擔 async transport I/O。`Requester` 先做 request composition，再把 final request 交給 `HttpClient`。`AuthProvider`、`TokenManager`、`TokenFetcher`、`TokenStorage` 都是 async-capable internal boundaries，但不得在 import-time 執行 I/O。

### Resource lifecycle decision

`HttpClient` 繼續擁有自己建立的 `httpx.AsyncClient`。未來 composition root 會組裝 `Requester`、`AuthProvider`、`TokenManager`、`TokenFetcher`、`TokenStorage` 與 domain clients。`TokenStorage` 只保存 token state；refresh success 前不得覆寫 existing state。

### Concurrency model

request path 採 sequential direct await：`Requester` 先取得 auth headers，再檢查 conflict，然後呼叫 `HttpClient`。`TokenManager.get_access_token()` 使用 `asyncio.Lock` + double-check locking；至少 10 個 concurrent coroutines 共用同一 manager 時，最多 refresh/fetch 一次。

### Failure model

`TokenFetcher` failure 由 `TokenManager` 以 auth-layer exception 向上 surface。`Requester` 的 `Authorization` conflict 直接 raise request-boundary exception。這些 failure 都不得繼續進入 domain request `HttpClient`。refresh/fetch failure 或 cancellation 不得覆寫 existing token state。

### Cancellation / timeout policy

`CancelledError` 由呼叫端 task 擁有；`Requester`、`AuthProvider`、`TokenManager` 不吞 cancellation。`HttpClient` timeout 仍由既有 `RequestTimeouts` / `ClientRequestOptions` 控制。若 auth flow 需要 timeout，必須留在 auth layer，不可偷偷重用 domain request timeout。

### Validation plan

1. `tests/unit/core/test_token_manager.py` 驗證 10-coro concurrency、single refresh/fetch、failure/cancellation state preservation、與 skew behavior。
2. `tests/unit/core/test_requester_auth_boundary.py` 驗證 safe defaults、`Authorization` conflict、merge ordering、與 transport gating。
3. `tests/unit/core/test_auth_provider.py`、`tests/unit/core/test_token_storage.py`、`tests/unit/core/test_auth_contract.py` 驗證 thin auth behavior、dumb storage semantics、與 contract shape。
4. `tests/unit/transport/test_http_client.py` 驗證 `HttpClient` transport-only scope 沒被 auth logic 汙染。

### Handoff notes for the implementer

不要把 auth lifecycle 下沉到 `HttpClient`。`Requester` 是唯一 request composition layer，且只把 final request data 交給 `HttpClient`。`TokenFetcher` 只可依賴 raw `HttpClient`，不可經過 `Requester` / `AuthProvider`。若 implementation 過程需要 401 retry、distributed lock、或 public facade stabilization，停止並另開 topic。

## Public Contract / API Changes

No public API changes in this topic.

Internal-only additions may include:

- `AuthProvider`
- `TokenManager`
- `TokenFetcher`
- `TokenStorage`
- `AccessToken`
- `Requester`

These remain internal contracts or internal implementations and are not re-exported from `src/mlops_async/__init__.py`.

## Affected Files / Modules

Likely affected files:
- `docs/ARCHITECTURE.md`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_token_storage.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/transport/test_http_client.py`

Candidate files to inspect:
- `analysis/http-client-auth-boundary/requirements.md`
- `analysis/http-client-auth-boundary/technical-spec.md`
- `plan/http-client-auth-boundary/http-client-auth-boundary.spec.md`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/request_options.py`
- `src/mlops_async/core/types.py`

## Test Plan

1. Happy path: `Requester` 在 configured `AuthProvider` 下成功取得 auth headers、merge defaults/auth/caller headers，並把 final request 交給 `HttpClient`；`AuthProvider` 成功把 token 轉成 `Authorization` header。
2. Invalid input: caller 在 configured `AuthProvider` 下傳入任意大小寫的 `Authorization` header 時，`Requester` 直接拒絕；`TokenFetcher` failure 會 surface 為 auth-layer exception。
3. Edge case: `AccessToken` configurable skew 預設 60 秒；`now + skew >= expires_at` 視為 expired；至少 10 個 concurrent coroutines 共用同一 `TokenManager` 時只 refresh/fetch 一次。
4. Regression: `HttpClient` 仍拒絕在 default headers 中帶入 `Authorization`，且 constructor / transport behavior 不被 auth lifecycle 汙染。
5. Backward compatibility: 既有 `tests/unit/transport/test_http_client.py` raw/json/timeout/error/resource lifecycle 行為維持通過。

## Validation Commands

Use existing project validation commands from `pyproject.toml` / `README`:

```bash
uv run pytest tests/unit/transport/test_http_client.py tests/unit/core/test_auth_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_manager.py tests/unit/core/test_token_storage.py tests/unit/core/test_auth_provider.py
uv run ruff check src tests
uv run pyright
uv run tach check
uv run pytest
```

## Risks

1. 若 `Requester` 與 `HttpClient` 的邊界沒有被明確鎖定，容易再次把 auth logic 下沉到 transport。
2. 若 `TokenManager` failure/cancellation state 沒測到，可能會在 refresh 失敗時汙染 token state。
3. 若 `TokenFetcher` 反向依賴 `Requester`，會重新引入 circular dependency。

## Rollback Plan

若這次 creator work 需要回滾，revert 下列 paths 的 topic changes:

- `docs/ARCHITECTURE.md`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_token_storage.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/transport/test_http_client.py`

Do not revert unrelated files outside the topic artifact paths without explicit alignment.

## Open Questions

None.
