# Coverage Agent — Python Implementation Plan

> **Analysis-layer routing: STRICT MODE**
> Both `analysis/coverage-agent/requirements.md` (FROZEN) and
> `analysis/coverage-agent/technical-spec.md` (READY FOR IMPLEMENTATION PLANNING) exist.
> This plan maps 100% to the technical spec.
> Chat-time instructions do not override analysis artifacts unless the human explicitly says `override`.
>
> **D1 verdict: `non-trivial`**
> New `scripts/coverage_agent.py` module with AST-based logic, stop-condition detection, stub generation,
> subprocess orchestration, and file I/O; plus 4 config-file modifications. Requires `spec.md`.

---

## Goal

新增 80% coverage gate（pyproject.toml + pre-commit hook）並建立靜態分析腳本 `scripts/coverage_agent.py`：讀取 `coverage.json`，找出覆蓋率不足模組，以 AST 靜態分析生成 test stub 或在觸發停止條件時輸出 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` feedback，最後重跑 pytest 驗證門檻。

---

## Non-goals

- 本次不修改 `.github/copilot-instructions.md`（門檻維持 90%，不降至 80%）
- 本次不建立 CI / GitHub Actions 的 coverage gate（僅 local pre-commit）
- 本次不修改 `src/mlops_async/` 任何 source code（coverage_agent.py 只讀 source，不寫）
- 本次不生成語義正確的測試（只生成 stub 佔位，語義正確性由人工驗證）
- 本次不觸碰 `tests/integration/`（agent 只寫入 `tests/unit/`）
- 本次不修改 `README.md`、`VERSION` 穩定函式庫介面

---

## Current Context

- `pyproject.toml`（line 72–77）：`[tool.pytest.ini_options]` 已存在，但無 `addopts`；dev deps 已有 `pytest-cov>=7.1.0`；無任何 `[tool.coverage.*]` sections
- `.gitignore`：有 Python 基本 artifacts，無任何 coverage 相關條目（`.coverage`、`.coverage-reports/`）
- `.pre-commit-config.yaml`：pytest hook 設定 `stages: [manual]`（有意設計，避免 commit 前卡住）；無 coverage gate hook
- `tach.toml`：`source_roots = ["src"]`，追蹤 `src/mlops_async.*` 模組邊界；`scripts/` 目前不存在且在 tach scope 之外
- `scripts/`：目錄不存在，需新建
- `tests/unit/`：有 `__init__.py` 與多個 unit test 檔案；無 `test_coverage_agent.py`

---

## Requirements

1. `uv run pytest tests/unit/` 在 coverage < 80% 時返回非零 exit code
2. 每次 `pytest` 執行後，`.coverage-reports/coverage.json` 自動生成於固定路徑
3. `git commit` 前，coverage-check hook 強制執行 `tests/unit/` 覆蓋率 ≥ 80%；覆蓋率不足則 commit blocked
4. 既有 `.pre-commit-config.yaml` 的 `stages: [manual]` pytest hook 不受影響
5. `python scripts/coverage_agent.py` 對覆蓋率 < 80% 且不觸發停止條件的模組，生成 `tests/unit/test_<module>.py` stub 檔案
6. `python scripts/coverage_agent.py` 對觸發任一停止條件的函式，輸出 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` 格式 feedback（不修改測試檔）
7. Stub 生成後 `coverage_agent.py` 重跑 pytest 確認是否達標，並回傳對應 exit code
8. `ruff check scripts/coverage_agent.py` 通過（no violations）

---

## Decisions

- **Async-planning status**: `exempt — cite exemption evidence: scripts/coverage_agent.py 是純同步 CLI 腳本，使用 stdlib (json, ast, subprocess, pathlib, re)；無 async boundary、無 httpx.AsyncClient、無 asyncio、無 concurrency model change、無 lifecycle 管理。`
- **Module/package placement**: `scripts/coverage_agent.py`（新建 `scripts/` 頂層目錄，在 `tach source_roots = ["src"]` 範圍之外）
- **New public API**: yes — `main() -> int`（CLI entry point，`if __name__ == "__main__"` 呼叫）；所有其他函式為 module-private（`_` prefix）
- **Interface changes**: no — 不修改 `src/mlops_async/` 任何公開介面
- **Breaking changes allowed**: no
- **New dependencies**: no — 僅使用已安裝的 `pytest-cov`（`coverage.json` 格式）與 stdlib；無新 runtime 依賴
- **Error handling strategy**: `_load_coverage_json()` 在 `coverage.json` 不存在時先跑 pytest 再嘗試；若仍不存在則 `sys.exit(1)` 並輸出 stderr 訊息；`_extract_functions()` 捕捉 `OSError` / `SyntaxError` 回傳空 list；stop-condition 觸發時輸出 feedback 但不 raise（繼續處理其他 gap）
- **Typing strategy**: 全型別標注（`from __future__ import annotations`）；`coverage.json` dict 使用 `dict`（無型別參數）加 `# type: ignore[type-arg]` 標注；`_FunctionInfo` 使用 `NamedTuple`；public `main()` 回傳 `int`

---

## Public Contract / API Changes

`scripts/coverage_agent.py` 新增以下唯一公開入口：

```python
def main() -> int:
    """Coverage Agent 的 entry point.

    Returns:
        0 if coverage threshold is met after processing.
        1 if coverage threshold is not met after stub generation.
    """
```

CLI 用法：`python scripts/coverage_agent.py`

所有其他函式為 module-private（`_` prefix），不構成公開 API。

`src/mlops_async/` 的任何公開介面 **不變**（backward compatibility: 完全維持）。

---

## Affected Files / Modules

Likely affected files:

- `pyproject.toml` — 新增 `[tool.coverage.*]` 三個 sections；`[tool.pytest.ini_options]` 加 `addopts`
- `.gitignore` — 新增 `.coverage`、`.coverage-reports/` 兩條目
- `.pre-commit-config.yaml` — 新增 `coverage-check` local hook（不動既有 pytest hook）
- `scripts/coverage_agent.py` — 新建（scripts/ 目錄新建）
- `tests/unit/test_coverage_agent.py` — 新建

Candidate files to inspect:

- `tach.toml` — 確認 `scripts/` 是否在 source_roots 範圍內（預期：不在，不需修改）

---

## Implementation Steps

1. 開啟 `pyproject.toml`，在 `[tool.pytest.ini_options]` block（現有 `python_functions` 欄位後）加入 `addopts = "--cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing"`
2. 開啟 `pyproject.toml`，在 `[tool.pytest.ini_options]` block 之後 append `[tool.coverage.run]` section：`source = ["src/mlops_async"]`、`omit = ["**/tests/**", "**/__pycache__/**"]`
3. 開啟 `pyproject.toml`，繼續 append `[tool.coverage.report]` section：`fail_under = 80`、`show_missing = true`
4. 開啟 `pyproject.toml`，繼續 append `[tool.coverage.json]` section：`output = ".coverage-reports/coverage.json"`
5. 開啟 `.gitignore`，在最後 append `# Coverage reports`、`.coverage`、`.coverage-reports/` 三行
6. 開啟 `.pre-commit-config.yaml`，在既有 `pytest` hook（`stages: [manual]`）之後插入新的 `coverage-check` hook：`entry: uv run pytest tests/unit/ --cov=src/mlops_async --cov-fail-under=80 --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing -q --no-header`；`pass_filenames: false`；`always_run: true`；**不修改**既有 pytest hook
7. 建立 `scripts/` 目錄；建立 `scripts/coverage_agent.py`，實作以下函式（依序）：
   - `_STOP_KEYWORDS`、`_COVERAGE_JSON_PATH`、`_COVERAGE_THRESHOLD = 80`、`_TESTS_UNIT_DIR`、`_DOCS_DIRS` 常數定義
   - `class _FunctionInfo(NamedTuple)` with fields: `name, args, return_annotation, docstring, missing_lines`
   - `_run_pytest() -> int`：呼叫 `subprocess.run` 跑 pytest --cov，回傳 exit code
   - `_load_coverage_json() -> dict`：若 json 不存在先呼叫 subprocess pytest 生成；讀取並回傳 dict；仍不存在則 `sys.exit(1)`
   - `_gap_modules(coverage_data: dict) -> list[tuple[str, list[int]]]`：過濾 `percent_covered < 80` 的 files
   - `_has_stop_condition(text: str) -> bool`：對 `_STOP_KEYWORDS` 做大小寫不敏感 substring match
   - `_find_docs_explanation(module_stem: str) -> str`：在 `docs/` 和 `analysis/` rglob `*.md` 中尋找包含 module_stem 的說明，回傳前 500 字元或空字串
   - `_extract_functions(source_path: Path, missing_lines: list[int]) -> list[_FunctionInfo]`：`ast.parse()` 解析 source；找出行範圍與 `missing_lines` 有交集的 `FunctionDef` / `AsyncFunctionDef`；收集 name、args（排除 self）、return annotation、docstring
   - `_module_stem(file_path: str) -> str`：回傳 `Path(file_path).stem`
   - `_test_file_path(file_path: str) -> Path`：回傳 `_TESTS_UNIT_DIR / f"test_{stem}.py"`
   - `_generate_stub(func: _FunctionInfo, module_import: str) -> str`：生成 `def test_<name>(): assert False, "stub"` + TODO comment
   - `_write_stubs(test_file: Path, stubs: list[str], module_import: str) -> None`：避免重複（用 `re.search` 檢查函式名），將新 stub append 或新建 test file
   - `_human_review_feedback(file_path, reason, missing_lines) -> None`：print `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` 格式
   - `_process_module(file_path, missing_lines) -> None`：整合 AST 解析 + stop condition 判斷 + stub 生成 or feedback
   - `main() -> int`：load → gap detection → for each gap `_process_module()` → `_run_pytest()` → return exit code
8. 執行 `uv run tach check` 確認 `scripts/` 不違反邊界（預期：通過，無需修改 `tach.toml`）
9. 建立 `tests/unit/test_coverage_agent.py`，實作 Test Plan 中的所有測試案例（見 Test Plan section）
10. 執行 `uv run ruff check scripts/coverage_agent.py` 並修正所有 violations（包括 D415、RUF001-003 等 CJK 相關規則）
11. 執行 `uv run pytest tests/unit/test_coverage_agent.py -v` 確認所有測試通過
12. 執行 `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=term-missing` 確認整體 coverage gate 仍通過

---

## Test Plan

Test file: `tests/unit/test_coverage_agent.py`

Test cases:

- **Happy path**: Given a `coverage.json` with one module at 65% coverage and one function `foo(x: int) -> bool` with a valid docstring, when `_process_module()` is called (mocking file I/O), then `tests/unit/test_<module>.py` is created containing `def test_foo()` with `assert False`
- **Happy path 2**: Given `main()` is called and all gap modules produce stubs, when `_run_pytest()` (mocked) returns 0, then `main()` returns 0
- **Invalid input**: Given `.coverage-reports/coverage.json` does not exist, when `_load_coverage_json()` is called, then `subprocess.run` is invoked (mocked) to generate coverage; if the file still doesn't exist after subprocess call, `sys.exit(1)` is called
- **Edge case — stop condition**: Given a function's docstring contains `"upload"`, when `_has_stop_condition("upload file to remote")` is called, then returns `True`
- **Edge case — stop condition triggers feedback**: Given `_has_stop_condition` returns `True` for a function, when `_process_module()` runs, then `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` is printed and no stub file is written
- **Edge case — no docstring**: Given a function with no docstring and no docs explanation, when `_process_module()` runs, then `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` is printed (stop condition: no spec)
- **Edge case — threshold already met**: Given `coverage.json` shows `percent_covered = 85.0` for all files, when `main()` runs, then exits with 0 without calling `_process_module()`
- **Edge case — duplicate prevention**: Given `tests/unit/test_module.py` already contains `def test_existing_func()`, when `_write_stubs()` is called with a stub for `test_existing_func`, then the function is not duplicated in the file
- **Regression**: After `addopts` is added to `pyproject.toml`, `uv run pytest tests/unit/` generates `.coverage-reports/coverage.json` (verified via integration run in validation step 12)
- **Backward compatibility**: Verify via `grep` that `stages: [manual]` pytest hook is unchanged in `.pre-commit-config.yaml` after adding `coverage-check` hook

---

## Validation Commands

```
uv run pytest tests/unit/test_coverage_agent.py -v
uv run ruff check scripts/coverage_agent.py
uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=term-missing
uv run tach check
```

---

## Risks

- `addopts` 含 `--cov` 後，每次 `pytest` 執行（含 IDE test run）都會啟動 coverage 收集，預期拖慢 +10–30%；測試套件增大後影響會增加
- `coverage-check` hook 設 `always_run: true`，在 `tests/unit/` 完全為空時 hook 會失敗並阻擋所有 commit（RISK-3 from technical-spec；open question）
- `_write_stubs()` 以 regex 比對防重複，若 coverage.json 損毀或路徑資訊異常，可能對錯誤模組生成 stub

---

## Rollback Plan

- Revert via git: `pyproject.toml`（移除 4 個新 coverage sections 及 addopts 修改）
- Revert via git: `.gitignore`（移除 `.coverage` 和 `.coverage-reports/` 兩行）
- Revert via git: `.pre-commit-config.yaml`（移除 `coverage-check` hook block）
- Delete: `scripts/coverage_agent.py`；若 `scripts/` 目錄為空則 `rm -rf scripts/`
- Delete: `tests/unit/test_coverage_agent.py`

---

## Open Questions

- **RISK-3（owner: topic author）**：`coverage-check` hook 在 `tests/unit/` 完全為空時是否允許通過？若需保護，在 hook `entry` 末尾加 `|| true`，但這會讓 coverage 未達標的 commit 悄悄通過。請在 Step 6 實作前確認。

---

<!-- ================================================================ -->
<!-- 以下為 plan/agent-handoff-workflow.md 所需的 repo 生命週期合約節 -->
<!-- ================================================================ -->

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: `python-implementation-workflow` 執行 Phase 0–5；完成後走 publish → PR → merge 路徑；本 topic 無 release action，`merged` 為 terminal。
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan (Python) | `plan/coverage-agent/coverage-agent.plan.md` | Planning actor | Python 實作合約（13 sections）+ repo 生命週期合約 |
| Step tracking | `plan/coverage-agent/coverage-agent.step.md` | Creator | `python-implementation-workflow` step gate |
| Spec (non-trivial) | `plan/coverage-agent/coverage-agent.spec.md` | Planning actor | TDD test authoring 依據（D1 non-trivial） |
| Requirements baseline | `analysis/coverage-agent/requirements.md` | Planning actor | FROZEN 業務需求基準 |
| Technical spec | `analysis/coverage-agent/technical-spec.md` | Planning actor | 實作面向技術規格 |
| Coverage config | `pyproject.toml` | Creator | 新增 `[tool.coverage.*]` + `addopts` |
| Gitignore update | `.gitignore` | Creator | 新增 coverage 產物條目 |
| Pre-commit hook | `.pre-commit-config.yaml` | Creator | 新增 `coverage-check` hook |
| Coverage agent | `scripts/coverage_agent.py` | Creator | 靜態分析 stub 生成腳本 |
| Agent unit tests | `tests/unit/test_coverage_agent.py` | Creator | coverage_agent 的 unit tests |

Artifact path notes:

- 本 topic **不修改** `README.md`、`VERSION`、`.github/copilot-instructions.md`。
- 若 tach check 確認 `tach.toml` 需更新（Step 8），`tach.toml` 加入 Artifact Paths；目前預期不需修改。
- 無 correction/delta artifacts；無 review-log。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

本 topic 不影響穩定函式庫介面（`README.md`、`VERSION` 均未修改）。
`merged` 為 terminal 狀態，無需 release action。
