# Resilient Request Execution Technical Specification

## Goal

Replace PR #68's fixed private `Requester` decorator with a composable dependency-injection boundary. `Requester` is always raw; consumers explicitly decorate it with ordered policies when they require resilience.

## Non-Goal

- Do not make policy composition implicit, global, or package-root exported.
- Do not retry/replay unsafe methods, change endpoint public APIs, wrap token requests, or promote/release the new stable submodule APIs in this topic.

## Locked Contracts

### Stable submodule contracts

- `mlops_async.core.request_execution` exports `RequestExecutor`, `RequestInvocation`, `AuthRecoveryExecutor`, `AuthRecoveryAttempt`, and `RequestFailureClassifier`; none are re-exported from `mlops_async` package root.
- `RequestExecutor.request` keeps the current request call shape: `method`, `path`, optional `headers`, `params`, `json_body`, `content`, and `options`, returning `RawClientResponse` asynchronously.
- `RequestInvocation` is frozen and contains the complete request data used by the policy chain. Policies must forward the same immutable invocation; they may not use shared mutable request or token state.
- `AuthRecoveryAttempt` is frozen and includes the response/failure outcome for one send plus the exact observed `AccessToken | None`. `AuthRecoveryExecutor` provides attempt-aware send and conditional-refresh/replay support. It does not expose a mutable “last token”.
- `RequestFailureClassifier.classify(error) -> RequestFailure | None` is injected into policies. `Client.failure_for` is removed; core does not import transport or `httpx`.

### Resilience package and composition

- `mlops_async.resilience` exports `RequestPolicy`, `PolicyRequestExecutor`, `UnauthorizedRecoveryPolicy`, `TransientRetryPolicy`, and `TransportRequestFailureClassifier` from that submodule only.
- `PolicyRequestExecutor(raw, policies, classifier=TransportRequestFailureClassifier())` is the outer decorator. The input sequence is left-to-right from outermost to innermost. The canonical assembly is `PolicyRequestExecutor(requester, [UnauthorizedRecoveryPolicy(...), TransientRetryPolicy(...)])`.
- A policy receives a `RequestInvocation` and a typed downstream executor. Built-ins preserve `AuthRecoveryExecutor` capability where the wrapped raw executor supports it, so an Unauthorized replay enters its complete inner chain, including a fresh transient retry budget.
- Construction rejects a value that is not a `RequestPolicy`, a built-in policy that lacks its required recovery capability, and repeated built-in policy types. Custom policies may be supplied once or multiple times when they satisfy `RequestPolicy`.
- Placement is fixed: `resilience/classifier.py` owns `TransportRequestFailureClassifier`, `resilience/executor.py` owns `PolicyRequestExecutor`, `resilience/policies.py` owns `RequestPolicy`, `UnauthorizedRecoveryPolicy`, and `TransientRetryPolicy`, and `resilience/__init__.py` owns stable submodule exports. Existing classifier/executor logic in `policies.py` alone is implementation drift and must be split; this specification does not follow the drift.
- `tach.toml` adds exactly `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`. This is a narrow one-way architecture projection, not a repository-wide relax/suppression; no reverse or transport dependency is authorized.

### Raw requester and classification boundary

- `Requester` implements `RequestExecutor` and `AuthRecoveryExecutor`. Its responsibilities are auth/header composition, request dispatch, immutable attempt observation, and `TokenManager.refresh_if_current`; it installs no policy and does no retry/replay itself.
- `HttpClient` remains single-send. Transport exceptions retain identity, message, context, and observable properties while exposing the existing failure metadata consumed by `TransportRequestFailureClassifier`.
- `TokenEndpointClient.request_json` remains raw and cannot enter a `PolicyRequestExecutor` through production composition.

### Policy behavior

- Both built-ins determine safe-method eligibility with exactly:

  ```python
  match method:
      case HttpMethod.GET | HttpMethod.HEAD:
          ...
      case _:
          ...
  ```

  Membership and string comparisons are forbidden for this decision.
- `TransientRetryPolicy` retries only classified connection, timeout, response `429`, `502`, `503`, or `504`; nonclassified errors pass through. Each invocation path has at most three sends including its initial send. Delay is jittered exponential from `0.25`, capped at `2`; valid delta-seconds or HTTP-date `Retry-After` is clamped to `0..30`, otherwise ordinary delay applies. Every send retains its existing per-send timeout.
- `UnauthorizedRecoveryPolicy` handles only a classified 401 on an authenticated GET/HEAD initial attempt. It uses the exact observed token with `refresh_if_current`, performs at most one refresh and one replay, never refreshes during replay, and passes unauthenticated 401 unchanged. A changed token skips refresh and replays current state; cleared storage does no fetch/refresh. `CancelledError` is immediately propagated and refresh failure does not overwrite existing storage.
- Initial request and replay each enter `TransientRetryPolicy` with independent three-send budgets. POST/PUT/PATCH/DELETE never retry or replay.

## File and Test Contract

The exact Written/Modify/ReadOnly/Deleted paths in `requirements.md` are binding. Projects, Models, and Job Execution constructors retain their existing call shape but type their requester dependency as `RequestExecutor`. Tests must prove raw/decorated substitutability, policy ordering, 401 and retry scenarios, pipeline rejection, classifier behavior, token raw-route bypass, and unchanged endpoint request shapes.

## Validation and Risk Boundary

Run focused WSL tests, Ruff format check, Ruff check, Pyright, Tach, and full pytest. Tach must prove the exact `mlops_async.resilience -> mlops_async.core` projection and no broader relaxations. PR #68 remains Draft through rework, independent plan review, implementation review, and code review; human review is the next automatic stop after the updated Draft PR. Do not represent the known linked-worktree Git guard exception as a green full suite.
