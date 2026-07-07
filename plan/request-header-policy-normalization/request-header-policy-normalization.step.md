---
topic: request-header-policy-normalization
phase: code-review
created: 2026-07-06
---

# request-header-policy-normalization Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/request-header-policy-normalization/request-header-policy-normalization.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Create `analysis/request-header-policy-normalization/requirements.md` and freeze family-aware request-header policy scope, release/doc surfaces, and non-goals.
- [X] 2. Create `analysis/request-header-policy-normalization/technical-spec.md` mapping the requirements baseline to helper design, runtime call sites, TDD evidence, and release/doc alignment.
- [X] 3. Create `plan/request-header-policy-normalization/request-header-policy-normalization.plan.md`, `plan/request-header-policy-normalization/request-header-policy-normalization.spec.md`, and keep this step tracker aligned with the same locked decisions and artifact paths.
- [X] 4. Author RED tests in `tests/unit/core/test_requester_auth_boundary.py`, `tests/unit/core/test_token_endpoint_client.py`, and `tests/unit/transport/test_http_client.py` proving centralized request-header policy expectations before production code changes.
- [X] 5. Record the TDD verdict and requirement-to-test mapping in `plan/request-header-policy-normalization/request-header-policy-normalization.tdd-test-authoring.yaml`, explicitly capturing the production-code-precondition exception instead of falsely certifying a clean RED-before-production sequence.
- [X] 6. Update `src/mlops_async/core/headers.py` to keep `merge_headers()` and add internal request-header policy helpers/constants for JSON domain and auth token request families.
- [X] 7. Update `src/mlops_async/core/requester.py` to consume the centralized JSON domain request policy without changing merge order, caller override behavior, or `AuthorizationConflictException` semantics.
- [X] 8. Update `src/mlops_async/core/token_endpoint_client.py` to consume the centralized token request policy without changing client-credentials request shape or response parsing.
- [X] 9. Make only the minimum supporting adjustments in `src/mlops_async/transport/http_client.py`, `docs/ARCHITECTURE.md`, `docs/standards/http-client-auth-boundary.md`, and `README.md` so runtime, docs, and release-facing descriptions all match the final implementation truth.
- [X] 10. Run bounded validation for unit/request-contract coverage plus full repo checks, then prepare release-surface follow-up evidence for `VERSION`, `pyproject.toml`, and `uv.lock` without mutating release metadata until the Main Agent release step.
