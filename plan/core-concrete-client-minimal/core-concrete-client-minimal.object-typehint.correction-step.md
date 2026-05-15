---
topic: core-concrete-client-minimal
type: correction-step
parent_correction: plan/core-concrete-client-minimal/core-concrete-client-minimal.object-typehint.correction-plan.md
created: 2026-05-15
status: review-ready
---

# core-concrete-client-minimal — Object Typehint Correction Step Tracking

> 本檔追蹤 object type-hint tightening 的掃描順序、分類規則、與何時需要重跑測試。

## Workflow Stages

- [X] correction-authoring
- [ ] touched-file-scan
- [ ] code-alignment
- [ ] test-alignment
- [ ] correction-closed

## Correction Steps

- [ ] 1. 依 touched-files 順序掃描 `object` 用法。
  - **順序**：
    1. `src/mlops_async/transport/http_client.py`
    2. `tests/unit/transport/test_http_client.py`
  - **完成條件**：
    - 每個 `object` 都被分類為「可保留」或「應收斂」
  - **需要測試**：否

- [ ] 2. 套用分類規則。
  - **分類規則**：
    - unknown runtime boundary = 可保留
    - internal narrowing cast = 可保留
    - 刻意製造 non-JSON runtime value 的 test object = 可保留
    - always-raise helper 的模糊 return type = 應收斂為 `NoReturn`
  - **需要測試**：否

- [ ] 3. 完成 code-side alignment。
  - **完成條件**：
    - production code 只收斂會弱化 contract 的 type hint
    - `_is_json_value(value: object)` 與必要 casts 未被誤刪
  - **需要測試**：視實際變更而定

- [ ] 4. 完成 test-side alignment。
  - **完成條件**：
    - 測試中的 always-raise helpers 已改為 `NoReturn`
    - 刻意保留的 `object()` 測試資料仍存在且意圖清楚
  - **需要測試**：是

- [ ] 5. 在 touched files 真正改動後重跑相關測試。
  - **完成條件**：
    - `uv run pytest tests/unit/transport/test_http_client.py -v` 已執行
    - 若型別/lint 直接受影響，補跑 `uv run pyright --strict` 與 `uv run ruff check .`
  - **需要測試**：是

## Reviewer Evidence

reviewer 應看：

1. `src/mlops_async/transport/http_client.py` 中保留的 `object` boundary
2. `tests/unit/transport/test_http_client.py` 中已收斂成 `NoReturn` 的 helper
3. 測試中刻意保留的 `object()` runtime-value case

## Closure Condition

本 correction 可視為 closed，必須同時滿足：

1. touched files 已完成分類式收斂
2. 合理的 `object` 保留，模糊的 `object`/return type 已收斂
3. 與此次 touched files 直接相關的測試已重跑

## Historical Retention Note

即使 correction closed，本檔仍保留，以支援後續 decision audit。
