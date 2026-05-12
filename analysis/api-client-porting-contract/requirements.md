# API Client Porting Contract Requirements

## Purpose

本文件凍結 `mlops-async` 平移 `sasctl` 與 legacy SDK API 時的 Agent 行為需求。此階段要固定的是「Agent 如何判斷、測試、留下證據、何時停止」，不是先固定最終 client 架構或實作所有 SAS Viya endpoint。

## Scope

本需求適用於任何將來源 SDK API 平移成 `mlops-async` async-first client 行為的工作，第一個 primary source 是：

- `sasctl`
- legacy `sas-api` repository（實際本機或遠端路徑由使用者提供）

本需求不直接要求修改 `src/mlops_async/` production code。production code 應在後續 endpoint family topic plan 中依本合約執行。

## Core Rule

Agent 不得從直覺開始實作 target async method。每個 ported API 必須先通過下列順序：

1. Source discovery
2. Request contract extraction
3. Request contract test first
4. Minimal implementation
5. Response contract extraction
6. Pydantic external schema definition
7. Response contract test
8. Error contract test
9. Porting ledger update
10. Stop / continue decision

## Required Planner Behavior

Planner 類工作只能分析，不得實作 production client method。每個 endpoint family 或 source function set 必須輸出：

- endpoint family map
- source API list
- request contract draft
- risk classification
- porting order
- stop flags
- human-review notes

Planner 必須記錄 source SDK module、function、file、line range、source commit 或可追溯版本資訊。

## Request Contract Gate

在 target method implementation 前，Agent 必須先擷取並記錄：

```yaml
source:
  sdk:
  module:
  function:
  file:
  line_range:
  commit:

request_contract:
  method:
  path:
  required_headers:
  query_params:
  body:
  auth_behavior:
```

Request contract test 必須先於 minimal implementation 建立，並驗證：

- HTTP method
- endpoint path
- required header subset
- query parameter key-value semantics
- request body shape

Request contract test 不得驗證：

- query parameter order
- transport-generated headers
- content length
- host
- connection headers

## Batch Porting Rule

同一 endpoint family 至少兩個 API 通過 request contract tests 且沒有 ambiguity 後，Agent 可以沿用相同 request pattern 處理同 family 的其他 API。

Agent 不得跨 endpoint family 自動套用 pattern。

遇到下列任一情況時，Agent 必須停止自動批次展開並標記 human review：

- upload / download
- streaming
- polling 或 job status wait
- retry behavior
- pagination expansion
- global session side effects
- conditional endpoint selection
- request contract 無法從 source 穩定推出
- response fixture 不足以定義 schema
- source function 包含非 HTTP wrapper 的複雜行為

## Response Contract Gate

Request contract 穩定後，Agent 才能進入 response contract。每個 response contract 必須記錄：

```yaml
response_contract:
  success_status_codes:
  schema_model:
  extra_policy:
  nullable_fields:
  optional_fields:
  aliases:
  transformations:
  pagination:
  empty_response_behavior:
```

Response schema 必須比 request extraction 更保守。Agent 不得因 request pattern 穩定就自動全開 response schema。

## Pydantic Schema Policy

| Type | Default policy |
| --- | --- |
| request model | `extra="forbid"` |
| response model | `extra="ignore"` or `extra="allow"` |
| error response model | `extra="allow"` |
| internal normalized model | may be strict |
| public API return model | strict only after stable behavior is proven |

Request models should be strict. Response models should be tolerant at the external API boundary.

## Compatibility Labels

Allowed compatibility labels:

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

Agent 不得把已轉換成 typed Pydantic schema 的 response 標成 `equivalent`。若 target 對 raw SDK output 做 schema normalization，response compatibility 必須標成 `normalized`。

## Required Ledger Output

每個 ported API 必須輸出可追溯的 ledger entry，至少包含：

- source SDK function
- source file
- source line range
- source commit or version
- target module / class / method
- request contract status
- response contract status
- compatibility decisions
- tests added
- known divergences
- human-review notes
- final decision

## Decision Labels

每個 porting task 結尾必須使用下列其中之一：

- `continue`
- `stable`
- `needs-human-review`
- `blocked`

Agent 不得隱藏 uncertainty；缺少 source、fixture、response evidence 或 source behavior 不清楚時，必須標記 `needs-human-review` 或 `blocked`。

## Non-goals

- 不在本階段實作 SAS Viya production client methods。
- 不在本階段決定最終 module split、class name 或 resource hierarchy。
- 不在本階段替所有 endpoint family 建完整 mapping。
- 不新增同步 wrapper 或 `asyncio.to_thread` fallback。
- 不把 `sasctl` global session side effects 原樣帶入 `mlops-async`。

## Acceptance Criteria

本需求完成後，後續實作應能引用這些 repo-visible artifacts：

- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`
- `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
- `plan/api-client-porting-contract/api-client-porting-contract.step.md`
- `.github/skills/api-client-porting-planner/`
- `.github/skills/api-client-porting-implementer/`
- `docs/porting-ledger.md`
