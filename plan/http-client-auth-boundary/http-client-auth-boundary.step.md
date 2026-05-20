---
topic: http-client-auth-boundary
phase: plan-authoring
created: 2026-05-20
---

# http-client-auth-boundary — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/http-client-auth-boundary/http-client-auth-boundary.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. Update `docs/ARCHITECTURE.md` so it states that `HttpClient` is transport-only, `Requester` is the request composition layer, and the dependency direction is Domain client -> `Requester` -> `HttpClient` with optional `AuthProvider`.
- [ ] 2. Open `src/mlops_async/core/token_storage.py` if it exists, or create it if implementation scope allows new internal state types; add internal `AccessToken` value object plus minimal `TokenStorage` contract and `InMemoryTokenStorage` for token read/write only.
- [ ] 3. Open `src/mlops_async/core/auth.py` if it exists, or create it if implementation scope allows new internal contracts; define minimal fully typed `AuthProvider`, `TokenManager`, and `TokenFetcher` contracts and keep `AuthProvider` as a thin token-to-header adapter.
- [ ] 4. Open `src/mlops_async/core/auth.py` and/or `src/mlops_async/core/token_storage.py`; implement `TokenManager.get_access_token()` with `asyncio.Lock` double-check locking so only one coroutine refreshes/fetches while others wait and then reuse the updated token.
- [ ] 5. Open `src/mlops_async/core/requester.py` if it exists, or create it if implementation scope allows a requester boundary; add a minimal async `Requester` that may apply safe defaults such as `Accept` / `Content-Type`, awaits `AuthProvider.get_auth_headers()`, rejects caller-supplied `Authorization` case-insensitively when auth provider is configured, merges defaults / auth headers / caller headers, and delegates final headers to `HttpClient`.
- [ ] 6. Open `src/mlops_async/transport/http_client.py` and verify no auth/token/refresh constructor parameters or lifecycle logic are added; only adjust comments/docstrings if needed to clarify transport-only intent.
- [ ] 7. Open `tests/unit/core/test_token_manager.py` and add concurrent tests proving expired/missing token paths trigger one refresh only with at least 10 concurrent coroutines, non-expired tokens bypass the lock path, waiting coroutines reuse the refreshed token, `TokenFetcher` failures surface as auth-layer failures, and failure/cancellation preserves previous storage state.
- [ ] 8. Open `tests/unit/core/test_auth_provider.py`, `tests/unit/core/test_token_storage.py`, and `tests/unit/core/test_auth_contract.py`; add tests for thin auth header generation, dumb storage behavior, async contract shape, and minimal in-memory storage semantics.
- [ ] 9. Open `tests/unit/core/test_requester_auth_boundary.py` and add tests proving `Requester` obtains auth headers before delegating, rejects caller-supplied `Authorization` when auth provider is configured, allows caller `Authorization` only when auth provider is absent, may apply safe defaults, merges defaults/auth/caller headers in the approved order, and does not expose token manager to domain clients.
- [ ] 10. Open `tests/unit/transport/test_http_client.py` and add or preserve regression coverage that `HttpClient` rejects `Authorization` in default headers and has no token/refresh constructor parameters.
