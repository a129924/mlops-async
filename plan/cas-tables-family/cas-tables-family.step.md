---
topic: cas-tables-family
phase: implementation-review
status: approved
created: 2026-08-11
---

# CAS Tables Endpoint Family Step Tracking

> `[X]` 僅表示目前 worktree 已有相符的 code/test/Tach artifact 證據；不表示本次
> planning actor 已執行測試或品質工具。完整驗證仍由第 6 步及後續 reviewer 判定。

## Workflow Stages

- [X] plan-authoring
- [X] plan-review（independent Plan-Reviewer 已回傳
  `{"verdict":"approved","blocking_issues":[],"copilot_feedback_triage":{"ADDRESS":[],"DISCUSS":[],"SKIP":[]}}`）
- Current gate: independent implementation review; workflow status is `approved`.
- [X] tdd-test-authoring（CAS unit-test modules 已於 canonical paths 完成；其涵蓋範圍記錄於已勾選的實作步驟 1 與 4）
- [X] implementation（family source、tests、Tach declarations 與 validation evidence 已由實作步驟 1 至 6 記錄）
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. 已將 value-object CAS unit-test module rename 為 collision-free unique
  canonical path `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py`，
  並保留 `TableState`、frozen/slotted `TableDetail`、
  `TablesPage.items: tuple[TableDetail, ...]` 與 strict parser tests。
- [X] 2. `src/mlops_async/clients/cas_tables/value_objects.py` 已含 family response
  error、enum、兩個 value objects 及 strict semantic parsers 的 artifact 證據。
- [X] 3. `src/mlops_async/clients/cas_tables/client.py` 與 `__init__.py` 已含
  caller-owned client、pre-I/O state conversion、三條 `/casManagement` endpoint paths、
  specified return types 與 family-local re-exports 的 artifact 證據。
- [X] 4. 已將 client CAS unit-test module rename 為 collision-free unique canonical
  path `tests/unit/clients/cas_tables/test_cas_tables_client.py`，並保留 list/get/state
  shape、pre-I/O validation、failure propagation、encoding 與 public-surface tests。
- [X] 5. `tach.toml` 已含 `mlops_async.clients.cas_tables`、`.client`、`.value_objects`
  declarations 的 artifact 證據。
- [X] 6. Validation evidence rework 已確認 main-worktree Linux
  `.venv/bin/python` 以 feature `PYTHONPATH` import feature package，並驗證
  feature `GIT_DIR` 與 `GIT_WORK_TREE`。approved paired target pytest command
  將兩個 renamed test files 與 `--override-ini addopts=""` 一併執行，結果為
  `49 passed in 7.05s`；在 `--no-sync` 下，main Python 3.10.20 與要求的
  Python 3.10.0 不相容，uv 因而輸出 incompatible-environment warning。保留的
  scoped Ruff、Pyright、Tach evidence 為 exit 0。經 feature Git variables 的
  retained latest default full pytest evidence 精確為 `603 passed, 10 skipped`、
  95.54% coverage。八個 untracked topic paths 逐檔以
  `git diff --no-index --check -- /dev/null <path>` 檢查，均未輸出 whitespace
  diagnostic（exit 1 是預期的 no-index content-difference status）；這是
  untracked-content evidence，不是普通 `git diff --check`。沒有下載、安裝或修改
  dependency；implementation 仍可路由至 `review-ready`。
