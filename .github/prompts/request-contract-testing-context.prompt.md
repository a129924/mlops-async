---
name: request-contract-testing-context
description: Single-injection prompt for sasctl / legacy source request-contract testing topics. Route to the standards doc first and stop on prompt/doc drift.
---

這份 prompt 只適用於 `sasctl` / legacy source 的 request-contract testing / request gate 類 topic。

## Agent first-read

1. 先讀 `docs/standards/request-contract-testing.md`
2. 該文件是唯一 **source of truth**
3. 本 prompt 只是新 session 的注入入口，不是第二份標準
4. 若本 prompt 與 standards doc 漂移，立即回報 `blocked` / `needs-human-review`，不要自行和解
5. 若當前工作不是 request-contract testing / request gate 類 topic，不要套用這份 baseline

## 啟動時必須能重述的四個核心語意

1. **request shape / contract**
   - method
   - endpoint path
   - required header subset
   - query parameter semantics
   - request body shape
2. **auth steps 與 mock-response handling**
   - observed auth steps 必須保留在 request-flow fixture
   - `mock-response answer set` 保存該次 capture 所需的 mock responses
   - 若 target 不鏡像 auth，必須明確記錄 excluded comparison scope 與 rationale
3. **preflight**
   - 若 source 有 preflight，必須在 observed flow 中顯式保留
4. **target-api / intercepted flow capture**
   - 所有 outbound HTTP requests 都必須納入 fully intercepted capture
   - `target-api` 是 observed flow 的一部分，不可假設只有單一步驟

## Gate 核心規則

request-contract gate 只有在下列條件都成立時才可視為通過：

1. `fully intercepted capture` 成功完成
2. `request-flow fixture` 已持久化，且包含 `full_observed_flow`
3. `mock-response answer set` 已持久化，且可追溯到同一 capture run
4. 可由 fixture 反推出 target request-contract test

## 邊界提醒

- 不要把這份 prompt 擴張成 harness / DSL / runtime redesign 指令
- 完整 contract 以 `docs/standards/request-contract-testing.md` 為準
