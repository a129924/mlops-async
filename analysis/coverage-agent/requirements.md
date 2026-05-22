# Coverage Agent — Business Requirements Baseline

**Status: FROZEN — ready for technical translation**
**Topic path (target):** `analysis/coverage-agent/requirements.md`

---

## 問題陳述

目前 `mlops-async` 沒有強制覆蓋率門檻。
開發者提交程式碼時，無機制阻止覆蓋率持續下降；
發現覆蓋率不足後，也沒有結構化流程協助找出並填補缺口。

---

## Actors

| Actor | 角色 |
|---|---|
| **Developer（開發者）** | 本地提交程式碼、在 pre-commit 失敗後手動執行補測試腳本 |
| **Coverage Gate（pre-commit hook）** | 自動在每次 `git commit` 前執行 unit tests，強制 ≥ 80% |
| **Coverage Agent Script（靜態分析腳本）** | 讀取 coverage.json + source + docs，生成測試 stub 或輸出 feedback |
| **Human Reviewer** | 收到 HUMAN REVIEW REQUIRED feedback 後決定如何補測試 |

---

## 需求清單

### REQ-1：覆蓋率門檻強制（gate）

- **Actor**：Coverage Gate（pre-commit hook）
- **條件**：每次 `git commit` 時，`tests/unit/` 中有任何測試存在
- **可觀測結果**：若 `src/mlops_async/` 覆蓋率 < 80%，commit 被阻擋，顯示未覆蓋模組與行號
- **門檻**：80%（以 `[tool.coverage.report] fail_under = 80` 為 canonical source）
- **排除範圍**：`tests/integration/`（E2E）預設不跑，除非 topic spec 明確標注 E2E
- **業務失敗後果**：無門檻 → 覆蓋率持續漂移 → 迴歸錯誤無測試保護

### REQ-2：覆蓋率報告格式（可機器讀取）

- **Actor**：Developer、Coverage Agent Script
- **條件**：pytest 完成後（無論通過或失敗）
- **可觀測結果**：生成 `.coverage-reports/coverage.json`（JSON）與 `term-missing` 終端輸出
- **門檻**：JSON 路徑固定，Agent 可無需額外設定直接讀取
- **業務失敗後果**：路徑不固定 → Agent 無法自動讀取 → 補測試流程斷裂

### REQ-3：Agent 靜態分析與測試生成

- **Actor**：Developer（手動觸發）→ Coverage Agent Script
- **觸發條件**：pre-commit gate 失敗後，開發者手動執行 `python scripts/coverage_agent.py`
- **輸入**：`.coverage-reports/coverage.json`、source code、docstrings、type hints、`docs/*.md`、`analysis/<topic>/requirements.md`、現有 `tests/unit/` 結構
- **可觀測結果（成功路徑）**：
  - 腳本在 `tests/unit/` 寫入測試 stub 檔案
  - 重新執行 `pytest --cov`，覆蓋率達到 ≥ 80%
- **可觀測結果（失敗路徑）**：
  - 輸出結構化 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` feedback（見 REQ-4）
  - **不**自行猜測行為，不寫入任何測試檔案
- **門檻**：重跑 coverage 後 ≥ 80% 視為成功；低於則繼續輸出 feedback

### REQ-4：Agent 停止條件與 Feedback 格式

- **Actor**：Coverage Agent Script → Human Reviewer
- **停止條件（任一成立即停止）**：
  1. 對應函式無 docstring 且無 `docs/` 說明
  2. spec 描述模糊或有歧義，無法安全推斷預期行為
  3. 未覆蓋程式碼屬於 stop condition 類別（upload/download/streaming/polling/retry/pagination/session side effects）
  4. 測試需要 live API 或 integration fixture（非 unit test）
  5. 函式涉及外部 I/O 但無 mock 策略可從 spec 推斷
- **Feedback 格式**（每個 gap 一則）：
  ```
  [COVERAGE GAP - HUMAN REVIEW REQUIRED]
  模組：src/mlops_async/xxx.py
  未覆蓋行：45-67
  函式：function_name
  停止原因：{一句話說明為什麼 Agent 無法補測試}
  建議人工操作：{具體可執行的建議}
  ```

---

## 顯式假設

1. 「spec」= docstrings + type hints + `docs/*.md` + `analysis/<topic>/requirements.md` + 現有測試結構。沒有其他來源。
2. Agent 是**純靜態分析腳本**，不呼叫 LLM API。推理能力受限於可從原始碼讀取的靜態資訊。
3. pre-commit hook 只跑 `tests/unit/`，Integration / E2E 測試不在門檻計算範圍內。
4. 80% 門檻以 `src/mlops_async/` 整體為計算單位，不以單一模組計算。
5. Agent 寫入的測試 stub 需通過 `pytest`（能執行），但測試是否「測到正確行為」由人工驗證。
6. `.coverage-reports/coverage.json` 路徑固定，並加入 `.gitignore`（不提交）。

---

## Non-goals

1. Agent 不呼叫 LLM / AI API 自動生成語義豐富的測試（靜態腳本限制）。
2. Agent 不對 `tests/integration/` 生成測試。
3. Agent 不修改 source code；只修改 `tests/unit/` 目錄。
4. 不要求生成的測試 100% 語義正確；只要求覆蓋率數字達標且測試能執行。
5. 不在 CI（GitHub Actions）層面做覆蓋率強制（此 topic 範圍外）。

---

## 矛盾記錄（Contradiction Log）

### C-1：pre-commit 同步性 vs Agent 非同步性 ✅ 已解決

- **矛盾**：pre-commit 必須秒級完成；Agent 分析 + 生成測試是分鐘級工作。
- **決議**：拆分為兩個獨立步驟：
  - Step 1：pre-commit hook = 只做 gate（pytest 跑完給 pass/fail）
  - Step 2：Developer 手動執行 `python scripts/coverage_agent.py`

### C-2：靜態腳本 vs 「自動補寫測試」預期 ✅ 已解決

- **矛盾**：靜態腳本不具備 LLM 推理能力，無法「理解行為」。
- **決議**：腳本只做 **template-based stub generation**：
  - 基於 function signature + docstring + type hints 生成測試結構
  - 無法確定行為時 → 輸出 HUMAN REVIEW REQUIRED，不猜測
  - **生成的測試是 stub（有函式簽名、`assert` 佔位），不保證語義正確**

### C-3：`addopts` 自動跑 coverage vs pre-commit hook ✅ 已解決

- **矛盾**：`addopts` 讓每次 `pytest` 都自動跑 coverage；pre-commit 也跑 pytest。若 pre-commit 和 `addopts` 設定衝突（如路徑不同），會有雙重計算問題。
- **決議**：`addopts` 含 `--cov=src/mlops_async`（使用者確認）；pre-commit hook 明確指定 `tests/unit/` 並帶相同路徑，確保一致。

---

## 極端邊界檢查（Extreme Boundary Checks）

| 情境 | 處理方式 |
|---|---|
| `.coverage-reports/coverage.json` 不存在（首次執行） | pytest 執行時自動生成；若腳本先於 pytest 執行則報錯說明 |
| 覆蓋率剛好 79.9%（一行之差） | gate 阻擋；Agent 找出那幾行，嘗試生成 stub |
| 所有未覆蓋函式均無 docstring | 全部輸出 HUMAN REVIEW REQUIRED；不生成任何測試 |
| Agent 寫入測試後，重跑仍 < 80% | 輸出剩餘 gap 的 HUMAN REVIEW REQUIRED，不循環 |
| E2E topic（spec 明確標注） | 開發者手動修改 pre-commit hook 指令以包含 integration tests（超出 agent 範圍）|
| 開發者有未提交變更（dirty tree） | Agent 只讀 coverage.json + source；不影響 git status |
| 測試 stub 寫入後破壞現有測試 | pytest 執行失敗；開發者需手動修復（Agent 不處理 merge conflict）|

---

## Blockers（技術翻譯前必須確認）

無。所有矛盾已解決，可進入技術翻譯。

---

## Acceptance Signal

以下可由另一位開發者驗證：

1. 在 `tests/unit/` 中刪除一個測試 → `git commit` 被阻擋，terminal 顯示哪些行未覆蓋
2. 執行 `python scripts/coverage_agent.py` → 在 `tests/unit/` 出現新的 `test_*.py` stub 檔案
3. 重跑 `pytest --cov` → 覆蓋率 ≥ 80%（若 stub 足夠）
4. 若 gap 有 stop condition → terminal 輸出 `[COVERAGE GAP - HUMAN REVIEW REQUIRED]` 格式訊息
