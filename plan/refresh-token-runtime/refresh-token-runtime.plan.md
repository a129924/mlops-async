# refresh-token-runtime

> **Analysis-layer semantic warning**
>
> `analysis/refresh-token-runtime/requirements.md` 與
> `analysis/refresh-token-runtime/technical-spec.md` 均不存在。此 plan 依已接受的
> human baseline 與 current-code evidence 撰寫；不得重用 historical
> `request-gate-saslogon-refresh-access-token` 的 tests-only / shape-only artifacts。

## Goal / Outcome

### Goal

在既有 injected async `Client`、`PasswordTokenEndpointClient` 與
`TokenManager` 架構中，實作 internal refresh-token state 與真正 refresh grant，
不新增或修改 public obtain/refresh API。

## Scope

### In-Scope

- password obtain response 的 refresh-token validation 與 internal state。
- refresh response omission 時保留舊 token；提供有效 token 時原子 rotation。
- 既有 async lifecycle、failure、cancellation、concurrency contract 的測試。
- feature PR 內的 docs 與 `0.15.0` version synchronization。

### Out-Of-Scope

- 新 public API、package-root export、facade、sync `httpx.Client`、retry/backoff、
  timeout policy、persistent storage。
- `scope` 或 refresh form-body 的 `client_id` / `client_secret` variants。
- historical request-gate artifacts、tag 與正式 release。

## Non-goals

### Non-Goal

- 本變更不會改變 `AuthClient`、`TokenStorage` protocol 或
  `TokenEndpointClientProtocol` signatures。
- 本變更不會改變 UTC expiry / 60-second skew、Basic Auth 或 `sas.ec` exception。
- 本變更不會新增 dependency 或擴張 transport lifecycle ownership。
- 本變更不會修改 historical refresh request-gate 的 frozen scope。

## Current Context

`src/mlops_async/core/token_endpoint/password.py` 的
`PasswordTokenEndpointClient.refresh_access_token()` 目前重跑 password grant。
`src/mlops_async/core/token_storage.py::AccessToken` 尚未保存 refresh token；
`TokenManager` 已具 double-check `asyncio.Lock`、成功後單次 storage replacement、
generic exception 到 `TokenFetchException` 的 translation 與 cancellation passthrough。

### ReadOnly

- `reference/docs/refresh-token.md`
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/headers.py`
- `tests/unit/clients/test_auth_client.py`
- `analysis/request-gate-saslogon-refresh-access-token/requirements.md`
- `analysis/request-gate-saslogon-refresh-access-token/technical-spec.md`
- `plan/request-gate-saslogon-refresh-access-token/request-gate-saslogon-refresh-access-token.plan.md`

### Repository-relative path rule

Every artifact path written is repository-relative. No absolute path may be written into
any artifact. `reference/docs/refresh-token.md` remains ReadOnly under this rule.

## Requirements

1. password obtain 成功 response 必須含非空字串 `refresh_token`；否則在 endpoint
   boundary 失敗。
2. refresh 必須使用 injected async client、existing Basic Auth、token headers，並送出
   `grant_type=refresh_token` 與既有 refresh token。
3. refresh response 缺省 `refresh_token` 時，新 access state 必須保留先前 refresh token。
4. refresh response 提供有效 `refresh_token` 時，access token、expiry、refresh token
   必須作為一個 immutable state 被單次替換。
5. 在單次 storage replacement 前，`TokenManager` 必須把 refresh response 缺省的
   `refresh_token` 正規化為 cached refresh token；回傳相同的完整 immutable state，
   並在 response 提供有效 token 時採用 rotation。
6. fetch、generic endpoint、transport 或 schema failure 仍須維持既有 semantics：
   generic failure 轉成 chained `TokenFetchException`，`AuthException` 與 cancellation
   原樣傳播，且不覆寫舊 state。
7. 既有 UTC expiry、60-second skew、`sas.ec` empty-secret exception、protocol signatures
   與 public import surface 必須保持相容。
8. `VERSION`、`pyproject.toml` 與 `uv.lock` 必須同步為 `0.15.0`，並更新指定 docs。

## Decisions

- Async-planning status: triggered — cite trigger evidence: async `Client.request_json()`,
  `PasswordTokenEndpointClient` async fetch/refresh，以及 `TokenManager` 的
  `asyncio.Lock`、refresh lifecycle、exception translation 與 cancellation contract。
- Module/package placement: `src/mlops_async/core/token_storage.py`、
  `src/mlops_async/core/token_endpoint/_shared.py`、
  `src/mlops_async/core/token_endpoint/password.py`、`src/mlops_async/core/auth.py`。
- New public API: no。
- Interface changes: no public/protocol change；`AccessToken` 僅新增具預設值的 internal
  refresh-token state。
- Breaking changes allowed: no。
- New dependencies: no。
- Error handling strategy: 沿用 `TokenEndpointClientError` 與
  `TokenFetchException` translation。
- Typing strategy: 維持 Pyright strict，internal refresh state 使用 `str | None`，不使用
  `Any`，不引入 public Pydantic response model。

### Locked Decisions

- password obtain 必有 refresh token；refresh response omission 保留舊值，有效提供時
  原子 rotation。
- `TokenManager` 在單次 storage replacement 前正規化缺省 refresh token，使回傳與
  storage replacement 為相同完整 immutable state；fetch/failure/AuthException/cancellation
  semantics 不變。
- `AuthClient` 不取得 refresh 或 grant-selection responsibility；endpoint client 不直接
  寫 `TokenStorage`。
- topic 影響 stable-library surfaces；docs/version timing 是 `publish-in-progress`，納入
  feature PR。
- merge 後 tag/release 需另一個 human gate；本 topic 不授權 `merged -> released`。

### Boundaries / Exclusions

- `TokenManager` 不理解 endpoint form-body 或 Basic credentials。
- endpoint client 不建立/關閉 transport，也不建立 task、queue 或 worker。
- 任何未列 Artifact Paths 的 source、test、doc、API 或 dependency path 都是 scope drift。

### Status / Allowed Transitions

- **Current**: `review-ready`。
- **Execution model**: creator -> reviewer -> publish -> merge；implementation 需後續
  human confirmation。
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

### Async boundary decision

維持 injected async `Client` 的 direct await；不得建立 sync client、task、queue 或 worker。

### Resource lifecycle decision

caller 擁有 transport；endpoint client 不 close transport、不直接寫 storage；
`TokenManager` 是唯一 state-update owner。

### Concurrency model

維持 `TokenManager` double-check lock；多個 expired-token callers 僅允許一個 refresh
request，成功後單次發佈完整 state。

### Failure model

obtain response 缺少或含無效 refresh token 時失敗。`TokenManager` 在單次 storage
replacement 前，將 refresh response 缺省欄位正規化為 cached refresh token；有效提供
欄位時採用 rotation。欄位存在但無效時失敗。fetch/failure/AuthException/cancellation
semantics 不變，且成功前不得修改 storage。

### Cancellation / timeout policy

`asyncio.CancelledError` 原樣傳播；timeout 仍由 caller-configured transport 決定；
不新增 retry 或 backoff。

### Validation plan

覆蓋 obtain validation、omission preservation、rotation、single-refresh concurrency、
failure/cancellation preservation、Basic Auth / `sas.ec` compatibility 與 public-boundary
non-regression。

### Handoff notes for the implementer

若實作需要改變 public surface、protocol、transport ownership、expiry policy 或新的 state
model，停止並回到 planning gate。

### Async contradiction log

| Contradiction | Source A | Source B | Risk impact | Decision owner / next action | Classification |
| --- | --- | --- | --- | --- | --- |
| sync direct httpx API | `reference/docs/refresh-token.md` | existing injected async Client | bypasses lifecycle and cancellation ownership | human baseline selects current runtime | non-blocking |
| 10-second naive expiry | draft computed field | UTC AccessToken / 60-second skew | two expiry truths | retain current policy | non-blocking |
| complete public response model | draft Pydantic model | current internal parser | expands public/schema surface | add only internal refresh state | non-blocking |
| password re-obtain MVP | current password client | true refresh grant baseline | incorrect refresh lifecycle | update password refresh path | non-blocking |

## Public Contract / API Changes

No public API changes. `AuthClient`、package exports、`TokenStorage` protocol、
`TokenEndpointClientProtocol` method signatures 與既有
`AccessToken(value, expires_at)` construction 均保持相容。

## Affected Files / Modules

### Written

- `plan/refresh-token-runtime/refresh-token-runtime.plan.md`
- `plan/refresh-token-runtime/refresh-token-runtime.step.md`
- `plan/refresh-token-runtime/refresh-token-runtime.spec.md`

### Modify

- `src/mlops_async/core/token_storage.py`
- `src/mlops_async/core/token_endpoint/_shared.py`
- `src/mlops_async/core/token_endpoint/password.py`
- `src/mlops_async/core/auth.py`
- `tests/unit/core/test_token_storage.py`
- `tests/unit/core/test_password_token_endpoint_client.py`
- `tests/unit/core/test_token_manager.py`
- `README.md`
- `docs/standards/http-client-auth-boundary.md`
- `VERSION`
- `pyproject.toml`
- `uv.lock`

### Deleted

- None.

### Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/refresh-token-runtime/refresh-token-runtime.plan.md` | Plan-Creator | execution contract |
| Step tracker | `plan/refresh-token-runtime/refresh-token-runtime.step.md` | Plan-Creator | workflow gate |
| Behavior spec | `plan/refresh-token-runtime/refresh-token-runtime.spec.md` | Plan-Creator | non-trivial acceptance contract |
| Token state | `src/mlops_async/core/token_storage.py` | Code-Implementer | internal access/refresh state |
| Shared parsing | `src/mlops_async/core/token_endpoint/_shared.py` | Code-Implementer | response validation/state construction |
| Password endpoint | `src/mlops_async/core/token_endpoint/password.py` | Code-Implementer | obtain/refresh behavior |
| Token manager | `src/mlops_async/core/auth.py` | Code-Implementer | omission normalization before one storage replacement |
| Unit tests | `tests/unit/core/test_token_storage.py` | Code-Implementer | state compatibility tests |
| Unit tests | `tests/unit/core/test_password_token_endpoint_client.py` | Code-Implementer | endpoint behavior |
| Unit tests | `tests/unit/core/test_token_manager.py` | Code-Implementer | concurrency/failure/cancellation proof |
| Release documentation | `README.md` | Code-Implementer | runtime release truth |
| Boundary documentation | `docs/standards/http-client-auth-boundary.md` | Code-Implementer | state ownership/rotation |
| Version source | `VERSION` | Code-Implementer | `0.15.0` |
| Package metadata | `pyproject.toml` | Code-Implementer | synchronized version |
| Lockfile | `uv.lock` | Code-Implementer | synchronized metadata |

### Stable library metadata

- `README row`: 更新舊有 runtime-excluded 描述，使其與 v0.15.0 runtime behavior 一致。
- `VERSION bump`: `0.14.0` -> `0.15.0`。
- `timing`: `publish-in-progress`，納入 feature PR。
- `rationale`: runtime behavior、docs 與 version source 必須同步。
- `release-note expectations`: feature PR 說明 true refresh grant、omit-preserve、rotation
  與 public API 不變；tag/release 不在本 topic 授權內。

## Implementation Steps

1. 修改 `src/mlops_async/core/token_storage.py`，加入 compatible internal refresh-token state。
2. 修改 `src/mlops_async/core/token_endpoint/_shared.py`，支援 obtain-required 與
   refresh-preserve-or-rotate validation。
3. 修改 `src/mlops_async/core/token_endpoint/password.py`，以 refresh grant 取代
   re-obtain MVP。
4. 修改 `src/mlops_async/core/auth.py`，在單次 storage replacement 前將缺省 refresh
   token 正規化為 cached refresh token，維持同一完整 immutable state、valid rotation、
   fetch/failure/AuthException/cancellation semantics。
5. 擴充 `tests/unit/core/test_token_storage.py` 與
   `tests/unit/core/test_password_token_endpoint_client.py`，覆蓋 state、endpoint、
   response 與 compatibility behavior。
6. 擴充 `tests/unit/core/test_token_manager.py`，覆蓋 normalization、atomicity、
   concurrency、failure 與 cancellation。
7. 更新 `README.md` 與 `docs/standards/http-client-auth-boundary.md`。
8. 將 `VERSION` 與 `pyproject.toml` 設為 `0.15.0`，再更新 `uv.lock`。

## Test Plan

### TestCase

- Happy path: password obtain 初始化 refresh state；expired state 成功 refresh。
- Invalid input: obtain 或 refresh response 的 refresh token 缺失、空白、非字串。
- Edge case: refresh response omission 保留舊 token；提供新 token 完整 rotation。
- Manager normalization TestCase: cached state 有 refresh token 且 refresh response 缺省
  `refresh_token` 時，`TokenManager` 在單次 storage replacement 前補入 cached token，
  回傳相同完整 immutable state；提供有效 token 時 rotation，
  fetch/failure/AuthException/cancellation semantics 不變。
- Regression: 十個 concurrent waiters 僅一次 refresh；failure/cancellation 保留舊 state。
- Backward compatibility: existing `AccessToken` construction、client-credentials behavior、
  `AuthClient` boundary 與 protocol signatures 不變。

## Validation Commands

```powershell
uv run --frozen python -m ruff format --check .
uv run --frozen python -m ruff check .
uv run --frozen python -m pyright
uv run --frozen python -m tach check
uv run --frozen python -m pytest -m "not viya_e2e"
uv lock --check
```

### Validation / Acceptance Checks

- 修改限定於 Artifact Paths；不新增 public API、dependency、sync client、retry policy
  或 transport lifecycle owner。
- `VERSION`、`pyproject.toml` 與 `uv.lock` 同步為 `0.15.0`。
- CI-equivalent validation 成功後才可送獨立 reviewer。

### Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

### Post-merge / release actions

merge 後停止於 `merged`。tag、GitHub release 與任何 `merged -> released` 動作均需
新的 human authorization，不由本 feature PR 自動執行。

## Risks

- optional state field 若無 default，可能破壞既有 construction。
- endpoint client 若直接寫 storage，會破壞 TokenManager ownership。
- version source / lockfile 不同步會使 feature PR metadata 不一致。
- Windows WDAC/Code Integrity 可能妨礙 local validation；不得將 environment failure
  誤判為 code failure。

## Rollback Plan

revert 所有 `Modify` paths；不刪除或修改 historical request-gate artifacts。若已進入
PR，停止 publish/release 並等待 human decision。

## Open Questions / Unresolved Items

### Open Questions

None. analysis-layer warning 已接受；implementation、docs/version 寫入、commit、push、
PR、tag 與 release 仍各自需要後續授權。

### Stop conditions

- 尚未收到 implementation confirmation：不得修改 source、tests、docs、version 或 lockfile。
- 任一需求擴張至 public API、protocol、sync client、retry、timeout policy、credential
  variants 或未列 path：停止並 re-plan。
- merge 後停止；不得 tag 或 release，直到新的 human gate。
