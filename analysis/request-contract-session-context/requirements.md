# request-contract-session-context requirements baseline

## Status

- `FROZEN` — ready for topic-plan authoring

## Problem Statement

repo 目前已有 `docs/standards/request-contract-testing.md` 與歷史 session evidence，可用來
描述 sasctl / legacy source 的 request-contract gate；但這套上下文仍不夠容易在**新 session**
中直接注入與重用。結果是 Main Agent 或 human operator 重新進入這塊工作時，仍需要回頭查
舊 session、翻找歷史對話，才能恢復「應該先看什麼、四類測試語意是什麼、遇到 doc/prompt 漂移
該怎麼做」這些關鍵上下文。

## Actors and Consumption Boundary

1. **Primary actor — 新 session 的 Main Agent**
   - 需要一個可直接注入的入口 artifact，讓它能快速進入 request-contract testing 相關工作。
   - 不應被迫回溯歷史 session 才能理解這塊的最小 baseline。
2. **Secondary actor — human operator**
   - 需要一份可重複使用的 repo-visible 注入 artifact，在新 session 中手動提供給 Agent。
   - 不應每次重新整理口語摘要或臨時重述四類測試語意。
3. **Reviewer / maintainer**
   - 需要一份明確的 source of truth，判斷 prompt 是否仍與 request-contract 標準一致。

## Measurable Requirements

| ID | Actor | Condition | Observable Outcome | Metric / Decision Rule | Failure Meaning |
| --- | --- | --- | --- | --- | --- |
| BR-1 | Main Agent、human operator | 新 session 要開始處理 sasctl / legacy source 的 request-contract testing topic | repo 中有一個可直接注入的 prompt / injection artifact 可作為單一入口 | 在新 session 中，注入該 prompt 後，Agent 能開始相關分析/規劃工作，且不需要再查舊 session history | 每次重啟同類工作都要重新人工回憶與補上下文 |
| BR-2 | Main Agent | 注入 prompt 後開始 request-contract testing 相關工作 | Agent 能明確重述固定的核心測試語意與 gate 規則 | Agent 至少必須能說出：`request shape / contract`、`auth steps 與 mock-response handling`、`preflight`、`target-api / intercepted flow capture`，以及 `fully intercepted capture`、`request-flow fixture`、`mock-response answer set` 這三個 gate 核心 | Agent 只拿到模糊摘要，仍可能誤解 request-contract gate 的最低要求 |
| BR-3 | Reviewer / maintainer | standards doc 與 prompt 都存在 | 兩者的權威關係清楚且可驗證 | `docs/standards/request-contract-testing.md` 必須是 source of truth；prompt 只能作為注入入口 / 摘要；若兩者漂移，Agent 必須停下，不可自行和解 | repo 會同時存在多個彼此衝突的 request-contract baseline |
| BR-4 | human operator、Main Agent | 新 topic 並非 request-contract testing 相關工作 | Agent 不會被這份 artifact 誤導去套用不相關的 baseline | prompt 與 standards doc 都必須明確標示只適用於 sasctl / legacy source 的 request-contract testing / request gate 類 topic | 不相關 topic 被錯誤套用這份 baseline，造成 scope 漂移 |
| BR-5 | Reviewer / maintainer | standards doc 與 prompt 建立完成後 | repo 中可辨識哪份文件是完整標準、哪份是操作入口 | standards doc 必須保留完整標準語意；prompt 必須指向該 doc，且不可重新發明另一套 contract | 注入入口與正式標準脫鉤，未來維護成本升高 |

## Assumptions

1. `docs/standards/request-contract-testing.md` 會繼續作為這塊的正式標準文件，而不是一次性說明。
2. 「單次注入即可開工」的實際入口會是 prompt artifact；prompt 再引導 Agent 讀 standards doc。
3. 這個 topic 只建立上下文注入與 source-of-truth 關係，不重新設計 request-contract harness 或 porting workflow。

## Non-goals

1. 不修改 `src/mlops_async/**` 或 `tests/**` 的 runtime / test behavior。
2. 不重新設計 sasctl request capture harness、DSL 介面、或 integration test 架構。
3. 不新增 `analysis/<topic>/technical-spec.md` 作為本 topic 的必要前置條件。
4. 不修改 `README.md`、`VERSION`、release notes、或其他 stable-library surfaces。
5. 不把這份 artifact 擴張成一般 API porting 全域手冊。

## Extreme-Boundary Checks

1. **Wrong topic**
   - 若新 session 處理的不是 request-contract testing / request gate 類 topic，這份 artifact 不應被當成通用 baseline。
2. **Partial completion**
   - 若只有 standards doc 或只有 prompt，另一份缺失時，不算完成；因為 user 需要的是 source-of-truth + injection entry 的雙工件。
3. **Prompt/doc drift**
   - 若 prompt 與 standards doc 漂移，Agent 必須停下，不得自行平均解讀。
4. **No session history lookup**
   - 成功條件必須在不查舊 session history 的情況下仍成立；否則不算達成「可直接注入」目標。
5. **Low-volume / repeat use**
   - 這份 artifact 不只要支援單次使用；重複開新 session 時也必須能保持同樣的可注入性與判讀結果。

## Contradiction Log

1. **需要單次注入即可開工 vs standards doc 才是正式標準**
   - Statement A：新 session 希望只注入一次就能開始工作。
   - Statement B：完整標準不應被塞進每次 prompt，否則 prompt 會逐漸變成第二份 source of truth。
   - Decision：prompt 是單次注入入口；standards doc 是 source of truth。prompt 需指向 doc，並在漂移時要求停止，而不是自行覆寫 doc。
2. **human operator 手動使用 vs Main Agent 自動重用**
   - Statement A：artifact 要讓 human operator 能直接拿來注入。
   - Statement B：artifact 也要讓 Main Agent 在新 session 中可直接採用。
   - Decision：兩者都屬 actor，但 Main Agent 優先；artifact wording 應先滿足 Agent 可直接消費，再兼容 human operator 的手動注入。

## Blockers

- None for this business baseline.

## Handoff Boundary for Plan Authoring

此 baseline 已凍結下列需求，不需要在 topic plan 中重新發明：

1. 這是 **雙工件 topic**：更新既有 `docs/standards/request-contract-testing.md`，並新增一份 prompt / injection artifact。
2. standards doc 是 source of truth；prompt 只是注入入口。兩者若漂移，Agent 必須停下。
3. 成功訊號包含兩件事：
   - 單次注入即可開始相關工作
   - Agent 能重述固定的四類測試語意與 gate 核心規則
4. 這個 topic 不包含 runtime/test/release 變更。
