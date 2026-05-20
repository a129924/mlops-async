# Correction / Delta Lifecycle Contract Alignment — Technical Spec

## Status

- **Status**: frozen technical baseline
- **Topic**: `correction-delta-lifecycle-contract-alignment`
- **Source baseline**:
  `analysis/correction-delta-lifecycle-contract-alignment/requirements.md`
- **Upstream source of truth**: released `agent-skills` `0.58.0` lifecycle
  contract
- **This round**: analysis + plan only; no implementation execution

## Baseline Summary

`mlops-async` already contains the local workflow surfaces that should carry this
contract:

- `plan/agent-handoff-workflow.md`
- `.github/agents/python-implementation-workflow.agent.md`
- `.github/skills/plan-creator/**`
- `.github/skills/plan-reviewer/**`

It also already has a concrete retained sample in `v0.9.2`:

- parent artifacts backfilled as current truth
- correction / delta artifacts retained as decision trail
- repo-visible `review-log`
- a three-round creator / reviewer loop in the sample topic

The technical problem is governance drift: the local workflow / planning surfaces
do not yet fully encode the clarified lifecycle rules that `agent-skills` `0.58.0`
now expresses explicitly.

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 Align local workflow surfaces with released contract | Refresh the exact local workflow / planning files listed in the topic plan so they encode the lifecycle contract directly | Released `agent-skills` `0.58.0`; current local copies in `mlops-async` | Medium wording and consistency work; no runtime burden | feasible |
| R2 Keep workflow body slim | Put field-level correction artifact guidance in `plan-creator` / `plan-reviewer` reference and examples instead of expanding `plan/agent-handoff-workflow.md` into a schema dump | Existing local `plan-creator` and `plan-reviewer` folders | Low to medium | feasible |
| R3 Encode current truth vs historical truth | Refresh `plan/agent-handoff-workflow.md`, `plan-creator`, and `plan-reviewer` wording to make the separation explicit | Existing sample evidence in `v0.9.2` | Low | feasible |
| R4 Make `review-log` conditional | Update local artifact-path and review guidance so `review-log` is required only for routing-controlling or multi-round cases | Local plan-authoring and review surfaces | Low | feasible |
| R5 Keep round caps topic-scoped | Add wording and examples that allow declared topic caps without promoting the sample cap into repo-wide law | Local plan-authoring and review surfaces | Low | feasible |
| R6 Enforce exact artifact paths | Refresh local artifact-path guidance and review checks so vague evidence labels are rejected | Local plan-authoring and review surfaces | Low | feasible |
| R7 Preserve role separation | Refresh local role-boundary rules, checklists, and examples so creator steps exclude reviewer-owned logging and Main Agent routing | Local workflow and planning surfaces | Low | feasible |
| R8 Exclude domain payload from internalization | Keep the implementation topic strictly within workflow surfaces and reject `src/**`, `tests/**`, or release files | Topic plan scope boundary | Low | feasible |

## Implementation-facing Workstreams

### Workstream 1 — Workflow contract refresh

Refresh `plan/agent-handoff-workflow.md` so it states:

1. workflow-body lifecycle / routing rules only;
2. parent artifacts become current truth after accepted backfill;
3. correction artifacts remain historical truth;
4. `review-log` is conditional on routing control or multi-round rework;
5. round caps are topic-scoped policy, not repository-wide law.

### Workstream 2 — Workflow-agent consumer refresh

Refresh `.github/agents/python-implementation-workflow.agent.md` so it remains a
consumer of the repo-level lifecycle contract rather than an independent or
conflicting owner.

### Workstream 3 — Plan-authoring contract refresh

Refresh the exact local `plan-creator` surfaces so they require:

1. slim workflow-body wording;
2. exact parent / correction / review-log artifact paths when used;
3. current-truth versus historical-truth separation;
4. topic-scoped round-cap policy;
5. detailed correction artifact contract in reference / examples instead of the
   workflow body.

### Workstream 4 — Plan-review contract refresh

Refresh the exact local `plan-reviewer` surfaces so reviewers can block:

1. vague evidence paths;
2. reviewer-owned work inside creator implementation steps;
3. unconditional `review-log` requirements;
4. repo-wide round-cap wording;
5. workflow-body bloat that embeds long correction schemas.

## Exact Planned Artifact Surface

The later implementation topic should be bounded to these exact files:

1. `plan/agent-handoff-workflow.md`
2. `.github/agents/python-implementation-workflow.agent.md`
3. `.github/skills/plan-creator/reference.md`
4. `.github/skills/plan-creator/checklist.md`
5. `.github/skills/plan-creator/examples.md`
6. `.github/skills/plan-creator/references/artifact-path-rule.md`
7. `.github/skills/plan-creator/references/role-boundary-rule.md`
8. `.github/skills/plan-creator/templates/topic-plan-template.md`
9. `.github/skills/plan-reviewer/reference.md`
10. `.github/skills/plan-reviewer/checklist.md`
11. `.github/skills/plan-reviewer/examples.md`

## Architecture-compliance Self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo positioning | fits | This is governance-only repo work inside existing local workflow surfaces |
| Local skill model | fits | `mlops-async` already carries local copies of plan-authoring and plan-review surfaces |
| Sample preservation | fits | The retained `v0.9.2` sample can stay as evidence while contracts move into workflow surfaces |
| Code / test boundary | fits with scope control | No `src/**` or `tests/**` work should be authorized in this topic |
| Release timing | fits | This topic should explicitly remain non-release and non-stable-library |
| Role separation | fits with prerequisites | Planner, creator, reviewer, and Main Agent boundaries can be expressed in existing workflow files |

## Constraints and Risks

| Issue | Type | Handling |
| --- | --- | --- |
| The sample topic is prominent in README and repo history | generalization risk | Keep a clear non-internalizable payload boundary in the analysis and plan artifacts |
| `review-log` exists in the sample | overreach risk | Encode it as conditional, not universal |
| Three-round loop exists in the sample | policy drift risk | Encode it as optional topic policy only |
| Local files may differ slightly from upstream release wording | merge risk | Align on contract meaning, not line-by-line textual identity |
| Shared governance files are edited across worktrees | coordination risk | Keep all execution for this topic inside the managed `mlops-async` worktree |

## Rollback-to-alignment Triggers

Stop later implementation and route back to planning if any of these become true:

1. a required change would touch `src/**`, `tests/**`, `README.md`, `VERSION`, or
   release/tag artifacts;
2. `mlops-async` needs an intentional divergence from the released upstream
   lifecycle contract that is not yet expressed in repo-visible analysis;
3. the local workflow body cannot stay slim without first creating a separate
   shared lifecycle reference;
4. the change starts implying a new standalone skill instead of a bounded refresh
   of existing workflow surfaces.

## Recommended Implementation Topic

- **Topic**: `correction-delta-lifecycle-contract-alignment`
- **Shape**: governance-only workflow-surface refresh
- **Not authorized in this round**: creator implementation, commit, push, PR,
  release, or sample-topic rewrites

## Final Technical Verdict

This downstream alignment is technically feasible and low-risk because it only
refreshes local governance surfaces already present in `mlops-async`. The safe
implementation shape is a bounded 11-file workflow-contract refresh, not a code
change and not a new standalone skill.
