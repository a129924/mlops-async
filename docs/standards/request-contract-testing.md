# 請求合約測試標準

## 目的

定義 `mlops-async` 在 source 可執行時的 `Request Contract Gate` 標準流程，確保 request evidence 先被捕捉與固化，再進入 target request-contract tests。

本文件是 `sasctl` / legacy source 的 request-contract testing / request gate 類 topic 的
**source of truth**。`.github/prompts/request-contract-testing-context.prompt.md` 只是一份可供
新 session 注入的 prompt 入口，不得獨立重寫或覆蓋本文件的 contract。

若 prompt 與本文件漂移，Agent 必須立即停止並回報 `blocked` / `needs-human-review`，不得自行
和解。

## Agent first-read / session reuse

當新 session 要處理 request-contract testing topic 時：

1. 可先注入 `.github/prompts/request-contract-testing-context.prompt.md`
2. Agent 隨後必須回到本文件，並以本文件作為唯一正式標準
3. 若當前 topic 不是 request-contract testing / request gate 類工作，不得套用這份 baseline

這個 first-read 路徑的目的，是讓 Main Agent 或 human operator 不必回溯舊 session history，
也能恢復最小可執行語意。

## 範圍

適用於：

- `sasctl`（primary）
- legacy source runner（可本機執行）

不適用於：

- 無法執行的 source（第一版直接 stop/escalate）

## 新 session 必須能恢復的四個核心測試語意

1. **request shape / contract**
   - 核心是比對 request contract，而不是只看 endpoint 名稱
   - 至少涵蓋 method、endpoint path、required header subset、query parameter semantics、
     request body shape
2. **auth steps 與 mock-response handling**
   - observed auth steps 屬於 capture evidence，不得因 target 設計不同而從 flow 移除
   - `mock-response answer set` 必須保存為完成該次 capture 所提供的 mock responses
3. **preflight**
   - 若 source 在 target-api 前先做 preflight，必須在 observed flow 中顯式保留
   - 不可把獨立的 preflight request 靜默折疊進 target-api
4. **target-api / intercepted flow capture**
   - target-api 是 observed flow 的一部分，不是唯一部分
   - capture 必須完整攔截 outbound HTTP requests，才能作為後續 target request-contract test
     的基礎

## Request-contract gate 核心三件事

每個新 session 在進入實作或測試設計前，都必須先能明確重述下列 gate 核心：

1. **fully intercepted capture**
2. **request-flow fixture**
3. **mock-response answer set**

缺少任何一項，都不能宣告 request-contract gate 通過。

## Gate 通過定義

當 source 可執行時，`Request Contract Gate` 只有在下列條件都成立時才通過：

1. fully intercepted capture 成功完成
2. request-flow fixture 已持久化
3. mock-response answer set 已持久化
4. 可由 fixture 反推出 target request-contract test

缺任一項即不得通過 gate。

## 攔截規則

1. 所有 outbound HTTP request 必須被攔截。
2. 未註冊 request 或 real-network escape 一律 fail-fast。
3. capture run 必須留下失敗證據（包含違規 request）。

## 快照與回應產物

### 必要輸出格式

每次 capture invocation 都必須持久化兩份分離 artifact：

1. **request-flow fixture**
   - `full_observed_flow`
   - 保存觀察到的全部步驟（`auth` / `preflight` / `target-api`）與順序
2. **mock-response answer set**
   - 保存本次 invocation 為完成流程而提供的 mock responses

兩份 artifact 必須可互相追溯到同一 capture run id。

## 步驟用途分類

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

## 請求比對規則

### 必須比對

- HTTP method
- endpoint path
- required header subset
- query parameter semantics (key-value meaning)
- request body shape

### 不得比對

- query order
- transport-generated headers
- host
- content-length
- connection headers

## Auth 差異處理

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

## 衝突處理政策

若 capture evidence 與 source review 對 baseline 的解讀衝突，且會改變 contract semantics：

- 一律 `blocked` / `needs-human-review`
- 禁止自動和解

## 第一版停止條件

以下情境第一版不得自動放行：

- `non_executable_source`
- `partial_capture_only`
- `upload_download`
- `pagination_expansion`
- `polling_or_retry`
- `hidden_session_side_effects`
- `unstable_repeat_capture`

## 技能整合備註

- `api-client-porting-planner` / `api-client-porting-implementer` 應引用本標準並執行
- skill 應保留 trigger/boundary/validation 摘要，不重複定義本標準全文
