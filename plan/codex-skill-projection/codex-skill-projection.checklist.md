# Codex Skill Projection Checklist

## Authoring

- [X] `requirements.md` 已改為 repo-local `.agents/skills` migration 方向。
- [X] `technical-spec.md` 已把 source 鎖定為
  `agent-skills/.codex/skills/<name>/`。
- [X] `technical-spec.md` 已把 target 鎖定為 `mlops-async/.agents/skills/<name>/`。
- [X] `plan.md` 已移除 `platform-projection-adapter` 與 canonical `skills/`
  language。
- [X] `AGENTS.md` 已納入本 topic 的 discovery contract。
- [X] `audit.md` 已建立，且只涵蓋 frozen 32 names。
- [X] `corrective-prompt.md` 已存在並對齊 `.agents/skills/` 方向。

## Review

- [ ] reviewer 已確認 `AGENTS.md` 明確宣告 `.agents/skills/` discovery surface。
- [ ] reviewer 已確認 32 個 target skill roots 都存在於 `.agents/skills/`。
- [ ] reviewer 已確認 audit ledger 與實際 target 狀態一致。
- [ ] reviewer 已確認 topic-managed `.codex/skills/` 副本已移除。
- [ ] reviewer 已確認沒有碰 `.github/agents/*`、blockers、`.github/skills/*`、
  或 `skills/*`。
- [ ] reviewer 已確認 `step.md` 勾選與實際 creator work 一致。

## Final Gate

- [ ] planner 已確認 topic 停在 reviewer 後的正確狀態。
- [ ] planner 已確認此 topic 未進 publish / release routing。
- [ ] topic 已停在 wait-human-check。
