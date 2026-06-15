---
name: workflow-artifact-contract
description: Shared contract for repo-local Codex workflow artifacts. Use when creating, updating, or reviewing custom agents, wrapper skills, and their validation so paths, minimal schemas, and role boundaries stay consistent.
---

# Workflow Artifact Contract

Use this skill when work touches repo-local Codex workflow artifacts under `./.codex/agents/` or `./.agents/skills/`.

## Contract

- Custom agents live only at `./.codex/agents/*.toml`.
- Reusable skills live only at `./.agents/skills/<skill-name>/SKILL.md`.
- Per-skill metadata lives only at `./.agents/skills/<skill-name>/agents/openai.yaml`.
- Do not create workflow artifacts under `./codex/**`, `./agents/**`, `./.agents/openai.yaml`, or `./.codex/openai.yaml`.

## Custom Agent Rules

- Keep each custom agent TOML minimal.
- Only use these keys:
  - `name`
  - `description`
  - `developer_instructions`
- Match the filename to `name`.
- Do not add optional fields.
- Do not create runtime dependencies on legacy `.github/agents/*.agent.md` files.

## Skill Metadata Rules

- Explicit-only workflow skills use this exact metadata:

```yaml
policy:
  allow_implicit_invocation: false
```

- Do not add interface metadata or repo-specific keys unless a runtime failure explicitly requires them.

## Boundary Notes

- Legacy `.github/agents/*.agent.md` files are frozen provenance inputs only.
- Wrapper skills describe how a parent Codex session should use custom agents; they are not runtime orchestration engines.
- Shared contract skills define reusable rules and validation targets; they should not own topic-specific phase execution.
