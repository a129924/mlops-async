# Request Shape Priority Workflow Checklist

## Session resume checklist

- [ ] 已先讀 `docs/request-shape-priority-workflow/README.md`
- [ ] 已再讀 `docs/request-shape-priority-workflow/standards.md`
- [ ] 已再讀 `docs/request-shape-priority-workflow/checklist.md`
- [ ] 已確認 `README.md`、`standards.md`、`checklist.md` 三者都存在
- [ ] 已確認目前 worktree / branch / topic state
- [ ] 已確認本次要處理的是哪個 family
- [ ] 已確認沒有跳過既定 queue 順序

## Dispatch board

本檔是跨 family 的 dispatch board，不是任何單一 topic 的 `*.step.md`。

不得在本檔記錄：

- 單一 topic implementation checkbox
- creator completion gate
- code-level test pass/fail 細節

上述資訊應留在各 topic 自己的 `*.step.md`。

## Family queue

| Family | Current phase | Status | Next dispatch | Notes |
| --- | --- | --- | --- | --- |
| `models` | template-aligned | ready | `Code-Reviewer` or `Planner` depending on active topic | 作為 shape-only 模板 family |
| `projects` | queued | pending | `Planner` after `models` lane is closed | 沿用 `models` 的 oracle 與 gate |
| `tables` | blocked | `BLOCKED` | none | HATEOAS / conditional endpoint selection 未解 |

## Routing checks

- [ ] 若當前 family 是 `projects`，已確認 `models` lane 已完成 review / triage
- [ ] 若有人要求直接處理 `tables`，已回報 `human-check`
- [ ] 若 session 只需要看 queue / next dispatch，未混用任何 topic-local `*.step.md`
- [ ] 若需要單一 topic completion gate，已改讀該 topic 的 `plan/<topic>/<topic>.step.md`

## Human-check triggers

以下情況直接停在 `human-check`：

- `tables` 要求解鎖
- family queue 被要求改序
- `tests/contracts` 被要求升格成主 request-shape surface
- 需要重開已凍結的 path / contract / architecture decision
