# Request Contract Testing Requirements

## Purpose

本文件凍結 `mlops-async` 在 source 可執行時的 Request Contract Gate 業務基線：

- 先在 fully intercepted HTTP 環境跑 source (`sasctl` 或 legacy code)
- 捕捉完整 request flow
- 產生可追溯 fixture
- 再反推 target async client 的 request-contract tests

## Scope

本需求只涵蓋「request contract evidence 取得與驗證 gate」，不涵蓋 production endpoint implementation。

適用來源：

- `sasctl`（第一優先）
- legacy `sas-api` 或其他可本機執行的 source runner

## Actors and ownership

- Planner agent：定義 capture 範圍、分類規則與 stop flags
- Implementer agent：執行 capture、輸出 fixture、建立 request-contract tests
- Human reviewer：衝突仲裁與 override

Ownership model:

- `shared_with_human_override`

## Measurable requirements

1. **Executable source gate**
   - Condition: source 可執行
   - Required outcome: 必須完成 `capture -> fixture -> derived request-contract test`
   - Acceptance signal: 三者缺一不可；任一缺失即 gate 不通過

2. **Full observed flow capture**
   - Condition: 執行單一 source invocation
   - Required outcome: capture fixture 必須包含該次 invocation 觀察到的全部步驟（`auth` / `preflight` / `target-api`）與順序
   - Acceptance signal: fixture 中存在 step-ordered flow，且無「僅保留 target-api」的截斷

3. **No real-network escape**
   - Condition: capture run 期間
   - Required outcome: 所有 outbound request 均被攔截；未註冊或外逃 request 直接失敗
   - Acceptance signal: run result 為 fail-fast 並留下違規 request 證據

4. **Answer persistence**
   - Condition: source invocation 需要 mock 回應才能完成
   - Required outcome: 持久化兩份分離 artifact
     - request-flow fixture
     - mock-response answer set
   - Acceptance signal: 兩份檔案皆可追溯到同一 capture run

5. **Auth divergence handling**
   - Condition: source capture 有 auth flow，但 target family 故意不鏡像 auth 行為
   - Required outcome: auth steps 仍保留在 fixture；comparison 可排除該步驟，但必須標記 `intentionally_changed` 並記錄理由
   - Acceptance signal: 不允許靜默刪除 auth steps

6. **Conflict escalation**
   - Condition: capture 與 source review 結論衝突，且會改變 contract baseline
   - Required outcome: 一律阻擋自動推進並升級人決策
   - Acceptance signal: decision 標記為 blocked / needs-human-review，不得自動和解

## Contradictions surfaced and resolved

1. `capture mandatory for executable source` vs `source review is still required`
   - Resolution: capture 是主要證據來源；source review 是變體與歧義補充；衝突時人決策

2. `target may not mirror auth` vs `capture must preserve observed truth`
   - Resolution: 保留 auth steps 於 fixture，差異以 `intentionally_changed` 明確記錄

## Extreme-boundary checks

以下情境第一版不得自動放行，需 stop 或升級人工：

- `non_executable_source`
- `partial_capture_only`
- `upload_download`
- `pagination_expansion`
- `polling_or_retry`
- `hidden_session_side_effects`
- `unstable_repeat_capture`

## Non-goals

- 不在此需求直接實作 `src/mlops_async/**` endpoint code
- 不保證單次 capture 可覆蓋所有輸入變化
- 不在第一版自動處理高風險/不穩定家族的自動平移

## Blockers

本需求目前無未決 blocker，可進入 technical translation。

## Freeze status

Status: `FROZEN`
