---
topic: resilient-request-execution
phase: plan-authoring
created: 2026-08-11
---

# Resilient Request Execution Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Current workflow state is `planned`; Main Agent routing is required before `creator-in-progress`.

## Workflow Stages

- [ ] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. In `src/mlops_async/core/request_failure.py` and `src/mlops_async/core/client.py`, add the immutable non-exported failure carrier and fully typed `Client.failure_for(exception) -> RequestFailure | None` classification without importing transport or `httpx` from core.
- [X] 2. In `src/mlops_async/transport/exceptions.py` and `src/mlops_async/transport/http_client.py`, attach failure metadata while retaining `HttpClient` single-send behavior and original exception identity, message, context, and properties.
- [X] 3. In `src/mlops_async/core/auth.py`, implement the locked `TokenManager.refresh_if_current` coordination for same-token refresh, changed-token skip/current replay, cleared-storage no-fetch, and refresh/cancellation storage preservation.
- [X] 4. In `src/mlops_async/core/requester.py`, compose private `_RequesterResilienceDecorator` around the canonical primitive request path with literal `match`/`case` GET/HEAD eligibility, default noneligible handling, eligible failure classification, independent initial/replay three-send budgets, jitter, `Retry-After`, and per-send timeout.
- [X] 5. In `src/mlops_async/core/requester.py` and the raw `TokenEndpointClient.request_json` composition route, implement initial-only conditional `401` refresh plus one replay with no secondary refresh, while preserving the raw-token decorator bypass.
- [X] 6. In `tests/unit/core/test_request_failure.py`, `tests/unit/core/test_request_resilience.py`, `tests/unit/core/test_client_contract.py`, `tests/unit/core/test_requester_auth_boundary.py`, `tests/unit/core/test_token_manager.py`, `tests/unit/transport/test_exceptions.py`, and `tests/unit/transport/test_http_client.py`, add focused tests for carrier boundaries, GET/HEAD/default method branches, recovery/budgets/delay, concurrent 401, cancellation, bypass, and exception compatibility.
- [X] 7. In `docs/ARCHITECTURE.md` and `docs/standards/http-client-auth-boundary.md`, document the private resilience boundary, bounded retry/replay, raw-token bypass, and the prohibition on POST retry/replay without endpoint runtime evidence and explicit approval.

> Reviewer rework (python-implementation-review): final evidence now covers the completed tests and documentation boundaries for Steps 6 and 7. The independent implementation-review workflow stage remains pending.

## Completed Validation Evidence

- Feature static checks: Ruff format check, Ruff check, Pyright, and Tach PASS.
- Feature targeted tests: 112 passed.
- Exact feature WSL run: 591 passed, 10 skipped, 1 failed, with 93.72% coverage; the sole failure was the WSL Git linked-worktree `.git` guard subprocess.
- ext4 byte-identical overlay: 592 passed, 10 skipped functionally; Git import guard 7 passed and the feature manifest was unchanged before/after. Coverage was 0 because the copied environment used a symlinked virtual environment.
- Exact feature native `git diff --check`: PASS.
