# Request Shape Priority Workflow Steps

## Implementation Steps

- [X] 建立 `analysis/request-shape-priority-workflow/requirements.md`，凍結 docs-first session-entry、family queue、blocked policy、Observer / Dispatcher 邊界、與 request-shape 主測試面定位。
- [X] 建立 `analysis/request-shape-priority-workflow/technical-spec.md`，將需求轉成 exact artifact responsibilities、entry precedence、queue contract、dispatch board / step tracker 分工、與 stop rules。
- [X] 建立 `docs/request-shape-priority-workflow/README.md`，使其成為新 session 第一入口，明確宣告固定讀取順序與 workflow artifact hierarchy。
- [X] 建立 `docs/request-shape-priority-workflow/standards.md`，把 Observer / Dispatcher 的角色、allowed subAgent roles、禁止事項、dispatch 規則、queue law、與 stop conditions 寫成 repo-visible contract。
- [X] 建立 `docs/request-shape-priority-workflow/checklist.md`，使其只承擔跨 family queue / phase / blocked / next dispatch / resume checks，不與任何單一 topic 的 `*.step.md` 混用。
- [X] 建立 `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`，使用 canonical topic-plan sections，並把本 topic 的 review 後 wait-human-check 停點寫清楚。
- [X] 建立 `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`，只追蹤本 topic artifact 建立與 review readiness。

## Workflow Stages

These stage markers are informational only. Completion gates must read only `## Implementation Steps`.

- [X] Create analysis
- [X] Create agent plan
- [X] Creator implementation ready
- [ ] Independent review
