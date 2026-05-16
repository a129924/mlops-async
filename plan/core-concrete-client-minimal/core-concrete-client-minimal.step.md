---
topic: core-concrete-client-minimal
phase: code-review
created: 2026-05-14
---

# core-concrete-client-minimal — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Open `src/mlops_async/core/http_client.py` and `src/mlops_async/transport/`. If the old core path exists, plan its deletion rather than preserving an alias, then create `src/mlops_async/transport/__init__.py` and `src/mlops_async/transport/http_client.py` as the only concrete client home.
- [X] 2. In `src/mlops_async/transport/http_client.py`, implement the internal-only minimal concrete HttpClient so it satisfies the existing `Client` Protocol, accepts only the locked constructor parameters, owns only the `httpx.AsyncClient` it creates itself, and rejects complete `httpx.AsyncClient` injection.
- [X] 3. In `src/mlops_async/transport/http_client.py`, implement request-building behavior that keeps the thin header policy: default `Accept: application/json`, add `Content-Type: application/json` only for JSON bodies, allow per-request same-name header override, and forbid client-level default params or client-level default options merge.
- [X] 4. In `src/mlops_async/transport/http_client.py`, preserve the existing failure boundary by making `request()` a success-only raw path and `request_json()` a JSON-success-only path, with non-2xx, transport failures, and invalid JSON routed through the transport exception hierarchy.
- [X] 5. Update `src/mlops_async/exceptions.py` so the file ends with only `MlopsAsyncBaseException`, with no transport concrete exceptions, no root re-export, and no alias / transition compatibility layer.
- [X] 6. Create `src/mlops_async/transport/exceptions.py` and define `HttpErrorContext`, `HttpTransportException`, `HTTPStatusException`, and `InvalidJSONResponseException`, keeping the locked hierarchy `MlopsAsyncBaseException` -> `HttpTransportException` -> semantic subclasses.
- [X] 7. Create or update `tests/unit/transport/test_http_client.py`, `tests/unit/transport/test_exceptions.py`, and `tests/unit/core/test_client_contract.py` so they verify the sole `transport/http_client.py` path, exception placement, hierarchy, request/raw/json boundaries, transport ownership, and absence of root re-export or alias behavior.
- [X] 8. If implementation leaves the repository narrative misleading, update `docs/ARCHITECTURE.md` to state that the concrete internal HttpClient lives under `transport/http_client.py`, that `core/` remains contract-only, and that no public facade is introduced in this topic.
