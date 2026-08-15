# refresh-token-runtime Specification

## Acceptance Criteria

1. password obtain succeeds only when the response contains a valid non-empty refresh token.
2. refresh uses the injected async client, existing Basic Auth, token headers, and the refresh-token grant.
3. before one storage replacement, TokenManager normalizes a refresh response omitting `refresh_token` with the cached refresh token and returns that same complete immutable state.
4. a valid response refresh token atomically replaces access token, expiry, and refresh token through TokenManager-managed storage.
5. fetch/failure semantics remain unchanged: generic failure becomes chained `TokenFetchException`; `AuthException` and `asyncio.CancelledError` propagate without storage mutation.
6. public API, protocol signatures, UTC expiry/60-second skew, and `sas.ec` compatibility remain unchanged.
7. `README.md`, `docs/standards/http-client-auth-boundary.md`, `VERSION`, `pyproject.toml`, and `uv.lock` align to the feature-PR `0.15.0` scope.

## Behavioral Scenarios

### Scenario 1: Password obtain initializes refresh state

- **Given**: empty TokenStorage and a valid password-grant response containing access token, positive expiry, and refresh token.
- **When**: TokenManager resolves an access token through PasswordTokenEndpointClient.
- **Then**: storage receives one immutable state containing access token, UTC expiry, and the response refresh token.

### Scenario 2: Refresh response omits refresh token

- **Given**: expired stored state with refresh token `old-refresh`.
- **When**: the refresh endpoint returns valid access data but omits `refresh_token`.
- **Then**: TokenManager normalizes the result before one storage replacement; storage and the returned value are the same complete immutable state with new access data and `old-refresh`.

### Scenario 3: Refresh response rotates refresh token

- **Given**: expired stored state with refresh token `old-refresh`.
- **When**: the refresh endpoint returns valid access data and `new-refresh`.
- **Then**: storage contains one new state with `new-refresh`, and concurrent waiters observe that state.

### Scenario 4: Refresh is cancelled

- **Given**: expired stored state and an in-flight refresh.
- **When**: the refresh owner task is cancelled.
- **Then**: cancellation propagates and the prior full state remains stored.

## Error / Edge Cases

- password obtain response lacks `refresh_token`, has whitespace-only content, or has non-string content.
- refresh response provides malformed `refresh_token`; it is not treated as omission.
- transport/schema failures preserve previous state and follow existing exception translation.
- fetch failure, `AuthException`, and cancellation preserve their existing propagation and storage semantics.
- ten concurrent expired-token callers cause one endpoint refresh.
- existing `AccessToken(value, expires_at)` construction and client-credentials flow remain valid.
- no direct sync `httpx.Client`, public refresh API, retry, timeout parameter, or endpoint-client storage write is introduced.
