Analysis-layer routing: **strict mode** — both `analysis/http-client-auth-boundary/requirements.md` and `analysis/http-client-auth-boundary/technical-spec.md` exist. This plan treats `analysis/http-client-auth-boundary/technical-spec.md` as the execution-facing source of truth and uses `analysis/http-client-auth-boundary/requirements.md` as the business guardrail. Chat-time context is used only where it does not conflict with the analysis layer.

## Goal / Outcome

建立一個 repo-visible execution contract，讓後續 creator 可以在不擴張 scope 的前提下，實作 `HttpClient` / `Requester` / `AuthProvider` / `TokenManager` / `TokenStorage` / `TokenFetcher` 的 internal 邊界、測試與文件。

Topic 完成時，repo 內應明確存在 auth/request composition 所需的 internal contracts、request composition boundary、transport regression coverage、以及對應的 architecture documentation。

## Scope

- **In scope**:
  - `analysis/http-client-auth-boundary/requirements.md`
  - `analysis/http-client-auth-boundary/technical-spec.md`
  - `plan/http-client-auth-boundary/http-client-auth-boundary.plan.md`
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

- **Current**: `planned`
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
5. Add `src/mlops_async/core/requester.py` so it may apply safe request defaults, obtains auth headers from `AuthProvider`, rejects caller-supplied `Authorization` when `AuthProvider` is configured, merges defaults/auth/caller headers, and delegates final request data to `Client`.
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
