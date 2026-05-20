# http-client-auth-boundary Specification

## Acceptance Criteria

1. `HttpClient` remains pure transport and may only transmit a final `Authorization` header already present in request headers; it must not generate, validate, refresh, override, or persist auth data.
2. `Requester` is the only request composition layer for domain calls; when `AuthProvider` is configured, caller-supplied `Authorization` is rejected case-insensitively before domain request transport executes.
3. `AuthProvider` only converts `TokenManager` output into auth headers and does not own storage, refresh locking, or HTTP calls.
4. `TokenManager` owns token lifecycle, expiry check, refresh decision, `asyncio.Lock`, and double-check locking; `TokenStorage` only stores token state; `TokenFetcher` performs token endpoint fetch/refresh via raw `HttpClient`.
5. `AccessToken` expiry supports configurable skew with default 60 seconds, and `now + skew >= expires_at` is treated as expired.
6. With at least 10 concurrent coroutines sharing one `TokenManager`, expired or missing token state triggers at most one refresh/fetch.
7. Refresh/fetch failure or cancellation surfaces as auth-layer failure, does not proceed into domain request transport, and preserves previous token state in `TokenStorage`.

## Behavioral Scenarios

### Scenario 1: Domain request with managed auth headers
- **Given**:
  - a configured `Requester`
  - a configured `AuthProvider`
  - a valid token available from `TokenManager`
- **When**:
  - a domain client issues a request through `Requester`
- **Then**:
  - `Requester` may apply safe defaults
  - `Requester` obtains auth headers from `AuthProvider`
  - `Requester` merges defaults/auth/caller headers
  - `Requester` sends final request data to `HttpClient`
  - `HttpClient` performs transport only

### Scenario 2: Concurrent refresh on expired token
- **Given**:
  - a shared `TokenManager`
  - expired or missing token state
  - at least 10 concurrent coroutines requesting auth
- **When**:
  - all coroutines call `get_access_token()`
- **Then**:
  - only one coroutine performs refresh/fetch
  - waiting coroutines reuse the refreshed token
  - no duplicate refresh storm occurs

### Scenario 3: Refresh failure preserves prior token state
- **Given**:
  - `TokenStorage` already contains a previous token
  - `TokenFetcher` fails or the refresh coroutine is cancelled
- **When**:
  - `TokenManager` attempts refresh/fetch
- **Then**:
  - auth-layer failure is surfaced
  - domain request transport is not called
  - previous token state remains in `TokenStorage`

## Error / Edge Cases

- Caller supplies `Authorization` while `AuthProvider` is configured; `Requester` must reject this case-insensitively.
- No `AuthProvider` is configured; caller-provided `Authorization` may pass through for low-level/test use.
- `AccessToken` is within skew window; it is treated as expired even if `expires_at` is still in the future.
- `TokenFetcher` returns failure; the failure must not be translated into transport exception.
- `TokenFetcher` depends on `Requester` or `AuthProvider`; this is outside contract and must be rejected as architecture drift.
