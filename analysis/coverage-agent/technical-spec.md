# Coverage Agent — Technical Specification

**Status: READY FOR IMPLEMENTATION — accepted backfill current truth**
**Topic path (target):** `analysis/coverage-agent/technical-spec.md`
**Baseline:** `analysis/coverage-agent/requirements.md` (FROZEN — accepted backfill)
**Backfill source:** `analysis/coverage-agent-simplification/technical-spec.md`

---

## Baseline Gate Check

✅ `requirements.md` 已回填為 correction 後 current truth。
✅ coverage gate 門檻為 90%，符合 repo governance。
✅ machine-readable evidence 由 pytest-cov / Coverage.py JSON 提供。
✅ 舊版 helper / test placeholder 產生設計已 superseded，且不得作為 current implementation requirement。

---

## Requirement Traceability Table

| REQ | 業務需求 | Technical Realization | 依賴 | 狀態 |
|---|---|---|---|---|
| REQ-1 | coverage gate：unit tests ≥ 90% | `[tool.coverage.report] fail_under = 90` + local `coverage-check` hook 使用 `--cov-fail-under=90` | pytest-cov | feasible |
| REQ-2 | 固定路徑 JSON + term-missing 報告 | `[tool.pytest.ini_options] addopts` 與 validation command 產生 `.coverage-reports/coverage.json` | Coverage.py JSON format | feasible |
| REQ-3 | Agent 只讀 JSON evidence 並 triage | Agent / reviewer 讀 `totals`、`files[*].missing_lines`、`files[*].functions[*].missing_lines` | topic Test Plan / spec / scope | feasible |
| REQ-4 | 停止條件 + HUMAN REVIEW feedback | 不自動補測試；scope gap 或 stop condition 交 human 決策 | project guidelines stop conditions | feasible |

---

## Architecture Compliance

### 1. pyproject.toml coverage 設定

**結果：fits existing architecture**

- `[tool.coverage.run]`、`[tool.coverage.report]`、`[tool.coverage.json]` 是 Coverage.py 的標準 TOML 設定位置。
- `[tool.pytest.ini_options] addopts` 保留 `--cov=src/mlops_async`、JSON output 與 `term-missing`。
- `fail_under = 90` 是 repo governance 的 current truth。

### 2. .pre-commit-config.yaml coverage gate

**結果：fits with existing manual pytest hook**

- 保留既有 `pytest` hook 的 `stages: [manual]` 行為。
- `coverage-check` 是獨立 local hook，entry 執行 `tests/unit/` 並使用 `--cov-fail-under=90`。
- 若本機 shell PATH 找不到 `python`，可用 `PATH="$PWD/.venv/bin:$PATH"` 執行 pre-commit；不修改 hook 解決本機環境問題。

### 3. Coverage evidence

**結果：use existing pytest-cov schema**

Agent 應讀取 `.coverage-reports/coverage.json` 中的既有欄位：

```json
{
  "totals": {"percent_covered": 95.14},
  "files": {
    "src/mlops_async/example.py": {
      "summary": {"percent_covered": 80.0},
      "missing_lines": [10, 11],
      "functions": {
        "example_function": {"missing_lines": [10, 11], "start_line": 8}
      }
    }
  }
}
```

不需要自訂 AST mapper、helper script 或 placeholder test writer。

---

## Technical Tasks

### T1 — Coverage config alignment

- `pyproject.toml`：`[tool.coverage.report].fail_under = 90`。
- 保留 JSON output：`.coverage-reports/coverage.json`。
- 保留 `term-missing`，讓 local validation 直接顯示未覆蓋行。

### T2 — Pre-commit gate alignment

- `.pre-commit-config.yaml`：`coverage-check` hook name 使用 90% 語意。
- `coverage-check` entry 使用 `--cov-fail-under=90`。
- 不改既有 manual pytest hook。

### T3 — Delete superseded helper artifacts

刪除並保持不存在：

- `scripts/coverage_agent.py`
- `tests/unit/test_coverage_agent.py`

### T4 — Documentation backfill

- Parent `analysis/coverage-agent/*` 與 `plan/coverage-agent/*` 說明舊 helper / placeholder generation 已 superseded。
- README v0.10.4 row 改為 90% gate + pytest-cov JSON / human feedback triage。
- Correction artifacts 保留為 historical decision record。

---

## Validation Commands

```bash
uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing
uv run pre-commit run coverage-check --all-files
uv run ruff check
uv run pyright
uv run python .github/skills/plan-step-tracker/scripts/step_tracker.py check_impl_steps_succeeded coverage-agent-simplification
```

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| 90% gate fails after deleting helper tests | Do not generate placeholders; report file / function gaps from coverage JSON |
| Parent artifacts retain stale current-truth helper requirements | Search for `coverage_agent`, `stub`, `assert False`, and `80%`; reword parent current truth |
| Generated coverage JSON appears in git status | `.coverage-reports/` remains ignored; verify `git status --short` |
| README implies release mutation | Do not change `VERSION`, `uv.lock`, or git tags |

---

## Superseded Design Log

The previous technical design introduced a custom helper script, AST parsing, and generated test
placeholders. That design is no longer active. The accepted implementation is the simpler pytest-cov
JSON workflow described above.
