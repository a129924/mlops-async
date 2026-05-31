# tests-importlib-next-spec-xxx-module-cleanup

## Goal
在僅調整 `tests/` 的前提下，將一般行為測試中的 `importlib` 清零，並把允許的動態引入收斂到 `tests/contracts/test_import_contract_*`，同時建立 BLOCKED 分流與人工 recheck 交接規則。

## Non-goals
- 不修改任何 `src/` 內生產程式碼或公開 API。
- 不變更 contract meaning（scope/handoff/close semantics）。
- 不把本 topic 擴張為 CI、release 或工作流重設計。
- 不以 fixture/helper 包裝 `importlib` 作為規則豁免。

## Current Context
- `analysis/tests-importlib-next-spec-xxx-module-cleanup/requirements.md` 已凍結零容忍與例外規則。
- `analysis/tests-importlib-next-spec-xxx-module-cleanup/technical-spec.md` 已定義分類、BLOCKED 與 rollback routing。
- 目前 `tests/` 中偵測到 `importlib` 用法位於 `tests/unit/core/test_client_contract.py`，且 import contract 與一般測試混在同檔。
- 目前尚無 `tests/contracts/` 目錄與 `test_import_contract_*` 命名落地。

## Requirements
1. `tests/contracts/` 以外不得存在任何 `importlib` 呼叫（含 direct 與 indirect wrapper）。
2. 所有允許動態引入的案例必須位於 `tests/contracts/`，檔名符合 `test_import_contract_*`。
3. 無法穩定判定是否屬於 import contract 的案例必須標記為 BLOCKED 並交人工 recheck，不得自行猜測分類。
4. 若任何調整會改變 contract meaning（scope/handoff/close semantics），流程必須回滾到 alignment，不得直接推進。
5. 變更範圍僅限 `tests/`，不得觸及 `src/`。

## Decisions
- Async-planning status: exempt — cite exemption evidence: 本 topic 僅處理測試檔 import 規則與分類，不引入新的 async 邊界、資源生命週期、併發模型、timeout 或 cancellation 決策（見 requirements/technical-spec 的 frozen inputs 與 workstreams）。
- Module/package placement: 僅在 `tests/unit/` 與 `tests/contracts/` 內調整；必要 policy guard 測試放在 `tests/unit/`。
- New public API: no。
- Interface changes: yes — 測試分類介面由「混放」改為「import contract 必須集中在 `tests/contracts/test_import_contract_*`」。
- Breaking changes allowed: no — 不允許改變既有 contract meaning；若偵測到語意變更風險即 rollback。
- New dependencies: no。
- Error handling strategy: 測試層以 assertion fail 呈現違規；分類不確定案例標記為 BLOCKED 並停止自動收斂，交人工 recheck。
- Typing strategy: 測試程式維持既有型別紀律；新增/調整測試函式與 helper 需完整型別註記，不使用 `Any` 規避。

## Public Contract / API Changes
No public API changes.

## Affected Files / Modules
Likely affected files:
- tests/unit/core/test_client_contract.py
- tests/contracts/test_import_contract_http_client_module_path.py
- tests/unit/test_importlib_policy_guard.py

Candidate files to inspect:
- tests/unit/**/*.py
- tests/contracts/**/*.py
- analysis/tests-importlib-next-spec-xxx-module-cleanup/requirements.md
- analysis/tests-importlib-next-spec-xxx-module-cleanup/technical-spec.md

## Implementation Steps
1. 開啟 `tests/unit/core/test_client_contract.py`，移除 `importlib` 相關 import 與 import contract 專用斷言，保留一般行為測試並改為 explicit import 路徑。
2. 新增 `tests/contracts/test_import_contract_http_client_module_path.py`，把原本驗證 module path/importability 的動態引入斷言集中到 `tests/contracts/`，檔名符合 `test_import_contract_*`。
3. 新增 `tests/unit/test_importlib_policy_guard.py`，實作 policy guard：掃描 `tests/` AST，若在 `tests/contracts/` 以外偵測到 `importlib`（含 fixture/helper 內間接包裝呼叫）即測試失敗。
4. 在 `tests/unit/test_importlib_policy_guard.py` 加入命名檢查：凡使用動態引入的測試檔都必須位於 `tests/contracts/` 且檔名前綴為 `test_import_contract_`，不符即失敗。
5. 於 `tests/contracts/test_import_contract_http_client_module_path.py` 增加 BLOCKED 註記欄位（例如常數清單）與說明，若遇到無法判定案例先列入 BLOCKED 並要求人工 recheck，不直接自動歸類。
6. 重新檢查 `tests/unit/core/test_client_contract.py` 與 `tests/contracts/test_import_contract_http_client_module_path.py` 斷言語意，若任何調整會改變 scope/handoff/close semantics，立即停止並回滾到 alignment（不繼續提交實作）。

## Test Plan
Test file: `tests/unit/core/test_client_contract.py`, `tests/contracts/test_import_contract_http_client_module_path.py`, `tests/unit/test_importlib_policy_guard.py`

Test cases:
- Happy path: `tests/unit/core/test_client_contract.py` 在移除 `importlib` 後仍通過既有 client protocol 行為斷言。
- Invalid input: `tests/unit/test_importlib_policy_guard.py` 對違規路徑（`tests/contracts/` 以外）偵測到 `importlib` 時應明確 fail。
- Edge case: `tests/unit/test_importlib_policy_guard.py` 偵測 fixture/helper 內包裝 `importlib` 的間接呼叫並 fail。
- Regression: `tests/contracts/test_import_contract_http_client_module_path.py` 保持 importability 驗證可用，避免先前 contract 測試遺失。
- Backward compatibility: 既有 `tests/unit/core/test_client_contract.py` 非 import contract 斷言語意與 pass/fail 意義維持一致。

## Validation Commands
```bash
uv run pytest tests/unit/core/test_client_contract.py tests/contracts/test_import_contract_http_client_module_path.py tests/unit/test_importlib_policy_guard.py -v
uv run pytest tests/ --cov=src/mlops_async --cov-report=term-missing
uv run pyright --strict
uv run ruff check tests/
```

## Risks
- AST policy guard 若規則過寬，可能把合法的 import contract 測試誤判為違規，導致假陽性。
- import contract 測試拆檔後若遺漏原始斷言，可能造成 coverage 看似通過但 contract 意義縮水。

## Rollback Plan
- 透過 git 還原以下檔案：`tests/unit/core/test_client_contract.py`、`tests/contracts/test_import_contract_http_client_module_path.py`、`tests/unit/test_importlib_policy_guard.py`。
- 若已建立 `tests/contracts/` 新檔，回滾時一併移除新增檔案與對應引用。
- 若發現 contract meaning 已被改動，停止執行並回到 alignment 重新凍結決策。

## Open Questions
- BLOCKED 人工 recheck 的責任角色（reviewer/owner）是否固定為同一群人？Owner: topic reviewer。
- 若未來出現多個 import contract 主題，`tests/contracts/` 是否需要再細分子目錄？Owner: 測試維護者與 reviewer。
