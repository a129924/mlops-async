# Models Content Download Requirements

## Goal

在 `ModelsClient` 新增 `get_model_content()`，下載模型 content 的原始 bytes，並回傳必要的 HTTP metadata。

## Non-Goal

- 不實作其他 66 個 Models operations、stream、multipart、mutation、polling 或 link-follow。
- 不修改 `Requester`、transport、Auth、Tach、README、VERSION 或 release。
- 不改變既有 `list_models()`、`get_model()` 的 public contract 或 legacy request-gate evidence。

## In-Scope

- 新增 `ModelContent` value object、Models family-local export、content download client method 與 unit tests。
- 支援 200/206、原始 `Range`／`If-Range` request headers、pre-I/O validation 與原樣 exception propagation。

## Out-Of-Scope

- JSON/text 自動解碼、retry、client-level timeout、resource ownership、background tasks。
- 將 legacy snapshot 或 request-shape gate 當成 response/runtime behavior evidence。

## ReadOnly

- `reference/legacy_code/長庚備份程式/10_48_11_146/sas-docker-api/utils/_api/get_model.py`
- `docs/api-endpoints/swagger-spec/upstream/modelRepository-openapi.yml`
- `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md`
- `tests/unit/request_contract/models_content_request_gate/**`
- `src/mlops_async/core/requester.py`
- `src/mlops_async/core/types.py`
- `tach.toml`

## Written

- `analysis/models-get-content/requirements.md`
- `analysis/models-get-content/technical-spec.md`
- `plan/models-get-content/models-get-content.plan.md`
- `plan/models-get-content/models-get-content.spec.md`
- `plan/models-get-content/models-get-content.step.md`

## Modify

- `src/mlops_async/clients/models/client.py`
- `src/mlops_async/clients/models/value_objects.py`
- `src/mlops_async/clients/models/__init__.py`
- `tests/unit/clients/models/test_client.py`
- `tests/unit/clients/models/test_value_objects.py`

## Deleted

- 無。

## TestCase

- 200 full content、206 partial content、metadata case-insensitive lookup。
- 未指定時不傳送 `Range`、`If-Range`、`Access-Quarantine`。
- invalid/blank identifiers 或 headers、孤立 `if_range` 皆於 I/O 前 `ValueError`。
- encoded identifiers、416/non-2xx、transport failure、`CancelledError` 原樣傳播。
- `ModelContent` frozen/slotted 與 list/get regression。
