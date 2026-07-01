# request-gate-saslogon-obtain-access-token - Behavior Spec

## Purpose

本 spec 凍結 `SASLogon/oauth/token -> obtain_access_token` 的最小 request-shape contract。

本 spec 明確宣告：

- `tests-only / shape-only`
- `client_credentials` only
- `scope` blocked

本 topic 只證明 request shape，不證明 runtime auth behavior。

---

## Canonical request

### Allowed case

| Case ID | Method | Path | Query | Body |
| --- | --- | --- | --- | --- |
| `client_credentials_basic` | `POST` | `/SASLogon/oauth/token` | `{}` | `grant_type=client_credentials&client_id=<id>&client_secret=<secret>` |

### Required input

- `client_id`
  - required
  - non-empty string
- `client_secret`
  - required
  - non-empty string
- `grant_type`
  - only `client_credentials`
- `scope`
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
| non-string `client_id` | `123` | fast-fail |
| blank `client_id` | `"   "` | fast-fail |
| non-string `client_secret` | `{"secret": "x"}` | fast-fail |
| blank `client_secret` | `""` | fast-fail |
| wrong `grant_type` | `"authorization_code"` | fast-fail |
| any `scope` | `"openid"` | fast-fail |

---

## Out-of-scope variants

- `refresh_access_token`
- `scope` contract support
- token response parsing
- `AccessToken` / `TokenFetcher` implementation
- `TokenManager` / `AuthProvider` / `Requester` wiring
- `src/**`
- creator / publish-in-progress 的 docs / version 變更

---

## Fixture expectations

### Request-flow fixture

- file:
  `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.request-flow.json`
- cases:
  - `client_credentials_basic`

### Mock-response fixture

- file:
  `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.mock-responses.json`
- response body:
  - minimal JSON object only
  - no response-schema assertion in this topic

---

## Test expectations

### Positive

- `obtain_access_token(client_id="client-id-abc-123", client_secret="secret-value-xyz")`
  emits:
  - `POST /SASLogon/oauth/token`
  - `Accept: application/json`
  - `Content-Type: application/x-www-form-urlencoded`
  - body:
    `grant_type=client_credentials&client_id=client-id-abc-123&client_secret=secret-value-xyz`

### Negative

- non-string `client_id`
- blank `client_id`
- non-string `client_secret`
- blank `client_secret`
- wrong `grant_type`
- any `scope`

### Guard

- any path drift causes failure
- any query params cause failure
- any request body drift causes failure
- any attempt to introduce a second outbound request is topic drift

### Edge

- reserved characters in `client_id` / `client_secret` 必須被 percent-encoding

---

## Stable-library note

- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`

以上三者只在 final `release` 對齊，不在本 topic creator / publish-in-progress 落地。
