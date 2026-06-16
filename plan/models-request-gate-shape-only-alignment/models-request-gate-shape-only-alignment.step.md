# Models Request-Gate Shape-Only Alignment Workflow Steps

## Implementation Steps

- [ ] 更新 `tests/unit/request_contract/models_request_gate/conftest.py`，移除把 `FakeResponse` 或 source-observed response fixture 當成 equality oracle 的流程，同時保留 intercepted request capture、request-shape 對齊、required header subset 驗證與單一 outbound request gate。
- [ ] 收窄 `tests/unit/request_contract/models_request_gate/fixtures/list_models.mock-responses.json` 與 `tests/unit/request_contract/models_request_gate/fixtures/get_model_by_id.mock-responses.json`，只保留讓 invocation 成功完成所需的最小 mock scaffolding；不得讓 response payload、response headers、或 fixture equality 再次成為測試 oracle。
- [ ] 重寫 `tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py`，使正向 case 只覆蓋 bare GET 與既有 `filter=in(projectId,"proj-uuid")`，並僅斷言 request method、path、required header subset、query semantics 與 body shape；unsupported filter semantics 只作為 blocked gate 保留。
- [ ] 重寫 `tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`，使正向 case 只覆蓋 direct identifier branch，且只斷言 request method、path、required header subset、query/body shape；非 UUID 字串、dict-like item、`refresh=True` 等既有 blocked variants 維持為 out-of-scope gate。
- [ ] 執行並通過下列驗證，不得為了通過而修改授權範圍外檔案：
  - `uv run --python 3.10.0 pytest tests/unit/request_contract/models_request_gate -q`
  - `uv run --python 3.10.0 ruff check tests/unit/request_contract/models_request_gate`
  - `uv run --python 3.10.0 pyright tests/unit/request_contract/models_request_gate/conftest.py tests/unit/request_contract/models_request_gate/test_list_models_request_contract.py tests/unit/request_contract/models_request_gate/test_get_model_request_contract.py`
- [ ] 確認最終 diff 只落在本 topic 授權的五個 implementation 檔案，加上 `plan/models-request-gate-shape-only-alignment/models-request-gate-shape-only-alignment.step.md` 的必要 lifecycle 更新；`*.request-flow.json`、`projects_request_gate`、`src/**`、`pyproject.toml`、`uv.lock`、`docs/**`、`analysis/**`、其他 topic 的 `plan/**` 全部未改動；同時測試中不再以 returned object、response payload、response header、或 fixture equality 作為成功 oracle。

## Workflow Stages

These stage markers are informational only. Completion gates must read only `## Implementation Steps`.

- [X] Plan authoring
- [ ] Creator implementation
- [ ] Independent review
