# viya-password-token-e2e Specification

## Acceptance Criteria

1. Password token E2E reaches the configured real HTTPS Viya origin only after explicit process opt-in.
2. The only successful result is status `200` with a non-empty `access_token` and positive integer `expires_in`.
3. Disabled, invalid-config, transport, TLS, timeout, JSON, and schema paths are not reported as success.

## Behavioral Scenarios

### Explicit real token validation

- **Given** a Git-ignored config file with valid password-grant credentials and `RUN_VIYA_E2E=1` in the process.
- **When** the marked E2E invokes `PasswordTokenEndpointClient.fetch_access_token()`.
- **Then** it passes only for a real HTTP 200 token response that satisfies the token schema.

### Disabled E2E

- **Given** no process opt-in.
- **When** ordinary pytest runs.
- **Then** the E2E case is skipped; selecting `-m viya_e2e` explicitly fails configuration.

## Error / Edge Cases

- Missing config keys, malformed config lines, loopback/non-HTTPS URL, and invalid `sas.ec` secret combinations fail before the request.
- Failure output never includes credential values, access token, Authorization value, or response body.
