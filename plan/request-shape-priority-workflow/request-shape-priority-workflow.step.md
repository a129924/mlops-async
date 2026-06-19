# Request Shape Priority Workflow Steps

## Implementation Steps

- [X] 更新 `analysis/request-shape-priority-workflow/requirements.md`，把 queue 單位從抽象 family 正規化成 `surface + API`，並明寫 `tables` 不得單獨作為 queue 名稱。
- [X] 更新 `analysis/request-shape-priority-workflow/technical-spec.md`，把 drift、artifact responsibilities、board schema、與 correction rules 對齊成 surface-based workflow。
- [X] 更新 `docs/request-shape-priority-workflow/README.md`，把 `standards.md`、`checklist.md` 的描述改成 surface-based implementation workflow，並保留共享勾選污染警告。
- [X] 更新 `docs/request-shape-priority-workflow/standards.md`，移除 prompt / persona / allowed-subAgent / output-preference 內容，只保留 implementation sequencing、surface naming、artifact precedence、board / step 邊界、blocked policy、與 request-shape scope。
- [X] 更新 `docs/request-shape-priority-workflow/checklist.md`，使其同時承擔 session resume checklist template 與 global surface/API implementation board，並拆開 `modelRepository` HATEOAS tables 與 `casManagement` tables。
- [X] 更新 `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`，把 locked decisions、artifact roles、implementation steps、validation wording 對齊 surface-based correction。
- [X] 更新 `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`，使本輪 correction 的 implementation steps 與新 plan 一致，並把 `Independent review` 留為未完成。

## Workflow Stages

These stage markers are informational only. Completion gates must read only `## Implementation Steps`.

- [X] Create analysis
- [X] Create agent plan
- [X] Creator implementation ready
- [ ] Independent review
