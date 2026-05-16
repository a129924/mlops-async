# Core Concrete Client Minimal Plan

## Goal

在開始 implementation 前，凍結第一個 internal-only minimal concrete HttpClient 的正確落點與
exception contract，讓後續 creator work 只需依 `src/mlops_async/transport/http_client.py` 與
transport-local exceptions 前進，而不再受 root entry-layer、old path、或 alias 過渡設計干擾。

## Non-goals

- 本 change 不處理 auth、token state、refresh flow、retry/backoff、session persistence。
- 本 change 不新增 public facade、package-root re-export、或 `src/mlops_async/__init__.py` 的新公開匯出。
- 本 change 不引入 alias / transition layer 來保留舊的 concrete client 或 exception import path。
- 本 change 不改寫既有 `request()` / `request_json()` 的 success/failure boundary。
- 本 change 不擴張成 deeper exception package、planner family choice、README/VERSION/release 工作。

## Current Context

- `analysis/core-concrete-client-minimal/requirements.md` 與
  `analysis/core-concrete-client-minimal/technical-spec.md` 是本 topic 的 analysis baseline。
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-plan.md` 與
  `plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-step.md` 是歷史 delta 記錄；
  它們定義本次 needs-rework correction，但**不取代** parent plan / step / spec / analysis artifacts。
- 已知 drift 包含：
  - parent plan 曾把 `src/mlops_async/exceptions.py` 描述成 entry layer
  - parent spec 曾保留 `src/mlops_async/core/http_client.py` 舊路徑
  - analysis wording 曾替 root `exceptions.py` 保留 re-export 空間
- topic 的執行前提已鎖定：`core/` 保持 contract / types / options，concrete transport implementation
  只能落在 `src/mlops_async/transport/http_client.py`。

## Requirements

1. concrete client 的唯一正確 module path 必須是 `src/mlops_async/transport/http_client.py`；若
   `src/mlops_async/core/http_client.py` 存在，implementation 完成時必須刪除，且不得留下 dead/duplicate
   residual code。
2. `src/mlops_async/exceptions.py` 在 implementation 完成後只保留 `MlopsAsyncBaseException`，不得承接
   transport-specific concrete exceptions，也不得作 root re-export。
3. `src/mlops_async/transport/exceptions.py` 必須定義 `HttpErrorContext`、`HttpTransportException`、
   `HTTPStatusException`、`InvalidJSONResponseException`。
4. exception hierarchy 必須固定為：`MlopsAsyncBaseException` -> `HttpTransportException` ->
   `HTTPStatusException` / `InvalidJSONResponseException`。
5. 本 topic 不得新增 root re-export、alias、transition layer、或任何為舊 import path 保留的相容層。
6. `request()` 只在 HTTP 2xx 成功時回傳 `RawClientResponse`；non-2xx 與 transport failure 必須沿用既有
   low-level failure boundary 結束。
7. `request_json()` 只在 HTTP 2xx 且 success body 可解析為 JSON 時回傳值；non-2xx 與 non-JSON success
   body 必須維持既有 failure boundary。
8. constructor surface 只接受 `base_url`、`RequestTimeouts`、`verify`、optional low-level transport
   injection、optional `default_headers`；不得接受完整 `httpx.AsyncClient` injection。
9. auth / retry / public facade 不得被納入本 topic；docs 只允許在 `docs/ARCHITECTURE.md` 因 transport path
   變更而需要同步敘事時更新。
10. 單元測試必須覆蓋 transport path、exception placement、hierarchy、request/raw/json boundary、
    transport ownership、與無 root re-export/alias 的契約。

## Decisions

- Module/package placement: concrete client 只放在 `src/mlops_async/transport/http_client.py`；
  `src/mlops_async/exceptions.py` 只放 package-root base exception；transport-local exceptions 只放在
  `src/mlops_async/transport/exceptions.py`；若 `src/mlops_async/core/http_client.py` 存在則刪除。
- New public API: no — 本 topic 是 internal-only substrate，不新增 public facade 或 package-root export。
- Interface changes: yes — 只限 internal implementation/module placement 與 exception hierarchy 對齊；
  不引入新的 public/stable interface。
- Breaking changes allowed: yes — 允許刪除舊的 internal path、移除 `CustomException` 與 root re-export 假設，
  因為 corrected contract 明確要求無 alias / transition layer；不涉及新的 public API break。
- New dependencies: no — 維持既有 `httpx`、`pydantic`、pytest/ruff/pyright toolchain。
- Error handling strategy: `request()` / `request_json()` failure boundary 不變；transport、HTTP status、
  invalid JSON 皆由 transport-local exceptions 承接；root `exceptions.py` 只提供
  `MlopsAsyncBaseException` 作為基底。
- Typing strategy: 全面維持 strict typing；public/internal signatures 明確標註型別，不以 `Any` 或 alias
  過渡層掩蓋 boundary。

## Public Contract / API Changes

No public API changes.

本 topic 只調整 internal transport substrate 的實作位置與 exception contract。`src/mlops_async/__init__.py`
不新增 re-export，`client.py` 不提升為 public facade，也不保留 root-level exception convenience imports。

## Affected Files / Modules

Likely affected files:
- `src/mlops_async/exceptions.py`
- `src/mlops_async/transport/__init__.py`
- `src/mlops_async/transport/http_client.py`
- `src/mlops_async/transport/exceptions.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/core/test_client_contract.py`
- `docs/ARCHITECTURE.md`

Candidate files to inspect:
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/request_options.py`
- `src/mlops_async/core/http_client.py`
- `analysis/core-concrete-client-minimal/requirements.md`
- `analysis/core-concrete-client-minimal/technical-spec.md`
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-plan.md`
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-step.md`

## Implementation Steps

1. Open `src/mlops_async/core/http_client.py` and `src/mlops_async/transport/`. If the old core path exists, plan its deletion rather than preserving an alias, then create `src/mlops_async/transport/__init__.py` and `src/mlops_async/transport/http_client.py` as the only concrete client home.
2. In `src/mlops_async/transport/http_client.py`, implement the internal-only minimal concrete HttpClient so it satisfies the existing `Client` Protocol, accepts only the locked constructor parameters, owns only the `httpx.AsyncClient` it creates itself, and rejects complete `httpx.AsyncClient` injection.
3. In `src/mlops_async/transport/http_client.py`, implement request-building behavior that keeps the thin header policy: default `Accept: application/json`, add `Content-Type: application/json` only for JSON bodies, allow per-request same-name header override, and forbid client-level default params or client-level default options merge.
4. In `src/mlops_async/transport/http_client.py`, preserve the existing failure boundary by making `request()` a success-only raw path and `request_json()` a JSON-success-only path, with non-2xx, transport failures, and invalid JSON routed through the transport exception hierarchy.
5. Update `src/mlops_async/exceptions.py` so the file ends with only `MlopsAsyncBaseException`, with no transport concrete exceptions, no root re-export, and no alias / transition compatibility layer.
6. Create `src/mlops_async/transport/exceptions.py` and define `HttpErrorContext`, `HttpTransportException`, `HTTPStatusException`, and `InvalidJSONResponseException`, keeping the locked hierarchy `MlopsAsyncBaseException` -> `HttpTransportException` -> semantic subclasses.
7. Create or update `tests/unit/transport/test_http_client.py`, `tests/unit/transport/test_exceptions.py`, and `tests/unit/core/test_client_contract.py` so they verify the sole `transport/http_client.py` path, exception placement, hierarchy, request/raw/json boundaries, transport ownership, and absence of root re-export or alias behavior.
8. If implementation leaves the repository narrative misleading, update `docs/ARCHITECTURE.md` to state that the concrete internal HttpClient lives under `transport/http_client.py`, that `core/` remains contract-only, and that no public facade is introduced in this topic.

## Test Plan

Test files:
- `tests/unit/transport/test_http_client.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/core/test_client_contract.py`

Test cases:
- Happy path: 在 `tests/unit/transport/test_http_client.py` 驗證 2xx JSON request 可由 `transport/http_client.py` 成功回傳 `RawClientResponse` / decoded JSON，並套用最小 header policy。
- Invalid input: 在 `tests/unit/transport/test_http_client.py` 驗證 non-2xx response、invalid JSON success body、與被禁止的 `httpx.AsyncClient` injection 皆走失敗路徑。
- Edge case: 在 `tests/unit/transport/test_http_client.py` 與 `tests/unit/transport/test_exceptions.py` 驗證 injected transport caller-owned、per-request header override、以及空/非 JSON success body 的 exception mapping。
- Regression: 在 `tests/unit/transport/test_exceptions.py` 驗證 root `exceptions.py` 不再承接 transport concrete exceptions，且 hierarchy 維持 `MlopsAsyncBaseException` -> `HttpTransportException` -> semantic subclasses。
- Backward compatibility: 在 `tests/unit/core/test_client_contract.py` 驗證 concrete client 仍滿足既有 internal `Client` Protocol，同時不透過 root re-export、public facade、或 old `core/http_client.py` path 維持相容。

## Validation Commands

```bash
uv run pytest tests/unit/transport/test_http_client.py -v
uv run pytest tests/unit/transport/test_exceptions.py -v
uv run pytest tests/unit/core/test_client_contract.py -v
uv run pytest --cov=src/mlops_async --cov-report=term-missing
uv run pyright --strict
uv run ruff check .
```

## Risks

- 若 implementation 仍保留 `src/mlops_async/core/http_client.py` 或 root re-export convenience path，reviewer 可能誤判 corrected contract 已落地，實際上卻留下雙重實作與 import drift。
- exception hierarchy 若回退成 direct-to-root inheritance，會讓 transport-wide failure 攔截與測試 typing expectation 再次失真。

## Rollback Plan

- Revert via git: `src/mlops_async/exceptions.py`, `src/mlops_async/transport/__init__.py`, `src/mlops_async/transport/http_client.py`, `src/mlops_async/transport/exceptions.py`, `tests/unit/transport/test_http_client.py`, `tests/unit/transport/test_exceptions.py`, `tests/unit/core/test_client_contract.py`, `docs/ARCHITECTURE.md`.
- 若 rollback 發生在移除 `src/mlops_async/core/http_client.py` 之後，直接用 git 還原該檔與相關測試，再重新進行 plan correction；不得以 alias / transition layer 取代完整回滾。

## Open Questions

None.
