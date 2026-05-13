# Request Contract Testing Standard

## Purpose

定義 `mlops-async` 在 source 可執行時的 Request Contract Gate 標準流程，確保 request evidence 先被捕捉與固化，再進入 target request-contract tests。

## Scope

適用於：

- `sasctl`（primary）
- legacy source runner（可本機執行）

不適用於：

- 無法執行的 source（第一版直接 stop/escalate）

## Gate pass definition

當 source 可執行時，Request Contract Gate 只有在下列條件都成立時才通過：

1. fully intercepted capture 成功完成
2. request-flow fixture 已持久化
3. 可由 fixture 反推出 target request-contract test

缺任一項即不得通過 gate。

## Interception rules

1. 所有 outbound HTTP request 必須被攔截。
2. 未註冊 request 或 real-network escape 一律 fail-fast。
3. capture run 必須留下失敗證據（包含違規 request）。

## Snapshot and answer artifacts

### Required output shape

每次 capture invocation 都必須持久化兩份分離 artifact：

1. **request-flow fixture**
   - `full_observed_flow`
   - 保存觀察到的全部步驟（`auth` / `preflight` / `target-api`）與順序
2. **mock-response answer set**
   - 保存本次 invocation 為完成流程而提供的 mock responses

兩份 artifact 必須可互相追溯到同一 capture run id。

## Step purpose classification

至少支援：

- `auth`
- `preflight`
- `target-api`

可依需要擴充：

- `pagination`
- `polling`
- `refresh-token`
- `upload`
- `download`

## Request comparison rules

### Must compare

- HTTP method
- endpoint path
- required header subset
- query parameter semantics (key-value meaning)
- request body shape

### Must not compare

- query order
- transport-generated headers
- host
- content-length
- connection headers

## Auth divergence handling

當 source capture 觀察到 auth flow，但 target family 依設計不鏡像該 auth 行為時：

1. captured auth steps **不得**從 fixture 移除
2. target equivalence comparison 可排除該 auth steps
3. 必須明確記錄：
   - observed auth steps
   - target auth mode
   - excluded comparison scope
   - compatibility label: `intentionally_changed`
   - rationale

未明確記錄即視為不合格。

## Conflict policy

若 capture evidence 與 source review 對 baseline 的解讀衝突，且會改變 contract semantics：

- 一律 `blocked` / `needs-human-review`
- 禁止自動和解

## First-version stop conditions

以下情境第一版不得自動放行：

- `non_executable_source`
- `partial_capture_only`
- `upload_download`
- `pagination_expansion`
- `polling_or_retry`
- `hidden_session_side_effects`
- `unstable_repeat_capture`

## Notes for skill integration

- `api-client-porting-planner` / `api-client-porting-implementer` 應引用本標準並執行
- skill 應保留 trigger/boundary/validation 摘要，不重複定義本標準全文
