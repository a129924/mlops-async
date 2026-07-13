# PasswordTokenEndpointClient Specification

## Acceptance Criteria

1. `core/token_endpoint/` exists with locked files; `auth.py` remains lifecycle-only and unchanged.
2. `_shared.py` owns AuthTokenEndpoint, token-endpoint errors, credential validation, response parsing, and expiry conversion support.
3. TokenEndpointClient moves to `client_credentials.py` and preserves current request contract.
4. PasswordTokenEndpointClient posts password grant to `/SASLogon/oauth/token`, uses Basic auth for client credentials, and sends only `grant_type=password`, `username`, `password` in form body.
5. Compatibility module re-exports legacy symbols and implements no grant request.
6. Both clients reject invalid credentials/responses with existing error model, return AccessToken, and do not expose sensitive values.
7. password refresh re-obtains via password grant, not OAuth refresh-token.

## Behavioral Scenarios

### Scenario 1: client-credentials migration remains compatible

- **Given** injected fake transport and valid client credentials.
- **When** TokenEndpointClient fetches through compatibility import.
- **Then** it posts existing client-credentials form to existing endpoint and returns AccessToken.

### Scenario 2: password grant obtains a token

- **Given** injected fake transport and valid user/client credentials.
- **When** PasswordTokenEndpointClient fetches.
- **Then** it posts urlencoded password form, uses Basic client auth, returns parsed AccessToken.

### Scenario 3: password refresh re-obtains

- **Given** a prior AccessToken and password client.
- **When** refresh_access_token is called.
- **Then** it sends a second password obtain and no refresh-token grant.

### Scenario 4: TokenManager uses protocol lifecycle

- **Given** expired token in existing storage and PasswordTokenEndpointClient as fetcher.
- **When** TokenManager resolves a token.
- **Then** it invokes Protocol refresh and stores the new AccessToken without auth.py changes.

## Error / Edge Cases

- Blank/whitespace user/client credentials fail at construction without echoing values.
- Non-object response, missing/empty access_token, zero/negative/string/bool expires_in fail with TokenEndpointClientError.
- Reserved user credential characters encode correctly; client credentials never enter password form.
- fake records, assertions, exceptions, logs, reviewer evidence contain no raw sensitive values.
- CancelledError/transport failures preserve TokenManager behavior; no timeout/retry handling is added.
