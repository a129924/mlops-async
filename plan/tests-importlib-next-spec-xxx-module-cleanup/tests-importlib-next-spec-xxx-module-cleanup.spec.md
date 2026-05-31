# tests-importlib-next-spec-xxx-module-cleanup Specification

## Acceptance Criteria

1. `tests/contracts/` 以外的測試檔不允許任何 `importlib` 直接或間接呼叫；違規必須可被測試攔截。
2. 允許動態引入的案例必須位於 `tests/contracts/` 且檔名符合 `test_import_contract_*`。
3. 原 `tests/unit/core/test_client_contract.py` 的一般行為測試改為 explicit import 後，既有 assertion intent 與 pass/fail 意義不變。
4. import contract 驗證需保留在 `tests/contracts/test_import_contract_http_client_module_path.py`，可持續驗證支援與不支援的 module path。
5. 無法判定是否屬於 import contract 的案例必須進入 BLOCKED 並要求人工 recheck；不得由自動規則直接 close。
6. 一旦偵測任何變更會影響 contract meaning（scope/handoff/close semantics），流程需 rollback 至 alignment。

## Behavioral Scenarios

### Scenario 1: 行為測試移除動態引入
- **Given**: `tests/unit/core/test_client_contract.py` 含一般行為測試與 import contract 斷言混放。
- **When**: 執行 cleanup 並將 import contract 斷言搬移至 `tests/contracts/`。
- **Then**: `tests/unit/core/test_client_contract.py` 僅保留 explicit import 與一般行為斷言，不再使用 `importlib`。

### Scenario 2: import contract 合法保留
- **Given**: 需要驗證 `mlops_async.transport.http_client` 可被解析、`mlops_async.core.http_client` 不可被解析。
- **When**: 在 `tests/contracts/test_import_contract_http_client_module_path.py` 執行 contract 測試。
- **Then**: 動態引入可被允許，且檔名與路徑符合例外規則。

### Scenario 3: 規避路徑攔截
- **Given**: 某測試透過 fixture/helper 包裝 `importlib` 嘗試繞過規則。
- **When**: 執行 `tests/unit/test_importlib_policy_guard.py`。
- **Then**: policy guard 偵測到間接呼叫並 fail，阻止規避。

### Scenario 4: 無法判定分類
- **Given**: 某案例無法明確判定是行為測試或 import contract。
- **When**: 套用分類流程。
- **Then**: 案例必須列入 BLOCKED 並交人工 recheck，不得自動歸類。

## Error / Edge Cases

- `tests/contracts/` 不存在或檔名未遵守 `test_import_contract_*`，導致合法例外無法被辨識。
- policy guard 僅抓 direct import 而漏掉 helper/fixture 間接呼叫，造成偽陰性。
- 拆分 `test_client_contract.py` 時遺漏 contract 斷言，導致 import contract coverage 下滑。
- 為了讓測試過關而調整 scope/handoff/close semantics，觸發必須 rollback 的違規情境。
