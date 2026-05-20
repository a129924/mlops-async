> **Analysis layer — strict mode**
>
> `analysis/correction-delta-lifecycle-contract-alignment/requirements.md` and
> `analysis/correction-delta-lifecycle-contract-alignment/technical-spec.md`
> exist. This plan maps to that technical spec as the execution-facing baseline.
> Chat-time guidance may not widen or replace those artifacts without an explicit
> human `override`.

## Goal / Outcome

- Align `mlops-async` local workflow and planning surfaces with the released
  `agent-skills` `0.58.0` correction / delta lifecycle contract.
- When this topic is complete, `mlops-async` should carry the lifecycle rules in
  its local workflow surfaces instead of leaving them recoverable only from the
  `v0.9.2` sample topic and README wording.

## Scope

- **In scope**:
  - update `plan/agent-handoff-workflow.md`
  - update `.github/agents/python-implementation-workflow.agent.md`
  - update the bounded local `plan-creator` surfaces listed below
  - update the bounded local `plan-reviewer` surfaces listed below

- **Out of scope**:
  - `src/mlops_async/**`
  - `tests/**`
  - `README.md`, `VERSION`, release tags, or release notes
  - new standalone correction / delta skill extraction
  - rewriting `core-concrete-client-*` sample payload artifacts unless a later
    narrow wording-only topic explicitly authorizes it

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**. It does
  not change `README.md`, `VERSION`, release timing, or release metadata.
- The bounded source of truth is the released `agent-skills` `0.58.0`
  correction / delta lifecycle contract as frozen in:
  - `analysis/correction-delta-lifecycle-contract-alignment/requirements.md`
  - `analysis/correction-delta-lifecycle-contract-alignment/technical-spec.md`
- The workflow body must stay limited to lifecycle / routing contract only.
- Detailed correction artifact schema and long examples belong in reference /
  example surfaces, not in the workflow body.
- Parent artifacts become current truth again after accepted backfill;
  correction artifacts remain historical truth.
- `review-log` or equivalent handoff is conditional on routing-controlling
  feedback or multi-round rework; it is not universal.
- Any round cap is topic policy only and must not become repository-wide law.
- This topic does not create a new standalone skill.

## Boundaries / Exclusions

- Planning actor owns this plan and analysis artifacts only.
- Creator owns implementation strictly inside the exact artifact paths listed
  below.
- Reviewer owns the independent plan / implementation verdicts; reviewer-owned
  work must not appear inside creator `Implementation Steps`.
- Main Agent owns worktree, branch, routing, PR flow, publish routing, and
  post-merge orchestration.
- If later work requires paths outside the listed artifact contract, stop and
  repair this plan before continuing.

## Status / Allowed Transitions

- **Current**: `planned`
- **Execution model**: follow the canonical creator -> reviewer -> publish ->
  merge path; this topic stops at `merged` and declares no release action.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- Use the standard Phase 4.5 planner-alignment rule before publish.
- This topic does not declare a topic-specific round cap or mandatory
  `review-log`; if future review routing needs either one, repair the plan first
  with an exact repo-visible artifact path and policy note.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/correction-delta-lifecycle-contract-alignment/correction-delta-lifecycle-contract-alignment.plan.md` | Planning actor | Repo-visible execution contract for this alignment topic |
| Topic requirements baseline | `analysis/correction-delta-lifecycle-contract-alignment/requirements.md` | Planning actor | Frozen business baseline for the downstream governance alignment |
| Topic technical spec baseline | `analysis/correction-delta-lifecycle-contract-alignment/technical-spec.md` | Planning actor | Frozen technical baseline for the downstream governance alignment |
| Workflow contract | `plan/agent-handoff-workflow.md` | Creator | Repo-level lifecycle / routing contract that must absorb the released correction / delta rules |
| Python workflow consumer | `.github/agents/python-implementation-workflow.agent.md` | Creator | Consumer of the repo-level lifecycle contract that must stay aligned with it |
| Plan creator reference | `.github/skills/plan-creator/reference.md` | Creator | Local summary rule surface for correction lifecycle planning behavior |
| Plan creator checklist | `.github/skills/plan-creator/checklist.md` | Creator | Local authoring checks for exact paths, slim workflow body, role boundaries, and conditional `review-log` |
| Plan creator examples | `.github/skills/plan-creator/examples.md` | Creator | Local positive / negative examples for the correction lifecycle contract |
| Plan creator artifact-path rule | `.github/skills/plan-creator/references/artifact-path-rule.md` | Creator | Local exact-path rule for parent artifacts, correction artifacts, and conditional handoff artifacts |
| Plan creator role-boundary rule | `.github/skills/plan-creator/references/role-boundary-rule.md` | Creator | Local role-separation rule for planner, creator, reviewer, and Main Agent ownership |
| Plan creator topic-plan template | `.github/skills/plan-creator/templates/topic-plan-template.md` | Creator | Local topic-plan skeleton that must carry the refreshed correction-lifecycle prompts |
| Plan reviewer reference | `.github/skills/plan-reviewer/reference.md` | Creator | Local review basis for blocking correction-lifecycle contract errors |
| Plan reviewer checklist | `.github/skills/plan-reviewer/checklist.md` | Creator | Local review checks for exact paths, role ownership, conditional `review-log`, and topic policy wording |
| Plan reviewer examples | `.github/skills/plan-reviewer/examples.md` | Creator | Local approved / needs-rework examples for the refreshed lifecycle contract |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: no change in this topic.
- Treat the listed paths as an executable contract. If later work drifts into
  `src/**`, `tests/**`, release files, or `core-concrete-client-*` payload
  artifacts, stop and repair this plan first.

## Implementation Steps

1. Refresh `plan/agent-handoff-workflow.md` so the workflow body keeps only
   correction lifecycle / routing contract and makes current-truth versus
   historical-truth separation explicit.
2. Refresh `.github/agents/python-implementation-workflow.agent.md` so it stays
   a consumer of the repo-level lifecycle contract instead of becoming a
   competing owner.
3. Refresh the listed local `plan-creator` surfaces so they require:
   - exact, role-labeled artifact paths
   - slim workflow-body wording
   - parent current truth versus correction historical truth
   - conditional `review-log`
   - topic-scoped round-cap policy
   - detailed correction artifact guidance in reference / examples rather than
     the workflow body
4. Refresh the listed local `plan-reviewer` surfaces so they block:
   - vague evidence paths
   - reviewer-owned work inside creator implementation steps
   - unconditional `review-log` requirements
   - repository-wide round-cap wording
   - workflow-body bloat that embeds detailed correction schema

## Validation / Acceptance Checks

- The plan follows analysis-layer strict mode and stays inside the frozen
  technical-spec boundary.
- Only the listed workflow / planning surfaces are changed.
- `plan/agent-handoff-workflow.md` stays slim and does not become a detailed
  correction schema dump.
- Local guidance explicitly distinguishes parent current truth from correction
  historical truth.
- `review-log` stays conditional and is not universalized.
- Any round-cap wording remains topic-scoped policy.
- Creator, reviewer, planning actor, and Main Agent ownership remain separate.
- No `src/**`, `tests/**`, `README.md`, `VERSION`, or release artifacts are
  changed by this topic.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- After merge, Main Agent may perform the normal local sync flow only after an
  explicit human resume message.
- No repository release action, README update, VERSION bump, or tag action
  belongs to this topic.
- This topic is terminal at `merged`.

## Open Questions / Unresolved Items

None.
