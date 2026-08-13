---
topic: project-info
phase: publish-in-progress
status: publish-in-progress
---

# project-info Step Tracking

> **Executor**: 僅在完成後將步驟標記為 `[X]`。
> 所有 Implementation Steps 均為 `[X]` 後，才可提交 implementation review。

## Workflow Stages

- [X] plan-authoring（已 materialize locked decisions，並記錄 optional analysis layer absent warning）
- [X] plan-review（獨立 Plan-Reviewer 已批准含 `plan/project-info/project-info.tdd-test-authoring.yaml` machine-readable TDD verdict artifact 的 current plan）
- [X] tdd-test-authoring（Tester 已完成 RED evidence：focused WSL pytest 61 collected，14 failed，47 passed；失敗對應尚未實作的 audit metadata，並已更新 `plan/project-info/project-info.tdd-test-authoring.yaml` verdict）
- [X] implementation（僅於三個 `Modify` paths 內實作）
- [X] implementation-review（獨立 implementation review 已完成並確認 implementation 符合 approved plan/spec、locked Modify paths 與 TestCase contract）
- [X] code-review（最終獨立 Reviewer 已批准；無待處理 code-quality blocker）

## Implementation Steps

- [X] 1. 在 `tests/unit/clients/projects/test_value_objects.py` 建立 field/default、exact-key、missing/string/null/non-string 和 unknown-field RED matrix。
- [X] 2. 在 `tests/unit/clients/projects/test_client.py` 建立 list/get parity 與 malformed metadata propagation tests，不改 request shape。
- [X] 3. 僅在 `src/mlops_async/clients/projects/value_objects.py` 實作四個 `str | None = None` fields 與 strict parser；保留 Champion nullable behavior。
- [X] 4. 在 WSL 執行 focused pytest、Ruff、Pyright、`uv run --frozen --no-sync tach check`、`git diff --check`，確認 future diff 僅含三個 `Modify` paths。

## Implementation Evidence

- Implementation: `ProjectSummary` 與 `ProjectDetail` 已投影 locked audit metadata keys，並對 present value 套用 strict validation。
- Validation: independent Tester 已確認 focused Projects pytest `61 passed`；Ruff format/check、Pyright、Tach 和 `git diff --check` 均通過。

## Stop Conditions

- 任一變更需要 `Modify` 外檔案、request-gate shape 調整、client/export/metadata change 或 release action 時，停止並 re-plan。
- reviewer 發現 list/detail parity、missing/null/non-string distinction 或 raw timestamp contract 不完整時，回到 `creator-in-progress` 修正再送審。
