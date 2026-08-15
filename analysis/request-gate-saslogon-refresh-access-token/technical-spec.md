# request-gate-saslogon-refresh-access-token technical specification

## Status

- `FROZEN`

## Source Baseline Summary

- 本 technical spec 以
  `analysis/request-gate-saslogon-refresh-access-token/requirements.md`
  為 execution-facing baseline。
- 本 topic 為 `tests-only / shape-only` request gate。
- 實作邊界固定在
  `tests/unit/request_contract/saslogon_refresh_token_request_gate/**`，不得修改 `src/**`。

## Request Contract

### Canonical positive case

- case id: `refresh_token_basic`
- method: `POST`
- path: `/SASLogon/oauth/token`
- query: `{}`
- required headers:
  - `Accept: application/json`
  - `Content-Type: application/x-www-form-urlencoded`
- canonical body order:
  `grant_type=refresh_token&refresh_token=<token>`

### Required inputs

- `refresh_token`
  - required
  - non-empty string
- `grant_type`
  - only `refresh_token`
- `scope`
  - blocked in this topic
- `client_id` / `client_secret`
  - blocked in this topic

## Fixture Layout

### Request-flow fixture

- path:
  `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json`
- exactly one case:
  - `refresh_token_basic`
- exactly one observed step:
  - purpose: `target-api`
  - request:
    - method `POST`
    - path `/SASLogon/oauth/token`
    - query `{}`
    - body form-urlencoded string

### Mock-response fixture

- path:
  `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.mock-responses.json`
- exactly one case:
  - `refresh_token_basic`
- response body:
  - minimal JSON object scaffold only
  - no response-schema assertion in this topic

## Topic-local Harness Rules

- harness 必須攔截單一 outbound request，並在第二個 outbound request 時立即失敗
- harness 必須將 prepared request 正規化成 semantic shape：
  - `method`
  - `path`
  - `query`
  - `body`
  - `headers`
- harness 必須驗證：
  - method 完全一致
  - path 完全一致
  - query 必須為 `{}`
  - body 必須為 canonical form-urlencoded 字串
  - `Accept` / `Content-Type` 必須存在且前綴一致
- harness 必須保留 topic fixture root fallback，不可跳出
  `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures`

## Blocked Variants

- non-string `refresh_token` -> fast-fail
- blank `refresh_token` -> fast-fail
- wrong `grant_type` -> fast-fail
- any `scope` value -> fast-fail
- any `client_id` value -> fast-fail
- any `client_secret` value -> fast-fail

## Test Expectations

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

### Edge / regression

- reserved characters in `refresh_token` 必須 percent-encoding
- topic-local harness 只允許單一步驟 observed flow
- topic-scoped pytest run detection 必須只在本 package target 時放寬 coverage gate

## Stable Library Metadata Intent

- `README.md`、`docs/api-endpoints/markdown-reference/README.md`、`VERSION`、
  `pyproject.toml`、`uv.lock` 僅在 final `release` 對齊。
- 本 topic creator / publish-in-progress implementation 不得落地 stable-library changes。

## Validation Commands

```bash
uv run pytest tests/unit/request_contract/saslogon_refresh_token_request_gate -v
uv run ruff check tests/unit/request_contract/saslogon_refresh_token_request_gate
uv run pyright tests/unit/request_contract/saslogon_refresh_token_request_gate/conftest.py tests/unit/request_contract/saslogon_refresh_token_request_gate/test_refresh_access_token_request_contract.py
```
