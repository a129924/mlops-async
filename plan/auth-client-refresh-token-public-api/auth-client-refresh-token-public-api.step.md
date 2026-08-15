---
topic: auth-client-refresh-token-public-api
phase: plan-authoring
created: 2026-08-06
---

# AuthClient refresh-token public API Step Tracking

> **Executor**: 僅在該步完成時標記 `[X]`。所有 Implementation Steps 都是 `[X]` 後，
> 才能提交 `python-implementation-review`。
> 此檔案路徑：`plan/auth-client-refresh-token-public-api/auth-client-refresh-token-public-api.step.md`。

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. 在 `src/mlops_async/clients/auth_client.py` 定義 `AuthClientRefreshTokenError`，並新增
  完全型別化 refresh method：absent token fetch，present token full-protocol refresh。
- [X] 2. 在 refresh method 實作 fetch-only rejection、no-fallback、cancellation passthrough
  與一般例外的 `AuthClientRefreshTokenError` exception chaining；不變更 constructor/get method。
- [X] 3. 在 `tests/unit/clients/test_auth_client.py` 新增五個 refresh branch/error tests，並保留
  constructor/get-method regression coverage。
- [X] 4. 更新 `README.md` 的 English 與繁體中文 `AuthClient` public-surface 段落，使其符合
  已凍結的 refresh API、capability 與 import boundary；不變更 VERSION 或 release metadata。
- [X] 5. 透過 Windows-to-WSL route 執行 scoped pytest、Ruff、Pyright、Tach 和
  `git diff --check`；WSL 不可用時記錄 blocked evidence。

## Current State

- Plan-Reviewer independently approved the topic plan before implementation.
- The implementation and validation are complete; the canonical workflow state
  is `review-ready` for independent implementation review.
- Implementation review, code review, topic commit, push, draft PR, human
  review, merge, and release are not complete.

## Completed Validation Evidence

- Environment: WSL Ubuntu with Python 3.10.20. The linked worktree required
  per-subprocess `GIT_DIR` and `GIT_WORK_TREE` only.
- `ruff format` and `ruff check`: pass.
- `pyright`: pass.
- `tach`: pass.
- `pytest -m not viya_e2e`: 420 passed, 9 skipped, 1 deselected; coverage
  95.12%.
- `uv lock --check`: pass.
- `git diff --check`: pass.

## Historical Current State

> Superseded by the current state and validation evidence above.

- Plan-Creator 已完成五個 planning artifacts，topic 是 `review-ready`。
- 下一步為獨立 Plan-Reviewer verdict；未授權 TDD、implementation、commit、push、PR、merge
  或 release。
