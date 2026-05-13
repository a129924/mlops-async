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
