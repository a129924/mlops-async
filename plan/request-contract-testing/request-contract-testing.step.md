# Request Contract Testing Workflow Steps

## Implementation Steps

- [X] Create `analysis/request-contract-testing/requirements.md` and keep it frozen.
- [X] Create `analysis/request-contract-testing/technical-spec.md` and keep it frozen.
- [X] Create `docs/standards/request-contract-testing.md` with gate, fixture, comparison, auth divergence, and stop-condition rules.
- [X] Add `plan/agent-handoff-workflow.md` as canonical workflow reference for plan-reviewer dependencies.
- [X] Restructure `plan/request-contract-testing/request-contract-testing.plan.md` to canonical contract sections.
- [X] Replace loose affected-files prose with precise, role-labeled `Artifact Paths`.
- [X] Keep `Reviewer Handoff` as one machine-readable JSON object.
- [X] Declare `Post-merge / release actions` explicitly (no release action in this topic).
- [X] Declare stable-library intent explicitly as non-stable for this topic.

## Workflow Stages

These stage markers are informational only. Completion gates must read only `## Implementation Steps`.

- [X] Analysis freeze
- [X] Standard authoring
- [X] Plan contract rework
- [ ] Independent plan-reviewer rerun
