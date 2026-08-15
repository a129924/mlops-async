# Resilient Request Execution Plan — DI Policy Rework

Analysis-layer routing: strict mode. The explicit human override replaces the previous fixed-decorator analysis. `analysis/resilient-request-execution/technical-spec.md` is the execution source of truth and `requirements.md` is the business-intent guardrail.

## Goal / Outcome

### Goal

Replace PR #68's fixed private `Requester` decorator with an explicit DI policy pipeline. Raw `Requester` remains usable as before; endpoint clients may receive a decorated `RequestExecutor` composed from independently injectable policies.

The repository-visible result is a stable non-root `core.request_execution` contract and `resilience` submodule surface, with PR #68 staying Draft until independent review and then stopping at human review.

## Scope

### In scope

- Stable non-root request-execution and resilience policy/pipeline contracts.
- Raw requester refactor, injected failure classification, constrained retry/recovery policies, affected endpoint annotations, transport metadata preservation, focused tests, `tach.toml`, and architecture/auth-boundary documentation.

### Out of scope / Non-goals

- Will not retry or replay `POST`, `PUT`, `PATCH`, or `DELETE`.
- Will not wrap the raw `TokenEndpointClient.request_json` route.
- Will not add a package-root export, aggregate facade, DI container, persistent token storage, constructor/runtime request-shape change, live Viya E2E, release, merge, or cleanup.
- Will not change `README.md`, `VERSION`, `pyproject.toml`, `uv.lock`, or release notes.

### Current Context

PR #68 currently contains an internal `_RequesterResilienceDecorator` and `Client.failure_for` coupling. The human rejected that architecture. Projects, Models, and Job Execution currently accept concrete `Requester` annotations; only their annotation becomes `RequestExecutor`, never their runtime constructor or outgoing request shape.

### Requirements

1. Add stable contracts in `core/request_execution.py`: async `RequestExecutor.request` with today's keyword shape, frozen `RequestInvocation`, frozen `AuthRecoveryAttempt`, `AuthRecoveryExecutor`, and injected `RequestFailureClassifier`.
2. Add `resilience` as an ordered outer decorator: supplied policies are left-to-right outermost-to-innermost; canonical order is Unauthorized outer, Transient inner.
3. Keep `Requester` raw-only: auth/header composition, one raw send, attempt-local observed token capture, and conditional refresh/replay capability; no installed policy or mutable last-token state.
4. Preserve single-send transport and exception identity/message/context/properties. Remove `Client.failure_for`; default transport classification is injected from `resilience`.
5. Use literal GET/HEAD `match/case`; retry only classified connection, timeout, 429, 502, 503, or 504 under locked budgets, delays, `Retry-After`, per-send timeout, and cancellation behavior.
6. Recover only classified authenticated GET/HEAD initial 401: at most one conditional refresh and one replay; replay enters the complete inner chain with an independent transient-retry budget.
7. Reject non-policies, repeated built-ins, and recovery policies without required capability. Keep token endpoint raw.

## Locked Decisions

### Decisions

- Async-planning status: triggered -- cite trigger evidence: this plan introduces async request retries, `asyncio.CancelledError` propagation, per-send timeout preservation, conditional token refresh, and concurrent 401 coordination.
- Module/package placement: stable contracts live only in `src/mlops_async/core/request_execution.py`; `resilience/classifier.py` owns `TransportRequestFailureClassifier`, `resilience/executor.py` owns `PolicyRequestExecutor`, `resilience/policies.py` owns `RequestPolicy`, `UnauthorizedRecoveryPolicy`, and `TransientRetryPolicy`, and `resilience/__init__.py` owns stable submodule exports.
- Public API: yes, stable non-root submodule APIs only. `mlops_async` package-root re-export is forbidden.
- Interface changes: endpoint annotations become `RequestExecutor`; public constructors, methods, values, and request shapes remain unchanged.
- Breaking changes: none. The rejected fixed decorator was private and raw `Requester` behavior remains raw.
- New dependencies: none.
- Error handling: `RequestFailureClassifier.classify` decides policy eligibility from preserved metadata; nonclassified/noneligible errors and `asyncio.CancelledError` propagate unchanged; invalid pipelines fail before I/O.
- Typing: fully typed Protocols and frozen dataclasses under existing strict Pyright conventions; no `Any` or shared mutable token handoff.
- `tach.toml` receives exactly `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`. This is a single one-way architecture projection, not a global relax/suppression, wildcard, reverse dependency, or transport exception.
- Current classifier/executor code in `resilience/policies.py` alone is implementation drift. It must be split into the locked `classifier.py` and `executor.py` files; the plan must not follow the drift.
- Stable-library promotion is explicitly deferred: no package-root export, README row, VERSION bump, release note, or release action in this topic.

#### Async boundary decision

`Requester.request` remains the raw async composition/send boundary. `PolicyRequestExecutor.request` is the only async decorator entry point; policies await downstream execution and create no background tasks or synchronous wrappers.

#### Resource lifecycle decision

Requester and HttpClient retain transport/session ownership and close behavior. Policies own no session/resource and never close the wrapped executor.

#### Concurrency model

Each invocation is sequential within its policy chain. Concurrent 401 callers coordinate only through `TokenManager.refresh_if_current`; each attempt carries its exact observed token without cross-request mutable state.

#### Failure model

The default classifier reads metadata without wrapping exceptions. Transient handles only locked temporary failures. Unauthorized handles one eligible initial 401; unauthenticated, changed/cleared-token, replay-401, unclassified, and noneligible outcomes follow the frozen propagation contract.

#### Cancellation / timeout policy

Each send preserves supplied request options and per-send timeout. `asyncio.CancelledError` from send, sleep, or refresh raises immediately and is never retried or translated. Refresh failures preserve storage.

#### Validation plan

Use deterministic tests for pipeline ordering/capability validation, retry/recovery budgets, concurrent refresh, token changes, cancellation, timeout, and raw-token bypass. Run WSL Ruff format, Ruff, Pyright, Tach, focused pytest, and full pytest. A linked-worktree Git guard failure remains an accurately disclosed environment exception.

#### Handoff notes for the implementer

Do not reintroduce an internal default decorator, `Client.failure_for`, shared mutable token state, membership/string eligibility, mutation retry/replay, token endpoint wrapping, root exports, or release work.

## Boundaries / Exclusions

- Creator works only in Artifact Paths. Any new path, root export, mutation policy, Tach relaxation, or semantic expansion is plan drift and returns to Main Agent routing.
- Planning actor owns plan artifacts; independent reviewers own verdicts; Main Agent owns worktree, PR update, publication, and human-boundary routing.
- Endpoint-family behavior is request-contract shape evidence only. Mock results are not live Viya runtime proof.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: existing Draft PR #68 receives a new creator pass after plan approval; after implementation it requires independent implementation review and code review before Draft PR update, then stops for human review.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes: Standard Phase 4.5 applies; every rework checklist item must be `[X]` before implementation review. `merged` -> `released` is intentionally absent.

## Artifact Paths

| Disposition | Exact path | Owner | Role |
| --- | --- | --- | --- |
| Modify | `analysis/resilient-request-execution/requirements.md` | Planning actor | Business boundary |
| Modify | `analysis/resilient-request-execution/technical-spec.md` | Planning actor | Frozen DI execution contract |
| Modify | `plan/resilient-request-execution/resilient-request-execution.plan.md` | Planning actor | Topic workflow and Python-plan contract |
| Modify | `plan/resilient-request-execution/resilient-request-execution.spec.md` | Planning actor | Acceptance specification |
| Modify | `plan/resilient-request-execution/resilient-request-execution.step.md` | Planning actor | Reset rework checklist |
| Written | `plan/resilient-request-execution/resilient-request-execution.python.plan.md` | Plan-Creator | Python-plan-review companion contract mirroring this topic's locked DI/Tach decisions and eight implementation steps |
| Written | `src/mlops_async/core/request_execution.py` | Creator | Stable request/recovery contracts |
| Written | `src/mlops_async/resilience/__init__.py` | Creator | Stable non-root resilience exports |
| Written | `src/mlops_async/resilience/classifier.py` | Creator | Transport-backed classifier |
| Written | `src/mlops_async/resilience/executor.py` | Creator | Ordered policy decorator |
| Written | `src/mlops_async/resilience/policies.py` | Creator | Policy Protocol and built-ins only |
| Modify | `src/mlops_async/core/requester.py` | Creator | Raw requester and recovery capability |
| Modify | `src/mlops_async/core/client.py` | Creator | Remove classifier coupling |
| Modify | `src/mlops_async/core/request_failure.py` | Creator | Immutable failure carrier |
| Modify | `src/mlops_async/core/auth.py` | Creator | Conditional refresh coordination |
| Modify | `src/mlops_async/transport/exceptions.py` | Creator | Metadata preservation |
| Modify | `src/mlops_async/transport/http_client.py` | Creator | Single-send metadata source |
| Modify | `src/mlops_async/clients/projects/client.py` | Creator | `RequestExecutor` annotation only |
| Modify | `src/mlops_async/clients/models/client.py` | Creator | `RequestExecutor` annotation only |
| Modify | `src/mlops_async/clients/job_execution/client.py` | Creator | `RequestExecutor` annotation only |
| Modify | `tests/unit/core/test_request_failure.py` | Creator | Carrier/classifier tests |
| Modify | `tests/unit/core/test_request_resilience.py` | Creator | Pipeline/policy tests |
| Modify | `tests/unit/core/test_client_contract.py` | Creator | Removed client classifier coupling |
| Modify | `tests/unit/core/test_requester_auth_boundary.py` | Creator | Raw requester/recovery tests |
| Modify | `tests/unit/core/test_token_manager.py` | Creator | Conditional refresh tests |
| Modify | `tests/unit/transport/test_exceptions.py` | Creator | Exception preservation tests |
| Modify | `tests/unit/transport/test_http_client.py` | Creator | Single-send tests |
| Modify | `tests/unit/clients/projects/test_client.py` | Creator | Projects raw/decorated request shape |
| Modify | `tests/unit/clients/models/test_client.py` | Creator | Models raw/decorated request shape |
| Modify | `tests/unit/clients/job_execution/test_job_execution_client.py` | Creator | Job Execution raw/decorated request shape |
| Modify | `docs/ARCHITECTURE.md` | Creator | DI boundary documentation |
| Modify | `docs/standards/http-client-auth-boundary.md` | Creator | Policy/raw-token standard |
| Modify | `tach.toml` | Creator | Exact resilience-to-core projection |
| ReadOnly | `src/mlops_async/__init__.py` | Creator | No package-root re-export |
| ReadOnly | `src/mlops_async/core/token_endpoint_client.py` | Creator | Raw token route bypasses policies unchanged |
| ReadOnly | `README.md` | Creator | No stable-library row change |
| ReadOnly | `VERSION` | Creator | No version change |
| ReadOnly | `pyproject.toml` | Creator | No dependency/metadata change |
| ReadOnly | `uv.lock` | Creator | No lockfile change |
| ReadOnly | `.github/agents/*` | Creator | Frozen governance provenance |
| Deleted | None | Creator | No path deletion authorized |

## Stable library metadata

- `README action`: no change.
- `VERSION bump`: no bump.
- `timing`: promotion/release deferred.
- `rationale`: controlled non-root DI API adoption with root compatibility preserved.
- `release notes`: none.

## Implementation Steps

1. In `src/mlops_async/core/request_execution.py`, define fully typed stable non-root `RequestExecutor`, frozen `RequestInvocation`, frozen `AuthRecoveryAttempt`, `AuthRecoveryExecutor`, and `RequestFailureClassifier` while preserving the current request keyword shape and `RawClientResponse` result.
2. In `src/mlops_async/core/requester.py`, remove the fixed decorator/context and internal resilience construction; implement raw auth/header composition and attempt-local recovery operations. In `src/mlops_async/core/client.py`, remove `Client.failure_for`; retain `request_failure.py` only as immutable carrier.
3. In `src/mlops_async/resilience/classifier.py`, implement `TransportRequestFailureClassifier`; in `executor.py`, implement ordered `PolicyRequestExecutor` plus recovery-capability preservation; in `policies.py`, implement only `RequestPolicy`, `UnauthorizedRecoveryPolicy`, and `TransientRetryPolicy`; in `__init__.py`, export only the locked stable submodule symbols.
4. In `src/mlops_async/resilience/policies.py`, implement literal GET/HEAD `match/case`, locked transient eligibility/delay/budget/cancellation, and one-initial-401 conditional refresh/replay that re-enters the inner policy chain without a second refresh.
5. In `src/mlops_async/core/auth.py`, `src/mlops_async/transport/exceptions.py`, and `src/mlops_async/transport/http_client.py`, retain conditional refresh, failure metadata, identity/message/context/properties, and single-send behavior; in the Projects, Models, and Job Execution client modules, replace only concrete requester annotations with `RequestExecutor`, leaving constructors, endpoint methods, values, and outgoing requests unchanged. In requester/auth-boundary tests, prove the read-only `src/mlops_async/core/token_endpoint_client.py` raw route bypasses every policy unchanged.
6. In every test path in Artifact Paths, replace fixed-decorator cases with pipeline/custom-policy/classifier/retry/recovery/token/cancellation/bypass/request-shape coverage; prove raw and decorated executors are substitutable.
7. In `tach.toml`, add exactly `[[modules]] path="mlops_async.resilience" depends_on=["mlops_async.core"]`; add no global relaxations, suppressions, wildcards, reverse dependencies, or transport exceptions.
8. In `docs/ARCHITECTURE.md` and `docs/standards/http-client-auth-boundary.md`, document manual composition, stable non-root API, raw requester responsibility, raw token endpoint bypass, canonical ordering, and mutation exclusion.

## Validation / Acceptance Checks

### Public Contract / API Changes

`core.request_execution` exports `RequestExecutor`, `RequestInvocation`, `AuthRecoveryExecutor`, `AuthRecoveryAttempt`, and `RequestFailureClassifier`; `resilience` exports `RequestPolicy`, `PolicyRequestExecutor`, `UnauthorizedRecoveryPolicy`, `TransientRetryPolicy`, and `TransportRequestFailureClassifier`. No symbol is re-exported at package root. Endpoint runtime contracts do not change.

### Test Plan

- **Happy path**: raw requester, custom policy, and canonical Unauthorized-outer/Transient-inner pipeline succeed; replay re-enters the inner transient chain.
- **Invalid input**: non-policy, repeated built-in, and missing recovery capability fail at construction; invalid `Retry-After` uses ordinary jitter.
- **Edge case**: GET/HEAD `match/case`, POST default/no replay, classifier `None`, Retry-After clamp/date parsing, changed/cleared tokens, independent budgets, timeout, and cancellation are deterministic.
- **Regression**: transport tests preserve exception identity/message/context/properties and single-send behavior while `Client.failure_for` is absent.
- **Backward compatibility**: Projects, Models, and Job Execution accept raw/decorated executors with identical request shape; raw token endpoint bypasses policies.

### Validation Commands

```powershell
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest tests/unit/core/test_request_failure.py tests/unit/core/test_request_resilience.py tests/unit/core/test_client_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_manager.py tests/unit/transport/test_exceptions.py tests/unit/transport/test_http_client.py tests/unit/clients/projects/test_client.py tests/unit/clients/models/test_client.py tests/unit/clients/job_execution/test_job_execution_client.py'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff format --check src tests'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff check src tests'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pyright'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync tach check'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest'
```

Tach must prove only the declared `mlops_async.resilience -> mlops_async.core` dependency. Full pytest may report the known linked-worktree Git guard failure; disclose that as an environment exception, not a pass.

### Risks

- Incorrect policy composition could bypass inner retry on replay or expose unsupported recovery capability.
- Moving classifier ownership could alter exception observability or cause an additional transport send.
- Shared token state could cause refresh storms or stale replay; a broad Tach exemption could hide dependency drift.

### Rollback Plan

Before publishing, revert only listed DI implementation paths to restore the parent commit's raw requester behavior. Do not add root exports, version changes, or endpoint API changes. If review finds drift later, make a bounded correction to the same Draft PR #68 rather than merge or release.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

None. Merge, stable promotion, release, tagging, versioning, and cleanup require separate explicit authorization.

## Open Questions / Unresolved Items

None. No unresolved item blocks implementation; mutation retry/replay and stable-library promotion require a separate topic and explicit human authorization.
