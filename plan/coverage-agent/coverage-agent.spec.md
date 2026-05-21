# coverage-agent Specification

## Acceptance Criteria

1. `pyproject.toml` 含 `addopts` 後，`uv run pytest tests/unit/` 執行成功時，`.coverage-reports/coverage.json` 自動存在於該固定路徑
2. `pyproject.toml` `[tool.coverage.report]` 設 `fail_under = 80` 後，pytest 在覆蓋率 < 80% 時返回非零 exit code
3. `.pre-commit-config.yaml` 新增 `coverage-check` hook 後，既有 `stages: [manual]` pytest hook 的行為 **不變**（git commit 時不觸發）
4. `python scripts/coverage_agent.py` 在覆蓋率 ≥ 80% 時返回 exit code 0，不生成任何 stub 檔案
5. `python scripts/coverage_agent.py` 在覆蓋率 < 80% 且函式有 docstring、無 stop-condition keyword 時，於 `tests/unit/test_<module>.py` 生成含 `def test_<func>()` 和 `assert False` 的 stub
6. `python scripts/coverage_agent.py` 在觸發停止條件（stop-condition keyword 或無 docstring 且無 docs 說明）時，stdout 輸出 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` block，**不**寫入任何測試檔案
7. 同一函式的 stub 在同一 test file 中不重複（duplicate prevention 正確運作）
8. `uv run ruff check scripts/coverage_agent.py` 輸出 0 violations
9. `uv run tach check` 通過，`tach.toml` 無需修改

---

## Behavioral Scenarios

### Scenario 1: 正常 stub 生成路徑
- **Given**: `coverage.json` 中 `src/mlops_async/foo.py` 的 `percent_covered = 65.0`，missing lines `[45, 46, 47]`；`foo.py` 的 `bar(x: int) -> bool` 函式包含 `"""Check if x is positive."""` 且無 stop-condition keyword；`tests/unit/test_foo.py` 不存在
- **When**: `_process_module("src/mlops_async/foo.py", [45, 46, 47])` 被呼叫
- **Then**: `tests/unit/test_foo.py` 被新建，內容含 `from src.mlops_async import foo`（或對應 import）、`def test_bar():` 和 `assert False, "stub"`

### Scenario 2: 停止條件觸發 — stop-condition keyword
- **Given**: `coverage.json` 中 `src/mlops_async/uploader.py` 的 `percent_covered = 50.0`；`upload_file(path: str) -> None` 的 docstring 含 `"upload"`；`tests/unit/test_uploader.py` 不存在
- **When**: `_process_module("src/mlops_async/uploader.py", [30, 31, 32])` 被呼叫
- **Then**: stdout 輸出包含 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]`；`tests/unit/test_uploader.py` **不**被建立

### Scenario 3: 停止條件觸發 — 無 docstring 且無 docs
- **Given**: `coverage.json` 中 `src/mlops_async/util.py` 的 `percent_covered = 70.0`；`mystery_fn()` 無 docstring；`docs/` 和 `analysis/` 中無任何包含 `util` 的說明
- **When**: `_process_module("src/mlops_async/util.py", [10])` 被呼叫
- **Then**: stdout 輸出包含 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]`，停止原因說明「無 spec/docs 可參考」；不生成 stub

### Scenario 4: 覆蓋率已達標
- **Given**: `coverage.json` 中所有 `src/mlops_async/*.py` 的 `percent_covered >= 80.0`
- **When**: `main()` 被呼叫
- **Then**: `_process_module()` 從未被呼叫；`_run_pytest()` 被呼叫一次以確認最終結果；`main()` 返回 `0`

### Scenario 5: 重複 stub 防護
- **Given**: `tests/unit/test_module.py` 已存在且含 `def test_existing_func():`
- **When**: `_write_stubs(test_file, [stub_for_existing_func], module_import)` 被呼叫
- **Then**: `test_existing_func` 在檔案中只出現一次（不重複 append）

---

## Error / Edge Cases

- `coverage.json` 不存在時，`_load_coverage_json()` 先觸發 `subprocess.run` 跑 pytest；若跑完後 json 仍不存在，`sys.exit(1)` 且 stderr 輸出明確訊息
- `ast.parse()` 對目標 source file 失敗（`SyntaxError`）時，`_extract_functions()` 捕捉例外、回傳 empty list，並輸出 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]`（無法解析）
- source file 路徑不存在（OSError）時，`_extract_functions()` 回傳 empty list
- `_find_docs_explanation()` 對 rglob 結果截取前 500 字元，避免超大 Markdown 拖慢腳本
- `coverage-check` hook 在 `tests/unit/` 完全為空時行為（RISK-3）— Open Questions 確認後決定 `|| true` 是否加入 hook entry
- 若一個模組同時有可生成 stub 的函式和觸發 stop condition 的函式，應各自獨立處理（partial stub + partial feedback，不互相阻擋）
