# request-gate-saslogon-refresh-access-token requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結 `POST /SASLogon/oauth/token` 對應 `refresh_access_token` 的最小 request contract。
- creator phase 只建立 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/**` request-gate artifacts。
- 本 topic 不修改 `src/**`，也不在 creator / publish-in-progress 階段執行 release。

## Goal

- 以 `refresh_token` grant 建立 `refresh_access_token` 的最小 request baseline。
- 與已完成的 `obtain_access_token` topic 分開治理，避免 auth surface 被誤視為同一批 endpoint。
- 凍結最小可行 request shape：
  - method: `POST`
  - path: `/SASLogon/oauth/token`
  - `Content-Type: application/x-www-form-urlencoded`
  - `Accept: application/json`
  - body:
    `grant_type=refresh_token&refresh_token=<token>`

## In-Scope

- `analysis/request-gate-saslogon-refresh-access-token/requirements.md`
- `analysis/request-gate-saslogon-refresh-access-token/technical-spec.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.plan.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.step.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.spec.md`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/__init__.py`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/conftest.py`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/test_refresh_access_token_request_contract.py`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.mock-responses.json`

## Out-of-scope

- `src/**`
- `obtain_access_token`
- `scope` request shape
- `client_id` / `client_secret` refresh variants
- token response parsing contract
- `AccessToken` / `TokenFetcher` concrete implementation
- `TokenManager` / `AuthProvider` / `Requester` wiring
- `README.md` / `docs/api-endpoints/markdown-reference/README.md` / `VERSION`
  在 creator / publish-in-progress 階段的任何變更

## Non-goal

- 不在本 topic 建立可運行的 OAuth refresh client。
- 不在本 topic 擴成 storage、retry、401 recovery、或 broader auth lifecycle。
- 不在本 topic 修改 transport 或 core auth modules。
- 不在本 topic 把 refresh runtime work 回填到 request-gate artifacts。
- 不在本 topic 提前做 VERSION bump、release tag、或 release note 落地。

## ReadOnly

- `analysis/http-client-auth-boundary/requirements.md`
- `analysis/http-client-auth-boundary/technical-spec.md`
- `analysis/request-gate-saslogon-obtain-access-token/requirements.md`
- `analysis/request-gate-saslogon-obtain-access-token/technical-spec.md`
- `tests/unit/request_contract/contract_case.py`
- `tests/unit/request_contract/saslogon_token_request_gate/conftest.py`
- `tests/unit/request_contract/saslogon_token_request_gate/test_obtain_access_token_request_contract.py`
- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`

## Written

- `analysis/request-gate-saslogon-refresh-access-token/requirements.md`
- `analysis/request-gate-saslogon-refresh-access-token/technical-spec.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.plan.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.step.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.spec.md`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/__init__.py`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/conftest.py`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/test_refresh_access_token_request_contract.py`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.request-flow.json`
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/fixtures/refresh_access_token.mock-responses.json`

## Modified

- creator phase: none outside the new topic-local artifacts and new request-contract package
- release phase only:
  - `README.md`
  - `docs/api-endpoints/markdown-reference/README.md`
  - `VERSION`
  - `pyproject.toml`
  - `uv.lock`

## Locked Decisions

- topic name 固定為 `request-gate-saslogon-refresh-access-token`
- `refresh_token` 是唯一正向 grant shape
- 正向 body 只包含 `grant_type` 與 `refresh_token`
- `scope` 在本 topic 內 blocked
- `client_id` / `client_secret` refresh variants 在本 topic 內 blocked
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- docs / version alignment 延後到 final `release`
- `publish-in-progress` 不做 `README.md` / endpoint docs / `VERSION` 變更

## Blocked Variants

- blank `refresh_token`
- non-string `refresh_token`
- 非 `refresh_token` 的 `grant_type`
- 任何 `scope` 輸入
- 任何 `client_id` / `client_secret` 輸入
- 任何試圖回漂到 `client_credentials` baseline 的正向 case

## Release-stage Alignment Intent

- `README.md`：final release 時補上或更新
  `SASLogon/oauth/token -> refresh_access_token` 的 request-gate status 描述。
- `docs/api-endpoints/markdown-reference/README.md`：final release 時同步更新 auth inventory / status。
- `VERSION`、`pyproject.toml`、`uv.lock`：only at final `release`。

## Acceptance Baseline

- topic-local 五個 analysis / plan artifacts 齊全且互相一致
- `tests/unit/request_contract/saslogon_refresh_token_request_gate/**` 是唯一 implementation surface
- 正向 case 只存在一個：`refresh_token_basic`
- `scope` 不出現在正向 fixture
- `client_id` / `client_secret` 不出現在正向 fixture
- blocked variants 明確覆蓋 invalid token、wrong grant、`scope`、與 credential drift
- 沒有任何 `src/**` 或 auth runtime module 納入修改集合
