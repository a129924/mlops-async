# request-gate-saslogon-refresh-access-token - Behavior Spec

## Purpose

本 spec 凍結 `SASLogon/oauth/token -> refresh_access_token` 的最小 request-shape contract。

本 spec 明確宣告：

- `tests-only / shape-only`
- `refresh_token` only
- `scope` blocked
- `client_id` / `client_secret` blocked

本 topic 只證明 request shape，不證明 runtime auth behavior。

---

## Canonical request

### Allowed case

| Case ID | Method | Path | Query | Body |
| --- | --- | --- | --- | --- |
| `refresh_token_basic` | `POST` | `/SASLogon/oauth/token` | `{}` | `grant_type=refresh_token&refresh_token=<token>` |

### Required input

- `refresh_token`
  - required
  - non-empty string
- `grant_type`
  - only `refresh_token`
- `scope`
  - blocked
- `client_id`
  - blocked
- `client_secret`
  - blocked

### Request-shape focus

本 topic 只驗證：

- method
- path
- query absence
- form-urlencoded body
- `Accept`
- `Content-Type`

本 topic 不驗證 response schema。

---

## Blocked variants

| Variant | Example | Expected result |
| --- | --- | --- |
| non-string `refresh_token` | `123` | fast-fail |
| blank `refresh_token` | `"   "` | fast-fail |
| wrong `grant_type` | `"client_credentials"` | fast-fail |
| any `scope` | `"openid"` | fast-fail |
| any `client_id` | `"client-id-abc-123"` | fast-fail |
| any `client_secret` | `"secret-value-xyz"` | fast-fail |

---

## Out-of-scope variants

- `obtain_access_token`
- `scope` contract support
- `client_id` / `client_secret` refresh variants
- token response parsing
- `AccessToken` / `TokenFetcher` implementation
- `TokenManager` / `AuthProvider` / `Requester` wiring
- `src/**`
- creator / publish-in-progress 的 docs / version 變更

---

## Fixture expectations

### Request-flow fixture

- file:
  `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json`
- cases:
  - `refresh_token_basic`

### Mock-response fixture

- file:
  `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.mock-responses.json`
- response body:
  - minimal JSON object only
  - no response-schema assertion in this topic

---

## Test expectations

### Positive

- `refresh_access_token(refresh_token="refresh-token-abc-123")` emits:
  - `POST /SASLogon/oauth/token`
  - `Accept: application/json`
  - `Content-Type: application/x-www-form-urlencoded`
  - body:
    `grant_type=refresh_token&refresh_token=refresh-token-abc-123`

### Negative

- non-string `refresh_token`
- blank `refresh_token`
- wrong `grant_type`
- any `scope`
- any `client_id`
- any `client_secret`

### Guard

- any path drift causes failure
- any query params cause failure
- any request body drift causes failure
- any attempt to introduce a second outbound request is topic drift

### Edge

- reserved characters in `refresh_token` 必須被 percent-encoding

---

## Stable-library note

- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

以上五者只在 final `release` 對齊，不在本 topic creator / publish-in-progress 落地。
