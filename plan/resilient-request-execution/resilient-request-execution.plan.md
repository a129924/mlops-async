# Resilient Request Execution Plan

Analysis-layer routing: strict mode. `analysis/resilient-request-execution/technical-spec.md` is the execution-facing source of truth and `analysis/resilient-request-execution/requirements.md` is the business-intent guardrail. Both were authored from the explicit human-approved chat contract, not inferred live Viya evidence.

## Goal / Outcome

Requester-boundary authenticated `GET`/`HEAD` requests gain bounded retry, a single conditional 401 refresh, and one replay while public API and existing exception contracts remain unchanged.

## Scope

- **In-Scope**:
  - Internal core request-failure carrier and transport-to-core metadata boundary.
  - Private `Requester` resilience decorator state machine for the canonical primitive request path.
  - `TokenManager.refresh_if_current` coordination for initial 401 only.
  - Exact source, test, and documentation paths listed in Artifact Paths.

- **Out-Of-Scope**:
  - Retry/replay for methods other than `GET`/`HEAD`, including `POST`.
  - Token endpoint retry or wrapping raw `TokenEndpointClient.request_json`.
  - Public API, facade, DI, background work, live E2E, README, VERSION, package metadata, lockfile, release, commit, push, or PR work.

## Locked Decisions

- This is review-ready-only with no stable-library surfaces and no release action.
- Add non-exported `src/mlops_async/core/request_failure.py` with immutable `ResponseFailureMetadata(status_code, retry_after)` and `RequestFailure(kind: connection|timeout|response)`; core imports neither transport nor `httpx`.
- `Client.failure_for(exception) -> RequestFailure | None` is internal. `HttpClient` stays single-send and preserves original exception identity, message, context, and properties while adding failure metadata.
- `_RequesterResilienceDecorator` is private and handles only primitive/canonical requests. `TokenEndpointClient.request_json` bypasses it.
- Eligibility must use Python `match`/`case`: `case HttpMethod.GET | HttpMethod.HEAD` is eligible and `case _` is noneligible. Membership and string checks are prohibited.
- Eligible failures are connection, timeout, and `429`, `502`, `503`, `504`. Initial and replay paths each allow three sends including the first. Delay is jittered exponential from base `0.25`, capped at `2`; `Retry-After` accepts delta or HTTP-date, clamps to `0..30`, and invalid data falls back to ordinary delay.
- Initial 401 may invoke exactly one existing-lock `refresh_if_current`; changed storage token skips refresh and replays current state; cleared storage does not fetch/refresh. Refresh failure and cancellation preserve storage. Replay has one independent three-send budget and never refreshes again. Each send retains per-send timeout.
- Runtime-evidence boundary: no `POST` replay without endpoint runtime proof and separate explicit approval.

## Boundaries / Exclusions

- Creator implements only the contracted paths; any new path or behavior is plan drift and must return to Main Agent routing.
- Reviewer independently evaluates contract conformance; reviewer verdict JSON is not creator work.
- Main Agent owns worktree, implementation routing, review/publish/PR orchestration, and any later release decision.
- No stable-library metadata section is included because this topic neither changes nor defers README, VERSION, release notes, or release timing.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: canonical creator -> reviewer path; this topic stops at review-ready and has no release action.
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

Routing notes:

- Standard Phase 4.5 applies: only after all creator implementation steps are checked may status move to `review-ready`.
- `merged` -> `released` is intentionally absent. No round cap is declared.

## Artifact Paths

| Disposition | Path | Owner | Role |
| --- | --- | --- | --- |
| Written | `analysis/resilient-request-execution/requirements.md` | Planning actor | Business-intent guardrail authored from approved chat contract |
| Written | `analysis/resilient-request-execution/technical-spec.md` | Planning actor | Execution-facing locked technical contract |
| Written | `plan/resilient-request-execution/resilient-request-execution.plan.md` | Planning actor | Repo-visible execution contract |
| Written | `plan/resilient-request-execution/resilient-request-execution.spec.md` | Planning actor | Create during plan-authoring: non-trivial Python acceptance specification |
| Written | `plan/resilient-request-execution/resilient-request-execution.step.md` | Planning actor / creator | Required implementation checklist |
| Written | `src/mlops_async/core/request_failure.py` | Creator | Non-exported core failure carrier |
| Written | `tests/unit/core/test_request_failure.py` | Creator | Failure-carrier contract tests |
| Written | `tests/unit/core/test_request_resilience.py` | Creator | State-machine resilience tests |
| Modify | `src/mlops_async/core/client.py` | Creator | Internal failure classification |
| Modify | `src/mlops_async/core/auth.py` | Creator | Existing-lock `refresh_if_current` behavior |
| Modify | `src/mlops_async/core/requester.py` | Creator | Private resilience decorator and canonical-path composition |
| Modify | `src/mlops_async/transport/exceptions.py` | Creator | Metadata-capable transport exception boundary |
| Modify | `src/mlops_async/transport/http_client.py` | Creator | Single-send metadata attachment with exception preservation |
| Modify | `tests/unit/core/test_client_contract.py` | Creator | Client failure-classification assertions |
| Modify | `tests/unit/core/test_requester_auth_boundary.py` | Creator | 401, bypass, replay, cancellation, and auth-boundary assertions |
| Modify | `tests/unit/core/test_token_manager.py` | Creator | Concurrent refresh/storage assertions |
| Modify | `tests/unit/transport/test_exceptions.py` | Creator | Exception metadata/preservation assertions |
| Modify | `tests/unit/transport/test_http_client.py` | Creator | Transport single-send metadata assertions |
| Modify | `docs/ARCHITECTURE.md` | Creator | Core/transport/requester boundary documentation |
| Modify | `docs/standards/http-client-auth-boundary.md` | Creator | Auth resilience and raw-token bypass standard |
| ReadOnly | public family constructors and exports | Creator | No public-surface change |
| ReadOnly | raw `TokenEndpointClient.request_json` route | Creator | Explicit decorator bypass |
| ReadOnly | `README.md` | Creator | No stable-library documentation change |
| ReadOnly | `VERSION` | Creator | No version change |
| ReadOnly | `pyproject.toml` | Creator | No package metadata change |
| ReadOnly | `uv.lock` | Creator | No dependency/lockfile change |
| ReadOnly | `.github/agents/*` | Creator | Frozen provenance; not a runtime dependency |
| Deleted | None | Creator | No deletion is authorized |

If implementation needs a path or behavior not listed above, stop and return it as plan-alignment drift; do not silently expand scope.

## Implementation Steps

1. Add the private immutable failure carrier in core and the internal `Client.failure_for` classification boundary without importing transport or `httpx` from core.
2. Preserve `HttpClient` single-send behavior while attaching response/transport failure metadata and retaining every existing exception identity and observable context property.
3. Add `TokenManager.refresh_if_current` behavior required for same-token coordination, changed-token skip, cleared-storage no-fetch, refresh-failure preservation, and cancellation preservation.
4. Compose private `_RequesterResilienceDecorator` around the primitive/canonical request path; implement exact match/case method eligibility, eligible failure classification, send budgets, jitter, `Retry-After`, and per-send timeout.
5. Implement initial-only 401 conditional refresh and exactly one replay with an independent budget and no secondary refresh; keep raw `TokenEndpointClient.request_json` bypassed.
6. Add the specified focused unit tests, including GET/HEAD/POST branches, retry timing/classification/budget, concurrent 401 scenarios, cancellation, bypass, and transport exception preservation.
7. Update architecture and auth-boundary documentation to describe the private boundary, limits, bypass, and runtime-evidence restriction.

## Validation / Acceptance Checks

- Failure carrier is internal, immutable, and core has no transport/`httpx` import.
- Public APIs, exports, constructors, raw token route, and existing exception contract remain unchanged.
- Exact `match`/`case` branches cover `GET`, `HEAD`, and noneligible `POST`; no membership or string comparison implements eligibility.
- Only connection, timeout, `429`, `502`, `503`, and `504` retry; each initial/replay sequence has at most three sends, uses the locked delay rules, and retains per-send timeout.
- 401 tests prove one initial conditional refresh, changed-token current replay, cleared storage no fetch, one replay, no second refresh, and storage preservation on refresh failure/cancellation.
- Raw `TokenEndpointClient.request_json` bypass and transport exception identity/message/context/properties are proven by tests.
- Run through WSL: Ruff format check, Ruff check, Pyright, Tach, and full pytest excluding live E2E; live E2E is not run.

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

None. This review-ready-only topic declares no stable-library metadata, release action, version change, tag, or cleanup action.

## Open Questions / Unresolved Items

None. The approved contract intentionally forbids expanding retry/replay to `POST` or other non-eligible methods without separate endpoint runtime proof and explicit approval.

## Goal

在不改變任何 public API 或既有例外可觀察契約的前提下，為 authenticated canonical `Requester` 的 `GET`/`HEAD` request 提供有界暫時性失敗重試、一次條件式 401 token refresh 與一次 replay。

## Non-goals

- 不為 `POST`、`PUT`、`PATCH` 或 `DELETE` 加入 retry 或 replay。
- 不對 token endpoint 或 raw `TokenEndpointClient.request_json` 套用 decorator、retry 或 refresh。
- 不新增或變更 public export、facade、constructor、DI contract 或 release surface。
- 不執行 live Viya E2E、發布、版本調整、commit、push 或 PR 操作。

## Current Context

`src/mlops_async/core/requester.py` 是 domain request 的 primitive/canonical request path；`src/mlops_async/transport/http_client.py` 必須保持 single-send transport boundary。`src/mlops_async/core/auth.py` 已持有 token lifecycle 與 lock coordination，而本 topic 的 `analysis/resilient-request-execution/technical-spec.md` 已凍結 failure carrier、retry、401 refresh/replay 與 raw-token bypass 契約。

## Requirements

1. 在 `src/mlops_async/core/request_failure.py` 建立 non-exported、immutable 的 `ResponseFailureMetadata(status_code, retry_after)` 與 `RequestFailure(kind)`；core 不可 import transport 或 `httpx`，而 `Client.failure_for(exception) -> RequestFailure | None` 是 internal classification boundary。
2. `HttpClient` 每次呼叫仍只 send 一次，並在不改變原 exception identity、message、context 或 properties 的條件下附加 failure metadata，供 core classification 使用。
3. method eligibility 必須以 Python `match`/`case` 實作：`case HttpMethod.GET | HttpMethod.HEAD` 是 eligible，`case _` 是 default noneligible；不得以 membership 或 string comparison 取代。
4. 只有 eligible request 的 connection、timeout、`429`、`502`、`503`、`504` 可 retry；initial path 與 replay path 各自最多三次 send（含第一次），使用 base `0.25`、cap `2` 的 jittered exponential delay；`Retry-After` 接受 delta 或 HTTP-date、clamp 為 `0..30`，無效值退回一般 delay。
5. initial `401` 只可進行一次既有 lock 的 `TokenManager.refresh_if_current`：storage token 已變更時跳過 refresh 並用 current state replay；storage 已清除時不得 fetch/refresh；refresh failure 或 cancellation 必須保留 storage；replay 有獨立三-send budget 且絕不第二次 refresh。
6. 每一次 send 皆保有 per-send timeout 並立即傳播 cancellation；raw `TokenEndpointClient.request_json` 必須繞過 `_RequesterResilienceDecorator`。
7. 測試須證明 failure carrier、GET/HEAD/default method branch、recovery/budget/delay、401 concurrent refresh/replay、raw bypass、cancellation，以及既有 public/exception compatibility。

## Decisions

- Async-planning status: triggered -- cite trigger evidence: `analysis/resilient-request-execution/technical-spec.md` locks retry/replay around async request I/O, per-send timeout, `asyncio.CancelledError` preservation, and existing-lock concurrent 401 refresh coordination.
- Module/package placement: add `src/mlops_async/core/request_failure.py`; extend only the listed core, transport, focused-test, and documentation paths in canonical `Artifact Paths`.
- New public API: no; `RequestFailure`, `ResponseFailureMetadata`, `Client.failure_for`, and `_RequesterResilienceDecorator` are internal/non-exported.
- Interface changes: yes, internal-only; `Client.failure_for(exception) -> RequestFailure | None` and `TokenManager.refresh_if_current` coordination support the private requester decorator while public constructors and exports remain unchanged.
- Breaking changes allowed: no; original transport exception identity, message, context, and observable properties remain compatible.
- New dependencies: no; use existing Python standard-library and project dependencies only.
- Error handling strategy: classify only connection, timeout, and response metadata listed in Requirements; retry only eligible methods; propagate noneligible/nonretryable failures and cancellation unchanged; preserve storage on refresh failure/cancellation.
- Typing strategy: fully type new internal carrier and helper boundaries using existing project typing conventions; do not introduce `Any` or public re-exports.

### Async boundary decision

The resilience state machine remains inside the async `Requester` request boundary. It awaits the existing canonical send and existing `TokenManager` refresh coordination; no synchronous wrapper, background task, or import-time I/O is introduced.

### Resource lifecycle decision

Existing composition owns `HttpClient`, requester, token manager, lock, and token storage lifecycles. The decorator owns no transport/session resource and neither creates nor closes a client; it only coordinates one request invocation and optional existing-lock refresh.

### Concurrency model

Each request executes by direct sequential await. Concurrent initial `401` callers coordinate through the existing `TokenManager` lock and `refresh_if_current`; each caller may observe changed storage and replay current state without launching another refresh. There is no fan-out, queue, worker, or background ownership.

### Failure model

`HttpClient` preserves and re-raises the same exception while metadata enables internal `Client.failure_for` classification. Only eligible temporary failures use the bounded retry policy. Initial `401` can cause one conditional refresh/replay; refresh failures, nonretryable failures, and cancellation propagate without translating the public exception contract.

### Cancellation / timeout policy

Every attempted send retains its existing per-send timeout. `asyncio.CancelledError` is immediately propagated, never retried or converted, and must preserve token storage. Retry delays and the optional refresh/replay remain within the caller task; no detached cleanup or timeout extension is allowed.

### Validation plan

Focused async unit tests will cover per-send timeout, immediate cancellation, bounded retry delay/budgets, concurrent 401 refresh coordination, refresh-failure storage preservation, and replay without second refresh. WSL quality gates will cover format, lint, typing, architecture, and non-live test suites.

### Handoff notes for the implementer

Keep `HttpClient` single-send and identity-preserving. Implement GET/HEAD eligibility literally with the locked `match`/`case` shape. Do not broaden retry/replay to `POST`, wrap raw token endpoints, add a public API, or infer endpoint runtime behavior beyond the frozen contract.

## Public Contract / API Changes

No public API changes. No public exports, client constructors, facades, method signatures, or raw-token endpoint contract change. Internal-only `RequestFailure`, `ResponseFailureMetadata`, `Client.failure_for(exception) -> RequestFailure | None`, `TokenManager.refresh_if_current` coordination, and `_RequesterResilienceDecorator` must preserve existing exception identity, message, context, properties, and cancellation behavior for callers.

## Affected Files / Modules

Likely affected files:
- `src/mlops_async/core/request_failure.py`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/transport/exceptions.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/core/test_request_failure.py`
- `tests/unit/core/test_request_resilience.py`
- `tests/unit/core/test_client_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/transport/test_http_client.py`
- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`

Candidate files to inspect:
- `analysis/resilient-request-execution/requirements.md`
- `analysis/resilient-request-execution/technical-spec.md`
- `src/mlops_async/core/request_options.py`
- `src/mlops_async/core/types.py`
- `plan/resilient-request-execution/resilient-request-execution.spec.md`

## Implementation Steps

1. In `src/mlops_async/core/request_failure.py` and `src/mlops_async/core/client.py`, add the immutable non-exported failure carrier and fully typed `Client.failure_for(exception) -> RequestFailure | None` classification without importing transport or `httpx` from core.
2. In `src/mlops_async/transport/exceptions.py` and `src/mlops_async/transport/http_client.py`, attach failure metadata while retaining `HttpClient` single-send behavior and original exception identity, message, context, and properties.
3. In `src/mlops_async/core/auth.py`, implement the locked `TokenManager.refresh_if_current` coordination for same-token refresh, changed-token skip/current replay, cleared-storage no-fetch, and refresh/cancellation storage preservation.
4. In `src/mlops_async/core/requester.py`, compose private `_RequesterResilienceDecorator` around the canonical primitive request path with literal `match`/`case` GET/HEAD eligibility, default noneligible handling, eligible failure classification, independent initial/replay three-send budgets, jitter, `Retry-After`, and per-send timeout.
5. In `src/mlops_async/core/requester.py` and the raw `TokenEndpointClient.request_json` composition route, implement initial-only conditional `401` refresh plus one replay with no secondary refresh, while preserving the raw-token decorator bypass.
6. In `tests/unit/core/test_request_failure.py`, `tests/unit/core/test_request_resilience.py`, `tests/unit/core/test_client_contract.py`, `tests/unit/core/test_requester_auth_boundary.py`, `tests/unit/core/test_token_manager.py`, `tests/unit/transport/test_exceptions.py`, and `tests/unit/transport/test_http_client.py`, add focused tests for carrier boundaries, GET/HEAD/default method branches, recovery/budgets/delay, concurrent 401, cancellation, bypass, and exception compatibility.
7. In `docs/ARCHITECTURE.md` and `docs/standards/http-client-auth-boundary.md`, document the private resilience boundary, bounded retry/replay, raw-token bypass, and the prohibition on POST retry/replay without endpoint runtime evidence and explicit approval.

## Test Plan

Test files: `tests/unit/core/test_request_failure.py`, `tests/unit/core/test_request_resilience.py`, `tests/unit/core/test_client_contract.py`, `tests/unit/core/test_requester_auth_boundary.py`, `tests/unit/core/test_token_manager.py`, `tests/unit/transport/test_exceptions.py`, and `tests/unit/transport/test_http_client.py`.

Test cases:
- Happy path: eligible `GET` and `HEAD` succeed, and initial eligible temporary failures recover within their three-send initial/replay budgets.
- Invalid input: invalid `Retry-After` values fall back to jittered delay, and failures without internal carrier classification do not receive resilience treatment.
- Edge case: exact `match`/`case` default branch keeps `POST` noneligible; delta and HTTP-date `Retry-After` values clamp to `0..30`; cleared token storage does not fetch/refresh.
- Regression: `HttpClient` remains single-send and preserves exception identity/message/context/properties; raw `TokenEndpointClient.request_json` bypasses the decorator.
- Backward compatibility: public constructors, exports, method signatures, original exception behavior, and raw token endpoint semantics remain unchanged.
- Async resilience: concurrent initial `401` callers perform at most one same-token refresh, changed-token callers replay current state, refresh failure/cancellation preserve storage, cancellation propagates immediately, and replay never refreshes twice.

## Validation Commands

```powershell
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest tests/unit/core/test_request_failure.py tests/unit/core/test_request_resilience.py tests/unit/core/test_client_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_manager.py tests/unit/transport/test_exceptions.py tests/unit/transport/test_http_client.py'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff format --check src tests'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync ruff check src tests'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pyright'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync tach check'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync pytest'
```

Live Viya E2E is excluded from this topic and must not be run by these validation commands.

## Risks

- A resilience decorator placed outside the canonical primitive path could accidentally alter raw-token behavior or duplicate transport sends.
- Incorrect `401` lock coordination could produce duplicate refreshes, stale replays, or token-storage loss under failure/cancellation.
- Changing exception wrapping rather than metadata attachment could break callers that depend on identity, context, or exception properties.
- Broadening retry/replay beyond GET/HEAD without endpoint runtime proof risks unsafe mutation duplication.

## Rollback Plan

Revert only this topic's creator paths: `src/mlops_async/core/request_failure.py`, `src/mlops_async/core/client.py`, `src/mlops_async/core/auth.py`, `src/mlops_async/core/requester.py`, `src/mlops_async/transport/exceptions.py`, `src/mlops_async/transport/http_client.py`, the seven listed focused test files, `docs/ARCHITECTURE.md`, and `docs/standards/http-client-auth-boundary.md`. Do not revert the read-only public, raw-token, release, or provenance surfaces.

## Open Questions

None. The approved contract is fully decided; retry/replay for noneligible methods requires separate endpoint runtime evidence and explicit approval.
