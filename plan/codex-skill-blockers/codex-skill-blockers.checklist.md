# Codex Porting Workflow Checklist

## Draft Package

- [X] `requirements.md` 明確改成 migration-design baseline。
- [X] `technical-spec.md` 明確固定為 `2 skills + 1 custom agent`。
- [X] `plan.md` 明確列出 analysis inputs、bootstrap inputs 與 future targets。
- [X] `step.md` 與 `checklist.md` 已重建。

## Migration Contract

- [X] planner skill 仍是 planning-only。
- [X] implementer skill 仍是 implementation-only。
- [X] workflow agent 仍是 orchestration-only。
- [X] `.github/skills/api-client-porting-*` 只被定義為 bootstrap input。
- [X] `.agents/skills/*` 與 `.codex/agents/*` 只被定義為 deferred targets。
- [X] `docs/migration-map.md` 與 `docs/porting-ledger.md` 不再被寫成 unconditional prerequisite。

## Pause-State Semantics

- [X] topic 目前停在新的 rerun draft plan commit。
- [X] topic `Current` 沒有宣稱 `reviewer-in-progress` 或 `approved`。
- [X] 尚未進入 `plan-reviewer`。
- [X] 尚未進入 planner final gate。

## Boundaries

- [X] 未混入其他 `.github/skills/*` migration。
- [X] 未混入實際 `.agents/skills/**` 或 `.codex/agents/**` 建立。
- [X] 未把 runtime installation 誤寫成已完成事項。
