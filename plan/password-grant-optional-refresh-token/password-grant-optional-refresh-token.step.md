---
topic: password-grant-optional-refresh-token
phase: publication-pr-ready
created: 2026-07-31
---

# password-grant-optional-refresh-token Step Tracking

> **Executor**：僅在對應工作與要求的證據完成後標記 `[X]`。
> 全部 Implementation Steps 為 `[X]` 前，不得送交 implementation review。

## Workflow Stages

- [X] plan-authoring
- [X] plan-review（獨立 Plan-Reviewer approved）
- [X] tdd-test-authoring
- [X] implementation
- [X] tester-validation（non-live 與單次 live assertion evidence recorded）
- [X] implementation-review（approved；無 topic blocker）
- [X] code-review（approved；無 topic blocker）
- [ ] publication / PR ready（尚未開始；等待獨立 human authorization for commit, push, and Ready PR）
- [ ] merge（尚未開始；獨立 human authorization）
- [ ] release `0.15.1`（僅 merge 後獨立 human gate）

## Current State

- planning artifacts 已建立完成；Plan-Reviewer `approved` 已完成。
- TDD 與 implementation 已完成；其前置的新 managed worktree 與唯讀 Git cleanliness/preflight
  gate 保持有效且已完成。
- non-live tester-validation 已完成：Ruff format/check、Pyright、Tach 與 `uv lock --check` 均通過；
  暫時以 WSL `GIT_DIR`/`GIT_WORK_TREE` workaround 執行 `pytest -m "not viya_e2e"`，得到
  `403 passed, 9 skipped, 1 deselected`、coverage `95.04%`。
- 該 workaround 僅是非 live validation 的環境相容處置，不是 Git 寫入、native fallback 或 live
  authorization。implementation review 與 code-review 均已 approved、無 topic blocker；
  publication/PR 只屬 ready 且尚未開始，commit、push、PR、merge 與 release 維持未完成。
- 唯一一次已授權 live external request 已完成：
  `test_password_token_e2e_validates_exact_success_contract` assertion 為 `1 passed`，沒有
  redacted failure、retry 或 secret 輸出。pytest process overall exit `1` 僅因 single-file
  全專案 coverage `64.96% < 90%`，不是 E2E assertion failure；不得重跑 live。
- release `0.15.1` 仍需 merge 後的獨立 human gate；review approval 或 publication/PR ready
  不構成 release 授權。

## Implementation Steps

- [X] 1. TDD 前確認 Plan-Reviewer `approved`，並在 expected base 的新 managed worktree 完成唯讀 Git preflight：registration/path、branch/base 關係與 `git status --short` 都沒有未授權或不相關變更。
- [X] 2. 取得 planning artifacts 保留、複製、stage 或 commit 的獨立 human authorization；未授權時不得由 implementation 自動處理。
- [X] 3. 在 `tests/unit/core/test_password_token_endpoint_client.py` 建立 omitted-refresh success、present-invalid rejection 與 legacy password re-obtain 的 RED cases。
- [X] 4. 只修改 `src/mlops_async/core/token_endpoint/password.py`，放寬 first obtain 的 omitted refresh token，並保留 refresh fallback。
- [X] 5. 在 `tests/unit/test_viya_e2e_pytest_guard.py` 建立雙 exact-value live opt-in 的 RED cases。
- [X] 6. 只修改 `tests/conftest.py`，要求 `RUN_VIYA_E2E=1` 與 `VIYA_E2E_VPN_CONFIRMED=1` 同時成立。
- [X] 7. 透過 WSL 完成 scoped/non-E2E validation；Ruff format/check、Pyright、Tach 與
  `uv lock --check` 通過。暫時以 `GIT_DIR`/`GIT_WORK_TREE` workaround 執行
  `pytest -m "not viya_e2e"`：`403 passed, 9 skipped, 1 deselected`，coverage `95.04%`；
  已確認 `git diff --check` 通過。
- [X] 8. 已在明確 human live authorization、兩 env vars 都精確為 `1`、且具有 fresh VPN human confirmation 後，以 ReadOnly `tests/integration/test_viya_password_token_e2e.py` 執行唯一一次 first-obtain live assertion：`test_password_token_e2e_validates_exact_success_contract` 為 `1 passed`，無 redacted failure/retry/secret 輸出。process exit `1` 僅為 single-file coverage `64.96% < 90%`，不是 assertion failure；不得重跑。

## Scope Guards

- **ReadOnly**：`tests/integration/test_viya_password_token_e2e.py`、`src/mlops_async/core/auth.py`、`src/mlops_async/core/token_storage.py`、`src/mlops_async/core/token_endpoint/_shared.py`、`config/.env.test` 及所有舊 worktree。
- **Modify**：僅 `src/mlops_async/core/token_endpoint/password.py`、`tests/unit/core/test_password_token_endpoint_client.py`、`tests/conftest.py`、`tests/unit/test_viya_e2e_pytest_guard.py`。
- **Deleted**：無。
