# Resilient Request Execution — Python Implementation Companion Plan

This companion is subordinate to `resilient-request-execution.plan.md`. It mirrors the approved DI/Tach contract and the existing eight-step tracker; it introduces no new design decision.

## Goal

Replace PR #68's private fixed requester decorator with an explicit, externally composed DI policy pipeline while preserving raw `Requester` and all endpoint runtime request contracts.

## Non-goals

- Do not retry or replay `POST`, `PUT`, `PATCH`, or `DELETE`.
- Do not wrap `TokenEndpointClient.request_json` or alter its raw transport route.
- Do not add package-root exports, facades, DI containers, persistent storage, external dependencies, release work, merge, or cleanup.
- Do not change endpoint constructors, methods, value objects, outgoing request shape, README, VERSION, package metadata, or lockfile.

## Current Context

PR #68 currently has a private `_RequesterResilienceDecorator` and `Client.failure_for` coupling. The approved replacement is raw-only `Requester`, stable non-root `core.request_execution` contracts, and a caller-supplied `resilience` pipeline. The existing tracker at `resilient-request-execution.step.md` contains the authoritative eight pending rework steps.

## Requirements

1. `RequestExecutor.request` retains the current asynchronous keyword request shape and `RawClientResponse` result; policies use immutable `RequestInvocation` and attempt-local `AuthRecoveryAttempt`.
2. `PolicyRequestExecutor` composes supplied policies left-to-right, outermost-to-innermost; canonical order is Unauthorized outer and Transient inner.
3. `Requester` stays raw-only and exposes recovery capability without mutable last-token state; `Client.failure_for` is removed and failure classification is injected.
4. Retry/recovery uses literal GET/HEAD `match/case`, the locked temporary failures, three-send budgets per initial/replay path, delay/Retry-After rules, per-send timeout, and immediate cancellation propagation.
5. A classified authenticated initial 401 gets at most one conditional refresh and one replay through the full inner chain; token endpoint remains raw.
6. `tach.toml` has only `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`; classifier/executor code must be split from current all-in-`policies.py` drift into locked files.

## Decisions

- Async-planning status: triggered -- cite trigger evidence: the frozen contract introduces async request retries, `asyncio.CancelledError` propagation, per-send timeout preservation, conditional token refresh, and concurrent 401 coordination.
- Module/package placement: `src/mlops_async/core/request_execution.py` owns contracts; `src/mlops_async/resilience/classifier.py` owns classifier, `executor.py` owns decorator, `policies.py` owns policy types, and `__init__.py` owns only stable submodule exports.
- Public API: yes, stable non-root submodule APIs only; package-root re-export is explicitly forbidden.
- Interface changes: endpoint annotations change to `RequestExecutor`; public constructors/methods/request shapes remain unchanged.
- Breaking changes allowed: no; rejected private internals are replaced while raw requester behavior remains compatible.
- New dependencies: no.
- Error-handling strategy: injected classifier reads preserved transport metadata; nonclassified/noneligible errors and cancellation propagate unchanged; invalid policy pipelines fail before I/O.
- Typing strategy: fully typed Protocols/frozen dataclasses using strict Pyright conventions; no `Any` or shared mutable token handoff.

### Async boundary decision

`Requester.request` remains raw async composition/send. `PolicyRequestExecutor.request` is the only async decorator entry; policies await downstream calls and create no background tasks or synchronous wrappers.

### Resource lifecycle decision

Requester and HttpClient retain existing session ownership and close behavior. Policies own no network resource and never close wrapped executors.

### Concurrency model

Each invocation is sequential within its pipeline. Concurrent 401 callers coordinate only through `TokenManager.refresh_if_current`; attempt values carry exact observed token without cross-request mutable state.

### Failure model

`TransportRequestFailureClassifier` classifies preserved metadata without wrapping errors. Transient handles only locked temporary failures; Unauthorized handles one eligible initial 401 and passes all other outcomes per the contract.

### Cancellation / timeout policy

Every send preserves supplied options and per-send timeout. `asyncio.CancelledError` from send, sleep, or refresh propagates immediately; it is neither retried nor translated and refresh failures preserve storage.

### Validation plan

Run deterministic policy/token/transport/endpoint tests, WSL Ruff format check, Ruff, Pyright, Tach, focused pytest, and full pytest. The known linked-worktree Git guard result is disclosed as an environment exception, not a successful full suite.

### Handoff notes for the implementer

Implement only the eight steps below. Do not restore an internal default decorator or `Client.failure_for`; do not broaden eligibility, wrap token endpoints, add root exports, or relax Tach beyond the exact projection.

## Public Contract / API Changes

`mlops_async.core.request_execution` exports `RequestExecutor`, `RequestInvocation`, `AuthRecoveryExecutor`, `AuthRecoveryAttempt`, and `RequestFailureClassifier`. `mlops_async.resilience` exports `RequestPolicy`, `PolicyRequestExecutor`, `UnauthorizedRecoveryPolicy`, `TransientRetryPolicy`, and `TransportRequestFailureClassifier`. These are stable non-root surfaces only; no package-root export or endpoint runtime contract changes.

## Affected Files / Modules

Likely affected files:

- `src/mlops_async/core/request_execution.py`, `requester.py`, `client.py`, `request_failure.py`, `auth.py`
- `src/mlops_async/resilience/__init__.py`, `classifier.py`, `executor.py`, `policies.py`
- `src/mlops_async/transport/exceptions.py`, `http_client.py`, and `tach.toml`
- affected Projects/Models/Job Execution clients, focused core/transport tests, endpoint request-shape tests, and the two architecture documents exactly listed in the canonical plan Artifact Paths.

Candidate files to inspect:

- `src/mlops_async/core/token_endpoint_client.py` (read-only raw bypass contract)
- `plan/resilient-request-execution/resilient-request-execution.spec.md`
- `plan/resilient-request-execution/resilient-request-execution.step.md`

## Implementation Steps

1. In `src/mlops_async/core/request_execution.py`, define fully typed `RequestExecutor`, frozen `RequestInvocation`, frozen `AuthRecoveryAttempt`, `AuthRecoveryExecutor`, and `RequestFailureClassifier`, preserving `Requester.request` call shape and `RawClientResponse`.
2. In `src/mlops_async/core/requester.py`, remove fixed decorator/context/internal policy construction and implement raw auth/header composition plus attempt-local recovery; in `core/client.py`, remove `Client.failure_for` while retaining `request_failure.py` as immutable carrier.
3. Add `resilience/__init__.py`, `classifier.py`, `executor.py`, and `policies.py` with locked ownership: classifier, decorator, and policy types respectively; repair all-in-`policies.py` drift rather than changing placement.
4. In `resilience/policies.py`, implement locked GET/HEAD `match/case`, transient retry/budget/delay/Retry-After/cancellation, and one-initial-401 conditional refresh/replay entering the inner chain without second refresh.
5. In `core/auth.py`, `transport/exceptions.py`, and `transport/http_client.py`, retain conditional refresh, metadata, exception observability, and single-send behavior; update Projects/Models/Job Execution annotations to `RequestExecutor` without runtime changes; prove read-only raw token route bypass in auth-boundary tests.
6. In all focused core/transport and endpoint test files listed by the canonical Artifact Paths, replace fixed-decorator cases with pipeline/custom-policy/classifier/retry/recovery/token/cancellation/bypass/request-shape coverage proving raw/decorated substitutability.
7. In `tach.toml`, add only `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`; do not add global relaxations, suppressions, wildcards, reverse dependencies, or transport exceptions.
8. In `docs/ARCHITECTURE.md` and `docs/standards/http-client-auth-boundary.md`, document manual DI composition, non-root API, raw requester/token behavior, canonical policy ordering, and mutation exclusion.

## Test Plan

- **Happy path**: `tests/unit/core/test_request_resilience.py` proves raw, custom-policy, and canonical pipeline success, including replay re-entry into Transient.
- **Invalid input**: policy tests reject non-policy values, repeated built-ins, and missing recovery capability before I/O; invalid Retry-After falls back to jitter.
- **Edge case**: focused tests cover GET/HEAD match/case, POST no retry/replay, classifier `None`, Retry-After clamp/date, token changed/cleared, independent budgets, timeouts, and cancellation.
- **Regression**: core/transport tests prove removed `Client.failure_for`, preserved exception identity/message/context/properties, and one-send behavior.
- **Backward compatibility**: endpoint family tests construct clients with raw/decorated executors and assert unchanged request shape; token endpoint bypass remains raw.

## Validation Commands

```powershell
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest tests/unit/core/test_request_failure.py tests/unit/core/test_request_resilience.py tests/unit/core/test_client_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_manager.py tests/unit/transport/test_exceptions.py tests/unit/transport/test_http_client.py tests/unit/clients/projects/test_client.py tests/unit/clients/models/test_client.py tests/unit/clients/job_execution/test_job_execution_client.py'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff format --check src tests'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff check src tests'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pyright'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync tach check'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest'
```

## Risks

- Incorrect wrapper composition could bypass inner retry during replay or expose unsupported recovery capability.
- Classifier relocation could alter observability or issue an extra transport send.
- Shared token state or broad Tach exception could permit refresh storms, stale replay, or dependency-direction drift.

## Rollback Plan

Before publishing, revert only the implementation files named in the canonical plan Artifact Paths to restore the parent raw requester behavior. Do not add root exports, version changes, or endpoint API changes. Make bounded corrections on Draft PR #68 rather than merge/release if review finds drift.

## Open Questions

None. All implementation decisions are locked; mutation retry/replay and stable-library promotion require a separate explicitly authorized topic.
