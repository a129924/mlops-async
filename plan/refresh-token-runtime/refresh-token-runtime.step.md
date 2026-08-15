---
topic: refresh-token-runtime
phase: plan-authoring
created: 2026-07-28
---

# refresh-token-runtime — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/refresh-token-runtime/refresh-token-runtime.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Modify `src/mlops_async/core/token_storage.py` with compatible internal refresh-token state.
- [X] 2. Modify `src/mlops_async/core/token_endpoint/_shared.py` for response validation and state construction.
- [X] 3. Modify `src/mlops_async/core/token_endpoint/password.py` to use the refresh grant.
- [X] 4. Modify `src/mlops_async/core/auth.py` to normalize an omitted refresh token before one storage replacement.
- [X] 5. Extend `tests/unit/core/test_token_storage.py` and `tests/unit/core/test_password_token_endpoint_client.py`.
- [X] 6. Extend `tests/unit/core/test_token_manager.py` for normalization, atomicity, concurrency, failure, and cancellation.
- [X] 7. Update `README.md` and `docs/standards/http-client-auth-boundary.md`.
- [X] 8. Synchronize `VERSION`, `pyproject.toml`, and `uv.lock` at `0.15.0`.
