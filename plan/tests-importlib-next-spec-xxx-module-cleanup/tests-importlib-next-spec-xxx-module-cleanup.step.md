---
topic: tests-importlib-next-spec-xxx-module-cleanup
phase: plan-authoring
created: 2026-05-30
---

# tests-importlib-next-spec-xxx-module-cleanup — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/tests-importlib-next-spec-xxx-module-cleanup/tests-importlib-next-spec-xxx-module-cleanup.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. 開啟 `tests/unit/core/test_client_contract.py`，移除 `importlib` 相關 import 與 import contract 專用斷言，保留一般行為測試並改為 explicit import 路徑。
- [ ] 2. 新增 `tests/contracts/test_import_contract_http_client_module_path.py`，把原本驗證 module path/importability 的動態引入斷言集中到 `tests/contracts/`，檔名符合 `test_import_contract_*`。
- [ ] 3. 新增 `tests/unit/test_importlib_policy_guard.py`，實作 policy guard：掃描 `tests/` AST，若在 `tests/contracts/` 以外偵測到 `importlib`（含 fixture/helper 內間接包裝呼叫）即測試失敗。
- [ ] 4. 在 `tests/unit/test_importlib_policy_guard.py` 加入命名檢查：凡使用動態引入的測試檔都必須位於 `tests/contracts/` 且檔名前綴為 `test_import_contract_`，不符即失敗。
- [ ] 5. 於 `tests/contracts/test_import_contract_http_client_module_path.py` 增加 BLOCKED 註記欄位（例如常數清單）與說明，若遇到無法判定案例先列入 BLOCKED 並要求人工 recheck，不直接自動歸類。
- [ ] 6. 重新檢查 `tests/unit/core/test_client_contract.py` 與 `tests/contracts/test_import_contract_http_client_module_path.py` 斷言語意，若任何調整會改變 scope/handoff/close semantics，立即停止並回滾到 alignment（不繼續提交實作）。
