---
topic: coverage-agent
phase: plan-authoring
created: 2025-07-07
---

# coverage-agent — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/coverage-agent/coverage-agent.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. 開啟 `pyproject.toml`，在 `[tool.pytest.ini_options]` block 加入 `addopts`
- [X] 2. 開啟 `pyproject.toml`，append `[tool.coverage.run]` section
- [X] 3. 開啟 `pyproject.toml`，append `[tool.coverage.report]` section（`fail_under = 80`）
- [X] 4. 開啟 `pyproject.toml`，append `[tool.coverage.json]` section（output path）
- [X] 5. 開啟 `.gitignore`，append `.coverage` 和 `.coverage-reports/`
- [X] 6. 開啟 `.pre-commit-config.yaml`，在既有 pytest hook 之後插入 `coverage-check` hook（不動既有 hook）
- [X] 7. 建立 `scripts/coverage_agent.py`，實作所有常數、`_FunctionInfo`、`_run_pytest`、`_load_coverage_json`、`_gap_modules`、`_has_stop_condition`、`_find_docs_explanation`、`_extract_functions`、`_module_stem`、`_test_file_path`、`_generate_stub`、`_write_stubs`、`_human_review_feedback`、`_process_module`、`main`
- [X] 8. 執行 `uv run tach check` 確認 `scripts/` 不違反邊界
- [X] 9. 建立 `tests/unit/test_coverage_agent.py`，實作 Test Plan 所有測試案例
- [X] 10. 執行 `uv run ruff check scripts/coverage_agent.py` 並修正所有 violations
- [X] 11. 執行 `uv run pytest tests/unit/test_coverage_agent.py -v` 確認所有測試通過
- [X] 12. 執行 `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=term-missing` 確認整體 coverage gate 通過
