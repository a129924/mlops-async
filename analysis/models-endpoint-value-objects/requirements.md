# Models Endpoint ValueObject Requirements

## 狀態

- Topic: `models-endpoint-value-objects`
- 狀態: `FROZEN`
- D1 verdict: `non-trivial`；此 topic 同時新增 endpoint-family facade、非同步 I/O 邊界與回應 Value Object，因此必須先完成 spec 與 step artifacts。

## Goal

- 以 `Requester` 注入的 `ModelsClient` 提供 Models family 的兩個唯讀作業：列出模型與依識別碼取得模型；成功回應必須轉為可驗證的語意 Value Object。

## Non-Goal

- 不實作自動分頁、下一頁追蹤、批次查詢或串流。
- 不實作模型檔案、內容下載、`dataUris`、`files` 或其他子資源。
- 不變更驗證、token、transport 生命周期、重試或 timeout 政策。
- 不做 release、版本、README、migration map 或 porting ledger 更新。

## In-Scope

- `GET /modelRepository/models` 的單頁 list；公開查詢輸入為 `start`、`limit` 與可選的 `project_id`。
- `project_id` 以 legacy filter `in(projectId,"<project_id>")` 渲染為單一 `filter` query value，並與 `start`、`limit` 作為 `params` 交給既有 `Requester.request()` 路徑。
- `GET /modelRepository/models/{model_id}` 的單一模型取得，動態識別碼以 `EndpointPath` 安全組成。
- `ModelsClient` 只依賴既有 `Requester`，每次呼叫以安全 path 執行一次 `Requester.request(method, path, params=...)`；它不得構造 `HttpRequest`、接收 `BaseUrl`、檢視 `Requester` private state 或新增/修改 Requester API。
- immutable、slots 的語意回應 Value Object，以及成功 JSON 的形狀驗證。
- 既有 transport 例外與取消的精確傳播契約。

## Out-Of-Scope

- `dataUris`、`files`、檔案內容、variables、links 與所有 Models 子資源。
- package-root export、尚未存在的 package-level facade、其他 endpoint-family client。
- 任何 HTTP method 以外的 GET、模型建立/更新/刪除、任意 filter 語法或 query 參數。
- response pagination 追蹤、404 轉換為 `None`、特製 HTTP status 例外、重試或吞掉取消。

## ReadOnly

- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/legacy-viya-outbound-endpoints/models.md`
- `docs/api-endpoints/swagger-spec/models-spec.yaml`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/http_request.py`
- `src/mlops_async/transport/http_client.py`
- `src/mlops_async/transport/exceptions.py`
- `tests/unit/request_contract/models_request_gate/**`
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`docs/migration-map.md`、`docs/porting-ledger.md`

## Written

- `review-log/models-endpoint-value-objects/implementation-review.yaml`：Reviewer-owned implementation alignment verdict；必須記錄 `verdict`、traceability、scope、contract 與 TestCase 檢查結果。
- `review-log/models-endpoint-value-objects/code-review.yaml`：Reviewer-owned Python quality verdict；必須記錄 `verdict`、tooling 與 typing/lint/readability/error-handling/anti-patterns/test-quality/observability findings。

- 規劃階段僅寫入本 topic 的兩個 `analysis/` artifacts 與三個 `plan/` artifacts。
- Tester 必須在 reviewer `approved` 後、任何 production implementation 前寫入 `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`；它是 test-first verdict 的唯一 machine-readable routing artifact。
- 後續 creator 的允許新增檔案為 `src/mlops_async/models.py`、`src/mlops_async/clients/models_client.py`、`tests/unit/test_models_value_objects.py`、`tests/unit/clients/test_models_client.py`。

## Modify

- 本規劃階段沒有既有檔案修改。
- 後續 creator 僅可修改 `tach.toml`，且限於讓 `src/mlops_async/models.py` 與 `src/mlops_async/clients/models_client.py` 納入既有 dependency guardrail 所需的 edges；不得改變其他 module dependency policy。
- 除上述 `tach.toml` 例外，creator 不得修改既有 production、configuration、documentation 或 request-gate 測試檔案；若實作證明需修改任何未列為 Written 或此 Modify 例外的路徑，必須停止並回報 scope drift。

## Deleted

- 無。

## TestCase

- `list_models` 以 `start=0`、`limit=20`、無 `project_id` 發出單一 GET，回傳一個 `ModelsPage`。
- `list_models` 以非預設 `start`、`limit` 與 `project_id` 發出 `start`、`limit`、`filter=in(projectId,"...")` 的語意 query，且只發出一次請求。
- `get_model` 將原始 `model_id` 交由 `EndpointPath.from_segments()` 安全組成路徑並回傳 `ModelDetail`。
- `start`、`limit`、`project_id`、`model_id` 的非法值在 I/O 前失敗且不呼叫 `Requester`。
- 非 JSON 成功回應、成功但語意不完整的 JSON、4xx/5xx、transport failure 與 `asyncio.CancelledError` 分別遵守凍結的錯誤政策。
- Test-first execution 先由 Tester 產生 YAML verdict；只有 `red-tests-ready` 才能讓 Creator 進入 implementation，其他 verdict 依 workflow 回到 rework 或保持 blocked，不能先寫 production code。
- `tach.toml` 修改後必須以 Tach validation 驗證僅存在兩個 Models modules 所需的 dependency edges。

## 可測量需求

1. `ModelsClient.list_models(start: int = 0, limit: int = 20, project_id: str | None = None)` 只執行一個 GET，且不隱藏地要求下一頁。
2. `ModelsClient.get_model(model_id: str)` 只執行一個 GET，且不解析或存取模型檔案相關欄位。
3. list 成功回應轉為 `ModelsPage` 與 `ModelSummary`；get 成功回應轉為 `ModelDetail`；這些 Value Object 不暴露 `dataUris` 或 `files`。
4. list 的成功 JSON 必須含有整數 `count`、`start`、`limit` 與陣列 `items`；get 的成功 JSON 必須含有非空字串 `id` 與 `name`。違反者為 response semantic failure。
5. `HTTPStatusException`、`HttpTransportException`、`InvalidJSONResponseException` 與 `asyncio.CancelledError` 必須保留原始 instance 並直接傳播；此 topic 不將 HTTP status 轉成 `None` 或 endpoint-specific exception。
