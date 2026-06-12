# Codex Porting Workflow Implementation Checklist

## Draft Package

- [X] `requirements.md` 明確改成 implementation baseline。
- [X] `technical-spec.md` 明確改成直接建檔的 implementation topic。
- [X] `plan.md` 明確列出 analysis inputs、bootstrap inputs 與 exact creator artifact paths。
- [X] `step.md` 與 `checklist.md` 已重建。

## Implementation Contract

- [X] 本 topic 被明確定義為 implementation topic。
- [X] planner skill artifact set 已列出 exact file paths。
- [X] implementer skill artifact set 已列出 exact file paths。
- [X] custom workflow agent artifact 已列出 exact file path。
- [X] `docs/migration-map.md` 與 `docs/porting-ledger.md` 已降為 optional/default input。
- [X] `.github/copilot-instructions.md` 已排除為 runtime prerequisite。

## Pause-State Semantics

- [X] topic 目前停在新的 implementation draft plan commit。
- [X] topic `Current` 沒有宣稱 `review-ready` 或 `approved`。
- [X] 尚未進入 `plan-reviewer`。
- [X] 尚未進入 planner final gate。

## Boundaries

- [X] 未混入其他 `.github/skills/*` implementation。
- [X] 未把 runtime installation 誤寫成本 topic 內工作。
- [X] 未把 `README.md` 或 `VERSION` 誤寫成 implementation scope。
