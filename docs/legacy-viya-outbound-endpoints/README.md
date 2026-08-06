# Legacy Viya outbound endpoint implementation reference

這組文件將 legacy `sas-docker-api` 的 outbound Viya observations 與目前
`mlops-async` 證據分開記錄，供後續單一 endpoint family 的 planner 使用。它是
handoff/reference，不是 runtime contract、正式 migration row，亦不授權實作。

先讀 `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md` 的
authority class；再讀本目錄中的 family 文件。正式實作 topic 才能在
`docs/porting-ledger.md` 新增 source、request、response、error 與 compatibility
decision。`docs/migration-map.md` 在本 topic 僅提供 inventory/navigation。

**Global stop rule:** 若任何 evidence 彼此衝突，或與 evidence matrix 的 authority
class 衝突，立即停止；不得自行選擇、合併或升格 evidence，必須要求 human decision。

| Family | Handoff | 目前 disposition |
| --- | --- | --- |
| Token | [token.md](token.md) | runtime 已存在；不重做 |
| Models | [models.md](models.md) | 第一個 read-only candidate |
| Model content | [model-content.md](model-content.md) | 獨立規劃；先決定 link/path 與 payload |
| Projects / champion | [projects-champion.md](projects-champion.md) | projects 與 champion 分開決策 |
| Job execution | [job-execution.md](job-execution.md) | 僅 job start 可規劃；detail/state 暫停 |
| CAS tables | [cas-tables.md](cas-tables.md) | 證據升級前不實作 |

所有 `Target mapping` 區塊刻意未填：mapping 只能由後續已核准的 endpoint topic
依當時 evidence 與 human decision 寫入正式 ledger；不得將本參考文件當成 ledger。
