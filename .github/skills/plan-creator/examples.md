# Plan creator examples

Use these examples after `SKILL.md` has already narrowed the task to repository
topic-plan authoring.

## Normal path

### Non-stable skill topic
```md
# Example topic intent
- create `.github/skills/cache-key-auditor/`
- stop at `review-ready`

## Artifact Paths
- `plan/cache-key-auditor/cache-key-auditor.plan.md`
- `.github/skills/cache-key-auditor/SKILL.md`
- `.github/skills/cache-key-auditor/reference.md`
- `.github/skills/cache-key-auditor/examples.md`

Artifact path notes:
- This topic does **not** modify `README.md`, `VERSION`, or release notes.
- `Stable library metadata` is intentionally absent because this topic is not a
  stable-library publish topic.
```

- Good because the non-stable intent is explicit and the paths are exact.

### Stable-library publish topic
```md
## Locked Decisions
- This topic updates the stable library entry for `cache-key-auditor`.

## Stable library metadata
- README row: `| cache-key-auditor | validates cache-key rules for repo-visible APIs |`
- VERSION bump: `MINOR`
- Timing: `publish-in-progress`
- Rationale: new approved stable skill enters the public library table
```

- Good because stable-library impact is declared instead of implied.

### Workflow-spec topic
```md
## Scope
- **In scope**:
  - update `plan/agent-handoff-workflow.md`
  - update `.github/guides/MAIN-AGENT-WORKFLOW.md` only if direct contradictions appear

## Artifact Paths
- `plan/workflow-spec-refresh/workflow-spec-refresh.plan.md`
- `plan/agent-handoff-workflow.md`
- `.github/guides/MAIN-AGENT-WORKFLOW.md`
```

- Good because the topic stays process-focused and bounds the coupled files.

### Small wording-only topic
```md
## Scope
- **In scope**:
  - clarify one misleading sentence in `.github/skills/foo/SKILL.md`

## Artifact Paths
- `plan/foo-wording-fix/foo-wording-fix.plan.md`
- `.github/skills/foo/SKILL.md`
```

- Good because the plan stays small instead of pretending the topic is broader.

## Anti-patterns

### Mixed stable-library intent
```md
## Post-merge / release actions
- maybe update `README.md` and `VERSION` if this feels stable enough later
```

- Bad because stable-library timing is implied but not declared.

### Vague artifact paths
```md
## Artifact Paths
- skill folder
- docs
- maybe version files
```

- Bad because no one can reliably validate drift against vague path labels.

### Wrong reviewer handoff format
```md
## Reviewer Handoff
| Issue | Severity | Notes |
| --- | --- | --- |
| Missing examples | high | please add more |
```

- Bad because workflow requires a machine-consumable JSON object.

### Wrong phase timing
```md
## Post-merge / release actions
- after approval, release the change and then open a PR
```

- Bad because approval, PR, merge, and release are distinct workflow phases.

### Invalid status model or transition
```md
## Status / Allowed Transitions
- **Current**: `planned`
- **Allowed transitions**:
  - `planned` -> `review-ready`
  - `review-ready` -> `approved`
  - `approved` -> `merged`
```

- Bad because it skips required workflow phases, invents an impossible direct
  approval path, and does not preserve the canonical creator -> reviewer ->
  publish sequence required by the repository contract.

### Role-boundary confusion
```md
## Locked Decisions
- reviewer will finish any missing creator work during approval
```

- Bad because reviewer and creator are separate roles.

## Correction / delta lifecycle

### Correction topic with correct path labeling and conditional handoff
```md
## Locked Decisions
- This topic is non-stable-library (no README, VERSION, or release action).
- Parent artifacts become current truth after accepted backfill; correction closure
  requires that backfill is complete before this topic is declared done.
- Correction artifacts are retained as historical truth only.
- No topic-specific round cap is declared for this topic.

## Artifact Paths
| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/foo-correction/foo-correction.plan.md` | Planning actor | Repo-visible execution contract |
| Parent plan (backfilled) | `plan/foo/foo.plan.md` | Creator | Current truth after accepted backfill |
| Correction delta | `plan/foo-correction/foo-correction.delta.md` | Creator | Historical truth — decision trail only; not active contract |

Routing notes:
- No `review-log` is required; routing does not depend on multi-round rework.
```

- Good because parent / correction truth separation is explicit, backfill closure
  is declared, `review-log` absence is stated with reason, and round cap is absent
  (not borrowed from a sample topic).

### Correction topic with conditional review-log and topic-scoped round cap
```md
## Locked Decisions
- Round cap for this topic: maximum 2 creator / reviewer rounds.
- A repo-visible `review-log` is required because reviewer feedback controls
  routing between round 1 and round 2.

## Artifact Paths
| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/bar-correction/bar-correction.plan.md` | Planning actor | Repo-visible execution contract |
| Parent spec (backfilled) | `plan/bar/bar.spec.md` | Creator | Current truth after accepted backfill |
| Correction delta | `plan/bar-correction/bar-correction.delta.md` | Creator | Historical truth — decision trail only |
| Review log | `plan/bar-correction/bar-correction.review-log.md` | Reviewer | Round-routing handoff; required because feedback controls routing |
```

- Good because the round cap is topic policy only, the `review-log` is conditional
  with reason stated, and all paths are exact and role-labeled.

### Anti-patterns for correction lifecycle

#### Round cap copied from sample as universal rule
```md
## Locked Decisions
- Round cap: maximum 3 creator / reviewer rounds (same as the
  core-concrete-client-delta-backfill sample).
```

- Bad because the round cap is justified by reference to a sample topic, not by
  this topic's own policy need; this implies a repository-wide rule.

#### Unconditional review-log requirement
```md
## Locked Decisions
- A `review-log` must be created after every review pass.
```

- Bad because `review-log` is conditional on routing control or multi-round
  rework; universal `review-log` requirements are not permitted.

#### Vague correction evidence labels
```md
## Artifact Paths
- merged implementation
- correction backfill folder
- review artifacts
```

- Bad because no one can validate drift against vague path labels; correction
  artifact paths must be exact, bounded, repo-visible, and role-labeled.

#### Workflow body embedding correction schema
```md
## Correction artifact schema
| Field | Type | Description |
| --- | --- | --- |
| delta_id | string | unique correction ID |
| base_sha | string | parent commit SHA |
```

- Bad because detailed correction artifact schema belongs in reference / examples
  surfaces, not in the workflow body.
