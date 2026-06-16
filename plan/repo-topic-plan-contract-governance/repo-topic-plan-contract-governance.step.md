# Step Tracker — repo-topic-plan-contract-governance

## Status

- **Topic status**: `review-ready`
- **Cycle**: 1

## Implementation Steps

- [X] Step 1: 建立 `plan/topic-plan-contract.md`，明確定義 shared topic-plan contract 的 purpose 與 authority boundary，並在同一檔案中凍結 canonical required topic-plan sections、template 缺失或不可用時的 fallback behavior、contract-level blocking semantics，以及它與 `plan/agent-handoff-workflow.md` / `plan/<topic>/<topic>.plan.md` 的責任分界。
- [X] Step 2: 以 read-only 方式驗證 `plan/agent-handoff-workflow.md`、`.agents/skills/plan-creator/SKILL.md`、`.agents/skills/plan-creator/reference.md`、`.agents/skills/plan-reviewer/SKILL.md`、`.agents/skills/plan-reviewer/reference.md`、`.agents/skills/plan-reviewer/checklist.md`、`.github/prompts/create-agent-plan.prompt.md` 可由新 shared contract 滿足，且無需在本 topic 擴張修改。
- [X] Step 3: 若發現 direct semantic contradiction 無法只靠 `plan/topic-plan-contract.md` 解決，停止並回報 divergence；不得在本 topic 靜默重寫 consumer、workflow surfaces 或其他治理面。

## Acceptance Evidence

- `plan/topic-plan-contract.md` 已建立，且明確定義 shared contract purpose、authority boundary、canonical required sections、template fallback、contract-level blocking semantics，以及與 `plan/agent-handoff-workflow.md` / `plan/<topic>/<topic>.plan.md` 的責任分界。
- Read-only compatibility evidence 已記錄涵蓋 `plan/agent-handoff-workflow.md`、`.agents/skills/plan-creator/SKILL.md`、`.agents/skills/plan-creator/reference.md`、`.agents/skills/plan-reviewer/SKILL.md`、`.agents/skills/plan-reviewer/reference.md`、`.agents/skills/plan-reviewer/checklist.md`、`.github/prompts/create-agent-plan.prompt.md`；其中對 prompt 的明確相容性依據，是目前 `plan.md` 已在 `## Inputs` 列出 `analysis/repo-topic-plan-contract-governance/requirements.md` 與 `analysis/repo-topic-plan-contract-governance/technical-spec.md`，並保留 `Artifact Paths` / `Implementation Steps` 對 `technical-spec.md` 的對映承諾。
- 目前文件明確支持的較窄結論是：本 topic plan 已補足 prompt 要求的 analysis input naming，且持續將 `plan/agent-handoff-workflow.md` 定位為 workflow lifecycle / routing contract；更廣泛的 consumer-wide 無矛盾結論，不在此 Acceptance Evidence 直接主張。
