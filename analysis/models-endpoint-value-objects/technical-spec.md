# Models Endpoint ValueObject Technical Specification

## 狀態與來源

- Topic: `models-endpoint-value-objects`
- 狀態: `FROZEN`
- Requirements guardrail: `analysis/models-endpoint-value-objects/requirements.md`
- Request evidence: `docs/legacy-viya-outbound-endpoints/models.md`、`tests/unit/request_contract/models_request_gate/**`
- API response evidence: `docs/api-endpoints/swagger-spec/models-spec.yaml`
- Runtime boundary: `Requester -> HttpClient`，由 `docs/ARCHITECTURE.md` 與 `src/mlops_async/core/requester.py` 定義。

## Goal

- 在不改變既有 auth、transport 或 package-root surface 的前提下，為 Models 的 list/get 建立窄小、非同步、語意化的 endpoint client 與 response Value Object 契約。

## Non-Goal

- 不把 request-gate fixture 當成 response correctness oracle。
- 不保留未知 JSON 的萬用 mapping，亦不向呼叫端暴露原始 payload。
- 不擴充為 ModelRepository 全 API、資料檔案 API 或專案 API。

## In-Scope

### Public contract

```python
class ModelsClient:
    def __init__(self, requester: Requester) -> None: ...
    async def list_models(
        self,
        *,
        start: int = 0,
        limit: int = 20,
        project_id: str | None = None,
    ) -> ModelsPage: ...
    async def get_model(self, model_id: str) -> ModelDetail: ...
```

- canonical import 為 `mlops_async.clients.models.ModelsClient`；`src/mlops_async/clients/models/__init__.py` 是 Models family 唯一公開 surface，不得 package-root re-export，也不得修改 `clients` package export。
- `ModelsClient` 只持有 caller 注入的 `Requester`，不建立、close、context-manage 或 cache transport；它不得接收 `BaseUrl`、檢視 `Requester` private state 或新增/修改 Requester API。
- 每個公開方法對應一個直接 await 的 `Requester.request(method, path, params=...)`；沒有 preflight、retry、polling、背景工作或分頁迴圈，也不得構造 `HttpRequest`。

### Request contract

| API | Method | EndpointPath | QueryParams | Body |
| --- | --- | --- | --- | --- |
| `list_models` | `GET` | `/modelRepository/models` | `start=<int>`、`limit=<int>`，另於 `project_id` 存在時加入 `filter=in(projectId,"<project_id>")` | `None` |
| `get_model` | `GET` | 由 `EndpointPath.from_segments("modelRepository", "models", model_id)` 產生 | 空 | `None` |

- `start` 必須為非 bool 的整數且 `>= 0`；`limit` 必須為非 bool 的整數且 `> 0`；`project_id` 與 `model_id` 必須為非空、未去除空白後仍有內容的字串。所有違反在發送前以 `ValueError` 失敗。
- list 以 `EndpointPath.literal("/modelRepository/models").value` 建構靜態 path，並傳入包含 `start`、`limit` 與可選 `filter` 的 `params`；get 以 `EndpointPath.from_segments(...).value` 建構動態 path，並傳入空 `params`。headers、body omission 與 JSON/auth policy 仍完全由既有 `Requester.request()` 處理。

### Semantic response Value Objects

- `ModelSummary` 為 frozen、slots dataclass，保存 list item 的必要語意 `id`、`name` 與可用的 `project_id`、`model_type`、`score_code_type`、`role`、`version`；JSON camelCase 在此唯一的 serialization boundary 轉為 snake_case。
- `ModelsPage` 為 frozen、slots dataclass，保存 `count`、`start`、`limit` 與 `tuple[ModelSummary, ...]`。它代表 server 已回傳的單一頁，不含 next-page method、iterator 或 total-page 推論。
- `ModelDetail` 為 frozen、slots dataclass，保存 get response 的必要 `id`、`name` 與可用的 `model_type`、`score_code_type`、`project_id`、`role`、`version`。它刻意不含 `dataUris`、`files`、variables、links 或任何檔案內容欄位。
- 每一個 VO constructor 或 factory 只接受已驗證的語意 primitive；解析 helper 對 list item 必須要求非空 `id`、`name`，對 optional string 欄位僅在存在時接受字串，對 optional version 僅在存在時接受非 bool 數值。
- 多餘或未建模的 JSON 欄位可忽略，以容忍上游新增欄位；受明確排除的欄位不得在任何 VO 成員、property 或回傳值出現。

### Response and errors policy

| 條件 | 結果 |
| --- | --- |
| 2xx 且可解碼、符合 list/get 必要語意 | 回傳對應 Value Object |
| 2xx 非 JSON 或非 JSONValue | 直接傳播原 instance 的 `InvalidJSONResponseException` |
| 2xx JSON 但不是預期 object、缺必要欄位或欄位型別不符 | raise 新的 module-public `ModelsResponseError`，訊息只描述 endpoint 與語意欄位，不保留或回顯完整 payload |
| 400、401、404 或任何非 2xx | 直接傳播 transport 已建立的原 instance `HTTPStatusException`；404 不轉為 `None` |
| 連線、TLS、timeout 或其他 transport failure | 直接傳播原 instance `HttpTransportException` |
| cancellation | 不攔截 `asyncio.CancelledError` |

- `ModelsResponseError` 只能表示成功 HTTP response 的 endpoint semantic mismatch；不得包裝、chain 或重新命名 transport 例外。
- client 必須以 `RawClientResponse` 的 `content` 解碼 JSON，並在解碼或 JSONValue 驗證失敗時用既有 `InvalidJSONResponseException` 與其 `HttpErrorContext`。不可將 response parsing 移入 `Requester`。

## Out-Of-Scope

- 自動 pagination、cursor、`links` follow-up、batching、streaming、retry、timeout override、cache 或 lifecycle ownership。
- Models create/update/delete、model files/content、`dataUris`、`files`、variables、下載與上傳。
- `src/mlops_async/__init__.py`、`src/mlops_async/clients/__init__.py`、README、VERSION、release metadata 或 dependency 檔案。
- 對 request-gate history、source SDK fixture、migration map 或 porting ledger 的修改。

## ReadOnly

- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/http_request.py`
- `src/mlops_async/core/types.py`
- `src/mlops_async/transport/http_client.py`
- `src/mlops_async/transport/exceptions.py`
- `src/mlops_async/__init__.py`
- `src/mlops_async/clients/__init__.py`
- `tests/unit/request_contract/models_request_gate/**`
- `pyproject.toml`、`uv.lock`、`README.md`、`VERSION`、`docs/**`

## Written

- `review-log/models-endpoint-value-objects/implementation-review.yaml`：Reviewer-owned implementation alignment verdict。
- `review-log/models-endpoint-value-objects/code-review.yaml`：Reviewer-owned Python quality verdict。

- `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`（Tester；reviewer `approved` 後、production implementation 前的 machine-readable TDD verdict）
- `src/mlops_async/clients/models/__init__.py`
- `src/mlops_async/clients/models/client.py`
- `src/mlops_async/clients/models/value_objects.py`
- `tests/unit/clients/models/test_client.py`
- `tests/unit/clients/models/test_value_objects.py`

## Modify

- `tach.toml` 是唯一可修改的既有檔案，且只可移除 `mlops_async.models` 與 `mlops_async.clients.models_client` edges，並新增 `mlops_async.clients.models -> [mlops_async.clients.models.client, mlops_async.clients.models.value_objects]`、`mlops_async.clients.models.value_objects -> [mlops_async.core, mlops_async.exceptions]`、`mlops_async.clients.models.client -> [mlops_async.clients.models.value_objects, mlops_async.core, mlops_async.transport]`。
- 不得改變其他 module dependency policy、source、test、configuration 或 documentation 檔案；任何其他既有檔案修改皆為 scope drift 並停止。

## Deleted

- `src/mlops_async/models.py`
- `src/mlops_async/clients/models_client.py`
- `tests/unit/test_models_value_objects.py`
- `tests/unit/clients/test_models_client.py`

## TestCase

1. list default、project filter 與 get path 都以 `EndpointPath` 建構安全 path，並各自只 await 一次 injected `Requester.request()`；fake collaborator 僅捕捉 method、path 與 params。
2. `ModelsPage` 與 `ModelDetail` 將 snake_case 語意欄位正確映射，且沒有 `files` 或 `data_uris` surface。
3. page 不發出第二個 request；`count` 不等於 `len(items)` 時仍保留 server semantic metadata，不嘗試補頁。
4. 輸入 invalid、JSON invalid、schema invalid、HTTP status、transport failure 與 cancellation 皆依本 spec 的 exact policy 驗證 identity/exception type。
5. Tach validation 通過；`tach.toml` diff 只移除兩個舊 Models module entries，並加入本 spec 列出的三個 Models family module entries。
6. `ModelsClient` 與其 VOs 的實體 source/test paths 與 family package 對應；不得僅更新 import 而保留任何舊 path。

## 實作順序

1. reviewer `approved` 後，Tester 先依 spec 產生 RED tests 與 `plan/models-endpoint-value-objects/models-endpoint-value-objects.tdd-test-authoring.yaml`；YAML 必須含 verdict、D1 verdict、test mapping、validation checks、issues 與 next step。只有 `red-tests-ready` 可以進入 production implementation。
2. Creator 再建立 Value Objects 與純解析/驗證 helper，使已存在的 RED tests 轉為綠色，並維持 HTTP/JSON 翻譯與 domain response 形狀的單一邊界。
3. Creator 實作 client 的 list/get 單一請求路徑；勿新增共用 facade、Protocol、Requester method 或 transport API。
4. 只以本 spec 列出的 exact module replacement 修改 `tach.toml`，並以 Tach validation 驗證；若需要其他 `tach.toml` policy、ReadOnly 路徑、未列 dependency、TDD verdict 不是 `red-tests-ready`，或未凍結 response 欄位，停止為 `BLOCKED` 或依 reviewer verdict 回到 rework，不得先寫 production code。

## 非同步基線

- Async boundary: 僅 `ModelsClient` 公開 I/O 方法為 async；VO 與 parser 維持同步且無副作用。
- Resource lifecycle: `Requester`、auth provider 與 transport 由 caller 擁有；`ModelsClient` 不提供 `aclose`、`__aenter__` 或 `__aexit__`。
- Concurrency: 每次呼叫為一個直接 await；不同呼叫的並行性由 caller 決定，client 不建立 task 或 semaphore。
- Failure/cancellation: 保留 cancellation 與既有 transport errors；不新增 retry 或 timeout policy。

## Family package rework gate

- `src/mlops_async/clients/models/` 是唯一的 Models endpoint-family package；`__init__.py` 只 re-export 此 family 的 `ModelsClient`、Value Objects 與 `ModelsResponseError`，不建立 root facade。
- 此 rework 取代先前 flat-module implementation，四個 Deleted paths 不得保留 compatibility shim。
- 先前 `review-log/models-endpoint-value-objects/implementation-review.yaml` 與 `review-log/models-endpoint-value-objects/code-review.yaml` 的 approved evidence 僅涵蓋 flat layout，對本 contract 無效；完成 rework 後必須由 independent Reviewers 重寫兩份 evidence 並重新審查。

## Workflow state

- current_step: `plan-authoring`
- next_step: `plan-review`
- status: `COMPLETE`
