# internal-auth-spine-mvp technical specification

## Status

- `FROZEN`

## Source Baseline Summary

- 本 technical spec 以 `analysis/internal-auth-spine-mvp/requirements.md`
  為 business baseline。
- 既有 architecture baseline 以：
  - `docs/ARCHITECTURE.md`
  - `docs/standards/http-client-auth-boundary.md`
  - `analysis/request-gate-saslogon-obtain-access-token/technical-spec.md`
  為 read-only source of truth。

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 lazy first authenticated request | 保留 `Requester -> AuthProvider -> TokenManager` 觸發鏈，新增 concrete `TokenEndpointClient`，以測試證明 first request 才 obtain token | existing `Requester`, `AuthProvider`, `TokenManager`, `Client` | 低到中；主要是 wiring 與 regression tests | feasible |
| R2 shared token endpoint spec source | 新增 token collaborator-local spec carrier，固定 `/SASLogon/oauth/token`，禁止 runtime 雙重 path literal | Python 3.10 enum support, token collaborator module | 低；單一路徑值但需 boundary test | feasible |
| R3 token collaborator boundary | 新增 boundary tests，確保 spec 不外溢到 `Requester` / family client | internal module boundaries | 低 | feasible |
| R4 minimal token lifecycle for MVP | 在既有 `TokenManager` 上導入 concrete collaborator；empty / expired path 都能取得新 token，保留 lock 與 state safety | `TokenStorage`, `TokenEndpointClient`, auth exceptions | 中；要避免 breaking current tests | feasible with prerequisites |
| R5 request composition boundary remains intact | 保留 `Requester` 現有 collision / JSON content-type policy，新增 lazy obtain integration test | existing requester tests | 低 | feasible |

## Technical Realization

### Workstream 1: Topic artifacts

- 建立：
  - `analysis/internal-auth-spine-mvp/requirements.md`
  - `analysis/internal-auth-spine-mvp/technical-spec.md`
  - `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.plan.md`
  - `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md`
  - `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md`
- topic artifacts 必須明文記錄：
  - token endpoint path 固定為 `/SASLogon/oauth/token`
  - Python 3.10 constraint
  - `StrEnum` 不可用
  - shared spec scope 只限 token collaborator 層

### Workstream 2: Token collaborator module

- 新增 internal-only token collaborator module。
- 內容至少包含：
  - Python 3.10 相容的 token endpoint spec carrier
  - concrete `TokenEndpointClient`
  - obtain path request construction
  - response -> `AccessToken` translation
- request contract 必須對齊既有 obtain request-gate：
  - `POST /SASLogon/oauth/token`
  - `Accept: application/json`
  - `Content-Type: application/x-www-form-urlencoded`
  - `grant_type=client_credentials`

### Workstream 3: TokenManager integration

- `TokenManager` 不再只停留在 abstract fetcher concept；需能直接與 token endpoint collaborator 協作。
- 必須保留：
  - reuse fast path
  - lock + double-check locking
  - success-before-store
  - auth exception direct propagation
  - generic exception -> `TokenFetchException`
- 對 MVP 而言，expired token 的 renewal path 可由 collaborator 以 obtain path 完成等價 renewal，
  不要求在本 topic 落地獨立 refresh grant contract。

### Workstream 4: Lazy auth integration proof

- 補一組 integration-style unit test，證明：
  - 建立 `Requester` / `AuthProvider` / `TokenManager` / `TokenEndpointClient`
    不會先打 token endpoint
  - 第一次 authenticated request 才會打 token endpoint
  - 成功後 final request 帶有 `Authorization: Bearer ...`

## Architecture-compliance Self-check

### Dependency direction

- `fits existing architecture`
- 原因：
  - `Requester` 仍只依賴 `AuthProvider`
  - `AuthProvider` 仍只依賴 `TokenManager`
  - `TokenManager` 依賴 `TokenStorage` + token collaborator
  - token endpoint spec 不外溢到 family client

### Python version compatibility

- `fits with prerequisites`
- prerequisite:
  - enum carrier 必須相容 Python 3.10
- explicit non-fit:
  - 標準庫 `StrEnum` 與 repo `requires-python >=3.10,<3.11` 不相容

### Request-gate alignment

- `fits existing architecture`
- obtain path request shape 直接沿用既有 request-gate baseline，不重開 contract 設計。

## Cost-of-realization

- Artifact authoring:
  - 低；新增 topic-local analysis / plan artifacts
- Runtime collaborator:
  - 中；需要把 abstract fetcher 概念收斂到 concrete collaborator，同時避免破壞既有 tests
- Test updates:
  - 中；需要新增 token endpoint collaborator tests 與 lazy auth proof tests
- Operational burden:
  - 低；本 topic 不新增 persistent storage、metrics、retry、release work

## Conflicts and Rollback Triggers

### Rollback trigger 1

- Failing business assumption:
  shared token endpoint spec 可以向更高層共享
- Contradicting technical fact:
  這會直接破壞 frozen dependency direction
- Required decision:
  若真要 broader endpoint registry，必須另開 topic

### Rollback trigger 2

- Failing business assumption:
  本 topic 可直接使用 `StrEnum`
- Contradicting technical fact:
  repo 鎖定 Python 3.10
- Required decision:
  保持 `str + Enum` 或更小的 internal carrier；若要 `StrEnum` 必須先改專案 Python baseline

### Rollback trigger 3

- Failing business assumption:
  本 topic 可以同時完成完整 refresh runtime contract
- Contradicting technical fact:
  這會超出 obtain-only collaborator MVP 與既定 scope
- Required decision:
  refresh grant contract 另開 topic

## Validation Artifacts

- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/transport/test_http_client.py`（若需 regression 補強）

## Validation Commands

```bash
uv run pytest tests/unit/core/test_token_endpoint_client.py tests/unit/core/test_token_manager.py tests/unit/core/test_auth_provider.py tests/unit/core/test_auth_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/transport/test_http_client.py
uv run ruff check src tests
uv run pyright
```
