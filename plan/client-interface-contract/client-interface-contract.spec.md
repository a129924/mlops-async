# Client Interface Contract Specification

## Acceptance Criteria

1. `src/mlops_async/core/client.py` defines an internal-only `Client` `Protocol` that exposes `request(...)`, `request_json(...)`, `aclose()`, and async context manager methods without leaking `httpx` types through public annotations.
2. `src/mlops_async/core/request_options.py` defines `RequestTimeouts` and `ClientRequestOptions` as frozen, slotted repo-owned value objects; `RequestTimeouts` uses optional float seconds for `total`, `connect`, `read`, and `write`, and rejects non-positive provided values.
3. `src/mlops_async/core/types.py` defines `JSONScalar`, `JSONValue`, uppercase `HttpMethod`, plain immutable `ResponseHeaders`, and minimal `RawClientResponse` exactly within the locked internal contract boundary.
4. `ResponseHeaders` provides case-insensitive lookup, duplicate preservation, original-order preservation, `get(name)`, `get_all(name)`, and `pairs()`, with `get(name)` returning the first match and `pairs()` preserving original header-name casing.
5. `src/mlops_async/exceptions.py` defines `HttpErrorContext` and handwritten `CustomException`; `CustomException` exposes `.context`, same-name forwarding properties, `body_snippet`, `request_id`, and normalized-path message formatting.
6. Normalized-path message formatting derives from the fully resolved URL path component, preserves any base-path prefix and trailing slash, excludes query string, and appends ` [request_id=...]` only when a request ID exists.
7. `src/mlops_async/__init__.py` does not re-export `core/...` contract types while this topic remains internal-only.
8. Unit tests exist at the locked contract-area paths and cover timeout validation, header behavior, client-surface boundaries, raw-response behavior, JSON-only success, `204 No Content` raw-only behavior, and exception message formatting.

## Behavioral Scenarios

### Scenario 1: JSON-first convenience path stays inside repo-owned types
- **Given**: an internal client implementation that satisfies the `Client` `Protocol` and returns a successful JSON response
- **When**: a domain endpoint uses `request_json(...)`
- **Then**: the caller receives a `JSONValue`, not a transport-library response object, and the contract surface remains inside repo-owned types through the frozen `options: ClientRequestOptions | None` request-extension argument

### Scenario 2: Raw observability path preserves header semantics
- **Given**: a successful raw response with duplicate headers and mixed header-name casing
- **When**: a caller inspects `RawClientResponse.headers`
- **Then**: `ResponseHeaders.get()` performs case-insensitive first-match lookup, `get_all()` returns all matching values in original order, and `pairs()` preserves original header-name casing and duplicates

### Scenario 3: Failure message uses normalized path, not full URL
- **Given**: a resolved request URL that contains a base path, trailing slash, and query string
- **When**: `CustomException` builds its message for a failing request
- **Then**: the message uses the resolved URL path with the base-path prefix and trailing slash preserved, excludes the query string, and keeps the full URL only in structured error context

## Error / Edge Cases

- A provided timeout value of `0` or a negative number is rejected instead of being silently accepted.
- A successful HTTP status with a non-JSON body causes `request_json(...)` to fail through `CustomException` rather than returning text or bytes.
- `204 No Content` does not become an implicit JSON-success shortcut; it remains a raw-path case in this topic.
- `RawClientResponse` does not grow `reason_phrase` or `http_version` in this topic even if transport metadata exists underneath.
- Duplicate headers are not collapsed into a plain mapping that would lose order or multiplicity.
- `src/mlops_async/__init__.py` remains free of accidental `core/...` re-exports even if internal imports are added elsewhere during implementation.
