# Models Endpoint ValueObject Specification

## Acceptance Criteria

0. Before topic commit, independent Reviewers record their approved-or-needs-rework results in `review-log/models-endpoint-value-objects/implementation-review.yaml` and `review-log/models-endpoint-value-objects/code-review.yaml`; a `needs-rework` result blocks commit.

1. `ModelsClient` 僅從 `mlops_async.clients.models_client` 提供，建構時要求 injected `Requester`，沒有 package-root export 或資源 lifecycle API。
2. `list_models(start=0, limit=20, project_id=None)` 以 `EndpointPath` 建構安全靜態 path，並只呼叫一次 `Requester.request(method, path, params=...)`；params 包含 `start=0` 與 `limit=20`，`project_id` 存在時額外且僅額外加入 `filter=in(projectId,"<project_id>")`。
3. `get_model(model_id)` 以 `EndpointPath.from_segments()` 建立安全動態 path，並只呼叫一次 `Requester.request(method, path, params=...)`。
4. list 成功回應產生 `ModelsPage` 與 tuple `ModelSummary`；get 成功回應產生 `ModelDetail`。任何回傳 Value Object 均沒有 `dataUris` 或 `files` surface。
5. `start`/`limit`/識別碼輸入在 I/O 前驗證；成功 JSON 的必填 shape 不合法只 raise `ModelsResponseError`。
6. `HTTPStatusException`、`HttpTransportException`、`InvalidJSONResponseException` 與 `asyncio.CancelledError` 的原 instance 直接傳播；404 不轉成 `None`。
7. ModelsClient 不構造 `HttpRequest`、不接收 `BaseUrl`、不檢視 `Requester` private state，且不新增/修改 Requester API；topic 也不新增 pagination、retry、timeout、lifecycle、data/file APIs、dependency、README、VERSION 或 release work。
8. reviewer `approved` 後，Tester 在任何 production implementation 前建立 `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`；它含完整 D1/test mapping verdict，且只有 `red-tests-ready` 可以使 implementation 繼續。
9. `tach.toml` 僅可含讓 `src/mlops_async/models.py` 與 `src/mlops_async/clients/models_client.py` 符合 dependency guardrail 的必要 edges，且 Tach validation 必須通過。

## Behavioral Scenarios

### Scenario 1: 預設單頁模型清單

- **Given**: fake `Requester` 回傳含 `count`、`start`、`limit` 與一個 model item 的 JSON 200 `RawClientResponse`。
- **When**: 呼叫 `await models_client.list_models()`。
- **Then**: fake 只收到一次 `Requester.request()` 的 GET method、`/modelRepository/models` path 與 `start=0`/`limit=20` params；結果是 `ModelsPage`，items 是 immutable tuple。

### Scenario 2: 專案模型清單

- **Given**: 呼叫端指定有效的 `start`、`limit`、`project_id`。
- **When**: 呼叫 `await models_client.list_models(start=20, limit=10, project_id="proj-uuid")`。
- **Then**: request query 含 `start=20`、`limit=10` 和 `filter=in(projectId,"proj-uuid")` 的 encoded value；client 不嘗試第二頁。

### Scenario 3: 取得單一模型

- **Given**: fake `Requester` 回傳符合 get shape 的 JSON 200 `RawClientResponse`，且 `model_id` 含需 encoding 的 path segment 字元。
- **When**: 呼叫 `await models_client.get_model(model_id)`。
- **Then**: request path 僅由 segments 建立，結果為 `ModelDetail`，不含檔案或 data URI 欄位。

### Scenario 4: 保留 transport 與取消語意

- **Given**: injected requester 依序 raise transport/status/invalid JSON/cancellation instance。
- **When**: 呼叫任一 ModelsClient 方法。
- **Then**: 呼叫端收到同一 instance；client 沒有 wrapper、retry、cleanup 或 fallback。

## Error / Edge Cases

- `start` 為 bool、非整數或負數；`limit` 為 bool、非整數或非正數；`project_id`/`model_id` 為空或僅空白字串：raise `ValueError` 且 requester 呼叫次數為零。
- 200 response 的 body 非 JSON、JSON 不是 JSONValue，或 JSON decode 失敗：raise 既有 `InvalidJSONResponseException`。
- list 200 JSON 缺少或錯型別的 `count`、`start`、`limit`、`items`，或 item 缺有效 `id`/`name`：raise `ModelsResponseError`，不回顯完整 body。
- get 200 JSON 缺有效 `id`/`name`：raise `ModelsResponseError`。
- 400/401/404/其他非 2xx：不解析為 domain response，直接傳播 `HTTPStatusException`；404 不轉成 sentinel。
- 已知 `count` 與 items 數量不同：保留 server 的 `count`，不做自動 pagination 或補償 request。
- 上游多餘欄位可忽略，但 `dataUris`、`files`、variables、links 不能成為 VO 成員或回傳值。
