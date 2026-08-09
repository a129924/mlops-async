---
topic: models-get-content
phase: plan-authoring
created: 2026-08-09
---

# Models Content Download Step Tracker

## Executor note

僅可在 feature worktree 執行；每一步完成後更新同一 tracker。所有 Python/Git/GitHub 操作必須透過 WSL；contract、validation 或 remote blocker 必須停止交 human-check。

## Workflow stages

1. [ ] `plan-authoring`
2. [ ] `plan-review`
3. [ ] `tdd-test-authoring`
4. [ ] `implementation`
5. [ ] `implementation-review`
6. [ ] `code-review`

## Implementation Steps

1. [X] 在 `tests/unit/clients/models/test_client.py` 擴充 fake requester 與 RED tests，涵蓋 encoded path、success response、conditional headers、所有 `model_id`/`content_id`/`range_header`/`if_range` 非字串輸入的 pre-I/O `ValueError`，以及 exception propagation。
2. [X] 在 `src/mlops_async/clients/models/value_objects.py` 新增 frozen/slotted `ModelContent`；在 `src/mlops_async/clients/models/__init__.py` 新增 family-local export；在 `tests/unit/clients/models/test_value_objects.py` 驗證 immutable/slotted fields。
3. [X] 在 `src/mlops_async/clients/models/client.py` 實作 `get_model_content()` 的 non-empty validation、encoded segments、`Range`／`If-Range` composition、200/206 bytes/metadata mapping。
4. [X] 在 `tests/unit/clients/models/test_client.py` 完成 416/non-2xx、transport failure、`CancelledError`、metadata casing 與 list/get regression assertions。
