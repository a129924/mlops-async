> **Semantic warning — analysis layer absent**
>
> `analysis/core-concrete-client-delta-backfill/requirements.md` and
> `analysis/core-concrete-client-delta-backfill/technical-spec.md` do not exist.
> This topic is authored without optional analysis-layer inputs and instead uses
> the merged `core-concrete-client-minimal` parent artifacts plus the accepted
> correction / delta artifacts as bounded repo-visible context.

## Goal / Outcome

- Backfill the merged `core-concrete-client-minimal` parent artifacts so they
  encode the final accepted contract from #10 instead of leaving part of that
  contract only in correction / delta artifacts.
- When this topic is complete, the repository should preserve correction /
  delta artifacts as decision-trail history while the parent artifacts become
  the single execution-facing source of truth for the accepted final contract.

## Scope

- **In scope**:
  - Update `analysis/core-concrete-client-minimal/requirements.md` to reflect
    the accepted final contract from the merged correction / delta artifacts.
  - Update `analysis/core-concrete-client-minimal/technical-spec.md` to reflect
    the accepted final contract from the merged correction / delta artifacts.
  - Update `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md`
    so its execution contract reflects the final merged behavior.
  - Update `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md`
    so its implementation-step wording reflects the final merged contract
    without resetting completed progress.
  - Record this topic-plan review cycle in a repo-visible reviewer feedback log.

- **Out of scope**:
  - production code changes under `src/mlops_async/**`
  - test changes under `tests/**`
  - changes to `README.md`, `VERSION`, `pyproject.toml`, release tags, or release notes
  - changes to PR #11 or any skill-migration files
  - deleting, rewriting, or collapsing correction / delta artifacts into one file

## Locked Decisions

- This topic is **review-ready-only with no stable-library surfaces**. It does
  not change `README.md`, `VERSION`, release timing, or release metadata.
- No optional analysis layer exists for this topic; the bounded context is the
  already-merged `core-concrete-client-minimal` parent artifacts plus:
  - `plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-plan.md`
  - `plan/core-concrete-client-minimal/core-concrete-client-minimal.nominal-inheritance.correction-plan.md`
  - `plan/core-concrete-client-minimal/core-concrete-client-minimal.object-typehint.correction-plan.md`
- Correction / delta artifacts remain repo-visible historical records and must
  not be deleted after the parent artifacts are backfilled.
- This topic does not redesign `HttpClient`; it only backfills accepted final
  contract decisions that are already merged in #10.
- The parent artifacts must explicitly encode all accepted final-contract items
  that currently live only in correction / delta artifacts, including:
  - `HttpClient` nominally inherits `mlops_async.core.client.Client`
  - object type-hint tightening keeps justified `object` boundaries and
    tightens contract-weakening always-raise helpers
  - `NaN`, `Infinity`, and `-Infinity` count as invalid JSON success bodies for
    `request_json()`
- Creator ↔ reviewer review routing for this topic is capped at three rounds.
  If the third reviewer verdict is still `needs-rework`, stop and escalate to
  human decision instead of continuing the loop.

## Boundaries / Exclusions

- Planning actor owns this plan and the step tracker only.
- Creator owns the parent-artifact backfill strictly inside the exact paths
  listed below.
- Reviewer owns the independent plan-review verdict and the repo-visible review
  log entry for each round.
- Main Agent owns worktree / branch management, review routing, publish routing,
  and the hard stop after a third `needs-rework` verdict.
- This topic must not widen into implementation repair, code review, release
  repair, or cross-topic governance cleanup.
- If later work needs changes outside the listed artifact paths, stop and repair
  this plan before continuing.

## Status / Allowed Transitions

- **Current**: `pr-open`
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

- This topic stores reviewer verdict rounds at
  `plan/core-concrete-client-delta-backfill/core-concrete-client-delta-backfill.review-log.md`.
- Reviewer feedback may iterate at most three rounds. Reviewer verdict logging is
  reviewer / Main Agent routing work, not creator implementation work.
- If round three still ends in `needs-rework`, stop and route to explicit human
  decision.
- Use the standard Phase 4.5 planner-alignment rule before publish.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/core-concrete-client-delta-backfill/core-concrete-client-delta-backfill.plan.md` | Planning actor | Repo-visible execution contract for this backfill topic |
| Topic step tracker | `plan/core-concrete-client-delta-backfill/core-concrete-client-delta-backfill.step.md` | Planning actor -> Creator | Machine-readable step tracking for the backfill work |
| Reviewer feedback log | `plan/core-concrete-client-delta-backfill/core-concrete-client-delta-backfill.review-log.md` | Reviewer -> Main Agent | Repo-visible record of each creator/reviewer round for this topic |
| Parent requirements baseline | `analysis/core-concrete-client-minimal/requirements.md` | Creator | Backfilled business-intent guardrail for the merged #10 contract |
| Parent technical spec baseline | `analysis/core-concrete-client-minimal/technical-spec.md` | Creator | Backfilled execution-facing source of truth for the merged #10 contract |
| Parent topic plan | `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md` | Creator | Backfilled parent execution contract reflecting final accepted #10 decisions |
| Parent topic step tracker | `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md` | Creator | Backfilled step wording that matches the final accepted #10 contract without resetting progress |
| Correction evidence | `plan/core-concrete-client-minimal/core-concrete-client-minimal.correction-plan.md` | Creator / Reviewer | Read-only historical evidence for exception / transport placement drift |
| Nominal inheritance evidence | `plan/core-concrete-client-minimal/core-concrete-client-minimal.nominal-inheritance.correction-plan.md` | Creator / Reviewer | Read-only historical evidence for the nominal inheritance tightening |
| Object type-hint evidence | `plan/core-concrete-client-minimal/core-concrete-client-minimal.object-typehint.correction-plan.md` | Creator / Reviewer | Read-only historical evidence for the object type-hint tightening |
| Merged transport client implementation | `src/mlops_async/transport/http_client.py` | Creator / Reviewer | Read-only implementation evidence for the merged `HttpClient` contract that the parent artifacts must describe accurately |
| Merged transport exception implementation | `src/mlops_async/transport/exceptions.py` | Creator / Reviewer | Read-only implementation evidence for the merged transport exception hierarchy |
| Merged root exception implementation | `src/mlops_async/exceptions.py` | Creator / Reviewer | Read-only implementation evidence for the base-home-only root exception contract |
| Merged transport client tests | `tests/unit/transport/test_http_client.py` | Creator / Reviewer | Read-only evidence for merged request/raw/json, nominal inheritance, object type-hint, and invalid-JSON test coverage |
| Merged transport exception tests | `tests/unit/transport/test_exceptions.py` | Creator / Reviewer | Read-only evidence for merged exception-placement and hierarchy behavior |
| Merged client contract tests | `tests/unit/core/test_client_contract.py` | Creator / Reviewer | Read-only evidence for merged internal contract expectations and nominal inheritance proof |

Artifact path notes:

- `README.md`: no change in this topic.
- `VERSION`: no change in this topic.
- `.github/copilot-instructions.md`: no change in this topic.
- Treat the listed paths as an executable contract. If later work drifts into
  `src/**`, `tests/**`, or PR #11 skill files, stop and repair this plan first.

## Implementation Steps

1. Compare the merged `core-concrete-client-minimal` parent artifacts against
   the accepted correction / delta artifacts and the merged #10 implementation
   to build an exact backfill map of final-contract gaps.
2. Update `analysis/core-concrete-client-minimal/requirements.md` so it records
   the accepted final contract for:
   - nominal inheritance of `HttpClient`
   - object type-hint keep/tighten rules
   - `NaN`, `Infinity`, and `-Infinity` as invalid JSON success bodies
   - correction artifacts as retained decision-trail history rather than a
     replacement for parent artifacts
3. Update `analysis/core-concrete-client-minimal/technical-spec.md` so its
   traceability tables, workstreams, and constraints reflect the same accepted
   final contract from step 2.
4. Update `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md`
   so its `Current Context`, requirements, decisions, implementation steps,
   validation checks, and test-plan wording reflect the final merged contract
   rather than only the pre-correction baseline.
5. Update `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md`
   so its implementation-step wording reflects the final merged contract while
   preserving the already-completed progress state.

## Validation / Acceptance Checks

- The plan explicitly warns that no optional analysis layer exists for this
  backfill topic.
- Correction / delta artifacts remain present and unchanged as historical input
  evidence.
- `analysis/core-concrete-client-minimal/requirements.md` reflects the accepted
  final contract for nominal inheritance, object type-hint tightening, and
  non-finite JSON invalid-body handling.
- `analysis/core-concrete-client-minimal/technical-spec.md` reflects the same
  final contract without inventing new implementation scope.
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md`
  reflects the same final contract and no longer leaves those items only in
  correction / delta artifacts.
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md`
  reflects the final merged contract without resetting completed steps.
- No production code, tests, `README.md`, `VERSION`, or release artifacts are
  changed by this topic.
- Reviewer feedback stays repo-visible and the creator/reviewer loop does not
  exceed three rounds.

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
