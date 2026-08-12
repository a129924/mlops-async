---
topic: cas-tables-family-table-detail-metadata
phase: publish-in-progress
status: publish-in-progress
created: 2026-08-12
---

# CAS Tables Table Detail Metadata Step Tracking

> 本 step tracker 屬於新的 bounded follow-up topic；既有
> `plan/cas-tables-family/cas-tables-family.step.md` 的完成狀態不適用於此處。
> 獨立 Plan-Reviewer 已回傳 `approved`，且 `blocking_issues` 為空（zero
> blockers）；canonical `review-ready -> reviewer-in-progress -> approved ->
> creator-in-progress` 已完成。implementation steps 現為下一個工作。

## Workflow Stages

- [X] plan-authoring
- [X] review-ready
- [X] plan-review（independent Plan-Reviewer `approved`；zero blockers）
- [X] reviewer-in-progress
- [X] approved
- [X] creator-in-progress
- [X] implementation-review (`python-implementation-review` approved)
- [X] code-review (`python-code-review` approved; zero findings)
- [X] publish-in-progress
- [ ] pr-open
- [ ] merged

## Implementation Steps

- [X] 1. 在 `tests/unit/clients/cas_tables/test_cas_tables_value_objects.py`
  建立完整 mapping、optional missing/null、required missing/null/non-string、
  optional wrong-type、raw string preservation、exact allowlist、unknown field、
  `caslibName` rejection 與 frozen/slotted contract tests。
- [X] 2. 在 `src/mlops_async/clients/cas_tables/value_objects.py` 擴充
  `TableDetail` 四個 public date fields，更新 exact wire allowlist、mapping 與
  required/optional failure semantics；保留既有 name/caslib/state semantics。
- [X] 3. 在 `tests/unit/clients/cas_tables/test_cas_tables_client.py` 更新三個
  endpoint response payloads/expected values 以提供 required `created` 與
  `lastModified`，並確認 request assertions 無變更。
- [X] 4. 執行 plan 指定的 targeted pytest、Ruff、Pyright、Tach 與 diff checks，
  確認沒有超出列出的 source/test write boundary，完成後 hand off
  `review-ready`。

## Completion Gate

- 獨立 Plan-Reviewer 已在 canonical `reviewer-in-progress` 中完成審查並回傳
  `approved`、zero blockers；不建立或使用 `independent-plan-review` stage。
- 已依 `reviewer-in-progress -> approved -> creator-in-progress` 完成狀態遷移；
  implementation steps 與後續 review/publish/PR/merge 仍未完成。
- Creator 完成上述四個 implementation steps 與 validation evidence 後，才可
  依 `creator-in-progress -> review-ready` hand off，供 implementation-review
  使用。
- Creator 只能更新本 step tracker 的 checkbox/status evidence；Creator 不得
  改寫或重產
  `plan/cas-tables-family-table-detail-metadata/cas-tables-family-table-detail-metadata.plan.md`
  或 `.spec.md`。
- implementation-review 通過後才可進 code-review；兩者都不是本次
  Plan-Creator authoring 的替代品。
- 不得以既有 CAS Tables topic 的 approved/implemented evidence 代替本 topic
  的任何未完成 step。

Workflow state:

- `current_step`: `publish-in-progress`
- `next_step`: `commit-and-push`
- `status`: `publish-in-progress`

## Current Completion Evidence

- `python-implementation-review`: approved.
- `python-code-review`: approved; zero findings.
- Validation: focused pytest 74 passed; Ruff, Tach, and Pyright passed.
- Canonical transition: `approved -> publish-in-progress`.
- Commit, push, PR, and merge remain pending and are not authorized or performed by this state update.

## 2026-08-12 Pyright Follow-up Evidence

- Read-only dependency inspection confirmed `pyright>=1.1.409` is in `[dependency-groups].dev`; `uv.lock` locks `pyright` 1.1.409 in that existing `dev` group.
- Before any further sync, Ubuntu marker check confirmed `.venv/bin/pyright` is executable, so no extra group sync was necessary.
- Planned command `uv run --no-sync --python 3.10.0 pyright` completed with `0 errors, 0 warnings, 0 informations`.
- The command retained the known warning that Python 3.10.20 does not satisfy the exact requested Python 3.10.0, and Pyright reported only an available 1.1.411 upgrade; neither is a validation failure.
- No further environment sync was executed. Focused pytest (74 passed), Ruff, Tach, and native diff checks had already passed after completed sync; step 4 is now complete and the topic is ready for independent implementation review.

## 2026-08-12 Additional Validation Evidence

- Authorized Ubuntu `uv sync` timed out after 64 seconds; follow-up marker check confirmed `.venv/bin/python` exists at `/mnt/d/code/python/mlops-async.worktrees/agent-20260812-cas-table-metadata/.venv/bin/python`.
- `uv run --no-sync --python 3.10.0 pytest --override-ini addopts="" tests/unit/clients/cas_tables/test_cas_tables_value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py -q`: 74 passed in 2.28s.
- `uv run --no-sync --python 3.10.0 ruff check src/mlops_async/clients/cas_tables/value_objects.py tests/unit/clients/cas_tables/test_cas_tables_value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py`: All checks passed.
- `uv run --no-sync --python 3.10.0 pyright`: failed before analysis because `pyright` could not be spawned (`No such file or directory`, os error 2).
- `uv run --no-sync --python 3.10.0 tach check`: All modules validated.
- Every `--no-sync --python 3.10.0` command warned that the materialized `.venv` Python does not satisfy 3.10.0. Pyright is an environment/sync-completeness blocker, not a functional or coverage failure; step 4 remains pending.

## 2026-08-12 Completed-Sync Validation Evidence

- Retry of the authorized Ubuntu `uv sync` completed: `Resolved 60 packages in 4ms` and `Checked 59 packages in 302ms`.
- `.venv/bin/python --version` reported `Python 3.10.20`; every plan command still warned that this does not satisfy the exact requested `Python 3.10.0`.
- After completed sync, focused pytest passed: `74 passed in 1.78s`; assertions and collection passed, while coverage was not evaluated because the approved command cleared `addopts`.
- After completed sync, Ruff reported `All checks passed!` and Tach reported `All modules validated!`.
- After completed sync, Pyright again failed before analysis because `pyright` could not be spawned (`No such file or directory`, os error 2). This is an environment/tooling blocker, so step 4 remains pending.

## Creator 實作與驗證證據

- 2026-08-12：已完成步驟 1--3；production 變更限於 `value_objects.py`，測試變更限於兩個 CAS Tables unit test 檔。
- 2026-08-12：Windows preflight 確認 `OS=Windows_NT` 與 `wsl.exe` 可用；WSL wrapper 無法列舉 distro，回報 `Wsl/EnumerateDistros/Service/E_ACCESSDENIED` 與 `WSL development command blocked: wsl.exe is blocked`（exit code `-1`）。
- 因 WSL 環境 blocker，未執行 targeted pytest、Ruff、Pyright 或 Tach，且未以 Windows Python 或 `.venv\\Scripts` 替代；步驟 4 保持 pending。
- 2026-08-12：native `git diff --check` 成功；本次 tracked diff 僅列出三個允許 source/test 檔案。
