# HTTP Request Value Objects Rework Specification

## Status

- **Current phase**: `creator-in-progress`
- **Reviewer handoff**: use the single machine-consumable JSON object in the
  topic plan and review log; the appended independent Plan-Reviewer `approved`
  verdict authorizes Tester to begin `rework-tdd-test-authoring`. Production
  implementation remains unauthorized pending separate authorization.
- **TDD-correction routing**: the current recorded transition is `approved` ->
  `creator-in-progress` for the Tester-owned TDD pass.

## Acceptance Criteria

- Only the six HUMAN-selected PR #57 threads below are acceptance work.
- `JsonBody` remains a validation/snapshot value object; wire serialization is
  a transport responsibility.
- All direct value-object construction paths preserve the same canonical
  invariants as named factories.
- No acceptance scenario changes the locked origin-only BaseUrl policy, body
  union, lowercase Headers model, token/form boundary, endpoint-family
  exclusion, or primitive-adapter compatibility role.

## Behavioral Scenarios

### TestCase 1 — `PRRT_kwDOSTt_386VAaWm`: JSON null wire preservation

- **Given**: a canonical `HttpRequest` whose `body` is `JsonBody(None)`.
- **When**: `HttpClient.execute()` builds and sends the HTTP request.
- **Then**: the value object still only exposes its snapshot; transport selects
  the `JsonBody` variant rather than interpreting its value as absent, and the
  observed wire content is exactly `b"null"`.

### TestCase 2 — `PRRT_kwDOSTt_386VAaWr`: direct constructors preserve invariants

- **Given**: callers directly construct `BaseUrl`, `EndpointPath`,
  `QueryParams`, or `Headers`, including invalid origin/path/key/header cases
  and valid mixed-case header input.
- **When**: direct construction is compared with the respective named
  construction path.
- **Then**: invalid values raise `ValueError`; valid values have the same
  canonical representation (including lowercase last-wins Headers), and no
  dataclass initializer or raw internal storage bypass exists.

### TestCase 3 — `PRRT_kwDOSTt_386VAaWs`: static literal path is canonical

- **Given**: `EndpointPath.literal()` receives a canonical percent-encoded
  absolute static path and non-canonical literals containing whitespace,
  non-ASCII characters, or control characters.
- **When**: the literal is constructed and used in `HttpRequest.url`.
- **Then**: canonical input is retained exactly and each non-canonical input is
  rejected before transport, so httpx does not encode or normalize a different
  wire URL.

### TestCase 4 — `PRRT_kwDOSTt_386VAaWw`: BaseUrl authority is construction-safe

- **Given**: BaseUrl input whose host has a space, backslash, or
  percent-encoded NUL, alongside a valid HTTP(S) origin with optional port.
- **When**: it is passed through both direct and named BaseUrl construction.
- **Then**: each invalid authority/hostname raises `ValueError` at construction
  and the valid origin remains origin-only; no invalid host reaches httpx.

### TestCase 5 — `PRRT_kwDOSTt_386VAaWx`: direct execute has no implicit Accept

- **Given**: a canonical `HttpRequest` executed directly with no `accept`
  header, and a second request with explicit canonical `accept`.
- **When**: `HttpClient.execute()` builds the wire request.
- **Then**: the first wire request has no `accept: */*` or other hidden Accept
  default, while the second preserves the caller's explicit canonical value.

### TestCase 6 — `PRRT_kwDOSTt_386VAaW2`: primitive embedded-query parity

- **Given**: legacy JSON-domain primitive callers invoke both `request()` and
  `request_json()` with a path such as `"/items?tag=a"`.
- **When**: each adapter constructs and executes its canonical request.
- **Then**: neither raises `ValueError`; the path is separated from its query,
  the final wire URL preserves `?tag=a`, and the adapter still delegates
  through the canonical execution path.

## Error / Edge Cases

- `JsonBody(None)` is distinct from `body is None` even though its exposed JSON
  value is `None`.
- Direct construction must not accept a raw empty query key or duplicate
  case-insensitive header storage that violates the canonical model.
- Literal static paths do not accept a query or fragment and now reject unsafe
  non-canonical characters rather than relying on transport normalization.
- Embedded primitive query compatibility does not authorize primitive cleanup,
  raw token/form migration, or a second URL assembly rule.

## Rework TDD Contract

- TDD begins under the recorded independent Plan-Reviewer approval. Tester owns
  the non-trivial D1 and RED-test pass, not Planning actor, Creator, or
  Plan-Reviewer.
- Tester may write only `tests/unit/core/test_http_request.py`,
  `tests/unit/transport/test_http_client.py`, and the exact verdict artifact
  `plan/http-request-value-objects/http-request-value-objects.tdd-verdict.yaml`.
  The verdict artifact may be written only during `rework-tdd-test-authoring`.
- The TestCase mapping contains exactly TestCase 1 through TestCase 6 and their
  six selected thread IDs. The excluded IDs are never test targets.
- Before writing tests, Tester runs `git diff --quiet HEAD -- src/`; exit `0`
  proves the HEAD comparison has no staged or unstaged production content
  change anywhere in `src/`, and Tester records `production_code_modified:
  false`. Do not use `git reset`, `git clean`, or `git checkout` to satisfy
  this guard.
- `validation_checks.expected_initial_status` is exactly `red`. The fixed
  mapping is: `PRRT_kwDOSTt_386VAaWm` ->
  `test_execute_serializes_json_null_as_json_literal` (`happy path`),
  `PRRT_kwDOSTt_386VAaWr` ->
  `test_direct_construction_matches_named_invariants` (`state/side effects`),
  `PRRT_kwDOSTt_386VAaWs` ->
  `test_endpoint_path_literal_rejects_noncanonical_static_paths`
  (`boundary/edge`), `PRRT_kwDOSTt_386VAaWw` ->
  `test_base_url_rejects_invalid_authority_characters` (`error/exception`),
  `PRRT_kwDOSTt_386VAaWx` ->
  `test_execute_removes_implicit_accept_but_preserves_explicit_accept`
  (`error/exception`), and `PRRT_kwDOSTt_386VAaW2` ->
  `test_primitive_request_adapters_preserve_embedded_query`
  (`integration points`). `coverage_category` permits only `happy path`,
  `error/exception`, `boundary/edge`, `state/side effects`, and `integration
  points`; the six mappings collectively cover all five.
- RED evidence records the failing result of the two allowed test modules
  before Creator changes production code and names every mapped
  `test_case_name` as an individual pytest RED failure.
