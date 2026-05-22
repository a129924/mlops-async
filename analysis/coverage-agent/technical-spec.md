# Coverage Agent — Technical Specification

**Status: READY FOR IMPLEMENTATION PLANNING**
**Topic path (target):** `analysis/coverage-agent/technical-spec.md`
**Baseline:** `analysis/coverage-agent/requirements.md` (FROZEN)

---

## Baseline Gate Check

✅ `requirements.md` 已凍結，包含具名 actors、可量測 outcomes、已解決矛盾、明確 non-goals。
✅ 無模糊語言（門檻 = 80%，具體路徑，具體格式）。
✅ 所有矛盾在本規格撰寫前已解決。

---

## Requirement Traceability Table

| REQ | 業務需求 | Technical Realization | 依賴 | 實現成本 | 狀態 |
|---|---|---|---|---|---|
| REQ-1 | coverage gate：commit 前 ≥ 80% | `.pre-commit-config.yaml` 新增獨立 `coverage-check` hook（Option A）+ `[tool.coverage.report] fail_under=80` | DECISION-1 已選定 Option A | 低 | feasible |
| REQ-2 | 固定路徑 JSON + term-missing 報告 | `[tool.pytest.ini_options] addopts`（含 `--cov`）+ `[tool.coverage.run]` + `.gitignore` | pyproject.toml + .gitignore 修改；DECISION-2 已確認含 `--cov` | 低 | feasible |
| REQ-3 | Agent 靜態分析 + stub 生成 | `scripts/coverage_agent.py` + `scripts/` directory | coverage.json 路徑（REQ-2）+ spec 格式規範 | 中 | feasible（有能力上限，見限制） |
| REQ-4 | 停止條件 + HUMAN REVIEW feedback | coverage_agent.py 內部邏輯 + feedback 格式 | REQ-3 | 低（跟著 REQ-3 實作） | feasible |

---

## 架構相容性自我檢查（Architecture Compliance）

### 1. pyproject.toml coverage 設定

**結果：fits existing architecture**

- `[tool.coverage.report]`、`[tool.coverage.run]`、`[tool.coverage.json]` 是 Coverage.py 的標準 TOML 設定位置
- `[tool.pytest.ini_options] addopts` 已有同類設定模式在其他 Python 專案
- 無任何邊界違反

**注意**：`addopts` 加入 `--cov` 後，**每次 `pytest` 都會跑 coverage 收集**，包括 IDE 內的 pytest run 和 pre-commit pytest hook，可能使 pytest 略慢（通常 +10-30%）。在測試套件增大後需留意。

---

### 2. .pre-commit-config.yaml — coverage gate hook

**結果：fits with prerequisites（DECISION-1 已確認：Option A）**

**背景（CONFLICT-1 已解決）：**

```
現有設計：pytest hook 使用 stages: [manual]（有意識設計，避免 commit 前卡住）
業務需求：REQ-1 要求每次 git commit 前強制執行 coverage gate
解決方案：新增獨立 coverage-check hook，不動既有 stages: [manual] pytest hook
```

**選定方案（Option A）：**

| 選項 | 作法 | 優點 | 缺點 |
|---|---|---|---|
| **A — 新增獨立 coverage hook**（✅ 已選定） | 新增 `coverage-check` hook（只跑 `pytest tests/unit/ --cov --cov-fail-under=80 -q --no-header`），stage 設為 `pre-commit`（非 manual）| 不影響既有 pytest hook；單獨控制 | 同一次 commit 測試跑兩次（若開發者也有 manual hook） |
| B — 修改既有 pytest hook | 將既有 pytest hook 的 `stages: [manual]` 移除或改為 `pre-commit` | 統一入口 | 推翻既有設計決定；可能拖慢所有 commit |

---

### 3. scripts/coverage_agent.py

**結果：fits with prerequisites（需要建立 scripts/ 目錄）**

- 目前 `scripts/` 目錄不存在，需新建
- Python 腳本不影響任何現有邊界（tach.toml 需確認是否需要更新，見 RISK-1）
- 腳本讀取 `.coverage-reports/coverage.json` → 需 REQ-2 先完成

---

### 4. .gitignore 更新

**結果：fits existing architecture**

- `.gitignore` 目前無 coverage 相關條目
- `.coverage`（Coverage.py SQLite DB）、`.coverage-reports/`（JSON 輸出目錄）都需加入

---

## 技術任務分解

### Workstream 1：pyproject.toml — coverage 設定（T1）

**任務清單：**
- T1-a：新增 `[tool.coverage.run]` — `source = ["src/mlops_async"]`、`omit = ["**/tests/**", "**/__pycache__/**"]`
- T1-b：新增 `[tool.coverage.report]` — `fail_under = 80`、`show_missing = true`
- T1-c：新增 `[tool.coverage.json]` — `output = ".coverage-reports/coverage.json"`
- T1-d：修改 `[tool.pytest.ini_options]` — 加入 `addopts = "--cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing"`（含 `--cov`，DECISION-2 已確認）

**成本評估**：低（純設定，無邏輯，可一次完成）
**排序**：T1 必須先於 T2 完成（coverage.json 路徑依賴）

---

### Workstream 2：.pre-commit-config.yaml — coverage gate（T2）

**任務清單（Option A，已確認）：**
- T2-a：新增 `coverage-check` local hook：
  ```yaml
  - id: coverage-check
    name: coverage check (unit tests ≥ 80%)
    entry: uv run pytest tests/unit/ --cov=src/mlops_async --cov-fail-under=80 --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing -q --no-header
    language: system
    types: [python]
    pass_filenames: false
    always_run: true
  ```

**成本評估**：低（設定）；**運行成本**：每次 commit 多跑一次 unit tests（需評估套件大小）
**排序**：T2 依賴 T1 完成後確認路徑

---

### Workstream 3：.gitignore 更新（T3）

**任務清單：**
- T3-a：新增 `.coverage`（Coverage.py SQLite）
- T3-b：新增 `.coverage-reports/`（JSON 輸出目錄）

**成本評估**：極低
**排序**：T3 可與 T1 並行

---

### Workstream 4：scripts/coverage_agent.py（T4）

**任務清單：**
- T4-a：建立 `scripts/` 目錄
- T4-b：實作 `scripts/coverage_agent.py`：
  - 讀取 `.coverage-reports/coverage.json`（若不存在 → 先執行 pytest）
  - 解析 `files[*]` → 找 `executed_lines` vs `missing_lines`
  - 過濾覆蓋率 < 80% 的模組
  - 對每個 gap module：讀取 source 的 docstring + type hints + `docs/*.md` + 對應 `tests/unit/` 結構
  - 判斷是否能生成 stub（見停止條件）
  - 能生成 → 寫入 `tests/unit/test_<module>.py`（stub 格式）
  - 不能生成 → 輸出 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` feedback
  - 執行完畢後重跑 `pytest --cov` 確認是否達標

**成本評估：中**
- 讀取 coverage.json：`json` 標準庫，低
- 解析 Python AST（docstring/type hints）：`ast` 標準庫，中
- stub 生成邏輯：需定義生成規則（見限制）
- 停止條件判斷：需枚舉 stop-condition 關鍵字

**排序**：T4 依賴 T1（coverage.json 路徑確定）和 T2（gate 先建立）

---

### Workstream 5：tach.toml 相容性（T5，risk mitigation）

**任務清單：**
- T5-a：確認 `scripts/` 目錄是否需要在 `tach.toml` 中設定邊界
- T5-b：若需要 → 更新 `tach.toml`

**成本評估**：極低（確認 + 可能修改一行）
**排序**：T5 依賴 T4 建立 scripts/ 後確認

---

## 能力限制聲明（Critical Constraints）

### LIMIT-1：靜態腳本的測試生成能力上限

REQ-3 要求靜態腳本生成「有意義的測試」。實際上，純靜態分析只能提供：

| 能力 | 靜態腳本可做 | 不可做（需 LLM）|
|---|---|---|
| 找出未覆蓋函式 | ✅ | — |
| 讀取函式 signature + type hints | ✅ | — |
| 解析 docstring 中的 Args/Returns | ✅（limited）| — |
| 生成函式呼叫 stub（`def test_xxx(): ...`）| ✅ | — |
| 生成含有意義 assert 的測試 | ❌ | ✅ |
| 理解預期行為並設計測試案例 | ❌ | ✅ |

**結論**：T4 生成的是**測試 stub（佔位）**，不是完整語義測試。Coverage 數字可能達標，但測試品質由人工驗證（符合 REQ-3 non-goal #4）。

---

## 風險清單

| 風險 | 可能性 | 影響 | 緩解 |
|---|---|---|---|
| RISK-1：`scripts/` 被 tach 邊界拒絕 | 低 | 中 | T5 確認 tach.toml |
| RISK-2：`addopts` 拖慢所有 pytest（IDE + CI）| 中 | 低 | 可用 `-p no:warnings -q` 加速；或把 addopts 中的 --cov 移到 pre-commit hook 只跑 |
| RISK-3：pre-commit coverage hook 在空 tests/unit/ 時失敗 | 低 | 低 | Hook entry 加 `|| true` 保護（需討論是否接受） |
| RISK-4：stub 測試意外通過覆蓋率但測試邏輯錯誤 | 中 | 中 | REQ-3/REQ-4 明確：語義正確由人工驗證，coverage 數字只是 gate |
| RISK-5：coverage.json 輸出到 `.coverage-reports/`，但 `.gitignore` 未加 | 低（T3 已規劃）| 高（意外提交）| T3 必須先於任何 pytest 執行 |

---

## 已確認的決策點

### DECISION-1：pre-commit hook 設計（已選定：Option A）✅

- **選定**：新增獨立 `coverage-check` hook，`stages: [pre-commit]`，不動既有 `stages: [manual]` pytest hook

### DECISION-2：`addopts` 中 `--cov` 的範圍（已確認：含 `--cov`）✅

- **確認**：`addopts = "--cov=src/mlops_async --cov-report=json:.coverage-reports/coverage.json --cov-report=term-missing"` 含 `--cov`

---

## 實作排序（Sequencing）

```
T1（pyproject.toml） + T3（.gitignore）  ← 可並行
        │
        ▼
T2（pre-commit hook，Option A）
        │
        ▼
T4（scripts/coverage_agent.py）
        │
        ▼
T5（tach.toml 確認）
```

---

## 整體可行性評估

**可行性：HIGH**
- 所有技術工具已安裝（pytest-cov 7.1.0、coverage 7.13.5、pre-commit）
- 無新的 runtime 依賴
- 所有設計決策已解決（DECISION-1 Option A，DECISION-2 含 `--cov`）
- T4 的能力有上限但在 REQ-3 non-goal 範圍內（stub 即可）

**Rollback 條件**（需回到 business alignment）：
- 若開發者不接受任何 pre-commit 阻擋（推翻 REQ-1）→ 需重新討論 trigger 為 CI-only
- 若 tach.toml 結果顯示 scripts/ 不允許（RISK-1 實現且無法解決）→ 需討論腳本放置位置
