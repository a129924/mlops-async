---
topic: tests-remove-nonessential-xxx-module-helpers
phase: code-review
created: 2026-05-31
---

# tests-remove-nonessential-xxx-module-helpers — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/tests-remove-nonessential-xxx-module-helpers/tests-remove-nonessential-xxx-module-helpers.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Phase 2 Prerequisites (machine-verifiable)

- [X] phase2-plan-approval-evidence-recorded (evidence_id: PHASE2-APPROVED-2026-05-31)
- [X] phase2-requirement-to-test-mapping-recorded (source: *.plan.md + *.spec.md)
- [X] phase2-planned-test-expected-initial-status-recorded (status: red for planned RED tests)
- [X] phase2-requirement-to-test-mapping-updated-for-ambiguous-blocked-rule (REQ-004 -> TC-BLK-001)
- [X] phase2-requirement-to-test-mapping-updated-for-req-003-and-req-006 (REQ-003 -> TC-REG-001, REQ-006 -> TC-BC-001)
- [X] phase2-tdd-test-authoring-executed (evidence: targeted pytest command executed with RED outcomes)
- [X] phase2-expected-initial-status-verified (TC-HP-001, TC-INV-001, TC-EDGE-001, TC-BC-001, TC-REG-001, TC-BLK-001 all observed red)
- [X] phase2-targeted-pytest-outcome-recorded (`6 failed, 5 passed`; failed IDs include TC-HP-001 / TC-BC-001 / TC-REG-001)

## Implementation Steps

- [X] 1. 建立 `tests/**` helper-style usage inventory，逐檔列出 `*_module()` / `xxx_module` 用法與測試目的。
- [X] 2. 產出 `allowed / rewrite / BLOCKED` 三類清單，並對 BLOCKED 案例標記人工 recheck owner。
- [X] 3. 將 `rewrite` 類行為測試改為 explicit import，確認無 helper-style usage 與無 fixture 轉移規避。
- [X] 4. 審核 `allowed` 類 import-contract 測試，確認每個保留用法皆屬 import path/importability/contract 驗證，且 patch-before-import 僅限此類。
- [X] 5. 新增/擴充 policy guard，阻擋行為測試 helper-style usage（含 indirect helper/fixture bypass）。
- [X] 6. 執行驗證命令；若存在 `tests/**` 變更，確認其 evidence path 全部位於 `tests/**`，無 `tests/**` 變更時此 guard 亦可通過；回填結果供後續 review gate。

## Implementation Evidence

### Step 1 — Helper-style usage inventory (`tests/**/*.py`)

- `tests/unit/core/test_auth_contract.py`
  - L11/L21: 定義 `_auth_module()`、`_token_storage_module()` wrapper（import helper）
  - L13/L23: `as auth_module`、`as token_storage_module` alias import
  - L42/L43/L55/L67/L68: contract 測試內呼叫 helper wrapper
- `tests/unit/core/test_auth_provider.py`
  - L8/L18: helper wrapper 定義
  - L10/L20: `_module` alias import
  - L41/L42: 行為測試呼叫 helper wrapper
- `tests/unit/core/test_client_contract.py`
  - L10/L17: `client_module`、`http_client_module` alias import
- `tests/unit/core/test_requester_auth_boundary.py`
  - L12/L22/L30: helper wrapper 定義
  - L14/L24/L32: `_module` alias import
  - L119/L152/L171/L190/L191: 行為測試呼叫 helper wrapper
- `tests/unit/core/test_token_manager.py`
  - L9/L19: helper wrapper 定義
  - L11/L21: `_module` alias import
  - L93~L369: 多個 token manager 行為測試呼叫 helper wrapper（auth/token_storage）
- `tests/unit/core/test_token_storage.py`
  - L8: helper wrapper 定義
  - L10: `_module` alias import
  - L20/L30/L41/L51/L61: 行為測試呼叫 helper wrapper
- `tests/unit/transport/test_exceptions.py`
  - L9/L15: helper wrapper 定義
  - L10/L17: `_module` alias import
  - L33/L44/L55/L56/L69/L87/L112/L141: 測試呼叫 helper wrapper
- `tests/unit/transport/test_http_client.py`
  - L19/L33/L43: `_module` alias import
  - L31/L42: helper wrapper 定義
  - L220/L249/L326: 測試呼叫 `_http_client_module()`

### Step 2 — Classification (`allowed / rewrite / BLOCKED`)

| class | cases | reason | owner |
|---|---|---|---|
| rewrite | 上述 `tests/unit/core/*.py` 與 `tests/unit/transport/*.py` 全部 helper-style 命中 | 屬行為/單元語義驗證，不屬 import path/importability/import-contract 例外 | implementation executor |
| allowed | `tests/contracts/test_import_contract_http_client_module_path.py`（import path/importability/contract 驗證） | 僅保留 import-contract 邊界；本次無 helper-style/patch-before-import 實際使用，已在常數明確記錄 none-observed | implementation executor |
| BLOCKED | 無 | 本輪 inventory 無無法安全判定案例 | N/A |

### Step 3 — Rewrite evidence

- 將 rewrite 類檔案改為 explicit import（移除 `*_module()` wrapper 與 `xxx_module` alias）：
  - `tests/unit/core/test_auth_contract.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_client_contract.py`
  - `tests/unit/core/test_requester_auth_boundary.py`
  - `tests/unit/core/test_token_manager.py`
  - `tests/unit/core/test_token_storage.py`
  - `tests/unit/transport/test_exceptions.py`
  - `tests/unit/transport/test_http_client.py`
- post-rewrite inventory evidence：`NO_HELPER_STYLE_USAGE`（AST scan for wrapper def / alias / call）

### Step 4 — Allowed import-contract + patch-before-import scope

- `tests/contracts/test_import_contract_http_client_module_path.py` 維持 import path/importability/contract 斷言：
  - `find_spec("mlops_async.transport.http_client")` 可匯入
  - `find_spec("mlops_async.core.http_client")` 不可匯入
- `IMPORT_CONTRACT_PATCH_BEFORE_IMPORT_CASES` 記錄：
  - `none-observed: tests/**/*.py inventory found no patch-before-import usage; owner=@a129924`
- 代表 patch-before-import 未被當成一般豁免，且證據只留在 contract 檔案。

### Step 5 — Policy guard expansion evidence

- `tests/unit/test_importlib_policy_guard.py`：
  - 新增 `_iter_behavior_test_files()`，僅掃描 `tests/unit/core`、`tests/unit/transport` 行為測試範圍
  - 保留 helper-style alias/call 與 wrapper definition 偵測
  - 新增 `_collect_fixture_helper_bypass_violations()`，補抓 fixture 內 indirect helper/alias bypass
  - `TC-BC-001` 由 placeholder 改為 `tests` scope evidence guard：只在存在 changed test paths 時驗證其皆位於 `tests/**`，沒有 changed test paths 亦可通過
- contracts 例外不被誤攔：helper-style/fixture bypass 檢查僅作用於 behavior test roots。

### Step 6 — Validation evidence

- `uv run pytest tests/ -q` → `113 passed, 1 warning`
- `uv run ruff check tests/` → `All checks passed!`
- `uv run pyright` → `0 errors, 0 warnings, 0 informations`
- `git --no-pager diff --name-only` → 當時 implementation diff 實際落在 `tests/**`；此為滿足 `REQ-006` 的一組有效證據，但 `REQ-006` canon 不要求必須存在 `tests/**` 變更
