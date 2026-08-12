# Resilient Request Execution — DI Rework Specification

## Public Contract

- `mlops_async.core.request_execution` exports the stable non-root `RequestExecutor`, frozen `RequestInvocation`, `AuthRecoveryExecutor`, frozen `AuthRecoveryAttempt`, and `RequestFailureClassifier` contracts.
- `mlops_async.resilience` exports the stable non-root `RequestPolicy`, `PolicyRequestExecutor`, `UnauthorizedRecoveryPolicy`, `TransientRetryPolicy`, and `TransportRequestFailureClassifier` surface.
- `resilience/classifier.py` owns the classifier, `resilience/executor.py` owns the decorator, and `resilience/policies.py` owns policy types; current all-in-`policies.py` implementation is drift to repair, not a placement decision.
- No symbol is re-exported by `mlops_async.__init__`. Existing endpoint constructors retain their runtime call shape and replace only their annotation with `RequestExecutor`.

## Required Behavior

1. Raw `Requester` composes auth/default/request headers and delegates exactly one transport send; it installs no resilience policy.
2. `PolicyRequestExecutor` decorates a raw executor using supplied policies left-to-right outermost-to-innermost. `UnauthorizedRecoveryPolicy` outer + `TransientRetryPolicy` inner is canonical; a replay enters the entire inner chain.
3. Policy construction rejects non-policies, duplicate built-in policy types, and an unauthorized policy around an executor without auth-recovery capability. Custom policies remain injectable and ordered.
4. Eligibility is literal `match/case`: only GET/HEAD receive retry/recovery. Transient retry is restricted to classified connection/timeout/429/502/503/504 with three sends per initial or replay path, locked jitter/backoff/Retry-After, and no cancellation swallowing.
5. Classified authenticated 401 receives at most one `refresh_if_current` and one replay. Exact observed token is attempt-local; changed token replays current state without refresh, cleared state does neither fetch nor refresh, and replay never refreshes again.
6. Default classifier reads preserved transport failure metadata. `Client.failure_for` does not exist. Token endpoint requests remain raw.
7. `tach.toml` declares exactly `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`; it is a one-way architecture projection, not a global relax/suppression or a reverse/transport dependency.

## Test Plan

- Core/resilience: raw/no-policy, single custom policy, ordered custom/built-in pipeline, duplicate/non-policy/missing-capability rejection, no root exports, and classifier `None` pass-through.
- Transient: GET/HEAD recovery, POST default branch/no replay, retry statuses/errors, initial/replay independent budgets, jitter fallback, valid/invalid/clamped Retry-After, timeout preservation, and cancellation.
- Unauthorized: initial one-refresh/one-replay, changed/cleared token behavior, concurrent callers, refresh error/cancellation preservation, unauthenticated 401 pass-through, and replay through transient chain.
- Integration contracts: Projects, Models, and Job Execution accept raw and decorated dependencies and emit unchanged requests; token endpoint bypasses policies; transport remains single-send and identity-preserving.
- Architecture: `tach check` accepts the exact resilience-to-core projection and detects no broader exception.

## Validation

Run the topic-focused pytest selection plus WSL Ruff format check, Ruff check, Pyright, Tach, and full pytest. Keep PR #68 Draft through independent plan, implementation, and code review. A linked-worktree Git guard failure must be reported as an environment exception, never a passing full-suite result.
