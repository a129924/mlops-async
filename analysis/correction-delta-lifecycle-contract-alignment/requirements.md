# Correction / Delta Lifecycle Contract Alignment — Requirements

## Status

- **Status**: frozen business baseline
- **Topic**: `correction-delta-lifecycle-contract-alignment`
- **Target repo**: `mlops-async`
- **Source contract**: released `agent-skills` correction / delta lifecycle
  contract at `0.58.0`
- **This round**: analysis + plan only; no implementation authorized

## Outcome

Align `mlops-async`'s local workflow-contract surfaces with the released
correction / delta lifecycle rules already adopted in `agent-skills`, so future
planner / creator / reviewer work inside `mlops-async` uses the same contract
that the repository's `v0.9.2` sample topic already implies.

When this topic eventually completes:

1. the local workflow surfaces say the same correction-lifecycle rules as the
   released upstream contract;
2. the local sample remains repo-visible evidence rather than being promoted into
   universal process law;
3. future planners and reviewers in `mlops-async` can evaluate correction /
   delta topics without guessing from sample-only evidence.

## Actors

- **Planner / maintainer**: needs local workflow contracts that match the
  repository's accepted governance baseline.
- **Creator**: needs exact, bounded authoring rules for correction artifacts,
  parent backfill, and role-owned implementation steps.
- **Reviewer**: needs explicit review checks for path exactness, role ownership,
  `review-log` conditionality, and topic-scoped round-cap policy.
- **Main Agent**: needs routing rules that do not depend on private chat memory
  or repo-specific guesswork.

## Measurable Requirements

| ID | Requirement | Acceptance signal |
| --- | --- | --- |
| R1 | `mlops-async` local workflow surfaces must encode the released correction / delta lifecycle contract rather than leaving it implied only by `v0.9.2` sample artifacts. | The future implementation topic updates the bounded local workflow surfaces listed in the topic plan and no longer depends on sample-only wording for lifecycle semantics. |
| R2 | The workflow body must stay limited to correction lifecycle / routing contract; field-level correction artifact schema and long examples must live in reference / example surfaces. | `plan/agent-handoff-workflow.md` stays slim, while detailed correction artifact guidance appears in `plan-creator` and `plan-reviewer` reference/example surfaces. |
| R3 | Parent artifacts must be treated as execution-facing current truth after accepted backfill; correction artifacts must remain historical truth. | Local workflow and review guidance explicitly distinguishes parent current truth from correction historical truth. |
| R4 | Repo-visible `review-log` or equivalent handoff must be required only when reviewer feedback controls routing or multi-round rework. | Local plan-authoring and plan-review guidance states the condition explicitly and does not universalize `review-log` creation. |
| R5 | Any round cap must be treated as topic policy, not a repository-wide invariant. | Local guidance permits declared topic caps without turning the `v0.9.2` three-round sample into general law. |
| R6 | Execution and review evidence paths must be exact, bounded, repo-visible, and role-labeled. | Local plan-authoring and plan-review surfaces reject vague labels such as `merged implementation` or broad folder references. |
| R7 | Planner, creator, reviewer, and Main Agent ownership must remain separate. | Local guidance rejects reviewer-owned logging inside creator `Implementation Steps` and keeps routing work outside creator scope. |
| R8 | The topic must not internalize `mlops-async` domain payload as workflow law. | The future implementation topic stays inside workflow / planning surfaces only and does not modify `src/**`, `tests/**`, `README.md`, `VERSION`, or release artifacts. |

## Assumptions

- `agent-skills` `0.58.0` is the approved upstream contract baseline for this
  lifecycle behavior.
- `mlops-async` intentionally carries local copies of the relevant workflow
  surfaces instead of consuming them from a remote shared package.
- The `core-concrete-client-delta-backfill` sample remains useful evidence, but
  it should not keep acting as the only place where the lifecycle contract can be
  inferred.

## Non-goals

- No production-code or test changes under `src/mlops_async/**` or `tests/**`.
- No new standalone correction / delta skill extraction.
- No README, VERSION, tag, or release-note work in this topic.
- No rewrite of the `core-concrete-client-*` sample payload unless a later,
  separately planned wording-only follow-up proves necessary.

## Surfaced Contradictions and Decisions

1. **Sample versus contract wording**
   - Observation: `v0.9.2` already documents a retained correction / delta sample
     and backfilled parent artifacts.
   - Risk: future agents may infer universal rules from the sample because the
     local workflow surfaces are older and thinner.
   - Decision: align the workflow surfaces, not the sample payload.

2. **Review-log visibility versus overreach**
   - Observation: the sample uses a repo-visible `review-log`.
   - Risk: blindly generalizing that sample would force review logs for every
     review.
   - Decision: internalize `review-log` as a conditional rule only when routing
     or multi-round rework depends on it.

3. **Three-round sample versus repo-wide policy**
   - Observation: the sample uses a three-round creator / reviewer cap.
   - Risk: copying it everywhere would create a false universal limit.
   - Decision: preserve round caps only as explicit topic policy.

## Extreme-boundary Checks

- If future alignment work requires touching domain code, tests, or release files,
  stop and split that work into another topic.
- If `mlops-async` intentionally needs to diverge from the released upstream
  contract, surface that divergence explicitly; do not leave it as silent drift.
- If detailed correction schema cannot stay outside the workflow body, stop and
  re-evaluate whether a separate lifecycle reference is needed before
  implementation.

## Freeze Decision

This baseline is frozen for downstream technical translation. The smallest safe
next move is a governance-only topic that updates `mlops-async` local workflow
surfaces to match the released lifecycle contract while keeping the sample topic
as evidence, not as process law.
