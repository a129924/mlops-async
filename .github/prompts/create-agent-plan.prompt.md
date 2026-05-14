---
name: create-agent-plan
description: Turn the current plan-mode conclusion into a repo-visible topic plan at `plan/<topic>/<topic>.plan.md`. Produce only the planning artifact, do not enter implementation, and follow `plan/agent-handoff-workflow.md`.
---

請使用 `plan-creator`，根據我們剛剛在 plan mode 的結論，產出 repo-visible 的 topic plan：

- 輸出路徑：`plan/<topic>/<topic>.plan.md`
- 只產出 planning artifact
- 不進入 implementation
- 必須遵守 `plan/agent-handoff-workflow.md`
- 內容需符合 topic plan contract
- 若資訊不足，先補齊 plan 所需欄位，不要直接進入實作

## 前置分析層檢查

**在產出計畫前，必須先檢查：**

1. **若存在** `analysis/<topic>/requirements.md` 和 `analysis/<topic>/technical-spec.md`
   - 計畫的「Inputs」或「Prerequisites」區段必須明確列出這兩份檔案
   - 註明版本、雜湊或引用路徑，使計畫與分析層有可追蹤的映射關係
   - 計畫必須在「Artifact Paths」和「Implementation Steps」中確保 100% 對應 technical-spec.md

2. **若不存在** analysis 層檔案
   - 計畫仍可正常進行
   - 但應在「Assumptions」或「Context」中記錄「未提供前置業務需求分析與技術規格」作為風險註記
