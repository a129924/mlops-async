# request-gate-projects-tables — Behavior Spec

## 範圍說明

本 spec 定義 `model-repository/projects` family 的 request-only gate 行為契約。`model-repository/tables` family 因 HATEOAS conditional endpoint selection（停止條件 §7）在本 topic 內無任何可執行行為。

---

## Projects Request Gate 行為規格

### 斷言層定義

本 gate 使用 **Layer 1: source-observed request-shape**。

- **宣告範圍**: sasctl 準備的 outbound request 的 method、path、required header subset、query key/value semantics、body shape。
- **不宣告**: auth 有效性、session / refresh 行為、real transport 行為、target runtime 回應、response schema、error contract。

### list_projects

#### 允許的 case

| Case ID | Method | Path | Query | Body |
|---------|--------|------|-------|------|
| `bare_get` | GET | `/modelRepository/projects` | `{}` | `null` |
| `limit_1000` | GET | `/modelRepository/projects` | `{"limit": "1000"}` | `null` |

#### Required header subset（兩個 case 共用）

- `Authorization`: scheme 必須為 `Bearer`（值前綴 `Bearer `）
- `Accept`: 必須存在（值不限）

#### Blocked variants

- `limit` 傳入除 `1000` 以外的整數值 → 觸發 `blocked_topic_scope_error`，match pattern: `"Only bare GET and limit=1000 are allowed"`
- 任何未在上表列出的 query field → 不得納入 contract

#### 不斷言的欄位

- query order
- host / port
- content-length
- connection headers
- transport-generated headers

---

### get_project_by_id

#### 允許的 case

| Case ID | Method | Path | Query | Body |
|---------|--------|------|-------|------|
| `direct_identifier` | GET | `/modelRepository/projects/{uuid}` | `{}` | `null` |

其中 `{uuid}` 為符合 UUID 格式的字串（如 `123e4567-e89b-12d3-a456-426614174001`）。

#### Required header subset

- `Authorization`: scheme 必須為 `Bearer`（值前綴 `Bearer `）
- `Accept`: 必須存在（值不限）

#### Blocked variants

| 輸入型態 | 範例 | 觸發 pattern |
|---------|------|-------------|
| 非 UUID 字串（name branch） | `"not-a-uuid"` | `"Only the direct identifier branch is allowed"` |
| dict / object（object branch） | `{"id": "...", "name": "demo"}` | `"Only the direct identifier branch is allowed"` |
| `refresh=True` | `get_project(uuid, refresh=True)` | `"refresh=True is out of scope"` |

以上 blocked variants 必須觸發 `blocked_topic_scope_error`，不得靜默執行或以 fallback 繼續。

---

## Harness 規格

### SasctlContractHarness

- 每個 `run(case)` 呼叫只允許一個 outbound request；若收到非預期 request，立即觸發 `AssertionError: Unexpected outbound request`。
- `last_request` 記錄最後一次 intercepted request 的 `method`、`path`、`query`（dict）、`headers`（dict）。
- Harness 不使用 real HTTP transport；所有 sasctl session 透過 mock/patch 機制建立。
- Harness 只使用既有 repo dependencies，不引入任何新的 package。

### blocked_topic_scope_error

- 型態：`RuntimeError` 的子類別（由 conftest fixture 提供）
- 觸發時機：呼叫者傳入 out-of-scope 參數時，由 conftest 的 scope guard 立即 raise
- 不得以 try/except 靜默處理

---

## Tables BLOCKED 規格

### 停止原因

`model-repository/tables` 的端點 URL 由前一個 project request 的 `links` 陣列動態決定（HATEOAS link resolution），無法從靜態 source 推出固定 path template。此行為觸發全域停止條件 §7: conditional endpoint selection。

### 本 topic 內的行為

- 不存在任何 tables 相關測試、fixture、或 harness。
- 不存在任何 `/modelRepository/projects/{id}/tables` 或類似路徑的 request-flow fixture。
- 若有任何工作嘗試建立 tables artifacts，必須停止並回到本 plan 對齊。

### 解除 BLOCKED 的前置條件（需人工決策）

1. 人工明確授權以下其中一種策略：
   - 接受 fixed path template 替代 HATEOAS link resolution，並標記 `intentionally_changed`；或
   - 提供可從 source 穩定推出 tables endpoint 的 HATEOAS resolution 策略。
2. 人工授權後，在獨立 topic 中從 planner 階段重新分析 `list_tables` 的 request contract。
3. 新 topic 的 analysis artifacts 必須明確記錄 HATEOAS divergence 決策，才可進入 implementation。
