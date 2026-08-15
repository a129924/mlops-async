---
topic: resilient-request-execution
phase: plan-review
created: 2026-08-11
---

# Resilient Request Execution — DI Rework Step Tracking

> **Executor**: Mark a step `[X]` only after the corresponding DI rework is complete.
> Every prior fixed-decorator completion mark is invalidated by the human-approved architecture replacement.
> All steps must be `[X]` before `python-implementation-review`.

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Add `core.request_execution` stable non-root contracts: `RequestExecutor`, immutable `RequestInvocation`, immutable `AuthRecoveryAttempt`, `AuthRecoveryExecutor`, and injected `RequestFailureClassifier`.
- [X] 2. Refactor `Requester` to raw-only auth/header composition and per-attempt recovery capability; remove the fixed decorator/context, shared token state, and `Client.failure_for` coupling.
- [X] 3. Add `src/mlops_async/resilience/__init__.py`, `classifier.py`, `executor.py`, and `policies.py` in their locked ownership split: classifier in `classifier.py`, decorator in `executor.py`, and policy types in `policies.py`; repair the current all-in-`policies.py` drift rather than changing the plan.
- [X] 4. Implement `UnauthorizedRecoveryPolicy` and `TransientRetryPolicy` with the locked GET/HEAD match/case, retry, refresh/replay, budget, Retry-After, and cancellation contracts.
- [X] 5. Preserve transport metadata/single-send semantics and change Projects, Models, and Job Execution dependency annotations to `RequestExecutor` without runtime request-contract changes.
- [X] 6. Replace focused tests with pipeline, custom policy, classifier, retry, recovery, token, cancellation, bypass, and endpoint request-shape coverage.
- [X] 7. Modify `tach.toml` with exactly `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`; prove the one-way projection using Tach with no global relax/suppression, reverse dependency, or transport exception.
- [X] 8. Update architecture and auth-boundary documentation for manual DI composition, non-root stable API, raw token bypass, and mutation exclusions.

## Required Validation Evidence

- Focused WSL validation: 270 passed; Ruff format check, Ruff check, Pyright, and Tach passed.
- Tach evidence confirms the exact `mlops_async.resilience -> mlops_async.core` declaration and no broader configuration relaxation.
- Full WSL pytest: 596 passed, 10 skipped, 92.70% coverage. The sole nonzero condition is the user-accepted known linked-worktree Git guard exit 128; it remains disclosed as an environment exception, not a full-suite pass.
- Source, tests, and docs for all eight DI rework steps are complete. Independent plan/implementation/code review and Draft PR publication/human review routing remain pending.
