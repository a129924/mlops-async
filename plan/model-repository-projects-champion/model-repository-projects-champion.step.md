---
topic: model-repository-projects-champion
phase: pr-open
created: 2026-08-10
status: pr-open
---

# model-repository-projects-champion Step Tracking

> **Executor**: 僅在完成後將步驟標記為 `[X]`。
> 所有 Implementation Steps 均為 `[X]` 後，才可提交 `python-implementation-review`。
> 更新位置：`plan/model-repository-projects-champion/model-repository-projects-champion.step.md`。

## Workflow Stages

- [X] plan-authoring（已依 human override 將 `ChampionModel.score_code_type` 修訂為 optional，並保留最小 Projects-local test collection boundary）
- [X] plan-review（corrected public contract 已完成獨立 Plan-Reviewer review）
- [X] tdd-test-authoring（已先以 corrected contract 撰寫並驗證 RED tests）
- [X] implementation（已完成 optional `scoreCodeType` correction 與既有 Projects scope implementation）
- [X] implementation-review（已完成對未 commit corrected implementation 的獨立 `python-implementation-review`）
- [X] code-review（已於 implementation review 通過後完成獨立 `python-code-review`）

## Implementation Steps

- [X] 1. 已確認既有空的 `tests/unit/clients/projects/__init__.py` 仍為唯一的 Projects family-local test package marker；未新增 Models marker、parent-package marker 或任何 runtime/public-contract 變更。
- [X] 2. 已在 `tests/unit/clients/projects/test_value_objects.py` 與 `tests/unit/clients/projects/test_client.py` 撰寫並驗證 RED tests，涵蓋 VOs/parsers、requests、validation、lookup invariants、Champion metadata/file references、`scoreCodeType` missing/null/non-string parser matrix 與 peer-family isolation。
- [X] 3. 已修訂 `src/mlops_async/clients/projects/value_objects.py` 中 frozen/slotted Project 與 Champion VOs、`ProjectsResponseError` 與 parser；`ChampionModel.score_code_type` 為 `str | None`，missing/null -> `None`，non-string/non-null -> `ProjectsResponseError`，且未建立 content result type。
- [X] 4. 已完成 `src/mlops_async/clients/projects/client.py`：requester-only construction、single-page list、encoded get、sequential exact-name lookup 與 Champion metadata retrieval。
- [X] 5. 已完成 family-local `src/mlops_async/clients/projects/__init__.py` exports，未變更 Models/core/transport public contract。
- [X] 6. 已確認 `tach.toml` 的 locked Projects package/client/value-objects declarations；未新增 `mlops_async.clients.models` edge。
- [X] 7. 已完成 implementation validation 與 path-limited diff：Projects targeted suite `46 passed`；full suite `554 passed`，coverage `95.35%`；並已覆蓋 `scoreCodeType` missing/null/non-string 行為。implementation review 與 code review 已完成；topic comment-fix commit、push，以及 GitHub review threads 的回覆／resolve 仍未完成。
