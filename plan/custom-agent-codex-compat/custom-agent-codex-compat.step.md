---
topic: custom-agent-codex-compat
phase: plan-authoring
created: 2026-06-15
---

# custom-agent-codex-compat — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> This round now tracks downstream implementation completion on the official repo-local artifact surface.
> Update this file at: `plan/custom-agent-codex-compat/custom-agent-codex-compat.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. Convert this topic's planning artifacts to an implementation baseline so downstream phases target official repo-local discovery paths instead of a paused planning draft.
- [X] 2. Create `./.codex/agents/planner.toml`, `./.codex/agents/implementer.toml`, and `./.codex/agents/reviewer.toml` as the minimal repo-local custom agent set.
- [X] 3. Create `./.agents/skills/workflow-artifact-contract/` as the shared reusable workflow contract skill with explicit-only metadata.
- [X] 4. Create `./.agents/skills/python-implementation-workflow/` as the wrapper workflow skill, including `SKILL.md`, `reference.md`, and explicit-only metadata.
- [X] 5. Verify all downstream artifact references use only `./.codex/agents/*.toml`, `./.agents/skills/<skill-name>/SKILL.md`, and `./.agents/skills/<skill-name>/agents/openai.yaml`.
- [X] 6. Verify the legacy dependency boundary: `.github/agents/python-implementation-workflow.agent.md` remains read-only source evidence only.
- [X] 7. Verify the wrapper skill boundary: wrapper artifacts hand off to the custom agents and do not replace core orchestration ownership.
- [X] 8. Add targeted validation coverage in `./tests/test_codex_custom_agent_baseline.py` and confirm `## Implementation Steps` is fully complete for Phase 3.

## Notes

- Canonical Phase 3 gate reads only `## Implementation Steps`.
- Implementation phase artifacts now exist on the official repo-local paths and are ready for reviewer validation.
