# Instruction layering reference

This skill always generates the target project's `.github/copilot-instructions.md`
with three fixed sections:

1. `## Project Truth`
2. `## Governance`
3. `## Implementation Rules`

## `## Project Truth`

Use this section for observed project reality only.

Include facts such as:
- active toolchain and package manager
- repository layout and important paths
- entrypoints, interfaces, or structural invariants that were actually sensed
- other current facts needed to keep agent behavior grounded

Do not put speculative policy here.
Do not elevate human preference above contradicting sensed facts.

## `## Governance`

Use this section for rules that govern work because they come from installed skills
or approved plan-level contracts.

Typical content:
- installed skill expectations that should shape later tasks
- locked plan constraints that remain valid for the target repository
- review or workflow rules that downstream work must respect

Governance may refine how to act on facts, but it must stay consistent with
`## Project Truth`.
If governance claims depend on a missing or unsupported skill, the skill must
hard-block instead of inventing the rule.

## `## Implementation Rules`

Use this section for concrete execution guidance that follows from the first two
sections.

Typical content:
- file-level or workflow-level rules that agents should follow in the target repo
- allowed commands, update rules, or maintenance guidance that match the sensed
  toolchain
- practical do / do-not guidance grounded in current project truth and governance

Do not use this section as a catch-all for unsensed assumptions.
Do not add rules that contradict `## Project Truth` or bypass `## Governance`.

## Layering discipline

Apply inputs in this order before content lands in a section:
1. sensed facts
2. installed skills
3. plan / blueprint / retrofit contract
4. human intent

This means:
- facts populate `## Project Truth`
- installed skills and approved contracts shape `## Governance`
- implementation guidance belongs in `## Implementation Rules` only after it is
  consistent with the higher layers

If two layers conflict, the lower-priority layer does not silently win.
Use the stop-and-ask path when human intent conflicts with current facts.
