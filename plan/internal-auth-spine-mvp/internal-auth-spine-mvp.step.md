---
topic: internal-auth-spine-mvp
phase: code-review
created: 2026-07-06
---

# internal-auth-spine-mvp — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Create `analysis/internal-auth-spine-mvp/requirements.md` and freeze the MVP boundary, Python 3.10 enum constraint, and shared endpoint-spec scope.
- [X] 2. Create `analysis/internal-auth-spine-mvp/technical-spec.md` mapping the business baseline to topic-local runtime work, tests, architecture checks, and rollback triggers.
- [X] 3. Create `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md` and `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md` aligned to the topic plan.
- [X] 4. Add `src/mlops_async/core/token_endpoint_client.py` with a concrete token endpoint collaborator and Python 3.10-compatible shared endpoint spec carrier.
- [X] 5. Update `src/mlops_async/core/auth.py` so `TokenManager` integrates with the concrete token collaborator while preserving lock, success-before-store, and auth exception boundaries.
- [X] 6. Preserve `src/mlops_async/core/requester.py` request-composition boundaries and add only the minimum lazy auth integration proof surface needed by tests.
- [X] 7. Add `tests/unit/core/test_token_endpoint_client.py` covering obtain request shape, response translation, shared endpoint-spec source, and invalid response errors.
- [X] 8. Update `tests/unit/core/test_token_manager.py`, `tests/unit/core/test_auth_contract.py`, and `tests/unit/core/test_requester_auth_boundary.py` to reflect the concrete token collaborator and to prove first authenticated request lazy-resolves the token.
- [X] 9. Run bounded validation for the touched unit tests plus `ruff` and `pyright`.
