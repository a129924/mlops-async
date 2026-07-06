# internal-auth-spine-mvp specification

## Goal

提供最小 internal auth spine，證明第一次 authenticated request 會 lazy resolve token，
且 token endpoint spec 只存在於 token collaborator 層的單一 source。

## Non-goals

1. 不提供 `AuthClient` public UX。
2. 不提供 broader endpoint registry。
3. 不實作 persistent token storage。
4. 不重開 obtain request-gate contract。
5. 不使用 Python 3.11 `StrEnum`。

## Current Context

1. repo 已有 `Requester`、`AuthProvider`、`TokenManager`、`TokenStorage` 的最小 internal baseline。
2. repo 尚無 concrete `TokenEndpointClient`。
3. `request-gate-saslogon-obtain-access-token` 已凍結 obtain path request contract。
4. repo Python baseline 為 `3.10`。

## Requirements

1. runtime 必須以單一 token endpoint spec source 使用 `/SASLogon/oauth/token`。
2. 只有 `TokenEndpointClient` 與未來 `AuthClient` 允許直接依賴該 spec。
3. 第一次 authenticated request 才可觸發 token obtain。
4. `TokenManager` 必須保留 reuse / fetch / expiry / lock / success-before-store。
5. `Requester` 必須維持 `Authorization` collision policy 與 `json_body`-only content-type policy。

## Decisions

- Async-planning status: triggered — topic 涉及 lazy request-time token resolution 與 shared lock coordination。
- Module placement:
  - `src/mlops_async/core/token_endpoint_client.py`
  - `src/mlops_async/core/auth.py`
  - `src/mlops_async/core/requester.py`
- New public API: no
- Breaking changes allowed: internal-only changes yes; package-root promotion no
- New dependencies: no
- Enum strategy: Python 3.10-compatible `str + Enum`; standard-library `StrEnum` forbidden

## Public Contract / API Changes

No public API changes.

Internal-only additions may include:

- `AuthTokenEndpoint`
- `TokenEndpointClient`

## Affected Files / Modules

- `analysis/internal-auth-spine-mvp/requirements.md`
- `analysis/internal-auth-spine-mvp/technical-spec.md`
- `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.plan.md`
- `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.spec.md`
- `plan/internal-auth-spine-mvp/internal-auth-spine-mvp.step.md`
- `src/mlops_async/core/token_endpoint_client.py`
- `src/mlops_async/core/auth.py`
- `src/mlops_async/core/requester.py`
- `tests/unit/core/test_token_endpoint_client.py`
- `tests/unit/core/test_token_manager.py`
- `tests/unit/core/test_auth_contract.py`
- `tests/unit/core/test_requester_auth_boundary.py`

## TestCase

1. `TokenEndpointClient` 使用 single endpoint spec source 發出正確 obtain request。
2. `TokenEndpointClient` 能把成功 JSON 回應轉成 `AccessToken`。
3. 第一次 authenticated request 之前沒有 token endpoint I/O。
4. 第一次 authenticated request 會 lazy obtain token 並注入 bearer header。
5. `TokenManager` 在 storage 為空時只 fetch 一次。
6. `TokenManager` 在 token expired 時保留 single-flight coordination。
7. `Requester` 仍拒絕 managed-auth 下的 caller `Authorization`。
8. token endpoint spec 不外溢到 `Requester` / `AuthProvider` / family client。

## Validation Commands

```bash
uv run pytest tests/unit/core/test_token_endpoint_client.py tests/unit/core/test_token_manager.py tests/unit/core/test_auth_provider.py tests/unit/core/test_auth_contract.py tests/unit/core/test_requester_auth_boundary.py tests/unit/transport/test_http_client.py
uv run ruff check src tests
uv run pyright
```

## Risks

1. 若把 token endpoint spec scope 放太高，會破壞 frozen dependency direction。
2. 若直接使用 `StrEnum`，會與 Python 3.10 baseline 衝突。
3. 若 obtain path 與 request-gate baseline 不一致，會重新引入 request drift。

## Rollback Plan

- Revert:
  - `analysis/internal-auth-spine-mvp/**`
  - `plan/internal-auth-spine-mvp/**`
  - `src/mlops_async/core/token_endpoint_client.py`
  - `src/mlops_async/core/auth.py`
  - `src/mlops_async/core/requester.py`
  - `tests/unit/core/test_token_endpoint_client.py`
  - `tests/unit/core/test_token_manager.py`
  - `tests/unit/core/test_auth_contract.py`
  - `tests/unit/core/test_requester_auth_boundary.py`

## Open Questions

- None.
