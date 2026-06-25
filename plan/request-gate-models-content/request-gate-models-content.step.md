---
topic: request-gate-models-content
phase: plan-authoring
created: 2026-06-25
---

# request-gate-models-content — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> 這個 step tracker 先追蹤 implement-plan workflow，reviewer 通過後停在 `human-check`。
> Update this file at: `plan/request-gate-models-content/request-gate-models-content.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] draft-plan-commit
- [ ] plan-review
- [ ] plan-review-fix-loop
- [ ] human-check

## Implementation Steps

- [X] 1. 完成 topic-local implement-plan artifacts：`requirements.md`、`technical-spec.md`、`plan.md`、`spec.md`、`step.md`，並使它們對 implement lane、frozen write set、與 direct-path-only rule 的語意一致。
- [ ] 2. 將 draft-plan commit 作為下一個 workflow step；本輪不自行 commit，但進 reviewer gate 前必須先完成 draft-plan commit。
- [ ] 3. 進入 reviewer gate；reviewer 只審這個 topic 的 plan artifacts 是否存在 scope drift、contract drift、或 workflow drift。
- [ ] 4. 若 reviewer 回 `needs-rework`，只允許在這 5 個 topic-local plan artifacts 內修正，形成 `plan-review-fix-loop`；不得提前進 implementation。
- [ ] 5. reviewer 通過後停在 `human-check`；不得自動建立 `tests/unit/request_contract/models_content_request_gate/**`，後續 implementation 需等待下一輪明確授權。
