# viya-password-token-e2e Specification

## Acceptance Criteria

1. Password token E2E reaches the configured real HTTPS Viya origin only after explicit process opt-in.
2. The only successful result is status `200` with a non-empty `access_token` and positive integer `expires_in`.
3. The framework user explicitly selects `system`, `insecure`, or `ca_bundle`; missing,
   blank, invalid, or conflicting TLS configuration fails before the request.
4. Disabled, invalid-config, transport, TLS, timeout, JSON, and schema paths are not reported as success.
5. `insecure` success is reported as TLS verification explicitly disabled and is never
   represented as TLS trust verified.

## Behavioral Scenarios

### Explicit real token validation

- **Given** a Git-ignored config file with valid password-grant credentials, an explicit
  TLS mode, and `RUN_VIYA_E2E=1` in the process.
- **When** the marked E2E invokes `PasswordTokenEndpointClient.fetch_access_token()`.
- **Then** it passes only for a real HTTP 200 token response that satisfies the token schema.

### Explicit TLS control

- **Given** `VIYA_E2E_TLS_MODE=system`, **then** the framework passes `verify=True`.
- **Given** `VIYA_E2E_TLS_MODE=insecure`, **then** the framework passes `verify=False`,
  emits the fixed warning, and does not fallback or claim TLS trust verification.
- **Given** `VIYA_E2E_TLS_MODE=ca_bundle` with a nonblank CA bundle path, **then** the
  framework builds and passes an `ssl.SSLContext` for that exact path.

### Disabled E2E

- **Given** no process opt-in.
- **When** ordinary pytest runs.
- **Then** the E2E case is skipped; selecting `-m viya_e2e` explicitly fails configuration.

## Error / Edge Cases

- Missing config keys, malformed config lines, loopback/non-HTTPS URL, and invalid `sas.ec` secret combinations fail before the request.
- Missing/blank/non-exact TLS mode, CA bundle outside `ca_bundle`, and missing/unloadable
  CA bundle in `ca_bundle` fail without exposing the configured value or path.
- Failure output never includes credential values, access token, Authorization value, or response body.

## Evidence Classification

- Post-merge non-E2E：pytest `311 passed, 9 skipped, 1 deselected`、Ruff passed、
  Pyright `0 errors, 0 warnings`。
- Post-merge live：`1 passed, 320 deselected`，真實 network request、HTTP `200`、
  nonempty token、positive expiry；正確結果為
  `live password-token E2E passed with TLS verification explicitly disabled`。
- 此 evidence 證明 HTTPS request success 與 explicit insecure mode success；不證明
  TLS trust verified。Merge-to-dev 尚未完成。
