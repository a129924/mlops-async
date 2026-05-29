---
topic: tests-importlib-plan-review
phase: reviewer-in-progress
created: 2026-05-28
---

# tests-importlib-plan-review — Step Tracker

> **Current gate purpose**：本檔的 canonical `## Implementation Steps` 只追蹤本輪 creator pass 是否已把 `tests/` import rewrite topic 的 planning artifacts 對齊到 reviewer gate。
> **Completion source**：依 `plan/agent-handoff-workflow.md`，只有 `## Implementation Steps` 的核取方塊會被當成目前 gate 的 completion source。
> **Downstream note**：未來真正的 `tests/` import rewrite 實作、review、PR-open、merge 與 release 對照，另見本文後段的獨立 future section；該段不是本輪 gate 的完成來源。

## Workflow Stages

- [X] workflow-alignment
- [X] topic-freeze
- [X] step-gate-complete
- [X] review-ready
- [X] reviewer-in-progress

## Implementation Steps

- [X] 1. 將本 tracker 的當前 gate 明確限定為 creator pass：只追蹤讓 `tests/` import rewrite topic 進入 reviewer gate 所需的 planning-artifact 對齊工作。
- [X] 2. 凍結本 topic 的執行主語與邊界：`tests/` 內移除非必要 `importlib`、保留真正 importability tests、並以語意一致為不可退讓條件。
- [X] 3. 保留 canonical `## Implementation Steps` 作為唯一 gate completion source，避免把未來 Implement / Reviewer / PR-open / merge / release 的工作混入目前 creator pass。
- [X] 4. 在本檔新增獨立的 future section，供後續 Implement / Reviewer / PR-open / merge / release 核對 topic 是否真的做到，但不把它作為目前 gate 的完成依據。
- [X] 5. 確認本輪 creator pass 已完成，故本 topic 可由 `creator-in-progress` 經 `review-ready` 進入 `reviewer-in-progress`，等待 reviewer 對最新版 planning artifacts 給出 verdict。

## Completion Signals

- [X] `## Implementation Steps` 現在只服務目前 creator pass / reviewer gate。
- [X] 當前 gate 不再混入未來 execution、PR 或 release 工作。
- [X] 本 topic 的主語仍是 `tests/` import rewrite，而非 planning-package meta 說明。
- [X] 後續實作與驗收核對需求已被移到獨立 future section。
- [X] reviewer 可直接用目前 artifacts 審查本輪 plan contract。

## Future Execution / Review Checklist

> 這一節提供未來 Implement / Reviewer / PR-open / merge / release 對照使用。
> 它是下游核對依據，不是當前 `review-ready` / `reviewer-in-progress` gate 的 completion source。

### Topic delivery target

- `tests/` 內非必要 `importlib` 用法應被移除或改寫為絕對引入。
- 真正以 import 成功／失敗、warning 或 import-time 可觀測結果為主題的測試，才可保留動態引入。
- 改寫後必須維持 module identity、fixture behavior、monkeypatch / mock 綁定點、assertion intent 與 pass / fail 意義一致。

### Removal / retention checklist

- [ ] 列出 `tests/` 內所有 `importlib` 使用點並完成分類。
- [ ] 移除所有只是在一般功能測試中替代普通 import 的 `importlib` 用法。
- [ ] 保留真正 importability tests 所需的動態引入，且每個保留案例都有明確理由。
- [ ] 對無法穩定證明等價的 loader-sensitive / reload-sensitive / `sys.modules` / `sys.path` 敏感案例停止並交人工 review。

### Implement Step

- [ ] 盤點每個使用點的檔案、scope、載入形式、被測對象與候選絕對引入路徑。
- [ ] 逐案改寫非例外案例，保留必要的 module namespace、引入時機與 fixture / helper scope。
- [ ] 移除因動態載入而存在、但在絕對引入後已非必要的輔助寫法，前提是不改變測試語意。

### Validation / Reviewer Step

- [ ] 驗證改寫前後的 module identity、fixture behavior、patch 綁定點與 assertion intent 一致。
- [ ] 執行受影響測試或等價驗證，確認 pass / fail 意義未漂移。
- [ ] reviewer 可追溯每個保留案例、改寫案例與 blocker 的理由。
- [ ] reviewer 確認沒有 scope 漂移到 `src/`、公開 API 或無關測試重構。

### PR-open Step

- [ ] PR 說明清楚列出：哪些 `importlib` 被移除、哪些 importability tests 被保留、哪些案例被標記人工 review。
- [ ] PR diff 保持在 `tests/` 與必要的 repo-visible planning artifacts 範圍內。
- [ ] PR 驗證摘要能支持「已維持語意一致」這個結論。

### Merge Step

- [ ] merge 前已解決所有 blocker，或已把 blocker 明確切分到後續 topic。
- [ ] merge 的內容只宣告本 topic 實際做到的範圍，不把未處理案例包裝成已完成。
- [ ] merge 後 repository 狀態仍符合「非必要 `importlib` 已移除、真正 importability tests 保留」的主語。

### Release Step

- [ ] 本 topic 不需要 release action；若未來有人主張需要 release，必須另開 topic 或更新 plan contract，而不是在此 tracker 內追加當前 gate 內容。
