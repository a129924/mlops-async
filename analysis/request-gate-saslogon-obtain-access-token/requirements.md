# request-gate-saslogon-obtain-access-token requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結 `POST /SASLogon/oauth/token` 對應 `obtain_access_token` 的最小 request contract。
- creator phase 只建立 topic-local analysis / plan artifacts 與
  `tests/unit/request_contract/**` request-gate artifacts。
- 本 topic 不修改 `src/**`，也不在 creator / publish-in-progress 階段執行 release。

## Goal

- 先以 `client_credentials` 作為唯一正向 grant shape，建立後續 auth implementation
  可沿用的 request baseline。
- 凍結最小可行 request shape：
  - method: `POST`
  - path: `/SASLogon/oauth/token`
  - `Content-Type: application/x-www-form-urlencoded`
  - `Accept: application/json`
  - body:
    `grant_type=client_credentials&client_id=<id>&client_secret=<secret>`
- 讓後續 release 時可依同一個 baseline 對齊 `README.md`、endpoint docs 與 `VERSION`。

## In-Scope

- `analysis/request-gate-saslogon-obtain-access-token/requirements.md`
- `analysis/request-gate-saslogon-obtain-access-token/technical-spec.md`
- `plan/request-gate-saslogon-obtain-access-token/request-gate-saslogon-obtain-access-token.plan.md`
- `plan/request-gate-saslogon-obtain-access-token/request-gate-saslogon-obtain-access-token.step.md`
- `plan/request-gate-saslogon-obtain-access-token/request-gate-saslogon-obtain-access-token.spec.md`
- `tests/unit/request_contract/saslogon_token_request_gate/__init__.py`
- `tests/unit/request_contract/saslogon_token_request_gate/conftest.py`
- `tests/unit/request_contract/saslogon_token_request_gate/test_obtain_access_token_request_contract.py`
- `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.request-flow.json`
- `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.mock-responses.json`

## Out-of-scope

- `src/**`
- `refresh_access_token`
- `scope` request shape
- token response parsing contract
- `AccessToken` / `TokenFetcher` concrete implementation
- `TokenManager` / `AuthProvider` / `Requester` wiring
- `docs/request-shape-priority-workflow/**` 任何再修改
- public API promotion
- `README.md` / `docs/api-endpoints/markdown-reference/README.md` / `VERSION`
  在 creator / publish-in-progress 階段的任何變更

## Non-goal

- 不在本 topic 建立可運行的 OAuth client。
- 不在本 topic 決定 refresh grant contract。
- 不在本 topic 修改 transport 或 core auth modules。
- 不在本 topic 把 auth runtime work 回填到 request-gate artifacts。
- 不在本 topic 提前做 VERSION bump、release tag、或 release note 落地。

## ReadOnly

- `analysis/http-client-auth-boundary/requirements.md`
- `analysis/http-client-auth-boundary/technical-spec.md`
- `tests/unit/request_contract/contract_case.py`
- `tests/unit/request_contract/job_requests_jobs_request_gate/conftest.py`
- `tests/unit/request_contract/job_requests_jobs_request_gate/test_start_job_request_contract.py`
- `plan/request-gate-jobexecution-start-job/request-gate-jobexecution-start-job.plan.md`
- `README.md`
- `docs/api-endpoints/markdown-reference/README.md`
- `VERSION`
- `pyproject.toml`

## Written

- `analysis/request-gate-saslogon-obtain-access-token/requirements.md`
- `analysis/request-gate-saslogon-obtain-access-token/technical-spec.md`
- `plan/request-gate-saslogon-obtain-access-token/request-gate-saslogon-obtain-access-token.plan.md`
- `plan/request-gate-saslogon-obtain-access-token/request-gate-saslogon-obtain-access-token.step.md`
- `plan/request-gate-saslogon-obtain-access-token/request-gate-saslogon-obtain-access-token.spec.md`
- `tests/unit/request_contract/saslogon_token_request_gate/__init__.py`
- `tests/unit/request_contract/saslogon_token_request_gate/conftest.py`
- `tests/unit/request_contract/saslogon_token_request_gate/test_obtain_access_token_request_contract.py`
- `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.request-flow.json`
- `tests/unit/request_contract/saslogon_token_request_gate/fixtures/obtain_access_token.mock-responses.json`

## Modified

- creator phase: none outside the new topic-local artifacts and new request-contract package
- release phase only:
  - `README.md`
  - `docs/api-endpoints/markdown-reference/README.md`
  - `VERSION`

## Locked Decisions

- topic name 固定為 `request-gate-saslogon-obtain-access-token`
- `client_credentials` 是唯一正向 grant shape
- 本輪正向 body 只包含 `grant_type`、`client_id`、`client_secret`
- `scope` 在本 topic 內 blocked
- topic 成果先停在 tests-side request gate；不碰 `src/**`
- docs / version alignment 延後到 final `release`
- `publish-in-progress` 不做 `README.md` / endpoint docs / `VERSION` 變更

## Blocked Variants

- blank `client_id`
- non-string `client_id`
- blank `client_secret`
- non-string `client_secret`
- 非 `client_credentials` 的 `grant_type`
- 任何 `scope` 輸入

## Release-stage Alignment Intent

- `README.md`：final release 時補上或更新
  `SASLogon/oauth/token -> obtain_access_token` 的 request-gate status 描述。
- `docs/api-endpoints/markdown-reference/README.md`：final release 時同步更新 endpoint
  inventory / status。
- `VERSION`：only at final `release`，不在本 topic creator phase 提前 bump。

## Acceptance Baseline

- topic-local 五個 analysis / plan artifacts 齊全且互相一致
- `tests/unit/request_contract/saslogon_token_request_gate/**` 是唯一 implementation surface
- 正向 case 只存在一個：`client_credentials_basic`
- `scope` 不出現在正向 fixture
- blocked variants 明確覆蓋 invalid credentials、wrong grant、以及 `scope`
- 沒有任何 `src/**` 或 auth runtime module 納入修改集合
