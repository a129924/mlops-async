# Custom Agent Codex Compat Checklist

## Official Discovery Paths

- [X] planning artifacts now use `./.codex/agents/*.toml` as the only allowed custom-agent discovery path
- [X] planning artifacts now use `./.agents/skills/<skill-name>/SKILL.md` as the wrapper skill path
- [X] planning artifacts now use `./.agents/skills/<skill-name>/agents/openai.yaml` as the wrapper binding path
- [X] planning artifacts explicitly forbid `./codex/**`
- [X] planning artifacts explicitly forbid `./agents/openai.yaml`

## Artifact Family Contract

- [X] `plan.md` enumerates the full implementation artifact family
- [X] `technical-spec.md` enumerates the same three downstream targets
- [X] `step.md` requires all three downstream artifacts before Phase 3 can pass
- [ ] downstream implementation artifacts themselves are still pending in this round

## Legacy Dependency Boundary

- [X] `.github/agents/python-implementation-workflow.agent.md` is preserved as read-only source evidence
- [X] planning artifacts do not treat `.github/agents/*` as the final discovery surface
- [X] no planning artifact requires direct edits to the legacy source file

## Wrapper Skill Boundary

- [X] `SKILL.md` is described as a wrapper layer, not a replacement for the custom agent
- [X] `agents/openai.yaml` is described as a binding artifact, not a standalone workflow surface
- [X] planning artifacts require the custom agent to remain the owner of core orchestration semantics

## Planning Round Status

- [X] this topic is now described as an implementation baseline
- [X] this round is clearly limited to planning artifacts ready for downstream implementation
- [X] Phase 3 implementation steps remain pending and visible in `step.md`
