# Resilient Request Execution Specification

## Acceptance Criteria

1. The canonical authenticated request path uses an internal, non-exported immutable failure carrier and `Client.failure_for(exception) -> RequestFailure | None`; core does not import transport or `httpx`.
2. `HttpClient` remains single-send and preserves the original failure exception identity, message, context, and properties while making allowed failure metadata available to core classification.
3. Python `match`/`case` makes only `HttpMethod.GET` and `HttpMethod.HEAD` eligible; all other methods, including `POST`, use the default noneligible branch.
4. Eligible connection, timeout, `429`, `502`, `503`, and `504` failures retry with an initial and a replay budget of at most three sends each, jittered exponential delay from `0.25` capped at `2`, and `Retry-After` delta/date parsing clamped to `0..30`.
5. An initial `401` may perform one same-lock `refresh_if_current`; changed token state replays without refresh, cleared storage performs no fetch/refresh, refresh failure or cancellation preserves storage, and replay never performs a second refresh.
6. Every send retains its per-send timeout, cancellation propagates immediately, and raw `TokenEndpointClient.request_json` bypasses the decorator.
7. No public API, export, constructor, facade, mutation retry, release surface, or raw-token endpoint contract changes.

## Behavioral Scenarios

### Scenario 1: Eligible temporary failure recovers
- **Given**: A canonical `GET` or `HEAD` request receives a classified connection, timeout, `429`, `502`, `503`, or `504` failure.
- **When**: The request is retried within its active initial or replay path budget.
- **Then**: It makes no more than three sends in that path, uses the locked delay policy, retains a per-send timeout, and returns the recovered response if a send succeeds.

### Scenario 2: Default method branch does not retry
- **Given**: A canonical `POST` request fails with a failure that would otherwise be retryable.
- **When**: `_RequesterResilienceDecorator` evaluates its method.
- **Then**: The `case _` branch leaves the failure unchanged and makes no retry, refresh, or replay.

### Scenario 3: Initial 401 refreshes once and replays
- **Given**: An initial eligible request receives `401` and storage still holds the request's current token.
- **When**: The decorator invokes `TokenManager.refresh_if_current` under the existing lock.
- **Then**: At most one same-token refresh occurs, the request replays once using the refreshed current state, and its replay path has an independent three-send budget with no second refresh.

### Scenario 4: Concurrent or changed token state avoids duplicate refresh
- **Given**: Another coroutine has already changed storage token state, or storage is cleared, before a caller handles initial `401`.
- **When**: The caller reaches the conditional refresh decision.
- **Then**: Changed state replays current token without a new refresh, while cleared state performs neither fetch nor refresh.

### Scenario 5: Raw token request remains direct
- **Given**: `TokenEndpointClient.request_json` sends a raw token endpoint request.
- **When**: The token endpoint request fails or succeeds.
- **Then**: It bypasses `_RequesterResilienceDecorator` and retains the existing raw transport behavior.

## Error / Edge Cases

- Invalid `Retry-After` values use the ordinary jittered exponential delay; valid delta and HTTP-date values are clamped to `0..30`.
- Nonclassified failures, noneligible methods, and retry budget exhaustion propagate the original exception without wrapping or extra send.
- `asyncio.CancelledError` propagates immediately from sends or refresh; it is not retried and token storage is unchanged.
- Refresh failure preserves prior storage and propagates the failure; it does not cause fetch, a second refresh, or a replay that invents a token.
- Exception metadata attachment must not replace or mutate away the original exception's identity, message, context, or observable properties.
