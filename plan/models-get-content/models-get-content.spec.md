# Models Content Download Specification

## Acceptance Criteria

- 新增 `ModelsClient.get_model_content(model_id, content_id, *, range_header=None, if_range=None) -> ModelContent`。
- `ModelContent` 為 frozen/slotted，含 `content: bytes`、`content_type`、`etag`、`content_range`（後三者可為 `None`），且只從 `mlops_async.clients.models` 匯出。
- 使用 `GET /modelRepository/models/{modelId}/contents/{contentId}/content`；兩個 dynamic segment 都 percent-encode。
- `model_id`、`content_id`、任何已提供 header 必須是 non-empty str；孤立 `if_range` 在 requester I/O 前 `ValueError`。
- 只在指定時送 `Range`／`If-Range`，預設不送它們或 `Access-Quarantine`；200/206 map raw bytes 與 case-insensitive metadata headers。
- HTTP non-2xx（包括 416）、transport error、`CancelledError` 原樣傳播；不改 list/get/core transport。

## Behavioral Scenarios

### Given complete content is requested

Given valid model/content identifiers and no conditional headers, When caller awaits the method, Then it makes one GET request without `Range`、`If-Range`、`Access-Quarantine` and maps a 200 bytes response plus present metadata.

### Given a byte range is requested

Given valid identifiers and `range_header`, optionally `if_range`, When caller awaits the method, Then it sends exact `Range`/`If-Range` headers and maps a 206 response including Content-Range when present.

### Given an invalid input combination

Given empty identifiers, blank supplied header, or `if_range` without `range_header`, When caller invokes the method, Then it raises `ValueError` before any requester call.

### Given response headers use different casing

Given a 200/206 response with differently cased header keys, When mapping completes, Then each matching metadata value is preserved.

## Error / Edge Cases

- A 416 or other requester HTTP exception is not caught or translated.
- Transport failures and `CancelledError` propagate unchanged and trigger no retry/follow-up I/O.
- Missing Content-Type, ETag, or Content-Range maps to `None`.
- Legacy snapshot/OpenAPI/request gate only constrain supported request-shape evidence; the gate does not establish runtime response behavior.
