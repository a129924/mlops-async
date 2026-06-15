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
- [X] custom workflow agent artifact path 已改成 `.codex/agents/api-client-porting-workflow.toml`。
- [X] custom workflow agent 的 `developer_instructions` 已被定義為主要 orchestration contract 承載面。
- [X] `docs/migration-map.md` 與 `docs/porting-ledger.md` 已降為 optional/default input。
- [X] `.github/copilot-instructions.md` 已排除為 runtime prerequisite。

## Human-Check Semantics

- [X] topic 已完成新的 implementation draft plan commit。
- [X] topic `Current` 已反映 post-review `approved` 狀態。
- [X] `plan-reviewer` 已完成。
- [X] planner final gate 已完成。
- [X] topic 目前停在 human check 之前，尚未進入 publish routing。

## Boundaries

- [X] 未混入其他 `.github/skills/*` implementation。
- [X] 未把 runtime installation 誤寫成本 topic 內工作。
- [X] 未把 `README.md` 或 `VERSION` 誤寫成 implementation scope。
