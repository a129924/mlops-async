# Codex Skill Projection Checklist

## Authoring

- [X] `requirements.md` 列出 32 個 projection candidates。
- [X] `requirements.md` 明確排除 `copilot-instructions-init`、blockers、與 agents。
- [X] `technical-spec.md` 明確鎖定 canonical `skills/` 與 projected `.codex/skills/`
  的兩層 surface。
- [X] `plan.md` 使用 canonical workflow sections。
- [X] `step.md` 與 `checklist.md` 已建立。

## Review

- [X] `Reviewer Handoff` 是單一 JSON 物件。
- [X] Stable-library intent 明確標示為 absent。
- [X] `Artifact Paths` 沒有把 `.github/agents/*` 納入本 topic。
- [X] `Artifact Paths` 沒有把 `copilot-instructions-init` 納入 candidate set。
- [X] `Artifact Paths` 已把 32 個 future creator targets 轉成 exact repo-visible、
  role-labeled contract。
- [X] `Artifact path notes` 已明確宣告 `.github/copilot-instructions.md` 為 no-change。
- [X] 未發明第二套 projection algorithm。

## Final Gate

- [X] draft plan commit 已建立。
- [X] independent `plan-reviewer` gate 已重新通過。
- [X] `plan-creator` fix/update pass 已完成。
- [X] planner final gate 已完成。
- [X] topic 目前只停在 wait-human-check，未進 publish routing。
