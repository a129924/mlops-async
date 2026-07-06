# internal-auth-spine-mvp requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結 `internal auth spine MVP` 的最小 business baseline，目標是讓 repo
  具備第一次 authenticated request 才 lazy resolve token 的最小內部能力。
- 本 topic 只補 internal auth spine，不補 public auth UX，也不開啟其他 family
  endpoint implementation。
- token endpoint path value 固定為 `/SASLogon/oauth/token`；但 runtime 不可在多處各自
  hardcode 同一路徑。

## Goal

- 建立最小 internal auth spine，讓 `Requester` 在需要 auth 時可經由：
  `AuthProvider -> TokenManager -> TokenStorage + TokenEndpointClient`
  取得 access token。
- 保持 frozen dependency direction，不得漂移成：
  - `OtherFamilyEndpoint -> AuthClient`
  - `Requester -> TokenEndpointClient`
  - `AuthProvider -> TokenEndpointClient`
  - `TokenManager -> AuthClient`
- 讓 token endpoint 規格只在 token collaborator 層有單一 source of truth。

## Actors and Conditions

### Primary actor

- repo 內部的 authenticated domain request path
  - 當 domain request 需要 managed auth header 時，必須只透過 `Requester`
    啟動 lazy token resolve。

### Secondary actor

- repo 維護者
  - 需要一個可測、可重用、且不污染 family client 邊界的 token endpoint collaborator。

### Supporting actor

- 未來的 `AuthClient`
  - 可以與 `TokenEndpointClient` 共用同一個 token endpoint spec，
    但本 topic 不實作 `AuthClient`。

## In-Scope Requirements

### R1. Lazy first authenticated request

- **Actor**: internal authenticated domain request path
- **Condition**: `Requester` 已配置 `AuthProvider`，且 `TokenStorage` 尚無有效 token
- **Observable outcome**: 第一次 authenticated request 才觸發 token obtain
- **Decision rule**:
  - `Requester.__init__` 不可預先拿 token
  - `AuthProvider.get_auth_headers()` 被呼叫前，不得發生 token endpoint I/O
- **Failure meaning**: 若不成立，`PackageLevelClient.__init__` 的 frozen baseline 會被破壞

### R2. Shared token endpoint spec source

- **Actor**: repo 維護者
- **Condition**: `TokenEndpointClient` 與未來 `AuthClient` 需要引用 token endpoint path
- **Observable outcome**: runtime 只有單一 token endpoint spec source
- **Decision rule**:
  - path value 固定為 `/SASLogon/oauth/token`
  - shared spec 只限 token collaborator 層使用
  - 若使用 enum，必須相容 Python 3.10；不得使用標準庫 `StrEnum`
- **Failure meaning**: 若不成立，後續 token path 會在多處漂移或重複定義

### R3. Token collaborator boundary

- **Actor**: repo 維護者與 reviewer
- **Condition**: 新增 token endpoint collaborator
- **Observable outcome**: 只有 `TokenEndpointClient` 與未來 `AuthClient`
  直接知道 token endpoint spec
- **Decision rule**:
  - `Requester` 不可直接依賴 token endpoint spec
  - `AuthProvider` 不可直接依賴 token endpoint spec
  - `ProjectsClient`、`ModelsClient`、`JobsClient`、`TablesClient`
    不可直接依賴 token endpoint spec
- **Failure meaning**: 若不成立，family client boundary 會再次污染

### R4. Minimal token lifecycle for MVP

- **Actor**: internal authenticated domain request path
- **Condition**: `TokenStorage` 無 token 或 token 被視為 expired
- **Observable outcome**: `TokenManager.get_access_token()` 可完成 reuse / fetch / expiry / lock
- **Decision rule**:
  - storage 有未過期 token 時，直接 reuse
  - storage 無 token 時，透過 `TokenEndpointClient` obtain
  - storage 有 expired token 時，仍可經 collaborator 完成 token renewal path
  - 成功前不得覆寫既有 `TokenStorage`
- **Failure meaning**: 若不成立，第一次 request 後的 token lifecycle 不可用或不穩定

### R5. Request composition boundary remains intact

- **Actor**: repo 維護者與 downstream family authors
- **Condition**: `Requester` 已配置 `AuthProvider`
- **Observable outcome**: `Requester` 只負責 request composition 與 auth header integration
- **Decision rule**:
  - 仍拒絕 caller-supplied `Authorization`
  - 只有 `json_body` 存在時才補 `Content-Type: application/json`
  - 不直接組 token endpoint request
- **Failure meaning**: 若不成立，transport/auth boundary 重新漂移

## Non-goals

- 不建立 `AuthClient` public UX
- 不凍結 `AuthClient` method naming
- 不補齊 `refresh_access_token` request-gate 以外的完整 refresh runtime contract
- 不建立 persistent token storage
- 不建立 broader endpoint registry
- 不把 enum/spec carrier 提升成全 repo shared endpoint system
- 不進入 `projects` / `models` / `jobs` / `tables` family implementation

## Assumptions

- `request-gate-saslogon-obtain-access-token` 已提供 obtain path request baseline。
- repo 支援 Python `3.10`，因此本 topic 的 enum 選擇不得依賴標準庫 `StrEnum`。
- 既有 `Requester` / `TokenManager` / `AuthProvider` / `TokenStorage` internal surfaces
  可作為本 topic 的 parent baseline。

## Surfaced Contradictions

### C1. Shared token endpoint spec vs broadened dependency surface

1. 需求希望避免 token endpoint path 在兩邊重複寫死。
2. 但若把 shared spec 提升給 `Requester` 或 family client，會違反 frozen dependency direction。
3. 兩者不能同時為真。
4. **Resolved decision**:
   shared token endpoint spec 只供 `TokenEndpointClient` 與未來 `AuthClient` 使用，
   不向更高層擴散。

### C2. MVP obtain-only path vs full refresh behavior

1. 本 topic 只允許 `TokenEndpointClient` 落地 obtain path。
2. 但 `TokenManager` 仍需處理 expired token。
3. 若要求完整 refresh grant，topic 會超出 MVP 範圍。
4. **Resolved decision**:
   本 topic 只要求 collaborator 以最小 renewal path 讓 `TokenManager` 完成 expired
   token 的 token renewal；正式 refresh grant contract 另屬後續 topic。

## Extreme-boundary Checks

- no network or degraded dependency:
  token endpoint failure 必須停在 auth-layer，不可讓 domain transport 假裝成功。
- wrong user role or missing approval:
  本 topic 不建立 public user role；若未來 `AuthClient` 需要額外權限模型，另開 topic。
- interrupted or partial completion:
  token obtain 失敗或 cancellation 時，不得覆寫既有 token state。
- low-volume and peak-volume conditions:
  多 coroutine 共用一個 `TokenManager` 時，仍需 single-flight coordination。

## Freeze Readiness

- 本 baseline 已可進 technical translation。
- 若後續有人要求：
  - 把 shared token endpoint spec 擴到 `Requester` / family client
  - 把 enum 擴成 broader endpoint registry
  - 直接使用標準庫 `StrEnum`
  則必須 rollback 到 alignment，不得在 technical spec 中靜默吸收。
