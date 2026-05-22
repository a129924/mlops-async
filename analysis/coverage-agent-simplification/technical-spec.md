# Coverage Agent Simplification — Technical Specification

**Status: READY FOR IMPLEMENTATION PLANNING**
**Baseline:** `analysis/coverage-agent-simplification/requirements.md`

## Baseline gate check

- Requirements 已凍結，且明確排除自動 stub generation。
- 本 topic 是 correction / simplification，不是新增 coverage helper module。
- `coverage-agent` parent artifacts 需在 correction plan 核准後回填，避免 source-of-truth drift。

## Requirement traceability

| REQ | Technical realization | Artifact paths |
| --- | --- | --- |
| REQ-1 | 將 coverage gate 改為 90% | `pyproject.toml`, `.pre-commit-config.yaml` |
| REQ-2 | 保留 pytest-cov JSON output，使用 Coverage.py 既有 schema | `pyproject.toml`, `.coverage-reports/coverage.json` |
| REQ-3 | 刪除自訂 helper 與 helper tests，不再寫入 `tests/unit/` | `scripts/coverage_agent.py`, `tests/unit/test_coverage_agent.py` |
| REQ-4 | 回填 parent analysis / plan / spec / step | `analysis/coverage-agent/*`, `plan/coverage-agent/*` |
| REQ-5 | README 改成 JSON triage / human feedback 描述，不做 version bump | `README.md` |

## Coverage JSON contract

Agent 應讀取 pytest-cov 產生的 `.coverage-reports/coverage.json`。Coverage.py format 3
已提供下列必要資訊，不需要自訂 AST 對映：

```json
{
  "totals": {
    "percent_covered": 95.14
  },
  "files": {
    "src/mlops_async/example.py": {
      "summary": {
        "percent_covered": 80.0
      },
      "missing_lines": [10, 11],
      "functions": {
        "example_function": {
          "missing_lines": [10, 11],
          "start_line": 8
        }
      }
    }
  }
}
```

### Agent triage interpretation

Agent 可用 coverage JSON 產生 feedback，但不得修改檔案：

1. `totals.percent_covered < 90`：整體 gate fail。
2. `files[*].missing_lines` 非空：檔案仍有未覆蓋 statement。
3. `files[*].functions[*].missing_lines` 非空：函式層級 gap，可對照 Test Plan。
4. 若函式 gap 不在 Test Plan 範圍內：標記 `scope-gap`，交 human 決定是否擴 scope。
5. 若函式 gap 涉及 upload / download / streaming / polling / retry / pagination /
   session side effect / live API / contract evidence 不足：標記 `needs-human-review`。

## Technical tasks

### T1 — Correction analysis / plan artifacts

建立：

- `analysis/coverage-agent-simplification/requirements.md`
- `analysis/coverage-agent-simplification/technical-spec.md`
- `plan/coverage-agent-simplification/coverage-agent-simplification.plan.md`
- `plan/coverage-agent-simplification/coverage-agent-simplification.spec.md`
- `plan/coverage-agent-simplification/coverage-agent-simplification.step.md`

### T2 — Parent artifact backfill

更新舊 artifacts，使它們明確宣告 stub-generation 設計已由 correction topic 取代：

- `analysis/coverage-agent/requirements.md`
- `analysis/coverage-agent/technical-spec.md`
- `plan/coverage-agent/coverage-agent.plan.md`
- `plan/coverage-agent/coverage-agent.spec.md`
- `plan/coverage-agent/coverage-agent.step.md`

Parent artifacts 是「accepted backfill 後的 current truth」；correction artifacts 是歷史決策
與修正證據，不應刪除。

### T3 — Coverage gate alignment

- `pyproject.toml`
  - `[tool.coverage.report].fail_under = 90`
  - 保留 JSON output：`.coverage-reports/coverage.json`
- `.pre-commit-config.yaml`
  - hook name 改為 `coverage check (>=90%)`
  - `--cov-fail-under=90`

### T4 — Delete overdesigned helper

刪除：

- `scripts/coverage_agent.py`
- `tests/unit/test_coverage_agent.py`

刪除後需搜尋 stale references，避免任何 current doc / plan 繼續宣稱 helper 必須存在。

### T5 — README correction

更新 README v0.10.4 coverage-agent 敘述：

- 保留 coverage gate 與 pytest-cov JSON 說明。
- 移除 `scripts/coverage_agent.py` 生成 stubs 的敘述。
- 明確說明未覆蓋函式 / 行號由 JSON evidence 提供，後續由 Agent / human 對照 Test Plan。
- 不修改 `VERSION` / `uv.lock` / git tag。

## Validation commands

```bash
uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing
uv run pre-commit run coverage-check --all-files
uv run ruff check
uv run pyright
uv run python .github/skills/plan-step-tracker/scripts/step_tracker.py check_impl_steps_succeeded coverage-agent-simplification
```

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Parent artifacts still mention stub generation | Search all `coverage_agent`, `stub`, and `assert False` references before review |
| 90% gate fails after deleting helper tests | Current baseline is 95.14%; run coverage validation after deletion |
| README implies version release | Stable metadata must declare README-only, no VERSION / uv.lock / tag |
| Generated coverage JSON accidentally staged | `.coverage-reports/` remains ignored and must not appear in git status |

## Rollback

If correction implementation causes gate failure or stale source-of-truth conflict:

1. Restore deleted helper and tests from git.
2. Revert coverage gate to previous value only if human explicitly accepts governance mismatch.
3. Revert README wording.
4. Keep correction artifacts as historical record if they were already reviewed.
