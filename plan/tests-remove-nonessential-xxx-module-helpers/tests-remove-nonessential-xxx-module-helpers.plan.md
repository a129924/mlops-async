# tests-remove-nonessential-xxx-module-helpers Plan (python-plan-authoring)

## Goal

在不修改 `src/` 前提下，針對整個 `tests/` tree 移除所有非必要 `*_module()` / `xxx_module` helper-style imports；僅允許 import path / importability / import contract 驗證測試保留必要用法。

## Non-goals

- 不改 `src/**` 任何檔案。
- 不把 helper-style import 政策改成建議值（維持零容忍）。
- 不在本階段執行 commit/push/PR。

## Current Context

- `tests/` 內可觀察到多個 `*_module()` helper-style import 使用點（core/transport 測試皆有）。
- `tests/contracts/test_import_contract_http_client_module_path.py` 已存在 import-contract 型測試，可作為例外路徑參考。
- frozen alignment 已要求：patch-before-import 不得作為一般豁免。

## Requirements

1. REQ-001：行為測試 helper-style usage 必須完全移除（0 usage）。
2. REQ-002：import-contract 類測試可保留必要 helper-style usage，但需有明確分類理由。
3. REQ-003：`patch-before-import` 僅在 import-contract 類可接受。
4. REQ-004：無法判定分類案例必須 BLOCKED，等待人工 recheck。
5. REQ-005：變更範圍僅 `tests/**`。

### Phase 2 Prerequisite Evidence (machine-verifiable)

```yaml
phase_2_prerequisites:
  plan_approval_status: approved
  approval_evidence_id: PHASE2-APPROVED-2026-05-31
  approval_artifacts:
    - plan/tests-remove-nonessential-xxx-module-helpers/tests-remove-nonessential-xxx-module-helpers.plan.md
    - plan/tests-remove-nonessential-xxx-module-helpers/tests-remove-nonessential-xxx-module-helpers.step.md
    - plan/tests-remove-nonessential-xxx-module-helpers/tests-remove-nonessential-xxx-module-helpers.spec.md
  requirement_test_mapping_status: recorded
  planned_test_expected_initial_status: verified
  tdd_test_authoring_status: executed
  tdd_execution_evidence:
    command: uv run pytest tests/unit/test_importlib_policy_guard.py tests/contracts/test_import_contract_http_client_module_path.py -q
    observed_pytest_outcome: 6 failed, 5 passed (coverage gate also red in this targeted run)
    failed_test_ids:
      - TC-INV-001
      - TC-HP-001
      - TC-EDGE-001
      - TC-BC-001
      - TC-BLK-001
      - TC-REG-001
    expected_initial_status_verification:
      - TC-HP-001: red (failed)
      - TC-INV-001: red (failed)
      - TC-EDGE-001: red (failed)
      - TC-BC-001: red (failed)
      - TC-REG-001: red (failed)
      - TC-BLK-001: red (failed)
    requirement_mapping_closure:
      - REQ-003 -> TC-REG-001
      - REQ-005 -> TC-BC-001
```

## Decisions

- Async-planning status: exempt（本 topic 為測試匯入樣式整理，不新增 async 邊界）。
- Async-planning exemption evidence（explicit）: `analysis/tests-remove-nonessential-xxx-module-helpers/requirements.md` 已凍結「不修改 `src/`；僅做 tests semantic translation」，且 `analysis/tests-remove-nonessential-xxx-module-helpers/technical-spec.md` 的 workstreams 僅涵蓋 `tests/**` 盤點/分類/重寫與 guard 驗收；未引入任何 coroutine lifecycle、concurrency、cancellation、或 async protocol 變更，因此不觸發 `python-async-planning`。
- Module/package placement: 測試調整僅發生在 `tests/**`；import-contract 測試維持於 `tests/contracts/**`。
- New public API: no。
- Interface changes: no（僅測試語義翻譯）。
- Breaking changes allowed: no。
- New dependencies: no。
- Error handling strategy: 分類不確定直接 BLOCKED，不做推測。
- Typing strategy: 測試檔維持既有型別紀律，不引入型別逃逸。

## Public Contract / API Changes

No public API changes.

## Affected Files / Modules

Likely affected files:
- tests/unit/core/test_auth_contract.py
- tests/unit/core/test_auth_provider.py
- tests/unit/core/test_requester_auth_boundary.py
- tests/unit/core/test_token_manager.py
- tests/unit/core/test_token_storage.py
- tests/unit/transport/test_exceptions.py
- tests/unit/transport/test_http_client.py
- tests/contracts/test_import_contract_http_client_module_path.py

Candidate files to inspect:
- tests/**/*.py
- analysis/tests-remove-nonessential-xxx-module-helpers/requirements.md
- analysis/tests-remove-nonessential-xxx-module-helpers/technical-spec.md

## Implementation Steps

1. 掃描並記錄下列目標檔案中的 helper-style usage：`tests/unit/core/test_auth_contract.py`、`tests/unit/core/test_auth_provider.py`、`tests/unit/core/test_requester_auth_boundary.py`、`tests/unit/core/test_token_manager.py`、`tests/unit/core/test_token_storage.py`、`tests/unit/transport/test_exceptions.py`、`tests/unit/transport/test_http_client.py`、`tests/contracts/test_import_contract_http_client_module_path.py`；逐檔標記 `*_module()` / `xxx_module` 的實際用途。
2. 依 `analysis/tests-remove-nonessential-xxx-module-helpers/technical-spec.md` 分類上述 usage 為 `allowed / rewrite / BLOCKED`，並在 plan 變更中為每個 `allowed` 或 `BLOCKED` 項目補上判定理由（含對應測試檔路徑）。
3. 在 `rewrite` 類目標檔（限定 `tests/unit/core/*.py` 與 `tests/unit/transport/*.py`）移除 helper-style import，改為 explicit module path import 或直接符號 import，且不得新增任何 fixture/helper 包裝來間接保留 `*_module()` 呼叫。
4. 在 `tests/contracts/test_import_contract_http_client_module_path.py`（`allowed` 類）逐一確認保留的 helper-style usage 只服務於 import path / importability / import contract 斷言；若需 `patch-before-import`，僅可存在於此 import-contract 檔案。
5. 在 `tests/unit/test_importlib_policy_guard.py` 更新測試 policy guard 規則：明確攔截 `tests/unit/**` 下任何 `*_module()` / `xxx_module` 使用，同時避免以 fixture/helper 轉移方式繞過；不得將 contracts 類合法例外一併誤攔。
6. 僅執行本 plan 的驗證命令（`uv run pytest tests/ -q`、`uv run ruff check tests/`、`uv run pyright`）確認測試層改動可通過；若出現無法分類案例，維持 BLOCKED 狀態並等待人工 recheck，不延伸到 `tests/**` 之外。

## Test Plan

Test scope:
- `tests/` 全樹回歸（unit/contracts/integration）

Test cases:
- TC-HP-001 (REQ-001) [category: happy path, expected_initial_status: red]：`tests/unit/core/*.py` 與 `tests/unit/transport/*.py` 中 helper-style imports 已移除，既有行為斷言仍通過。
- TC-INV-001 (REQ-001) [category: error/exception, expected_initial_status: red]：在 unit 測試範圍故意引入 `*_module()` / `xxx_module` 使用時，測試 policy guard 應明確 fail。
- TC-EDGE-001 (REQ-004) [category: boundary/edge, expected_initial_status: red]：當 helper-style usage 出現在 fixture/helper 包裝層（非直接測試函式）時，guard 仍可偵測並 fail。
- TC-BLK-001 (REQ-004) [category: boundary/edge, expected_initial_status: red]：無法穩定分類案例必須記錄於 BLOCKED registry 並要求人工 recheck owner。
- TC-BC-001 (REQ-005) [category: state/side effects, expected_initial_status: red]：對外 public API 與 `src/**` 無任何變更；僅測試層 import 風格調整，不改變既有對外契約行為。
- TC-REG-001 (REQ-002, REQ-003) [category: integration points, expected_initial_status: red]：`tests/contracts/test_import_contract_http_client_module_path.py` 既有 import-contract 驗證持續可用，且 patch-before-import 限制僅存在於 import-contract 範疇。

## Validation Commands

```bash
uv run pytest tests/ -q
uv run ruff check tests/
uv run pyright
git --no-pager diff --name-only
```

## Risks

- 分類邊界不清可能造成誤刪合法 import-contract 測試 helper。
- 若只移除表層 helper 呼叫，可能遺留 fixture 轉移規避。

## Rollback Plan

- 若分類規則造成誤判，回滾本 topic 在 `tests/**` 與 `plan/analysis` 對應改動，回到 BLOCKED 分類重審。
- 若偵測到 `src/**` 被觸及，立即停止並回退至 scope-correct 狀態。

## Open Questions

- BLOCKED 案例 owner 已定義為本 topic 指派 reviewer（非 implementation-start blocker）；實作可先行，僅個案分類定版走人工 recheck。
