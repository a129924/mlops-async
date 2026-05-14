---
name: create-analysis
description: Generate analysis-layer artifacts for a topic. Adaptively runs the analysis skills that are currently injected — business-intent-alignment produces `analysis/<topic>/requirements.md`, business-to-technical-translation produces `analysis/<topic>/technical-spec.md`. Works standalone without plan mode.
---

請根據目前 context 中注入的分析 Skill，依序產出對應的 analysis 層檔案。

## 準備

1. 確認 `<topic>` 名稱。若 context 中未明確提及，詢問使用者後再繼續。
2. 偵測目前注入的分析 Skill（`business-intent-alignment` 和／或 `business-to-technical-translation`）。
3. 依下方步驟的條件，決定執行哪些步驟。

## 步驟 1 — 需求分析

**僅在 `business-intent-alignment` Skill 已注入時執行。**

使用 `business-intent-alignment`，依照其 Process 步驟進行：

1. 採用 Socratic 訪談姿態，挑戰假設、量化模糊詞彙、揭露矛盾。
2. 執行極端邊界檢查，確認需求在最低量、最高量、異常中斷等條件下仍成立。
3. 凍結需求 baseline 後，產出至 `analysis/<topic>/requirements.md`。
4. 依 Skill Verification 確認每項需求皆可觀察或可量測，再繼續。

若 `business-intent-alignment` **未注入**，略過此步驟。

## 步驟 2 — 技術規格

**僅在 `business-to-technical-translation` Skill 已注入時執行。**

**前提條件**：`analysis/<topic>/requirements.md` 必須已存在且凍結。
若前提不成立，停止並告知使用者：需先完成需求分析（步驟 1）再執行本步驟。

使用 `business-to-technical-translation`，依照其 Process 步驟進行：

1. 採用悲觀實作者視角，假設隱藏耦合、遷移成本與操作負擔皆存在直到反證。
2. 將每項需求對應至最小技術實現：元件、介面、資料變更、驗證構件。
3. 進行架構合規自查，明確列出符合、不符合、需豁免之處。
4. 偵測技術現實與業務意圖的衝突；若衝突實質性，觸發 rollback-to-alignment 而非強行推進。
5. 產出至 `analysis/<topic>/technical-spec.md`。
6. 依 Skill Verification 確認每項業務需求都對應具體技術工作或明確阻礙點，再繼續。

若 `business-to-technical-translation` **未注入**，略過此步驟。

## 未注入任何分析 Skill 時

若兩個 Skill 皆未偵測到，告知使用者：

> 目前 context 中未偵測到分析 Skill。請在呼叫此 prompt 時注入需要的 Skill：
>
> - `@.github/skills/business-intent-alignment/` — 產出需求基準 `analysis/<topic>/requirements.md`
> - `@.github/skills/business-to-technical-translation/` — 產出技術規格 `analysis/<topic>/technical-spec.md`（需先有需求基準）
>
> 兩者可同時注入，也可分次執行。

## 完成後

analysis 層產出完成後，提示使用者：

> 分析層已就緒，可執行 `create-agent-plan` prompt 進入計畫建立流程。
> 計畫建立時會自動注入：
> - `analysis/<topic>/requirements.md`
> - `analysis/<topic>/technical-spec.md`（若已產出）
