# Models Content Download Technical Specification

## Goal

在既有 Models client boundary 提供單次 async raw-content download，不新增 core/transport 行為。

## Non-Goal

不做 stream、multipart、JSON/text 解碼、retry、timeout override 或其他 Models endpoint。

## Public Contract

```python
@dataclass(frozen=True, slots=True)
class ModelContent:
    content: bytes
    content_type: str | None
    etag: str | None
    content_range: str | None


async def get_model_content(
    self,
    model_id: str,
    content_id: str,
    *,
    range_header: str | None = None,
    if_range: str | None = None,
) -> ModelContent: ...
```

## HTTP Request Contract

- Method/path：`GET /modelRepository/models/{modelId}/contents/{contentId}/content`。
- `model_id`、`content_id` 為非空字串，並各自 percent-encode 成 path segment；不得將空值送往 requester。
- `range_header` 若提供，必為非空字串並映射為 `Range`；`if_range` 若提供，必為非空字串並映射為 `If-Range`。
- `if_range` 必須搭配 `range_header`；違反時在 I/O 前 `ValueError`。
- caller 未指定時不送 `Range`、`If-Range`，也絕不送 `Access-Quarantine`；Authorization 由 requester 管理。

## Response and Evidence Boundary

- 僅 200/206 建立 `ModelContent`；payload 保持 `bytes`。
- 從 case-insensitive headers 讀取 `Content-Type`、`ETag`、`Content-Range`，缺失時為 `None`。
- 非 2xx、transport failure、`CancelledError` 不 catch、不轉譯、不 retry。
- legacy snapshot、OpenAPI 與 request-contract gate 僅依各自 authority 作 request-shape evidence；request-gate 不是 runtime response/semantic evidence。

## Async Design

此 API 是 async because it awaits existing `Requester.request()` once. validation、encoding、header composition 與 mapping 保持同步；client 不擁有 requester/transport 資源，不建立 stream/task，不新增 timeout/retry，所有 failure/cancellation 沿既有 boundary 傳播。

## Validation

先以 async RED tests 固定 request、success、error、cancellation 和 regression contract，再僅透過 WSL 執行 pytest、Ruff、Pyright、Tach。
