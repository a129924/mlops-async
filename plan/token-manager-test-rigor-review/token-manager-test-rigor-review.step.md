---
topic: token-manager-test-rigor-review
phase: implementation
created: 2026-05-23
---

# token-manager-test-rigor-review — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. 更新 `requirements.md`、`technical-spec.md`、`plan.md`、`step.md`、`spec.md`，把 topic 鎖定為 `C-004`~`C-006` 的 implementation contract。
- [X] 2. 在 `tests/unit/core/test_token_manager.py` 新增 `AuthException` pass-through、manager-level custom skew、empty-storage concurrency fetch dedup 測試。
- [X] 3. 執行 pytest 驗證新測試；若揭露 production bug，僅在 `src/mlops_async/core/auth.py` 做最小修補並重跑驗證。
- [X] 4. 更新 `testcase-inventory.md`、`rigor-matrix.md`、`verdict.md`，保留 baseline audit trail 並標記 gaps 已由具體測試關閉。
