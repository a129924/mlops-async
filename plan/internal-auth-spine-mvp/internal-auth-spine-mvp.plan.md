Analysis-layer routing: **strict mode** — `analysis/internal-auth-spine-mvp/requirements.md` 與
`analysis/internal-auth-spine-mvp/technical-spec.md` 皆存在。本 plan 以兩者為 execution-facing
baseline，不得在 creator phase 靜默擴 scope。

## Goal / Outcome

建立 `internal-auth-spine-mvp` 的 repo-visible execution contract，讓後續 creator work
可在不擴張到 public auth UX、family endpoint implementation、或 broader endpoint registry
的前提下，補齊最小 internal auth spine。

Topic 完成時，repo 應具備：

- concrete `TokenEndpointClient`
- token collaborator-local shared endpoint spec source
- `Requester -> AuthProvider -> TokenManager -> TokenStorage + TokenEndpointClient`
  的最小可驗證 lazy auth path
- 對應 unit tests 與 topic artifacts

## Scope

- **In scope**:
  - `analysis/internal-auth-spine-mvp/requirements.md`
  - `analysis/internal-auth-spine-mvp/technical-spec.md`
  - `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.plan.md`
  - `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md`
  - `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md`
  - `src/mlops_async/core/auth.py`
  - `src/mlops_async/core/requester.py`
  - `src/mlops_async/core/token_storage.py`
  - `src/mlops_async/core/token_endpoint_client.py`
  - `src/mlops_async/transport/http_client.py`
  - `tests/unit/core/test_token_endpoint_client.py`
  - `tests/unit/core/test_token_manager.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_auth_contract.py`
  - `tests/unit/core/test_requester_auth_boundary.py`
  - 必要時 `tests/unit/transport/test_http_client.py`

- **Out of scope**:
  - `AuthClient` public UX / naming
  - `PackageLevelClient` full facade
  - `projects` / `models` / `jobs` / `tables` family implementation
  - persistent token storage
  - broader endpoint registry
  - Python 3.11 `StrEnum`
  - release / publish / merge / README / VERSION

## Locked Decisions

- token endpoint path value 固定為 `/SASLogon/oauth/token`
- runtime 不可在多處各自 hardcode 同一路徑
- shared token endpoint spec source 只供 `TokenEndpointClient` 與未來 `AuthClient` 使用
- shared token endpoint spec source 不可外溢到 `Requester`、`AuthProvider`、或 family client
- 若使用 enum，必須使用 Python 3.10 相容的 `str + Enum`
- `Requester` 只做 request composition 與 lazy auth integration，不組 token endpoint request
- `TokenManager` 保持 lifecycle owner；success-before-store、lock、exception boundary 均維持
- 本 topic 是 **review-ready-only with no stable-library surfaces**

## Boundaries / Exclusions

- creator 不可把本 topic 擴張成完整 refresh grant topic
- creator 不可把 enum/spec carrier 擴成全 repo endpoint abstraction
- reviewer 若發現 token endpoint spec scope 外溢，必須判為 blocking drift
- `docs/**` 在本 topic 僅作 read-only architecture source，不在本 topic 內修改

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; 本 topic
  不包含 release。
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

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business baseline | `analysis/internal-auth-spine-mvp/requirements.md` | Planning actor | Frozen measurable intent baseline |
| Technical baseline | `analysis/internal-auth-spine-mvp/technical-spec.md` | Technical translation actor | Execution-facing technical mapping |
| Topic plan | `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.plan.md` | Planning actor | Repo-visible execution contract |
| Topic spec | `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md` | Planning actor | Acceptance and behavior contract |
| Step tracker | `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md` | Planning actor | Completion gate mirror |
| Token collaborator | `src/mlops_async/core/token_endpoint_client.py` | Creator | Concrete token endpoint collaborator and local endpoint spec source |
| Auth lifecycle | `src/mlops_async/core/auth.py` | Creator | `AuthProvider` / `TokenManager` integration updates |
| Request composition | `src/mlops_async/core/requester.py` | Creator | Lazy auth path integration proof |
| Token state | `src/mlops_async/core/token_storage.py` | Creator | Existing token-state baseline consumed by topic |
| Token collaborator tests | `tests/unit/core/test_token_endpoint_client.py` | Creator | Obtain-path and endpoint-spec-source coverage |
| Token manager tests | `tests/unit/core/test_token_manager.py` | Creator | Reuse/fetch/expiry/lock coverage with concrete collaborator shape |
| Requester boundary tests | `tests/unit/core/test_requester_auth_boundary.py` | Creator | Lazy first-request auth integration and boundary guard |

## Implementation Steps

1. Create `analysis/internal-auth-spine-mvp/requirements.md` and freeze the MVP boundary, Python 3.10 enum constraint, and shared endpoint-spec scope.
2. Create `analysis/internal-auth-spine-mvp/technical-spec.md` mapping the business baseline to topic-local runtime work, tests, architecture checks, and rollback triggers.
3. Create `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md` and `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md` aligned to this plan.
4. Add `src/mlops_async/core/token_endpoint_client.py` with:
   - a Python 3.10-compatible token endpoint spec carrier
   - concrete `TokenEndpointClient`
   - obtain-path request construction
   - response translation into `AccessToken`
5. Update `src/mlops_async/core/auth.py` so `TokenManager` integrates with the concrete token collaborator while preserving lock, success-before-store, and auth exception boundaries.
6. Preserve `src/mlops_async/core/requester.py` request-composition boundaries and add only the minimum lazy auth integration proof surface needed by tests.
7. Add `tests/unit/core/test_token_endpoint_client.py` covering request shape, response translation, shared endpoint-spec source, and invalid response errors.
8. Update `tests/unit/core/test_token_manager.py`, `tests/unit/core/test_auth_contract.py`, and `tests/unit/core/test_requester_auth_boundary.py` to reflect the concrete token collaborator and to prove first authenticated request lazy-resolves the token.
9. Run bounded validation for the touched unit tests plus `ruff` and `pyright`.

## Validation / Acceptance Checks

- `analysis/internal-auth-spine-mvp/requirements.md` and `analysis/internal-auth-spine-mvp/technical-spec.md` exist and stay inside the MVP boundary.
- `TokenEndpointClient` emits `POST /SASLogon/oauth/token` with form-urlencoded body matching the existing obtain request-gate baseline.
- runtime uses a single token endpoint spec source; no duplicate path literal is introduced outside the collaborator-local surface.
- `Requester` still rejects caller `Authorization` when auth is managed.
- first authenticated request obtains a token lazily; wiring does not prefetch token at construction time.
- no package-root promotion of new auth internals occurs.
- validation commands remain bounded to the touched topic surface.

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

- After merge, no repository release action is required for this topic.
- No README row, VERSION bump, or release-note action is expected.

## Open Questions / Unresolved Items

- None. If future work needs a broader endpoint registry, a public `AuthClient`, or a true
  refresh grant contract, those belong to separate topics.

## In-Scope

- `analysis/internal-auth-spine-mvp/**`
- `plan/internal-auth-spine-mvp/**`
- `src/mlops_async/core/token_endpoint_client.py`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/requester.py`
- topic-scoped `tests/unit/core/**`

## Out-Of-Scope

- `AuthClient` public UX
- broader endpoint registry
- family endpoint implementation
- release surfaces

## ReadOnly

- `docs/ARCHITECTURE.md`
- `docs/standards/http-client-auth-boundary.md`
- `analysis/request-gate-saslogon-obtain-access-token/**`
- `tests/unit/request_contract/saslogon_token_request_gate/**`

## Written

- `analysis/internal-auth-spine-mvp/requirements.md`
- `analysis/internal-auth-spine-mvp/technical-spec.md`
- `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.plan.md`
- `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md`
- `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md`
- `src/mlops_async/core/token_endpoint_client.py`
- `tests/unit/core/test_token_endpoint_client.py`

## Deleted

- none by default

## NonGoal

- do not implement public auth UX
- do not implement broader endpoint registry
- do not introduce Python 3.11 `StrEnum`

## TestCase

1. `TokenEndpointClient` uses the single shared endpoint spec source and emits the canonical obtain request.
2. `TokenEndpointClient` translates a valid JSON response into `AccessToken`.
3. First authenticated request lazy-obtains a token and injects bearer auth.
4. `Requester` keeps collision and content-type boundaries intact.

