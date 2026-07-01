# Request Shape Priority Workflow Checklist

## Session resume checklist template

本段是 **template**，不是共享真值狀態。

- 不得直接在本共享文件上打勾。
- 若當前 session 需要使用 resume checklist，必須先複製到該 session 自己的
  topic-local notes、handoff、或 plan 附錄，再於複本上勾選。

可複製模板如下：

```md
## Session resume checklist

- [ ] 已先讀 `docs/request-shape-priority-workflow/README.md`
- [ ] 已再讀 `docs/request-shape-priority-workflow/standards.md`
- [ ] 已再讀 `docs/request-shape-priority-workflow/checklist.md`
- [ ] 已確認 `README.md`、`standards.md`、`checklist.md` 三者都存在
- [ ] 已確認目前 worktree / branch / topic state
- [ ] 已確認本次要處理的是哪個 surface / API
- [ ] 已確認沒有跳過既定 queue 順序
```

## Global surface/API implementation board

狀態欄位只允許使用：

- `[X]`：已完成
- `[ ]`：尚未開始 / 尚未完成
- `[BLOCKED]`：需人工決策，不得自動前進
- `[OUT-OF-SCOPE]`：存在於 repo surface，但不屬於本 workflow queue

| State | Surface | API | Order | Injection hint | Notes |
| --- | --- | --- | --- | --- | --- |
| `[X]` | `modelRepository/models` | `list_models` | `01` | 注入 `models_request_gate` baseline 與 `bare_get` / `filter_project_id` 語意 | shape-only 模板已存在 |
| `[X]` | `modelRepository/models` | `get_model` | `02` | 注入 `direct_identifier` branch 與 blocked variants | shape-only 模板已存在 |
| `[X]` | `modelRepository/models/content` | `get_model_content` | `03` | 先凍結 `modelId + fileId` 直接內容下載 shape，再判斷檔案類型是否留在同 topic | repo surface 已存在，尚未進 queue |
| `[X]` | `modelRepository/projects` | `list_projects` | `04` | 沿用 models oracle，聚焦 `bare_get` / `limit_1000` | request-only gate 已存在 |
| `[X]` | `modelRepository/projects` | `get_project` | `05` | 注入 `direct_identifier` branch 與 blocked variants | request-only gate 已存在 |
| `[X]` | `modelRepository/projects/champion` | `get_champion_model` | `06` | 注入 project identifier -> champion model 取回語意，避免混入 files payload 驗證 | request-only gate 已存在 |
| `[X]` | `modelRepository/projects -> tables-link surface` | `list_tables` | `07` | 注入 fixed-path MVP gate：`GET /modelRepository/projects/{project_id}/tables`，避免混回 HATEOAS-only blocker | fixed-path MVP request-only gate 已存在；與 CAS tables 仍是不同 surface |
| `[X]` | `jobExecution/jobRequests/jobs` | `start_job` | `08` | 先凍結 `jobRequestId -> POST jobs` 的 request shape，不預設輪詢策略 | request-only gate 已存在 |
| `[X]` | `jobExecution/jobs` | `get_job` | `09` | 聚焦單次 GET job detail shape，不混入 state polling contract | request-only gate 已存在 |
| `[X]` | `jobExecution/jobs/state` | `get_job_state` | `10` | bounded request-only / shape-only gate completed; do not auto-expand this row into polling / state-machine workflow | state request gate landed; broader polling semantics remain separate from the detail surface |
| `[OUT-OF-SCOPE]` | `casManagement/dataSources/tables` | `list_tables` | `--` | 不注入到目前 queue；repo truth 另有 `request-gate-casmanagement-list-tables` | concrete CAS tables surface；strict `limit=1000&start=0` request gate 已 merged / released，但不屬目前 request-shape queue |
| `[OUT-OF-SCOPE]` | `casManagement/dataSources/tables` | `get_table` | `--` | 不注入到目前 queue；repo truth 另有 `request-gate-casmanagement-get-table` | concrete CAS tables surface；direct `{caslib} + {tableName}` request gate 已 merged / released，但不屬目前 request-shape queue |
| `[OUT-OF-SCOPE]` | `casManagement/caslibs/tables/state` | `change_table_state` | `--` | 不注入到目前 queue | mutation surface，不屬目前 request-shape priority workflow |
| `[OUT-OF-SCOPE]` | `SASLogon/oauth/token` | `obtain_access_token` | `--` | 不注入到目前 queue；repo truth 另有 `request-gate-saslogon-obtain-access-token` | auth surface 另有 boundary topic；bounded `client_credentials` request gate 已 merged / released，但不屬目前 request-shape queue |
| `[OUT-OF-SCOPE]` | `SASLogon/oauth/token` | `refresh_access_token` | `--` | 不注入到目前 queue；repo truth 另有 `request-gate-saslogon-refresh-access-token` | auth surface 另有 boundary topic；`refresh_token` request gate 已 merged / released，但不屬目前 request-shape queue |

## Board usage rules

- 若多個 session 同時工作，應以本 board 作為共享排序與接口狀態來源。
- 本 board 必須與 merged repo truth 對齊，不得保留過期的 pending / blocked 狀態。
- 若人類要指定下一個實作接口，可直接點名 `surface + API`。
- 若 session 只需要決定注入內容，應優先使用 `Injection hint`。
- `tables` 一詞不得單獨拿來排隊；必須先指明是
  `modelRepository/projects -> tables-link surface` 或
  `casManagement/.../tables`。
- 若需要單一 topic completion gate，應改讀該 topic 的
  `plan/<topic>/<topic>.step.md`。
- queue 外 surface 若已有 merged truth，notes 也必須同步補齊；
  不得只留下 `OUT-OF-SCOPE` 而不說明當前 repo truth。

## Auth surface current-truth reminder

- `SASLogon/oauth/token -> obtain_access_token` 已透過
  `request-gate-saslogon-obtain-access-token` 獨立 topic 落地並 released。
- `SASLogon/oauth/token -> refresh_access_token` 已透過
  `request-gate-saslogon-refresh-access-token` 獨立 topic 落地並 released。
- shared board 仍維持 `OUT-OF-SCOPE`，因為它們都不屬於目前 request-shape queue。

## CAS surface current-truth reminder

- `casManagement/dataSources/tables -> list_tables` 已透過
  `request-gate-casmanagement-list-tables` 獨立 topic 落地並 released。
- `casManagement/dataSources/tables -> get_table` 已透過
  `request-gate-casmanagement-get-table` 獨立 topic 落地並 released。
- shared board 仍維持 `OUT-OF-SCOPE`，因為它們都不屬於目前 request-shape queue。
- `change_table_state` 不得因 `list_tables` 與 `get_table` 已 landed 而自動視為同批完成。

## Human-check triggers

以下情況直接停在 `human-check`：

- 已完成的 `modelRepository/projects -> tables-link surface / list_tables`
  被要求改回未解鎖狀態。
- surface / API queue 被要求改序。
- `tests/contracts` 被要求升格成主 request-shape surface。
- 需要重開已凍結的 path / contract / architecture decision。
