# http-client-auth-boundary technical specification

## Status

- `FROZEN` — derived from `analysis/http-client-auth-boundary/requirements.md`

## Source Baseline Summary

本 technical spec 以 `analysis/http-client-auth-boundary/requirements.md` 為 source of truth，將 auth/request composition baseline 轉成最小可執行的 engineering work。此 topic 不做實際 code implementation；它只凍結未來 creator work 所需的 technical realization、架構相容性、成本與 rollback triggers。

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| BR-1 | 建立 `src/mlops_async/core/requester.py` internal request composition boundary；保持 `src/mlops_async/transport/http_client.py` transport-only | `core/client.py`, `transport/http_client.py`, `docs/ARCHITECTURE.md` | 中等；需新增新模組且補 boundary tests | feasible |
| BR-2 | 在 `Requester` 加入 case-insensitive `Authorization` conflict detection，且 failure path 不呼叫 domain request `HttpClient` | `Requester`, auth-boundary tests | 低到中等；邏輯簡單，但必須用測試鎖死 precedence | feasible |
| BR-3 | `Requester` 僅在未配置 `AuthProvider` 時允許 caller `Authorization` | `Requester`, tests | 低；與 BR-2 同一邏輯面 | feasible |
| BR-4 | 建立 `AccessToken` value object 與 configurable skew expiry rule（預設 60 秒） | `src/mlops_async/core/token_storage.py`, tests | 中等；需決定 API shape 並避免把 expiry orchestration 放入 storage | feasible |
| BR-5 | `TokenManager.get_access_token()` 使用 `asyncio.Lock` + double-check locking，至少用 10 coroutine 測試 single refresh/fetch | `TokenManager`, fake `TokenFetcher`, fake `TokenStorage`, pytest-asyncio | 中等；主要成本在 deterministic async tests | feasible |
| BR-6 | 定義 auth-layer failure surface，禁止把 `TokenFetcher` failure 翻成 transport exception；Requester failure path 不進 domain transport | auth contract/tests, exception design note | 中等；需明確 exception boundary | feasible with prerequisites |
| BR-7 | refresh/fetch success 前不得覆寫 storage；failure/cancellation 保留 previous token state | `TokenManager`, `TokenStorage`, cancellation tests | 中等；需驗證 state update 時機 | feasible |
| BR-8 | 文件與測試固定依賴方向：Domain client -> `Requester` -> `HttpClient`; `AuthProvider` -> `TokenManager`; `TokenManager` -> `TokenStorage` + `TokenFetcher`; `TokenFetcher` -> raw `HttpClient` only | `docs/ARCHITECTURE.md`, tests, tach boundary awareness | 中等；主要是 boundary discipline 與 reviewer burden | feasible |

## Required Technical Tasks and Artifacts

### Workstream A — Core auth state and contracts

Required artifacts:

- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/core/auth.py`
- `tests/unit/core/test_token_storage.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_auth_provider.py`

Technical tasks:

1. 定義 `AccessToken` internal value object，至少包含 token value 與 expiry metadata。
2. 定義 `TokenStorage` contract 與最小 `InMemoryTokenStorage`。
3. 定義 `AuthProvider`、`TokenManager`、`TokenFetcher` contracts。
4. 保持 `AuthProvider` 為 thin adapter：只把 token 轉成 auth headers。

### Workstream B — Token lifecycle and concurrency control

Required artifacts:

- `src/mlops_async/core/auth.py`
- `tests/unit/core/test_token_manager.py`

Technical tasks:

1. 在 `TokenManager` 實作 request-before-refresh lifecycle。
2. 採用 `asyncio.Lock` + double-check locking。
3. 將 refresh/fetch state update 限制在成功後才寫入 storage。
4. failure/cancellation path 保留 previous token state。

### Workstream C — Request composition boundary

Required artifacts:

- `src/mlops_async/core/requester.py`
- `tests/unit/core/test_requester_auth_boundary.py`

Technical tasks:

1. 建立 `Requester` 作為唯一 request composition layer。
2. 在 `Requester` 套用 safe defaults（如 `Accept` / `Content-Type`）的 policy。
3. 配置 `AuthProvider` 時，拒絕 caller-supplied `Authorization`。
4. 未配置 `AuthProvider` 時，允許 low-level/test `Authorization` pass-through。

### Workstream D — Transport boundary preservation and documentation

Required artifacts:

- `src/mlops_async/transport/http_client.py`
- `tests/unit/transport/test_http_client.py`
- `docs/ARCHITECTURE.md`

Technical tasks:

1. 保持 `HttpClient` pure transport，不新增 auth/token lifecycle knowledge。
2. 維持 forbidden default headers 規則。
3. 在架構文件中明文化 responsibility split 與 dependency direction。

## Feasibility and Cost of Realization

| Workstream | Complexity | Sequencing pressure | Integration burden | Ongoing operational overhead |
| --- | --- | --- | --- | --- |
| Core auth state and contracts | medium | 需先於 requester 與 tests 決定 contract shape | 低到中等；主要是 internal module boundary | 低 |
| Token lifecycle and concurrency control | medium | 需在 requester wiring 前先固定 lifecycle semantics | 中等；async tests 與 state timing 容易出錯 | 低 |
| Request composition boundary | medium | 依賴 auth contracts 已固定 | 中等；與 existing `Client` / `HttpClient` contract 接合 | 低 |
| Transport/document preservation | low to medium | 可與其他 workstream 並行，但 regression tests 必須最後一起驗證 | 低 | 低 |

## Architecture-Compliance Self-Check

| Dimension | Result | Notes |
| --- | --- | --- |
| Async-first I/O | fits existing architecture | `HttpClient` 已是 `httpx.AsyncClient`-based；auth/requester 也可維持 async-first |
| Dependency direction and ownership boundaries | fits existing architecture | 新 baseline 與既有 `core` vs `transport` split 相容 |
| No import-time side effects | fits existing architecture | token fetch/refresh 只會在 method call 觸發，不需 import-time I/O |
| Stable-library surfaces | fits existing architecture | 本 topic 不宣告 public stable API，也不需 README/VERSION 變更 |
| Security / compliance expectation | fits with prerequisites | 需先把 auth-layer failure 與 header conflict policy 用 tests 鎖定，避免 ambiguous auth behavior |
| Observability / rollback support | fits with prerequisites | 需有清楚 regression tests 與 bounded artifact paths 才能安全 review / rollback |

## Conflicts, Blockers, and Rollback Triggers

### No current blockers

- 目前 requirements baseline 可完整轉譯為 technical work，沒有尚未解決的 business contradiction。

### Rollback-to-alignment triggers

若後續 creator work 出現以下情況，必須停止並回到需求對齊：

1. 需求改成支援 cross-process / distributed refresh coordination。
2. 需求改成支援 401 auto refresh/retry。
3. 需求改成在本 topic 宣告 public stable facade。
4. token endpoint contract 被發現需要在 `TokenManager` 內理解 OAuth grant details、payload schema、或 endpoint routing 才能運作。
5. library consumer success signal 不再以 docs + unit tests 為主，而改成 runtime demo / integration environment proof。

## Validation Artifacts

Expected validation surfaces:

- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_token_storage.py`
- `tests/unit/core/test_auth_provider.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`
- `tests/unit/transport/test_http_client.py`
- `docs/ARCHITECTURE.md`

Expected validation commands:

```bash
uv run pytest tests/unit/transport/test_http_client.py tests/unit/core/test_auth_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/core/test_token_manager.py tests/unit/core/test_token_storage.py tests/unit/core/test_auth_provider.py
uv run ruff check src tests
uv run pyright
uv run tach check
uv run pytest
```
