# request-header-policy-normalization requirements

## Status

- `FROZEN`

## Summary

- 本 topic 凍結 request-side header policy normalization 的 business baseline。
- 目標是把既有 request headers 差異依 family 明確集中，而不是新增通用 mutable
  `Headers` class 或擴張 public API。
- current truth 以 repo 現況為準：
  - 一般 domain request 由 `Requester` / `HttpClient` 組裝，預設
    `Accept: application/json`，且僅在 `json_body` 存在時補
    `Content-Type: application/json`
  - auth token request 由 `TokenEndpointClient` 固定送出
    `Accept: application/json` 與
    `Content-Type: application/x-www-form-urlencoded`
  - `jobExecution/jobs/state` request-contract 已凍結 family-specific `Accept`
  - `models/content` source-observed harness 已呈現 content/binary family 差異，
    但目前不屬於 repo runtime implementation surface

## Goal

- 在不改變 public API 與既有 request semantics 的前提下，建立單一 internal
  request-header policy source of truth，讓 JSON domain request、auth token
  request、family-specific `Accept` override 的規則不再分散硬編碼於多個 runtime
  call sites。
- 凍結 release/documentation intent，使本 topic 若進入 release step 時，
  `VERSION`、`pyproject.toml`、`uv.lock`、`README.md`、以及相關 docs 能與最終
  implementation truth 同步。

## Actors and Conditions

### Primary actor

- repo runtime author / maintainer
  - 需要在 `Requester`、`HttpClient`、`TokenEndpointClient` 之間維持一致的
    request-header composition policy

### Secondary actor

- reviewer / future endpoint-family author
  - 需要從單一 internal policy surface 看出不同 family 的 header baseline，
    而不是在 call sites 重新推理

### Supporting actor

- Main Agent release flow
  - topic 若完成並進入 release，需同步處理 shared release surfaces 與 README/docs
    敘述

## In-Scope Requirements

### R1. JSON domain request baseline stays centralized

- **Actor**: runtime author
- **Condition**: `Requester` 與 `HttpClient` 建立一般 JSON domain request
- **Observable outcome**:
  - 預設 `Accept: application/json`
  - 僅在 `json_body` 存在時補 `Content-Type: application/json`
  - caller/default/auth merge order 不變
- **Decision rule**:
  - JSON domain request policy 必須來自單一 internal helper surface
  - `Requester` / `HttpClient` 不得各自維護分叉的 default header rule
- **Failure meaning**: runtime family policy 分裂，reviewer 無法判定哪個 call site
  才是 source of truth

### R2. Auth token request baseline stays explicit and isolated

- **Actor**: runtime author
- **Condition**: `TokenEndpointClient` 建立 token endpoint request
- **Observable outcome**:
  - `Accept: application/json`
  - `Content-Type: application/x-www-form-urlencoded`
  - 不被一般 JSON policy 誤覆寫
- **Decision rule**:
  - auth token request policy 必須由 request-header policy surface 明確表達
  - token family 不得退回散落 literal
- **Failure meaning**: auth request family 與 JSON domain family 邊界模糊

### R3. Family-specific Accept override remains representable

- **Actor**: future family author / reviewer
- **Condition**: 某 request family 已有 repo-visible `Accept` 差異，例如
  `jobExecution/jobs/state`
- **Observable outcome**:
  - policy surface 能明確表達 family-specific `Accept`
  - 不需為了 override 而破壞通用 JSON baseline
- **Decision rule**:
  - family-specific override 必須保留為 bounded exception
  - 不得把 source-observed request-contract fixture 改寫成抽象化語言
- **Failure meaning**: 特例 family 被迫繞過 policy surface，再次回到 call-site
  hardcode

### R4. Content/binary family is a design input, not forced runtime expansion

- **Actor**: planner / reviewer
- **Condition**: `models/content` 相關 source-observed harness 顯示
  content/binary family 與 JSON request 不同
- **Observable outcome**:
  - topic 會把 content/binary family 差異記錄為 policy baseline input
  - 但不會因本 topic 強行新增尚未存在的 runtime family client implementation
- **Decision rule**:
  - content/binary family 在本 topic 可作為 read-only evidence
  - 若未來要讓 repo runtime 實際消費該 family policy，需由後續 topic 明確接手
- **Failure meaning**: planner 為了「完整抽象化」而擴 scope 到尚未存在的 runtime
  implementation

### R5. Public contract and error boundaries stay unchanged

- **Actor**: downstream caller
- **Condition**: topic 完成後使用既有 runtime surfaces
- **Observable outcome**:
  - 無 public API 變更
  - 既有 `AuthorizationConflictException`、`TokenEndpointClientError`、
    transport/default-header validation 等邊界維持既有語意
- **Decision rule**:
  - policy normalization 只允許 internal helper / internal call-site rewiring
  - 不得引入新的 public exception contract
- **Failure meaning**: internal normalization 變成 public behavior rewrite

### R6. Release and documentation surfaces stay synchronized

- **Actor**: Main Agent release flow
- **Condition**: topic merged 並進入 release step
- **Observable outcome**:
  - `README.md` status / release note 敘述與 implementation reality 一致
  - `VERSION`、`pyproject.toml`、`uv.lock` 版本同步
  - `docs/ARCHITECTURE.md` 與
    `docs/standards/http-client-auth-boundary.md` 的 request-header 描述對齊
- **Decision rule**:
  - release step surfaces 必須在 topic plan 中顯式列出
  - 不得把 release/doc alignment 留給 reviewer 臨場推理
- **Failure meaning**: repo-visible release truth 與 runtime truth 脫節

## Non-goals

- 不新增通用 mutable `Headers` class
- 不重做 response-side abstraction；`ResponseHeaders` 不在本 topic 改寫
- 不全面消滅 repo 中所有 header literals
- 不修改 request-contract fixture JSON 作為抽象化手段
- 不新增尚未存在的 content/binary runtime family client implementation
- 不更改 auth lifecycle、refresh policy、timeout policy、transport error model
- 不改 public facade / package root export / caller signatures

## Assumptions

- `docs/standards/http-client-auth-boundary.md` 與 `docs/ARCHITECTURE.md`
  為 auth/request boundary 的 read-only source of truth baseline。
- repo 目前的 content/binary family evidence 主要來自
  `tests/unit/request_contract/models_content_request_gate/**`，不是來自 `src/**`
  runtime implementation。
- `README.md` 在本 repo 同時扮演 project status 與 release-surface 敘述角色，
  因此本 topic 若 release 必須納入 README alignment。

## Surfaced Contradictions

### C1. Family-aware normalization vs no new runtime family expansion

1. 題目要求按 endpoint family 盤點差異。
2. repo runtime 目前只明確落地 JSON domain 與 auth token 兩類 request policy；
   content/binary family 主要仍存在於 source-observed harness。
3. 若直接把 content/binary 視為同等 runtime implementation target，會造成 scope
   擴張。
4. **Resolved decision**:
   content/binary family 在本 topic 作為 read-only policy evidence；runtime 消費與
   wiring 留待後續 topic。

### C2. Internal refactor topic vs release-surface inclusion

1. 本 topic 主要是 internal request-header normalization。
2. 使用者明確要求 plan 收錄 release step 會遇到的版本檔案與相關文件。
3. 若完全宣告為 non-stable topic，release surfaces 會被排除出 artifact truth。
4. **Resolved decision**:
   topic 仍維持無 public API 變更，但視為需要顯式 stable-library metadata 的 topic；
   release timing 在 `release` 階段執行，並同步 `README.md` / `VERSION` /
   `pyproject.toml` / `uv.lock`。

## Extreme-boundary Checks

- current tests all green:
  本 topic 不得假裝在修既有 failing tests；若後續驗證失敗，應視為本 topic 新引入的
  regression evidence。
- family-specific drift:
  若某 family 需要更特殊的 `Accept` / `Content-Type`，必須在 policy surface 明講，
  不能靠 caller magic headers 掩蓋。
- docs/release drift:
  若 implementation 變更已落地但 README/docs/release surface 未對齊，視為 topic
  未完成。

## Freeze Readiness

- baseline 已足以進入 technical translation 與 plan authoring。
- 後續若出現下列情況，必須停止並做人工作業對齊：
  - planner 想把 content/binary family 擴成新的 runtime endpoint-family implementation
  - planner 想以通用 mutable `Headers` class 取代 family-aware policy helper
  - planner 想以「internal-only」為由省略 release/docs surfaces
