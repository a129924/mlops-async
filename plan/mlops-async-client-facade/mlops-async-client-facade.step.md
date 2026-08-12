---
topic: mlops-async-client-facade
phase: plan-authoring
status: approved
created: 2026-08-12
---

# mlops-async-client-facade Step Tracking

> plan-review、implementation-review、code-review 與 full-validation 均已完成；僅 `publish` 保持 pending。下列 2026-08-12 記錄是歷史證據，不覆蓋 2026-08-13 的 authoritative completion evidence。

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring — scoped TDD/focused evidence only；不是本次 final validation。
- [X] implementation — existing provisional facade/root export/tests/docs retained；不表示 Tach correction 已完成。
- [X] tach-correction — root seven-target list 已依核准順序完成，transport list 維持只有 `mlops_async.core`, `mlops_async.exceptions`；`tach check` 通過。
- [X] full-validation — isolated Linux-native ext4 snapshot validation completed.
- [X] implementation-review
- [X] code-review
- [ ] publish

## Implementation Steps

- [X] 1. Independent plan reviewers 已核准六 artifacts 的 strict analysis routing、exact target contract 與 ReadOnly boundary；`plan-review` 為歷史完成 gate。
- [X] 2. 只修正既有 `tach.toml`：root list 依精確順序為 `mlops_async.clients`, `mlops_async.core`, `mlops_async.transport`, `mlops_async.clients.cas_tables`, `mlops_async.clients.job_execution`, `mlops_async.clients.models`, `mlops_async.clients.projects`；transport list 維持只有 `mlops_async.core`, `mlops_async.exceptions`。
- [X] 3. 在 `tests/unit/test_mlops_async_client.py` 補加 close 後 properties 可讀且 identity 不變、domain requester closed-transport propagation、first authenticated domain request lazy password-token flow tests；`tach check` 與 required focused/static validations 已完成。
- [X] 4. Independent implementation re-review、independent code review 與 isolated Linux-native ext4 full non-E2E validation completed.
- [ ] 5. 全部 gates 綠燈後，Main Agent 才可進入 `publish-in-progress`，再執行 topic commit、push、draft PR 與 human review；不含 VERSION/tag/release。

## Review Gate

## Implementation-review rework record (2026-08-12)

Independent main-workflow and Python-companion plan reviews returned `approved` with no blockers；`plan-review` 已完成。Independent implementation review 則為 `needs-rework`，所以 current status 是 `creator-in-progress`。已勾選的 scoped TDD/implementation 項目僅代表 historical/provisional work；它們不完成 `tach-correction`、`full-validation`、implementation re-review、code-review 或 `publish`。

## Implementer evidence (2026-08-12)

- `uv run --frozen --no-sync pytest --no-cov tests/unit/test_mlops_async_client.py tests/unit/clients/test_auth_client.py`: `30 passed`.
- `uv run --frozen --no-sync pytest -m "not viya_e2e"`: assertions completed as `693 passed, 9 skipped, 1 deselected`; coverage `94.38%` met the 90% threshold. The command is nevertheless nonzero because `tests/unit/test_importlib_policy_guard.py::test_tc_bc_001_req_006_tests_scope_evidence_guard_is_still_red` reads the linked-worktree `.git` Windows path as Linux-relative. This is an environment exception, not a product assertion or coverage failure, and keeps `full-validation` pending.
- `uv run --frozen --no-sync ruff check --no-fix .`: passed.
- `uv run --frozen --no-sync pyright`: `0 errors, 0 warnings, 0 informations`.
- `uv run --frozen --no-sync tach check`: passed; native Git `diff --check` passed.

Implementation-review required rework 已完成：root list 精確排序與三項 bounded facade tests 均已補足。`full-validation` 仍因 WSL linked-worktree environment exception pending；implementation re-review、`code-review` 與 `publish` 亦保持 pending。

## Authoritative completion evidence (2026-08-13)

This section supersedes the provisional 2026-08-12 evidence above. An isolated
Linux-native ext4 detached checkout rebuilt the current uncommitted snapshot
from base `e311e9e34c62979bb2ea5915e11c5d5fcbec07b2`; six tracked diffs and eight
topic-untracked files hash-matched before validation. `uv sync --frozen`
passed. Full non-E2E pytest passed with `694 passed, 9 skipped, 1 deselected`
and 94.38% coverage. Ruff, Pyright, Tach, and `git diff --check` also passed.
The retained transcript is
`/tmp/mlops-async-facade-validation-results-20260813-91d3b5e4.txt`
(SHA-256 `2b4d1be6dcf35fe78e44b5a6041a499c7ea2c8c452eab451368f57b35f8f0e83`).
The disposable checkout and bare cache were deleted after validation.

Independent implementation review and independent code review are approved.
Only `publish` is pending. No commit, push, draft PR, merge, version bump,
tag, or release has been performed.
