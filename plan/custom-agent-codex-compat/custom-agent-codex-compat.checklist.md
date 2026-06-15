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
- [X] downstream implementation artifacts now exist on the official repo-local paths

## Phase B Preflight Gate

- [X] planning artifacts define preflight as minimal-schema-only, not full implementation
- [X] planning artifacts require preflight to pass before full implementation can proceed
- [X] minimal custom-agent TOML schema is frozen to `name`, `description`, and `developer_instructions`
- [X] minimal `agents/openai.yaml` schema is frozen to `policy.allow_implicit_invocation: false`
- [X] preflight failure handling is exact-failure-only
- [X] preflight failure handling forbids schema guessing, pre-expansion, and official-path changes

## Legacy Dependency Boundary

- [X] `.github/agents/python-implementation-workflow.agent.md` is preserved as read-only source evidence
- [X] planning artifacts do not treat `.github/agents/*` as the final discovery surface
- [X] no planning artifact requires direct edits to the legacy source file

## Wrapper Skill Boundary

- [X] `SKILL.md` is described as a wrapper layer, not a replacement for the custom agent
- [X] `agents/openai.yaml` is described as a binding artifact, not a standalone workflow surface
- [X] planning artifacts require the custom agent to remain the owner of core orchestration semantics

## Implementation Status

- [X] this topic is now described as an implementation baseline
- [X] implementation artifacts are now landed on the official repo-local paths
- [X] implementation steps are complete and marked complete in `step.md`
- [X] the remaining workflow work is now limited to review stages in `step.md`
