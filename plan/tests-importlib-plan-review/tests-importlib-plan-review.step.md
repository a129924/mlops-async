---
topic: tests-importlib-plan-review
phase: code-review
created: 2026-05-28
---

# tests-importlib-plan-review — Step Tracker

> **Resume source**：`python-implementation-workflow` 的 Phase 0 會從本檔 `## Workflow Stages` 的 `[X]/[ ]` 重建目前 phase；第一個未完成項目就是目前 resume phase。
> **Gate source**：Phase 3 只會用 `python .github/skills/plan-step-tracker/scripts/step_tracker.py check_impl_steps_succeeded tests-importlib-plan-review` 掃描 canonical `## Implementation Steps`。
> **Current state**：`tests/` 內非必要 `importlib` 用法已改寫為絕對引入；唯一保留案例是 `tests/unit/core/test_client_contract.py` 的 `importlib.util.find_spec(...)` importability assertion。

## Workflow Stages

- [X] 0 Pre-flight
- [X] 1 Plan Review
- [X] 2 TDD Assessment
- [X] 3 Implementation Gate
- [X] 4 Implementation Review
- [X] 5 Code Review

## Implementation Steps

- [X] 1. 盤點 `tests/` 內所有 `importlib` 用法，記錄檔案位置、scope、載入形式、被測對象，以及候選絕對引入路徑。
- [X] 2. 逐案分類每個使用情境是「一般引入替代」、「真正 importability test」，還是「需要人工 review 的載入機制敏感案例」，並留下判定理由。
- [X] 3. 將所有非例外案例改寫為絕對引入；必要時保留 module namespace、延後引入時機與 fixture / helper scope，以維持原本測試語意。
- [X] 4. 驗證改寫前後的 module identity、fixture behavior、monkeypatch / mock 綁定點、assertion intent 與 test outcome 一致，並執行受影響測試的必要驗證。
- [X] 5. 彙整保留案例、人工 review blockers 與驗證結果，讓 `Implementation Review` / `Code Review` 能直接追溯每個改寫決策。

## Current Resume Notes

- workflow 已完成 `0 → 5` 全部 phase；若後續再有 delta，必須由新的 workflow run 重新進入相應 phase。
- 本次 rewrite 保留 helper scope 內的絕對 import，以維持原本 module namespace、延後引入時機與 `pytest.fail(...)` 訊息語意。
- `plan.md` 與 `spec.md` 無衝突；唯一保留的 importlib 使用是 `test_client_contract.py` 中的 `importlib.util.find_spec(...)` importability assertion。

## Future Implement / PR / Release Checklist

> 本節是附加提醒，不是 Phase 0 resume source，也不是 Phase 3 `check_impl_steps_succeeded` 的 gate source。
> 後續 Implement / PR / Release 如需核對，應讀這一節的敘述，但不得把這裡的項目當成 canonical `## Implementation Steps`。

### Implement / review evidence

- 已改寫 8 個測試檔的 `importlib.import_module(...)` helper；全部改為 helper scope 內的絕對 `import ... as ...`，避免改變 monkeypatch 綁定點與錯誤訊息語意。
- 保留案例：`tests/unit/core/test_client_contract.py::test_transport_http_client_is_only_supported_concrete_client_module_path` 仍使用 `importlib.util.find_spec(...)`，因為它直接驗證 importability/module-path contract。
- 無人工 review blocker；`plan.md` 與 `spec.md` 一致，且本 topic 未修改 `src/`。
- 驗證 evidence：`uv run ruff check ...` ✅、`uv run pyright --pythonpath . ...` ✅、`uv run pytest` ✅（103 passed, coverage 95.36%）。

### PR / merge expectations

- PR 應清楚列出哪些 `importlib` 被移除、哪些 importability tests 被保留、哪些案例被標記人工 review。
- merge 前只能宣告本 topic 實際完成的 rewrite 範圍；未處理案例必須留在 blocker 或後續 topic。
- 本 topic 不需要 release action；若未來有人主張需要 release，必須另開 topic 或更新 plan contract，而不是污染當前 gate source。
