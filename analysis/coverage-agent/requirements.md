# Coverage Agent — Business Requirements Baseline

**Status: FROZEN — accepted backfill current truth**
**Topic path (target):** `analysis/coverage-agent/requirements.md`
**Backfill source:** `analysis/coverage-agent-simplification/requirements.md`

---

## Backfill notice

此 parent artifact 已依 `coverage-agent-simplification` correction 回填。舊版 80%
coverage gate、`scripts/coverage_agent.py` 靜態分析 helper、以及 template-based test
stub generation 均已 superseded，不再是 current truth。

Correction artifacts 保留於 `analysis/coverage-agent-simplification/` 與
`plan/coverage-agent-simplification/` 作為 historical decision record；本檔案描述
accepted backfill 後的目前執行事實。

## 問題陳述

`mlops-async` 需要在本地開發流程維持 repository governance 定義的 **90%** unit-test
coverage gate，並提供 machine-readable coverage evidence，讓 Agent 與 human reviewer 能
依目前 topic 的 Test Plan / spec / scope 判斷未覆蓋缺口。

coverage gap 的定位由 pytest-cov / Coverage.py 產生的
`.coverage-reports/coverage.json` 提供；Agent 只讀取 JSON evidence 並提出 triage /
human feedback，不自動產生測試 stub，也不寫入 `tests/unit/`。

---

## Actors

| Actor | 角色 |
|---|---|
| **Developer（開發者）** | 執行 unit tests，根據 coverage JSON 與目前 topic Test Plan 補語義正確的測試 |
| **Coverage Gate（pre-commit hook）** | 執行 `tests/unit/` coverage gate，強制整體覆蓋率 ≥ 90% |
| **Agent** | 讀取 `.coverage-reports/coverage.json`，對照 topic scope / stop conditions 產生 triage 或 human feedback |
| **Human Reviewer** | 決定 scope gap、stop condition 或 contract evidence 不足時是否擴 scope 或補測試 |

---

## 需求清單

### REQ-1：覆蓋率門檻強制（gate）

- **Actor**：Coverage Gate（pre-commit hook）
- **條件**：本地執行 coverage validation 或 `coverage-check` hook
- **可觀測結果**：若 `src/mlops_async/` 覆蓋率 < 90%，指令返回非零 exit code，並顯示未覆蓋模組與行號
- **門檻**：90%（以 `[tool.coverage.report] fail_under = 90` 為 canonical source）
- **排除範圍**：`tests/integration/` 預設不跑，除非 topic spec 明確標注 E2E
- **業務失敗後果**：門檻低於 repo governance 會讓 coverage quality bar 產生語意漂移

### REQ-2：覆蓋率報告格式（可機器讀取）

- **Actor**：Developer、Agent
- **條件**：pytest-cov 執行完成後
- **可觀測結果**：生成 `.coverage-reports/coverage.json`（JSON）與 `term-missing` 終端輸出
- **必備 evidence**：`totals.percent_covered`、`files[*].summary.percent_covered`、`files[*].missing_lines`、`files[*].functions[*].missing_lines`、`files[*].functions[*].start_line`
- **業務失敗後果**：若 Agent 不能讀固定 JSON evidence，就會重新發明 coverage parser 或失去可追溯性

### REQ-3：Agent triage，不寫測試檔

- **Actor**：Agent、Human Reviewer
- **觸發條件**：coverage validation 產生 JSON 後，需要分析 gap 是否屬於目前 topic 範圍
- **可觀測結果**：Agent 可回報未覆蓋檔案 / 函式 / 行號、是否落在 Test Plan、是否需要 human review
- **禁止行為**：不生成 `assert False` placeholder、不寫入 `tests/unit/`、不用測試 stub 讓 coverage 數字達標
- **業務失敗後果**：自動 placeholder 會讓 coverage 數字與測試語義品質脫鉤

### REQ-4：停止條件與 Feedback 格式

- **Actor**：Agent → Human Reviewer
- **停止條件（任一成立即停止自動補測試）**：
  1. gap 不在目前 topic Test Plan / spec 範圍
  2. spec 描述模糊或有歧義，無法安全推斷預期行為
  3. 未覆蓋程式碼屬於 stop condition 類別（upload/download/streaming/polling/retry/pagination/session side effects）
  4. 測試需要 live API 或 integration fixture（非 unit test）
  5. request / response contract evidence 不足
- **Feedback 格式**（每個 gap 一則）：
  ```
  [COVERAGE GAP - HUMAN REVIEW REQUIRED]
  模組：src/mlops_async/xxx.py
  未覆蓋行：45-67
  函式：function_name
  停止原因：{一句話說明為什麼不能在目前 scope 內補測試}
  建議人工操作：{具體可執行的建議}
  ```

---

## 顯式假設

1. Coverage.py / pytest-cov JSON 是唯一 machine-readable coverage evidence。
2. Agent 不修改 source code，也不修改 `tests/unit/`。
3. pre-commit `coverage-check` hook 只跑 `tests/unit/`；Integration / E2E 測試不在門檻計算範圍內。
4. 90% 門檻以 `src/mlops_async/` 整體為計算單位，不以單一模組計算。
5. `.coverage-reports/coverage.json` 路徑固定，並由 `.gitignore` 排除提交。

---

## Non-goals

1. 不建立或保留自訂 AST coverage mapper / helper。
2. 不自動生成任何測試 placeholder 或 stub。
3. 不修改 `src/mlops_async/` library 行為。
4. 不對 `tests/integration/` 生成測試。
5. 不在 CI（GitHub Actions）層面新增 coverage gate。
6. 不提交 `.coverage-reports/coverage.json`。

---

## Superseded design log

舊版 design 曾計畫 `scripts/coverage_agent.py` 讀取 coverage JSON、解析 AST、產生測試
stub 並重跑 pytest。該設計已由 `coverage-agent-simplification` correction 取代，原因是
pytest-cov JSON 已提供必要 missing-line evidence，而自動 placeholder test 會降低語義品質。

---

## Acceptance Signal

以下可由另一位開發者驗證：

1. `pyproject.toml` 與 `.pre-commit-config.yaml` 均使用 90% coverage gate。
2. 執行 `uv run pytest tests/unit/ --cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing` 後，JSON evidence 存在且包含 file / function missing-line 資訊。
3. `scripts/coverage_agent.py` 與 `tests/unit/test_coverage_agent.py` 不存在。
4. README 與 parent plan artifacts 不再要求 coverage helper 或 test stub generation。
