# Python Implementation Workflow Reference

## Official Artifact Layout

- Custom agents:
  - `./.codex/agents/planner.toml`
  - `./.codex/agents/implementer.toml`
  - `./.codex/agents/reviewer.toml`
- Shared reusable skill:
  - `./.agents/skills/workflow-artifact-contract/SKILL.md`
  - `./.agents/skills/workflow-artifact-contract/agents/openai.yaml`
- Wrapper workflow skill:
  - `./.agents/skills/python-implementation-workflow/SKILL.md`
  - `./.agents/skills/python-implementation-workflow/reference.md`
  - `./.agents/skills/python-implementation-workflow/agents/openai.yaml`

## Responsibility Split

- `planner`: planning and scope clarification from approved topic artifacts
- `implementer`: repository mutation inside the approved topic scope
- `reviewer`: change review for correctness, path compliance, and contract drift
- `workflow-artifact-contract`: reusable path, schema, and boundary rules for workflow artifacts
- `python-implementation-workflow`: wrapper guidance for how the parent Codex session should coordinate those agents

## Frozen Provenance Boundary

- Legacy `.github/agents/python-implementation-workflow.agent.md` is frozen provenance only.
- The wrapper skill may cite that provenance boundary, but must not require the legacy file at runtime.

## Explicit-Only Metadata

Both workflow skills use explicit-only metadata:

```yaml
policy:
  allow_implicit_invocation: false
```

No extra metadata belongs in `agents/openai.yaml` unless the runtime emits an exact failure that requires it.
