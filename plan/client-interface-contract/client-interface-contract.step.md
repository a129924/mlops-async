---
topic: client-interface-contract
phase: code-review
created: 2026-05-13
---

# client-interface-contract — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/client-interface-contract/client-interface-contract.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Create `src/mlops_async/core/request_options.py`. Define `RequestTimeouts` and `ClientRequestOptions` as frozen, slotted repo-owned value objects; enforce `> 0` timeout validation, keep `request_context: Mapping[str, str]`, exclude retry fields, and export only the locked names through local `__all__`.
- [X] 2. Create `src/mlops_async/core/types.py`. Add `JSONScalar`, `JSONValue`, uppercase `HttpMethod`, plain immutable `ResponseHeaders`, and minimal `RawClientResponse`; keep lookup semantics, duplicate preservation, original-order preservation, and local `__all__` exactly aligned with the locked decisions.
- [X] 3. Create `src/mlops_async/exceptions.py`. Add `HttpErrorContext` and handwritten `CustomException`; implement `.context`, same-name forwarding properties, `body_snippet` / `request_id` contract fields, and normalized-path `_build_message()` behavior without exposing transport-library types.
- [X] 4. Create `src/mlops_async/core/client.py`. Define the internal-only `Client` contract as a `Protocol` with `request(...)`, `request_json(...)`, `aclose()`, and async context manager methods; keep the request surface on the frozen parameter families (`method`, `path`, `headers`, `params`, `json_body`, `content`, and a single `options: ClientRequestOptions | None` argument) and return only repo-owned response / JSON types.
- [X] 5. Open `src/mlops_async/__init__.py` and keep the package-root boundary unchanged. Do not re-export any `core/...` contract types from the package root while this topic remains internal-only.
- [X] 6. Create `tests/unit/core/test_request_timeouts.py` and `tests/unit/core/test_response_headers.py`. Cover positive timeout values, invalid timeout values, specific-overrides-total precedence, duplicate headers, first-match `get()`, `get_all()`, `pairs()`, case-insensitive lookup, and preserved original casing/order.
- [X] 7. Create `tests/unit/core/test_client_contract.py` and `tests/unit/test_exceptions.py`. Cover request/request_json type boundaries, raw-response preservation, non-JSON success-body failure, `204 No Content` staying on the raw path, normalized-path message formatting, and the absence of package-root `core` re-exports.
- [X] 8. If the implemented code would leave `docs/ARCHITECTURE.md` inconsistent with the internal-first placement, update `docs/ARCHITECTURE.md` to state that the first client contract lands under `core/...` while top-level `client.py` remains a future public design target.
