# Coverage Agent Simplification — Requirements

**Status: FROZEN — ready for technical translation**
**Topic path:** `analysis/coverage-agent-simplification/requirements.md`

## 問題陳述

既有 `coverage-agent` 主題把「找出未覆蓋函式與行號」擴張成自訂 Python 腳本：
AST 對映、stop keyword 判斷、測試 stub 生成、寫入 `tests/unit/`、再重跑 pytest。
這和實際需求不相稱，因為 pytest-cov 已能輸出 machine-readable coverage JSON，
足以讓 Agent 找到未覆蓋檔案、函式與行號。

本 correction topic 的目標是把 coverage 工作流收斂為：
pytest-cov 負責產生 coverage evidence；Agent 只讀 `.coverage-reports/coverage.json`
並對照目前 topic 的 Test Plan / spec / step scope；若 coverage gap 無法由既有測試
範圍或 contract evidence 合理處理，就回饋 human，不自動生成測試 stub。

## Actors

| Actor | 角色 |
| --- | --- |
| Developer | 執行 unit tests、閱讀 coverage gap、補語義正確的測試 |
| Coverage Gate | 透過 pytest-cov 與 pre-commit 執行 90% coverage gate |
| Agent | 讀取 coverage JSON，對照 topic 測試範圍並產生 human feedback |
| Human Reviewer | 決定 scope gap、stop condition 或 contract 不足時如何補測試 |

## Requirements

### REQ-1：Coverage gate 對齊專案政策

- **Actor**：Coverage Gate
- **可觀測結果**：`pyproject.toml` 與 `.pre-commit-config.yaml` 使用 90% coverage gate。
- **門檻來源**：`blueprint.md` 與 `.github/copilot-instructions.md` 既有政策皆為 90%。
- **失敗後果**：若 gate 保持 80%，會和 repo governance 產生語意不一致。

### REQ-2：pytest-cov JSON 是唯一 machine-readable evidence

- **Actor**：Coverage Gate、Agent
- **可觀測結果**：pytest-cov 產生 `.coverage-reports/coverage.json` 與 `term-missing`。
- **必備 evidence**：
  - `totals.percent_covered`
  - `files[<path>].summary.percent_covered`
  - `files[<path>].missing_lines`
  - `files[<path>].functions[<function>].missing_lines`
  - `files[<path>].functions[<function>].start_line`
- **失敗後果**：若 Agent 自行重建 coverage 計算，會重複 pytest-cov 已提供的核心能力。

### REQ-3：Agent 只做 triage，不寫測試檔

- **Actor**：Agent、Human Reviewer
- **可觀測結果**：Agent 可根據 coverage JSON 回報：
  - 哪個檔案 / 函式 / 行號未覆蓋
  - 該 gap 是否落在目前 topic 的 Test Plan 範圍內
  - 該 gap 是否需要 human review
- **禁止行為**：
  - 不生成 `assert False` stub
  - 不寫入 `tests/unit/`
  - 不用 stub 讓 coverage 數字達標
- **失敗後果**：自動 stub 會讓 coverage 數字與測試語義品質脫鉤。

### REQ-4：Parent artifacts 必須回填，避免 future agents 回到舊設計

- **Actor**：Creator、Reviewer
- **可觀測結果**：舊 `analysis/coverage-agent/*` 與 `plan/coverage-agent/*` 不再把
  stub generation 描述為 current truth，而是明確指向本 correction topic。
- **失敗後果**：若只新增 correction topic 但不回填 parent，future agents 可能依
  strict-mode routing 重新執行已 superseded 的 stub-generation 設計。

### REQ-5：README 修正但不做版本發布

- **Actor**：Creator、Main Agent
- **可觀測結果**：`README.md` 移除「`scripts/coverage_agent.py` 會生成 stubs」
  的描述，改為 coverage JSON + human feedback workflow。
- **明確排除**：不修改 `VERSION`、`uv.lock`，不建立 git tag。
- **失敗後果**：若 README 保留舊敘述，使用者會以為已刪除的 helper 仍是必要產物。

## Non-goals

1. 不新增或保留自訂 AST coverage mapper。
2. 不自動生成任何測試 stub。
3. 不修改 `src/mlops_async/` library 行為。
4. 不新增 GitHub Actions / CI coverage gate。
5. 不提交 `.coverage-reports/coverage.json`。
6. 不做 release tag 或 version bump。

## Acceptance signals

1. Coverage gate 門檻在設定與文件中一致為 90%。
2. `.coverage-reports/coverage.json` 可由 pytest-cov 產生，且含函式層級 missing-line evidence。
3. `scripts/coverage_agent.py` 與 `tests/unit/test_coverage_agent.py` 不存在。
4. README 不再描述 stub generation。
5. Parent `coverage-agent` artifacts 指向 `coverage-agent-simplification` correction，語意一致。
