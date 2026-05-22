# token-manager-test-rigor-review Specification

## Acceptance Criteria

1. `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md` must contain all 13 python-plan-authoring sections in required order.
2. `## Decisions` must include `Async-planning status` plus the seven standard decision items with no empty fields.
3. `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md` must exist and mirror every numbered `## Implementation Steps` item as pending checkboxes.
4. Planning artifacts must not introduce changes under `src/**` or `tests/**`.
5. `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md` must remain aligned with the current plan scope and non-goals.

## Behavioral Scenarios

### Scenario 1: reviewer checks python-plan-authoring completeness
- **Given**: topic plan was previously written in agent-handoff format only
- **When**: planner upgrades the plan to python-plan-authoring contract and adds step/spec co-artifacts
- **Then**: reviewer can validate 13-section completeness, async status evidence, and mirrored step entries without guessing missing fields

### Scenario 2: async applicability remains exempt
- **Given**: this topic only edits planning/analysis artifacts
- **When**: reviewer inspects the `Async-planning status` line
- **Then**: exemption evidence is explicitly stated and no triggered async subsections are required

## Error / Edge Cases

- If any required Decisions bullet is missing, mark plan `INCOMPLETE` and request repair before implementation.
- If step entries diverge from plan numbered steps, mark step tracker invalid and require remirroring.
- If D1 is later changed from `non-trivial` to `trivial`, reassess whether `.spec.md` remains required by process owner decision.
- If any `src/**` or `tests/**` file appears in this topic diff, treat it as scope violation and halt review-ready promotion.
