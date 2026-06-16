# Step Tracker — repo-topic-plan-contract-governance

## Status

- **Topic status**: `planned`
- **Cycle**: 1

## Implementation Steps

- [ ] Step 1: 建立本 step tracker 檔案，並使其與 `plan/repo-topic-plan-contract-governance/repo-topic-plan-contract-governance.plan.md` 的 creator steps 對齊。
- [ ] Step 2: 建立 `plan/topic-plan-contract.md`，明確宣告 shared topic-plan contract 的 purpose 與 authority boundary，且不得把 `plan/agent-handoff-workflow.md` 當成替代品。
- [ ] Step 3: 在 `plan/topic-plan-contract.md` 中定義 canonical required topic-plan sections、template 缺失或不可用時的 fallback behavior，以及 contract-level blocking semantics。
- [ ] Step 4: 以 read-only 方式驗證 `plan/agent-handoff-workflow.md`、`.agents/skills/plan-creator/SKILL.md`、`.agents/skills/plan-creator/reference.md`、`.agents/skills/plan-reviewer/SKILL.md`、`.agents/skills/plan-reviewer/reference.md`、`.agents/skills/plan-reviewer/checklist.md`、`.github/prompts/create-agent-plan.prompt.md` 可由新 shared contract 滿足，且無需在本 topic 擴張修改。
- [ ] Step 5: 若發現 direct semantic contradiction 無法只靠 `plan/topic-plan-contract.md` 解決，停止並回報 divergence；不得在本 topic 靜默重寫 consumer 或 workflow surfaces。
- [ ] Step 6: 重新檢查最終變更，確認僅限 `plan/topic-plan-contract.md` 與本 topic 的 planning artifacts，且未觸及 `src/**`、`tests/**`、其他 topic 的 `analysis/**` 或 `plan/**`、`README.md`、`VERSION` 或 release artifacts。

## Acceptance Evidence

- None yet. 此檔案目前只作為 planning-phase 的 creator step contract，所有 implementation steps 均待後續 creator phase 執行。
