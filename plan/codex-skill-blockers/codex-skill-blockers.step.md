# Codex Porting Workflow Implementation Steps

## Implementation Steps

- [X] Re-run implementation requirements in `analysis/codex-skill-blockers/requirements.md`.
- [X] Re-run implementation technical spec in `analysis/codex-skill-blockers/technical-spec.md`.
- [X] Recreate `plan/codex-skill-blockers/codex-skill-blockers.plan.md`.
- [X] Recreate `plan/codex-skill-blockers/codex-skill-blockers.step.md`.
- [X] Recreate `plan/codex-skill-blockers/codex-skill-blockers.checklist.md`.
- [X] Freeze exact planner skill artifact paths in the rerun plan.
- [X] Freeze exact implementer skill artifact paths in the rerun plan.
- [X] Freeze exact workflow agent artifact path in the rerun plan.
- [X] Re-align the workflow agent path contract from `.agent.md` to `.toml`.
- [X] Freeze that the TOML agent `developer_instructions` owns the orchestration contract.
- [X] Create a new draft plan commit for the rerun implementation topic.
- [X] Complete independent review for this rerun implementation topic.
- [X] Complete planner final gate for this rerun implementation topic.
- [X] Pause this topic at human check before any publish routing.

## Workflow Stages

These stage markers are informational only. Completion gates must read only
`## Implementation Steps`.

- [X] Analysis rerun
- [X] Draft implementation package rerun
- [X] Draft plan commit
- [X] Independent review
- [X] Planner final gate

## Current Handoff

- Waiting for human check before any publish routing begins.

## Creator Implementation Steps

- [X] Create `.agents/skills/api-client-porting-planner/SKILL.md`.
- [X] Create `.agents/skills/api-client-porting-planner/reference.md`.
- [X] Create `.agents/skills/api-client-porting-planner/examples.md`.
- [X] Create `.agents/skills/api-client-porting-planner/templates/family-map.md`.
- [X] Create `.agents/skills/api-client-porting-implementer/SKILL.md`.
- [X] Create `.agents/skills/api-client-porting-implementer/reference.md`.
- [X] Create `.agents/skills/api-client-porting-implementer/examples.md`.
- [X] Create `.agents/skills/api-client-porting-implementer/templates/porting-result.md`.
- [X] Create `.codex/agents/api-client-porting-workflow.toml`.
- [X] Verify repo-specific tracking paths are optional/default inputs, not hard dependencies.
- [X] Review implementation artifacts and this step tracker for scope drift.
- [X] Run planner final gate for implementation handoff.

## Implementation Workflow Stages

- [X] Creator implementation
- [X] Implementation review
- [X] Planner final gate

## Implementation Handoff

- Waiting for human check before any commit / push routing begins.
