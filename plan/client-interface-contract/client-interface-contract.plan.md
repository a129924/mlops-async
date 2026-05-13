> **Analysis-layer routing: STRICT MODE**
>
> - Execution-facing source of truth: `analysis/client-interface-contract/technical-spec.md`
> - Business guardrail: `analysis/client-interface-contract/requirements.md`
> - No human `override` instruction changes the analysis-layer priority for this topic.

## Goal / Outcome

- Produce the first repo-visible implementation contract for the internal-only client interface so creator work can add the frozen `core/...` client boundary, supporting types, error contract, and unit tests without rediscovering scope or widening package-root exposure.

## Scope

- **In scope**:
  - Add the repo-visible planning artifacts for this topic under `plan/client-interface-contract/`.
  - Implement the internal-first contract in `src/mlops_async/core/client.py`, `src/mlops_async/core/request_options.py`, `src/mlops_async/core/types.py`, and `src/mlops_async/exceptions.py`.
  - Add contract-focused unit tests in the exact `tests/unit/` paths listed in `Artifact Paths`.
  - Align `docs/ARCHITECTURE.md` with the now-frozen internal-first `core/...` placement if the implementation would otherwise leave the architecture narrative contradictory.

- **Out of scope**:
  - Public package promotion of `Client` or any package-root re-export of `core/...` contract types.
  - Full auth/refresh implementation, retry engine implementation, or any 429 retry behavior expansion.
  - Convenience methods outside the frozen surface, including `request_text(...)`, `request_bytes(...)`, or a `204 No Content` JSON-success shortcut.
  - Domain endpoint implementations, migration-map updates, porting-ledger updates, README changes, VERSION bumps, release notes, or tag/release work.

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**. It does not modify `README.md`, `VERSION`, release notes, or release timing metadata.
- The contract remains **internal-only** and lives under `src/mlops_async/core/...`; `src/mlops_async/__init__.py` must not re-export `Client`, `RequestTimeouts`, `ResponseHeaders`, `RawClientResponse`, or other `core` internals.
- `Client` is represented as an import-safe internal **`Protocol`**, not an abstract base class or public concrete implementation.
- `Client` exposes exactly these operational responsibilities:
  - `request(...)`
  - `request_json(...)`
  - `aclose()`
  - async context manager methods
- `request_json(...)` is the JSON-first convenience path and must treat non-JSON success bodies as failures; `204 No Content` stays on the raw path.
- Per-request extensibility uses a single narrow typed object: `ClientRequestOptions`.
- `RequestTimeouts` is a repo-owned `@dataclass(frozen=True, slots=True)` with:
  - `total: float | None = None`
  - `connect: float | None = None`
  - `read: float | None = None`
  - `write: float | None = None`
  - specific timeout fields overriding `total`
  - all provided values required to be `> 0`
- `ClientRequestOptions` is a repo-owned `@dataclass(frozen=True, slots=True)` carrying `timeout: RequestTimeouts` and `request_context: Mapping[str, str]`; retry fields are excluded.
- The single `ClientRequestOptions` parameter in `request(...)` / `request_json(...)` is named **`options`**.
- `core/types.py` owns the shared internal contract types:
  - `JSONScalar`
  - `JSONValue`
  - `HttpMethod`
  - `ResponseHeaders`
  - `RawClientResponse`
- `HttpMethod` uses common verbs only and keeps uppercase enum names/values.
- `ResponseHeaders` is a plain immutable class with:
  - case-insensitive lookup
  - duplicate preservation
  - original-order preservation
  - `get(name) -> str | None` returning the first match
  - `get_all(name) -> tuple[str, ...]`
  - `pairs() -> tuple[tuple[str, str], ...]` preserving original header-name casing
- `RawClientResponse` remains minimal and does not grow `reason_phrase` or `http_version` in this topic.
- `exceptions.py` owns:
  - `HttpErrorContext` as `@dataclass(frozen=True, slots=True)`
  - handwritten `CustomException`
- `CustomException` keeps `.context` plus same-name read-only forwarding properties for:
  - `status_code`
  - `method`
  - `url`
  - `body_snippet`
  - `request_id`
- `body_snippet` uses the first 512 bytes of the raw body decoded with UTF-8 `errors="replace"`.
- `_build_message()` uses normalized path, not full URL. The normalized path:
  - comes from the fully resolved URL path component
  - preserves any base-path prefix from the resolved URL
  - preserves trailing slash exactly as sent
  - excludes query string
- Conservative split exports apply:
  - `core/client.py -> Client`
  - `core/request_options.py -> ClientRequestOptions, RequestTimeouts`
  - `core/types.py -> JSONScalar, JSONValue, HttpMethod, RawClientResponse, ResponseHeaders`
  - `exceptions.py -> HttpErrorContext, CustomException`
- Unit tests stay split by contract area rather than collapsing into one file.

## Boundaries / Exclusions

- Planning actor owns this plan, spec, and step tracker only.
- Creator owns code and test drafting inside the exact artifact paths listed below.
- Reviewer owns the independent verdict and must not author implementation directly.
- Main Agent owns branch preparation, publish routing, PR flow, merge follow-up, and any future release handling; those routing actions are not creator scope.
- Auth strategy details, refresh concurrency, retry engine behavior, public facade design, and migration evidence remain separate topics even if this implementation adds seams needed by them later.
- If implementation work needs files outside the exact artifact list below, stop and repair this topic plan before continuing.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish -> merge path; this topic stops at `merged` and does not declare a release action.
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

- Use the standard Phase 4.5 planner-alignment rule from the workflow contract before publish.
- STOP POINT 1 still applies before commit / push / PR creation.
- STOP POINT 2 still applies after merge handoff; post-merge local sync requires a new explicit human resume message.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/client-interface-contract/client-interface-contract.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracker | `plan/client-interface-contract/client-interface-contract.step.md` | Planning actor -> Creator | Machine-readable step tracking for the locked implementation steps |
| Topic spec | `plan/client-interface-contract/client-interface-contract.spec.md` | Planning actor | Acceptance contract for this non-trivial topic |
| Requirements baseline | `analysis/client-interface-contract/requirements.md` | Planning actor | Business guardrail for strict-mode planning and review |
| Technical spec baseline | `analysis/client-interface-contract/technical-spec.md` | Planning actor | Execution-facing source of truth in strict mode |
| Client contract module | `src/mlops_async/core/client.py` | Creator | Internal-only `Client` contract surface and lifecycle boundary |
| Request options module | `src/mlops_async/core/request_options.py` | Creator | `ClientRequestOptions` and `RequestTimeouts` definitions plus local `__all__` |
| Shared types module | `src/mlops_async/core/types.py` | Creator | JSON aliases, `HttpMethod`, `ResponseHeaders`, and `RawClientResponse` |
| Exceptions module | `src/mlops_async/exceptions.py` | Creator | `HttpErrorContext`, `CustomException`, and message-building behavior |
| Timeout tests | `tests/unit/core/test_request_timeouts.py` | Creator | Unit tests for timeout value-object validation and precedence |
| Header tests | `tests/unit/core/test_response_headers.py` | Creator | Unit tests for duplicate-preserving, case-insensitive header behavior |
| Client contract tests | `tests/unit/core/test_client_contract.py` | Creator | Unit tests for the internal client surface and no-`httpx` leakage |
| Exception tests | `tests/unit/test_exceptions.py` | Creator | Unit tests for `HttpErrorContext`, `CustomException`, and normalized-path messages |
| Architecture narrative | `docs/ARCHITECTURE.md` | Creator | Update the human-facing package-shape narrative if code landing under `core/...` would otherwise leave the doc misleading |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: no change in this topic.
- If later work drifts outside these exact paths, stop and update this plan before continuing.

## Implementation Steps

1. Create `src/mlops_async/core/request_options.py`. Define `RequestTimeouts` and `ClientRequestOptions` as frozen, slotted repo-owned value objects; enforce `> 0` timeout validation, keep `request_context: Mapping[str, str]`, exclude retry fields, and export only the locked names through local `__all__`.
2. Create `src/mlops_async/core/types.py`. Add `JSONScalar`, `JSONValue`, uppercase `HttpMethod`, plain immutable `ResponseHeaders`, and minimal `RawClientResponse`; keep lookup semantics, duplicate preservation, original-order preservation, and local `__all__` exactly aligned with the locked decisions.
3. Create `src/mlops_async/exceptions.py`. Add `HttpErrorContext` and handwritten `CustomException`; implement `.context`, same-name forwarding properties, `body_snippet` / `request_id` contract fields, and normalized-path `_build_message()` behavior without exposing transport-library types.
4. Create `src/mlops_async/core/client.py`. Define the internal-only `Client` contract as a `Protocol` with `request(...)`, `request_json(...)`, `aclose()`, and async context manager methods; keep the request surface on the frozen parameter families (`method`, `path`, `headers`, `params`, `json_body`, `content`, and a single `options: ClientRequestOptions | None` argument) and return only repo-owned response / JSON types.
5. Open `src/mlops_async/__init__.py` and keep the package-root boundary unchanged. Do not re-export any `core/...` contract types from the package root while this topic remains internal-only.
6. Create `tests/unit/core/test_request_timeouts.py` and `tests/unit/core/test_response_headers.py`. Cover positive timeout values, invalid timeout values, specific-overrides-total precedence, duplicate headers, first-match `get()`, `get_all()`, `pairs()`, case-insensitive lookup, and preserved original casing/order.
7. Create `tests/unit/core/test_client_contract.py` and `tests/unit/test_exceptions.py`. Cover request/request_json type boundaries, raw-response preservation, non-JSON success-body failure, `204 No Content` staying on the raw path, normalized-path message formatting, and the absence of package-root `core` re-exports.
8. If the implemented code would leave `docs/ARCHITECTURE.md` inconsistent with the internal-first placement, update `docs/ARCHITECTURE.md` to state that the first client contract lands under `core/...` while top-level `client.py` remains a future public design target.

## Validation / Acceptance Checks

- The implemented files stay inside the exact artifact paths listed above, or the plan is repaired before continuing.
- The implementation matches strict-mode analysis routing:
  - `analysis/client-interface-contract/technical-spec.md` remains the execution-facing source of truth.
  - `analysis/client-interface-contract/requirements.md` remains the business guardrail.
- `src/mlops_async/core/client.py` exposes only the frozen internal contract and does not leak `httpx` types through annotations.
- `src/mlops_async/__init__.py` does not re-export `core/...` contract types.
- `RequestTimeouts` uses optional float seconds, enforces `> 0`, and preserves specific-overrides-total semantics.
- `ResponseHeaders` preserves duplicate headers, original order, original casing in `pairs()`, and case-insensitive lookup with first-match `get()`.
- `CustomException` message formatting uses normalized path derived from the resolved URL path, preserves base-path prefix and trailing slash, and excludes query string.
- Reviewer or main-agent validation should run:
  - `uv run pytest tests/unit/core/test_request_timeouts.py tests/unit/core/test_response_headers.py tests/unit/core/test_client_contract.py tests/unit/test_exceptions.py`
  - `uv run ruff check src tests`
  - `uv run pyright`
  - `uv run pytest --cov=src/mlops_async --cov-report=term-missing`

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  },
  "required_review_checks": [
    "strict-mode alignment with analysis/client-interface-contract/technical-spec.md",
    "artifact-path exactness against this topic plan",
    "package root does not re-export core contract",
    "contract tests exist for timeouts, headers, client surface, and exceptions",
    "validation commands were run and their scope matches the locked topic"
  ]
}
```

## Post-merge / release actions

- After merge, Main Agent may perform the normal local sync flow only after an explicit human resume message.
- No README update, VERSION bump, release-note work, tag creation, or repository release action belongs to this topic.
- This topic is terminal at `merged`.

## Open Questions / Unresolved Items

None.
