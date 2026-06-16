# Models Request-Gate Shape-Only Alignment Technical Spec

## Source requirements

本技術規格落實下列需求來源：

- `analysis/models-request-gate-shape-only-alignment/requirements.md`

本 topic 的現況證據主要來自：

- `tests/unit/request_contract/models_request_gate/conftest.py`
- `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
- `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
- `tests/unit/request_contract/models_request_gate/fixtures/list_models.request-flow.json`
- `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.request-flow.json`

## Goal

把 frozen baseline 轉成最小技術實現，讓後續 implementation 只透過既有
`models_request_gate` test harness 與 mock-response fixtures，移除 response-oriented test
oracle，並保留兩個 endpoint 的 request-shape 與 blocked-semantics coverage。

## Current state summary

目前 `models_request_gate` 的 drift 主要有三類：

1. `test_list_models_request_contract.py` 仍斷言：
   - `result == []`
   - `EMPTY_LIST_RESPONSE` 內容
   - response-oriented case 名稱與 fixture expectations
2. `test_get_model_request_contract.py` 仍斷言：
   - `result.id`
   - `result.name`
3. `conftest.py` 目前仍透過 `_assert_fake_response_matches_source_observed(...)` 把
   `FakeResponse` 與 source-observed response fixture 做 equality 對齊，讓 response payload /
   header 進入 test oracle

上述三類行為都超出本 topic 鎖定的 request-only / shape-only 邊界。

## Allowed file scope

後續 implementation 只能建立或更新：

- `tests/unit/request_contract/models_request_gate/conftest.py`
- `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
- `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
- `tests/unit/request_contract/models_request_gate/fixtures/*.mock-responses.json`

下列檔案在本 topic 中屬於唯讀輸入，不得改寫：

- `tests/unit/request_contract/models_request_gate/fixtures/*.request-flow.json`

下列路徑在本 topic 中不得修改：

- `src/**`
- `pyproject.toml`
- `uv.lock`
- `docs/**`
- `analysis/**`
- `plan/**`
- `tests/unit/request_contract/projects_request_gate/**`
- `tests/**` 其他未列入授權集合的檔案

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `conftest.py` | 保留 intercepted request capture 與 request-shape 驗證；把 response 降成 execution scaffolding，而非 assertion target |
| `test_list_models_request_contract.py` | 只驗證 `GET /modelRepository/models` 的 bare GET、既有 `filter=in(projectId,"proj-uuid")`，以及超出範圍 filter 的阻擋 |
| `test_get_model_request_contract.py` | 只驗證 direct identifier request shape 與既有 blocked variants |
| `fixtures/*.mock-responses.json` | 提供最小可執行的 mock response stub 與 request match，支撐 invocation 完成，但不承載 response correctness oracle |
| `fixtures/*.request-flow.json` | 作為 source-observed request evidence；保持唯讀，繼續定義 method/path/header subset/query/body baseline |

## Requirement-to-technical mapping

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| Endpoint boundary freeze | implementation 只保留 `list_models` 與 `get_model` 兩個 test module 內的 endpoint case，不新增第三個 endpoint 或跨 family 變更 | 既有 target file set、human-locked scope | 低：主要是刪除 drift assertions 與避免 scope creep | feasible |
| Shape-only assertion boundary | 移除正向測試中的 `result`、payload、response header、fixture equality 斷言；保留對 captured request 與 blocked semantics 的 assertions | `SasctlContractHarness.last_request`、`RequestShape`、request-flow evidence | 低到中：需要同步調整 case 結構與測試語句 | feasible |
| List-models query semantics freeze | 只保留 `bare_get` 與 `filter_project_id` 正向 case；保留 unsupported filter negative gate；不得新增其他 query cases | `list_models.request-flow.json`、`run_list_models_capture` | 低 | feasible |
| Get-model direct-identifier freeze | 正向 case 只保留 `direct_identifier`；負向 case 只保留非 UUID、dict-like item、`refresh=True` 三類 blocked variants | `get_model_by_id.request-flow.json`、`run_get_model_capture` | 低 | feasible |
| Response-independent completion gate | 停用或移除 `_assert_fake_response_matches_source_observed(...)` 這類 response equality oracle；mock responses 只保證呼叫可完成 | 現有 requests interception harness、`FakeResponse` | 中：需要避免 harness 語意仍把 response 帶回驗收層 | feasible |
| Topic isolation boundary | 不改 `*.request-flow.json`、`projects_request_gate`、`analysis/**`、`plan/**`；若 implementation 需要這些變更，直接視為 rollback trigger | user-locked scope、現有 evidence layer | 低 | feasible |
| Implementation surface freeze | 所有實作都侷限於 3 個 Python 檔與 `fixtures/*.mock-responses.json`；不改任何產品碼或環境檔 | 使用者明確邊界 | 低 | feasible |

## Required technical tasks

1. **收窄 harness oracle**
   - 在 `conftest.py` 移除或停用任何把 `FakeResponse` 與 source-observed response fixture
     綁成 equality oracle 的流程
   - 保留對 `RequestShape` 與 source-observed request fixture 的對齊檢查
   - 保留 intercepted request capture、header subset 驗證、以及單一 outbound request gate

2. **降低正向 case 對 response 的耦合**
   - `EndpointContractCase` 仍可保留 `response=FakeResponse(...)` 作為 execution scaffolding
   - 但正向測試不得再把 `result`、`response.headers`、`response.json_body`、或 fixture payload
     當成 assertion target
   - 若 `SourceObservedFixture` 在正向 case 中仍存在，應只保留 `request_path`；`response_path`
     不應再作為 shape-only topic 的驗收依據

3. **重寫 `list_models` 測試語意**
   - 移除 `test_list_models_empty_response(...)`
   - 在正向 case 中只斷言：
     - request path
     - request query
     - required header subset
   - 保留 unsupported filter negative test，因為它仍屬 query semantics gate
   - 重新評估 `unregistered_request` 類測試是否仍以 endpoint request-shape contract 為主體；
     若主體已變成 harness plumbing 行為，應移除而不是保留

4. **重寫 `get_model` 測試語意**
   - 正向 case 不再斷言 `result.id`、`result.name` 等 returned object 欄位
   - 保留 direct identifier path / query / header subset 斷言
   - 保留既有 blocked variants，因其仍屬 branch semantics gate

5. **最小化 mock-response fixtures**
   - `fixtures/*.mock-responses.json` 仍需保留 `match` 區塊，因為它是 intercepted request
     routing 的一部分
   - `response` 區塊只保留讓 `sasctl` invocation 成功完成所需的最小欄位；不得再以
     「等於 source observed response」作為 fixture 目標
   - 若某個 endpoint 需要最小 JSON body 才能讓 SDK 完成解碼，允許保留必要鍵，但這些鍵
     不得進入測試 assertion

## Deferred prerequisites and explicit non-work

以下事項不是本 topic 的工作，也不得被偷偷併入 implementation：

1. request-flow evidence 改寫
   - `*.request-flow.json` 是唯讀 evidence layer
   - 若現有 evidence 不足，必須停下來做人類決策或新 topic，而不是在本 topic 內補抓或重寫

2. product/runtime code changes
   - 不修改 `src/**`
   - 不導入新的 concrete client、auth flow、或 transport implementation

3. environment/bootstrap changes
   - 不修改 `pyproject.toml`
   - 不修改 `uv.lock`
   - 不新增 execution 依賴作為本 topic 前提

4. neighboring family cleanup
   - `projects_request_gate` 不在本 topic
   - 任何想同步整理鄰近 family 的提議，都必須分題處理

## Cost-of-realization assessment

### Workstream 1 — Harness oracle 收窄

- Complexity: 中
- Sequencing burden: 低
- Integration burden: 中；因為要移除 response equality oracle，同時保持既有 interception
  flow 可執行
- Operational overhead: 低；完成後測試語意反而更單純

### Workstream 2 — 測試模組收斂

- Complexity: 低到中
- Sequencing burden: 低
- Integration burden: 低；只影響兩個 test modules
- Operational overhead: 低；case intent 會更清楚

### Workstream 3 — Mock fixture 最小化

- Complexity: 低到中
- Sequencing burden: 低
- Integration burden: 中；需要在不驗證 response 的前提下仍讓 `sasctl` invocation 可完成
- Operational overhead: 低；fixture 維護負擔下降

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo language / governance | fits existing architecture | analysis 使用繁體中文，且 topic 邊界與 `AGENTS.md` 相容 |
| Request-contract evidence layering | fits existing architecture | request-flow fixture 繼續扮演 source-observed evidence；mock responses 退回 execution scaffolding |
| Test-only isolation | fits existing architecture | 後續 implementation 只在授權的 `models_request_gate` 測試檔案內進行 |
| Production boundary | fits existing architecture | 不碰 `src/**`、依賴檔、docs、plan、analysis |
| Cross-topic isolation | fits existing architecture | `projects_request_gate` 維持唯讀參考，不做同步整理 |
| SDK invocation survivability | fits with prerequisites | 需要 mock responses 保留讓 `sasctl` 呼叫可完成的最小欄位；若最小 stub 不足，需在既有檔案範圍內調整 fixture，而不是擴到產品碼 |

## Conflicts and rollback-to-alignment triggers

1. **若 implementation 需要驗證 response payload 才能保住測試**
   - Failing business assumption: response 可退回 execution scaffolding，不是驗收 oracle
   - Technical fact: 測試若必須以 payload equality 或 returned object 斷言才能成立，代表本 topic
     其實在測 response semantics
   - Required action: 停止 implementation，回到 alignment，由 human reviewer 決定是否另開
     response-contract topic

2. **若 implementation 需要改 `*.request-flow.json` 才能前進**
   - Failing business assumption: 既有 request-flow evidence 已足以支撐 shape-only 收斂
   - Technical fact: 這代表目前 evidence 與 topic 邊界不一致
   - Required action: 停止並交回 human reviewer，不在本 topic 內改 evidence layer

3. **若 implementation 需要修改 `src/**`、依賴檔或 `projects_request_gate`**
   - Failing business assumption: 這是一個純測試語意收斂 topic
   - Technical fact: 所需變更已超出授權 surface
   - Required action: 停止並回到 human-check；不得直接擴 scope

4. **若 implementation 想新增更多 query / branch semantics**
   - Failing business assumption: `list_models` 與 `get_model` 的語意邊界已鎖定
   - Technical fact: 新 case 會把本 topic 從 alignment 推向需求擴張
   - Required action: 停止，另開新 topic 處理新增 semantics

## Validation

必要檢查：

1. `analysis/models-request-gate-shape-only-alignment/requirements.md` 存在且狀態為
   `FROZEN`
2. `technical-spec.md` 明確記錄：
   - allowed file scope
   - request-only / shape-only oracle 定義
   - request-flow read-only boundary
   - mock-response fixture 的最小支架角色
   - rollback triggers
3. 後續 implementation 若開始執行，reviewer 應能用本 spec 檢查：
   - 是否移除了 `result` / payload / response-header assertions
   - 是否仍只保留兩個 endpoint 的既有 semantics
   - 是否未觸碰未授權檔案

建議檢查指令：

```bash
test -f analysis/models-request-gate-shape-only-alignment/requirements.md
test -f analysis/models-request-gate-shape-only-alignment/technical-spec.md
```

## Stop conditions

若出現以下情況，必須停止並回到 `human-check`：

- 有人要求直接修改 `plan/**`、`src/**`、`docs/**`、`pyproject.toml`、或 `uv.lock`
- 有人要求在本 topic 內同步整理 `projects_request_gate`
- shape-only 邊界無法在既有 request-flow evidence 與授權檔案集合內成立
- 為了讓 SDK 呼叫完成而必須重新把 response correctness 拉回測試 oracle
