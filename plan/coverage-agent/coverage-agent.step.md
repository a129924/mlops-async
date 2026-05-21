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
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. 開啟 `pyproject.toml`，在 `[tool.pytest.ini_options]` block 加入 `addopts`
- [ ] 2. 開啟 `pyproject.toml`，append `[tool.coverage.run]` section
- [ ] 3. 開啟 `pyproject.toml`，append `[tool.coverage.report]` section（`fail_under = 80`）
- [ ] 4. 開啟 `pyproject.toml`，append `[tool.coverage.json]` section（output path）
- [ ] 5. 開啟 `.gitignore`，append `.coverage` 和 `.coverage-reports/`
- [ ] 6. 開啟 `.pre-commit-config.yaml`，在既有 pytest hook 之後插入 `coverage-check` hook（不動既有 hook）
- [ ] 7. 建立 `scripts/coverage_agent.py`，實作所有常數、`_FunctionInfo`、`_run_pytest`、`_load_coverage_json`、`_gap_modules`、`_has_stop_condition`、`_find_docs_explanation`、`_extract_functions`、`_module_stem`、`_test_file_path`、`_generate_stub`、`_write_stubs`、`_human_review_feedback`、`_process_module`、`main`
- [ ] 8. 執行 `uv run tach check` 確認 `scripts/` 不違反邊界
- [ ] 9. 建立 `tests/unit/test_coverage_agent.py`，實作 Test Plan 所有測試案例
- [ ] 10. 執行 `uv run ruff check scripts/coverage_agent.py` 並修正所有 violations
- [ ] 11. 執行 `uv run pytest tests/unit/test_coverage_agent.py -v` 確認所有測試通過
- [ ] 12. 執行 `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=term-missing` 確認整體 coverage gate 通過
