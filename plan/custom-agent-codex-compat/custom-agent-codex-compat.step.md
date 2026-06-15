---
topic: custom-agent-codex-compat
phase: plan-authoring
created: 2026-06-15
---

# custom-agent-codex-compat — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> This round completes planning artifacts only; downstream implementation artifacts remain pending.
> Update this file at: `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. Convert this topic's planning artifacts to an implementation baseline so downstream phases target official repo-local discovery paths instead of a paused planning draft.
- [ ] 2. Create `./.codex/agents/python-implementation-workflow.toml` from the legacy `.github/agents/python-implementation-workflow.agent.md` workflow semantics.
- [ ] 3. Create `./.agents/skills/python-implementation-workflow/SKILL.md` as the wrapper skill entry for the custom agent.
- [ ] 4. Create `./.agents/skills/python-implementation-workflow/agents/openai.yaml` as the wrapper skill to custom-agent binding file.
- [ ] 5. Verify all downstream artifact references use only `./.codex/agents/*.toml`, `./.agents/skills/<skill-name>/SKILL.md`, and `./.agents/skills/<skill-name>/agents/openai.yaml`.
- [ ] 6. Verify the legacy dependency boundary: `.github/agents/python-implementation-workflow.agent.md` remains read-only source evidence only.
- [ ] 7. Verify the wrapper skill boundary: wrapper artifacts hand off to the custom agent and do not replace the custom agent's core orchestration logic.
- [ ] 8. Re-run the topic step tracker gate after implementation so `## Implementation Steps` is fully complete for Phase 3.

## Notes

- Canonical Phase 3 gate reads only `## Implementation Steps`.
- At the end of this round, only step 1 is expected to be complete.
