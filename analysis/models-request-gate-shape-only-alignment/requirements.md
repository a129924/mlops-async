# Models Request-Gate Shape-Only Alignment Requirements

## Purpose

本文件凍結 `models-request-gate-shape-only-alignment` 的需求基線，目的是把
`tests/unit/request_contract/models_request_gate/**` 收斂成純 request-only /
shape-only 測試，並把本 topic 的完成條件嚴格限制在兩個既有 GET 介面的請求形狀驗證。

本 topic 的價值不是擴張 coverage，也不是重新定義 `sasctl` runtime 行為；它只負責移除
目前混入的 response payload、response header、fixture equality 與 runtime object
assertions，讓 reviewer 可以明確判斷測試是否只在驗證 intercepted request shape。

## Scope

本需求只涵蓋下列介面：

- `GET /modelRepository/models`
- `GET /modelRepository/models/{modelId}`

成功範圍只到：

- request method 驗證
- request path 驗證
- required header subset 驗證
- query semantics 驗證
- body shape 驗證
- out-of-scope branch / query semantics 的阻擋規則

本需求不涵蓋：

- returned object 驗證
- response payload 驗證
- response headers 驗證
- response fixture equality 驗證
- intercepted request shape 之外的 runtime behavior
- `projects_request_gate`
- 額外 query semantics 擴張
- `src/**`、`docs/**`、`plan/**`、`analysis/**` 既有 artifact 的改寫

## Actors and ownership

- Primary actor：request-contract maintainer
- Supporting actor：human reviewer

Ownership model：

- maintainer-led with human review gate

## Measurable requirements

1. **Endpoint boundary freeze**
   - Actor: request-contract maintainer
   - Condition: 本 topic 開始收斂 `models_request_gate` request-contract tests 時
   - Required outcome: topic 必須且只能覆蓋 `list_models` 與 `get_model` 兩個既有 GET
     介面
   - Metric / decision rule: 若測試或 fixture 變更開始納入第三個 endpoint、額外 HTTP
     method、或 `projects_request_gate` 檔案，視為超出基線
   - Evidence signal: 實際變更檔案只落在已鎖定的 `models_request_gate` 子集合，且 assertions
     只對應上述兩個 endpoint
   - Failure meaning: 若 endpoint 邊界漂移，reviewer 無法判斷這次收斂是在修正測試語意，
     還是在偷偷擴張 topic scope

2. **Shape-only assertion boundary**
   - Actor: request-contract maintainer
   - Condition: 為正向 request-contract case 撰寫或調整斷言時
   - Required outcome: 測試只能驗證 method、path、required header subset、query、body
     shape
   - Metric / decision rule: 任一測試若斷言 returned object 欄位、response payload、
     response header、完整 fixture equality、或 request shape 以外的 runtime behavior，
     即不符合基線
   - Evidence signal: 測試中的 `assert` 目標只指向 captured request 或 topic 內明示允許的
     negative semantics gate
   - Failure meaning: 若 assertion target 混入 response 或 runtime 行為，`request_contract`
     這個名稱就失去可審核性

3. **List-models query semantics freeze**
   - Actor: request-contract maintainer
   - Condition: 調整 `GET /modelRepository/models` 的 case set 時
   - Required outcome: `list_models` 只允許 bare GET 與既有
     `filter=in(projectId,"proj-uuid")`
   - Metric / decision rule: 除這兩種 query semantics 外，不得新增其他 filter、paging、
     sort、search 或延伸查詢案例
   - Evidence signal: 正向 case 只有 `bare_get` 與 `filter_project_id`；負向 case 只阻擋
     已明示超出範圍的 filter semantics
   - Failure meaning: 若 query semantics 被重新打開，topic 會從 shape-only 收斂變成需求擴張

4. **Get-model direct-identifier freeze**
   - Actor: request-contract maintainer
   - Condition: 調整 `GET /modelRepository/models/{modelId}` 的 case set 時
   - Required outcome: `get_model` 只允許 direct identifier branch
   - Metric / decision rule: 非 UUID 字串、dict-like item、`refresh=True`、或任何需要重新推導
     identifier 的分支都必須維持 out-of-scope
   - Evidence signal: 正向 case 只有 `direct_identifier`；負向 case 只驗證已凍結的 blocked
     variants
   - Failure meaning: 若 branch semantics 被打開，測試焦點會從 request shape 漂移回 API 行為差異

5. **Response-independent completion gate**
   - Actor: request-contract maintainer
   - Condition: reviewer 判斷本 topic 是否完成時
   - Required outcome: topic 的完成條件只能是兩個 endpoint 的 request-shape assertions 完成，
     不能依賴 response payload 或 runtime object 斷言
   - Metric / decision rule: 只有當兩個 endpoint 都不再斷言 response / runtime object，
     且仍保留 request-shape coverage，topic 才算完成；若還有任一 response-oriented
     assertion 存活，topic 不算完成
   - Evidence signal: `test_list_models_request_contract.py` 與
     `test_get_model_request_contract.py` 中不再存在以 response / returned object 為 oracle
     的斷言
   - Failure meaning: 若 completion gate 依然綁定 response 行為，這次 alignment 只是表面改名，
     沒有真正收斂測試語意

6. **Topic isolation boundary**
   - Actor: request-contract maintainer
   - Condition: topic 執行期間遇到既有鄰近測試模式或架構討論時
   - Required outcome: 本 topic 不得連帶修改 `projects_request_gate`、不重開 architecture /
     spec / topic scope，也不把 request-flow 證據層改寫成新語意
   - Metric / decision rule: 若需要碰 `projects_request_gate`、新增 analysis / plan、
     或重寫 request-flow fixture 才能前進，必須停止並回到人類決策，而不是在此 topic 內擴 scope
   - Evidence signal: 變更只落在已授權檔案；既有 `*.request-flow.json` 保持唯讀證據層
   - Failure meaning: 若 topic 隔離失守，review 結果將無法區分「本次語意收斂」與
     「額外治理/證據改造」

7. **Implementation surface freeze**
   - Actor: request-contract maintainer
   - Condition: 實作層開始編輯檔案時
   - Required outcome: 未來 implementation 只能修改下列檔案集合：
     - `tests/unit/request_contract/models_request_gate/conftest.py`
     - `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`
     - `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
     - `tests/unit/request_contract/models_request_gate/fixtures/*.mock-responses.json`
   - Metric / decision rule: 若需要修改 `src/**`、`pyproject.toml`、`uv.lock`、`docs/**`、
     `analysis/**`、`plan/**`、或 `models_request_gate` 以外的 tests，視為超出基線
   - Evidence signal: implementation topic 的 git diff 只落在上述四類檔案
   - Failure meaning: 若實作面失控，後續 reviewer 會被迫同時評估測試語意、產品程式碼與治理檔，
     風險不再可隔離

## Contradictions surfaced and resolved

1. `測試需要可執行` vs `測試不得驗證 response semantics`
   - Resolution: 允許保留最小可執行的 mock response 作為 transport completion scaffolding，
     但 response 內容不得成為測試 oracle

2. `request-contract tests 想多覆蓋一些 API 變化` vs `本 topic 只做 shape-only 收斂`
   - Resolution: 本 topic 固定只保留既有兩個 endpoint 與既有 query / branch semantics，
     不藉此擴張 coverage

3. `鄰近的 projects_request_gate 已有類似模式可一起整理` vs `本 topic 不碰隔壁 family`
   - Resolution: `projects_request_gate` 只能作為讀取參考，不在本 topic 內修改

## Extreme-boundary checks

1. **No network / degraded dependency**
   - 即使外部 SAS 環境不可用，topic 仍應能靠 intercepted request 與最小 mock response
     完成 shape-only 驗證；成功訊號不依賴真實 transport 或真實 response semantics

2. **Wrong role / missing approval**
   - 若有人要求在本 topic 內新增 endpoint、擴 query semantics、改寫 request-flow fixture、
     或碰 `src/**` / `plan/**`，必須停止並交回 human reviewer，而不是自行擴 scope

3. **Interrupted / partial completion**
   - 若只收斂 `list_models` 或只收斂 `get_model`，或仍留下任一 response-oriented assertion，
     topic 不算完成

4. **Lowest-volume / peak-volume**
   - 本 topic 不重新打開 pagination、大量 models、搜尋、排序或 refresh path；低量與高量條件
     下，需求都維持同一個 request-shape boundary

5. **Audit / traceability**
   - request-flow fixture 仍必須作為 source-observed request evidence；mock responses 只是
     執行支架，不是需求證據

## Assumptions

- `tests/unit/request_contract/models_request_gate/fixtures/*.request-flow.json` 已經正確表達
  本 topic 允許的 request shape，且在本 topic 中保持唯讀
- `required_header_subset` 的基線維持為 `Authorization` Bearer scheme 與 `Accept` present
- 後續 implementation 仍可使用既有 `EndpointContractCase`、`RequestShape`、`FakeResponse`
  與攔截式 requests harness，不需要新增 production-side client
- 若 `sasctl` invocation 需要最小 JSON body 才能完成，該 body 只作為測試支架，不改變
  shape-only 的需求邊界

## Non-goals

- 不在此 topic 內修改 `src/**`
- 不在此 topic 內修改 `pyproject.toml` 或 `uv.lock`
- 不在此 topic 內修改 `docs/**`
- 不在此 topic 內修改 `plan/**`
- 不在此 topic 內修改 `analysis/**` 既有檔案
- 不在此 topic 內修改 `tests/unit/request_contract/projects_request_gate/**`
- 不在此 topic 內新增或改寫 `*.request-flow.json`
- 不在此 topic 內新增第三個 endpoint、額外 query semantics、或 response / error contract work

## Blockers

本需求目前無未決 blocker，可進入 technical translation。

## Freeze status

Status: `FROZEN`
