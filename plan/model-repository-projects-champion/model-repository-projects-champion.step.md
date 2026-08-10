---
topic: model-repository-projects-champion
phase: plan-authoring
created: 2026-08-10
status: review-ready
---

# model-repository-projects-champion Step Tracking

> **Executor**: 僅在完成後將步驟標記為 `[X]`。
> 所有 Implementation Steps 均為 `[X]` 後，才可提交 `python-implementation-review`。
> 更新位置：`plan/model-repository-projects-champion/model-repository-projects-champion.step.md`。

## Workflow Stages

- [X] plan-authoring（已加入最小 Projects-local test collection boundary，規劃可供獨立審查）
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. 建立空的 `tests/unit/clients/projects/__init__.py`，作為唯一的 Projects family-local test package marker；不得新增 Models marker、parent-package marker 或任何 runtime/public-contract 變更。
- [X] 2. 在 `tests/unit/clients/projects/test_value_objects.py` 與 `tests/unit/clients/projects/test_client.py` 撰寫 RED tests，涵蓋 VOs/parsers、requests、validation、lookup invariants、Champion metadata/file references 與 peer-family isolation。
- [X] 3. 建立 `src/mlops_async/clients/projects/value_objects.py` 中 frozen/slotted Project 與 Champion VOs、`ProjectsResponseError` 與 parser；保留 caller-observable `ChampionModel.files` / `ChampionFile` references，且不建立 content result type。
- [X] 4. 建立 `src/mlops_async/clients/projects/client.py`：requester-only construction、single-page list、encoded get、sequential exact-name lookup 與 Champion metadata retrieval。
- [X] 5. 建立 family-local `src/mlops_async/clients/projects/__init__.py` exports，不變更 Models/core/transport public contract。
- [X] 6. 以 post-review Implementer 身分，在 `tach.toml` 加入已鎖定的 Projects package/client/value-objects declarations；不得新增 `mlops_async.clients.models` edge。
- [X] 7. 執行已授權 implementation validation 與 path-limited diff；先以 `uv run pytest tests/ --collect-only` 驗證 Models/Projects sibling `test_client.py` 無 import-file-mismatch，再執行 topic tests、Ruff、Pyright 與 Tach。若需其他 path 或 public-error 變更，停止並 re-plan。
