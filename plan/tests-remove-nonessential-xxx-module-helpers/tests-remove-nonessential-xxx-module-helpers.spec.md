# tests-remove-nonessential-xxx-module-helpers Specification

## Acceptance Criteria

1. REQ-001：`tests/**` 中所有行為測試不得使用 `*_module()` / `xxx_module` helper-style imports（0 usage）。
2. REQ-002：只有 import path / importability / import contract 驗證測試可保留 helper-style usage。
3. REQ-003：`patch-before-import` 僅能出現在第 2 點例外案例；否則視為違規。
4. REQ-004：不得以 fixture/helper 轉移方式規避政策；若偵測到間接 helper-style usage 仍判違規。
5. REQ-004：若任一案例無法判定為行為測試或 import-contract，必須標記為 BLOCKED 並等待人工 recheck。
6. REQ-005：本 topic 變更不得觸及 `src/**`。

### Requirement → Planned Test Mapping (machine-verifiable)

| requirement_id | planned_test_case_id | scenario | expected_initial_status |
|---|---|---|---|
| REQ-001 | TC-HP-001 | Behavior tests zero helper-style usage | red |
| REQ-001 | TC-INV-001 | Policy guard rejects helper-style usage in unit tests | red |
| REQ-004 | TC-EDGE-001 | Indirect helper/fixture bypass is still detected | red |
| REQ-004 | TC-BLK-001 | Ambiguous classification cases are routed to BLOCKED registry | red |
| REQ-002 | TC-REG-001 | Import-contract helper-style exception remains valid | red |
| REQ-003 | TC-REG-001 | patch-before-import restricted to import-contract scope | red |
| REQ-005 | TC-BC-001 | No `src/**` changes and no public contract changes | red |

### Planned Test Category Mapping (explicit 5-category coverage)

| planned_test_case_id | coverage_category | category_label | rationale |
|---|---|---|---|
| TC-HP-001 | happy path | happy path | 正向驗證行為測試已移除 helper-style usage 且行為斷言維持通過。 |
| TC-INV-001 | error/exception | error/exception | 驗證違規 helper-style usage 會被 policy guard 明確拒絕（fail path）。 |
| TC-EDGE-001 | boundary/edge | boundary/edge | 驗證 fixture/helper 間接繞過這類邊界情境仍會被偵測。 |
| TC-BLK-001 | boundary/edge | boundary/edge | 驗證無法穩定分類案例必須落入 BLOCKED registry 並等待人工 recheck。 |
| TC-BC-001 | state/side effects | state/side effects | 驗證僅 `tests/**` 被變更，`src/**` 與 public contract 狀態不受影響。 |
| TC-REG-001 | integration points | integration points | 驗證 import-contract 與 patch-before-import 限制在 contracts 邊界內整合成立。 |

### Planned RED Test Locations (identifiable IDs)

| planned_test_case_id | file_path | identifiable_test_case |
|---|---|---|
| TC-HP-001 | `tests/unit/test_importlib_policy_guard.py` | `test_tc_hp_001_behavior_tests_have_zero_helper_style_usage` |
| TC-BC-001 | `tests/unit/test_importlib_policy_guard.py` | `test_tc_bc_001_req_005_tests_only_scope_guard_is_still_red` |
| TC-REG-001 | `tests/contracts/test_import_contract_http_client_module_path.py` | `test_tc_reg_001_req_003_patch_before_import_is_explicitly_scoped` |

### Phase 2 Executed RED Evidence (targeted pytest)

- command: `uv run pytest tests/unit/test_importlib_policy_guard.py tests/contracts/test_import_contract_http_client_module_path.py -q`
- observed_outcome: `6 failed, 5 passed`（coverage gate 亦為 red）
- observed_failed_test_ids:
  - TC-INV-001
  - TC-HP-001
  - TC-EDGE-001
  - TC-BC-001
  - TC-BLK-001
  - TC-REG-001

## Behavioral Scenarios

### Scenario 1: Behavior tests zero helper-style usage
- **Given**: `tests/unit/**` 存在 `*_module()` helper-style import 用法
- **When**: 完成本 topic 的 rewrite
- **Then**: 行為測試僅保留 explicit import，helper-style usage 為 0

### Scenario 2: Import-contract exception remains allowed
- **Given**: 測試主要目的為驗證 module path/importability/contract
- **When**: 測試位於 import-contract 範疇並使用 helper-style import
- **Then**: 用法可保留且需有分類理由

### Scenario 3: patch-before-import is not a general exemption
- **Given**: 某測試使用 patch-before-import
- **When**: 該測試不屬 import-contract
- **Then**: 判定違規，必須 rewrite

### Scenario 4: Ambiguous classification
- **Given**: 測試案例同時具有行為與 import-contract 訊號，無法穩定判定
- **When**: 套用分類規則
- **Then**: 案例進入 BLOCKED，不得自動放行

## Error / Edge Cases

- helper-style usage 從測試函式搬到 fixture/helper module，造成表面合規但實際規避。
- import-contract 測試與行為測試混放於同檔，導致分類不穩定。
- 為追求通過率而提議修改 `src/**`，違反 topic 邊界。
