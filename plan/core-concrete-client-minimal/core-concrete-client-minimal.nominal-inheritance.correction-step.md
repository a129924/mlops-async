---
topic: core-concrete-client-minimal
type: correction-step
parent_correction: plan/core-concrete-client-minimal/core-concrete-client-minimal.nominal-inheritance.correction-plan.md
created: 2026-05-15
status: review-ready
---

# core-concrete-client-minimal — Nominal Inheritance Correction Step Tracking

> 本檔追蹤 nominal inheritance tightening 的實作順序與 reviewer 應查看的證據。

## Workflow Stages

- [X] correction-authoring
- [ ] correction-review
- [ ] creator-alignment
- [ ] evidence-check
- [ ] correction-closed

## Correction Steps

- [ ] 1. 凍結 nominal inheritance 的邊界，只處理 `HttpClient` 與 `Client` 的名義繼承要求。
  - **完成條件**：
    - correction-plan 明確寫出這是 internal implementation contract tightening
    - public API widening 被明確排除
  - **需要測試**：否

- [ ] 2. 修改 `src/mlops_async/transport/http_client.py`，讓 class header 明確繼承 `Client`。
  - **完成條件**：
    - `class HttpClient(Client):` 已落地
    - 沒有引入 alias、public export、或 facade promotion
  - **需要測試**：是

- [ ] 3. 補上 nominal evidence tests。
  - **完成條件**：
    - 測試不只驗證 structural compatibility
    - 至少一個測試明確檢查 `__bases__` 或 `__mro__`
  - **需要測試**：是

- [ ] 4. 跑與 nominal inheritance 直接相關的驗證。
  - **完成條件**：
    - `uv run pytest tests/unit/transport/test_http_client.py -v`
    - `uv run pytest tests/unit/core/test_client_contract.py -v`
    - 若型別或 lint 明顯受影響，再補 `pyright --strict` / `ruff check .`
  - **需要測試**：是

## Reviewer Evidence

reviewer 應看：

1. `src/mlops_async/transport/http_client.py` 的 class header
2. `tests/unit/transport/test_http_client.py` 或 `tests/unit/core/test_client_contract.py` 中的 nominal evidence assertion
3. root/package export surface 沒有變寬

## Closure Condition

本 correction 可視為 closed，必須同時滿足：

1. class header 已顯式繼承 `Client`
2. nominal evidence tests 已存在且通過
3. internal-only boundary 未被破壞

## Historical Retention Note

即使 correction closed，本檔仍保留，以支援後續 review 與 decision audit。
