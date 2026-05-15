# Testing Boundary Decision Draft

## Purpose

本 decision draft 用來凍結目前 `models-request-gate-execution` 分支上的測試責任邊界，
並判定這支分支是否已足夠收斂，或是否還需要再開 follow-up hardening topic。

## Decision

本 repo 之後對 request 測試採 **兩層都要，但主從分明** 的 posture：

1. **Layer 1 — request-contract / request-shape**
   - 證明端點會怎麼打、需要哪些輸入、會送出什麼 request shape
   - 驗 method、path、query semantics、body shape、必要 header subset
   - 不宣稱驗到 token validity、refresh、session side effects、real transport

2. **Layer 2 — integration / E2E**
   - 證明 auth 注入、401 refresh、real transport、真實 response boundary
   - 作為 release confidence 的主要來源

## Current branch verdict

### Branch under review

- `models-request-gate-execution`

### Verdict

**目前這支分支可以收斂。**

原因：

1. 現有 tests-side artifacts 已足以支撐 Layer 1：
   - `tests/unit/request_contract/models_request_gate/conftest.py`
   - `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
   - `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
   - `tests/unit/request_contract/models_request_gate/fixtures/*.request-flow.json`
   - `tests/unit/request_contract/models_request_gate/fixtures/*.mock-responses.json`
2. 目前 bootstrap boundary 已凍結為：
   - 不修改 `pyproject.toml`
   - 不修改 `uv.lock`
   - 只使用既有 repo dependencies
3. 目前 harness 實際驗到的是 source-observed outbound request，不是假裝驗到 target runtime 行為。

## What this branch is allowed to claim

目前這支分支 **可以**宣稱：

- `sasctl` / legacy 的 request shape 可被穩定觀察
- `list_models` 與 `get_model` direct identifier branch 的 method/path/query/body/header subset 已被 Layer 1 request tests 保護
- unsupported variants 與 unresolved semantics 仍被正確保持在 blocked / unresolved boundary

目前這支分支 **不可以**宣稱：

- Bearer token 格式有效
- auth/session/refresh 行為已成立
- 真實 transport 成功
- 真實 SAS Viya response boundary 已被證明
- 未來 `mlops_async` target client 一定會送出與目前 source 完全相同的 header policy

## Source-observed vs target-intended rule

若 source observed 與 target intended 不一致，必須分成兩層表達：

1. **Observed assertion layer**
   - 只記錄目前可執行 harness 真正觀察到的 request semantics

2. **Divergence / target-intent layer**
   - 記錄 target 為什麼可能故意比 source 更嚴
   - 不可直接覆蓋 observed assertion layer

這代表：

- 目前若 `sasctl` 實際送出 `Accept: */*`，就不能把 target vendor media type 直接寫成同一層
  request assertion
- 若要表達 target 未來應改成更精準的 `Accept`，應放在 divergence metadata 或 follow-up
  topic，而不是改寫目前 source-observed fixture 的 matched request

## Hardening threshold

只有在出現以下情況時，才需要再開 `models-request-gate-hardening`：

1. reviewer 仍可能把目前 branch 誤讀成 Layer 2 證據
2. fixture / docs 無法清楚區分 source observed 與 target intended
3. `Accept` / media type policy 必須在 Layer 1 topic 內更精準表達，否則 reviewer 會誤判
   contract

若沒有上述情況，這支分支可以先收斂，不必為了「更理想的嚴謹性」立即繼續擴 scope。

## Mocking posture for this branch

目前分支的 requests-level interception 已足夠支撐 Layer 1 request-contract 目的。

因此：

- **不需要**為了收斂這支分支而新增 mock 套件
- 若未來只是想提升 request mocking 的可讀性，優先考慮沿用既有 requests interception
  模式
- 只有在既有模式無法表達必要 contract 時，才另開 topic 評估是否需要新增 mocking dependency

## Follow-up recommendation

最保守且一致的後續順序是：

1. 以本 decision draft 作為 branch 收斂依據
2. 關閉「目前這支分支是否還不夠嚴謹」的爭論
3. 若之後仍需要更精準的 media-type / divergence 表達，再另開
   `models-request-gate-hardening`
4. auth pre-flight（如 `BearerToken` / `InvalidBearerTokenError`）保持為獨立 topic，不混入
   目前這支 request-only 分支
