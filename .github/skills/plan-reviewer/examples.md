# Plan Reviewer Examples

Use these examples after `SKILL.md` has already narrowed the task to reviewing a
repo-visible topic plan for this repository.

## Approved / non-stable topic

A plan that:
- lives at `plan/cache-key-auditor/cache-key-auditor.plan.md`
- includes all required sections
- uses canonical transitions
- lists exact artifact paths
- explicitly says stable-library metadata is absent
- keeps `Reviewer Handoff` as one JSON object

Typical verdict:

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Approved + ADDRESS / stable topic

A stable-library publish plan that:
- includes `## Stable library metadata`
- declares README row, VERSION bump, and timing
- keeps artifact paths exact
- is broadly correct
- but needs one direct contract fix, such as clarifying a README row position or
  adding a missing role label in `Artifact Paths`

Typical verdict:

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [
      {
        "comment": "Clarify the README row position in Stable library metadata.",
        "location": "plan/topic/topic.plan.md:140-150",
        "why": "The publish contract is usable, but the row placement should be explicit."
      }
    ],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Needs-rework / workflow-breaking

A plan that:
- skips canonical transitions
- routes `planned` directly to `review-ready`
- declares release before PR or merge
- or writes `Reviewer Handoff` as Markdown prose or a table

Typical verdict:

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Status transitions are non-canonical and skip required workflow phases.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Replace the status model with the canonical creator -> reviewer -> publish -> merge transitions."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Needs-rework / scope-or-boundary-breaking

A plan that:
- lists artifact paths as `skill folder`, `docs`, or `maybe version files`
- mixes creator, reviewer, and Main Agent duties
- implies stable-library timing without explicit metadata
- leaves `TBD` where the workflow needs a real contract

Typical verdict:

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Artifact Paths are too vague to function as an executable contract.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Replace broad labels with exact repo-visible paths and explicit role labels."
    },
    {
      "issue": "Stable-library intent is implied but not explicitly declared.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Either add Stable library metadata with timing and rationale, or explicitly state the topic is non-stable."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Anti-pattern summary

- authoring the plan instead of reviewing it
- approving a plan with vague artifact paths because "the scope sounds right"
- treating a prose note as an acceptable reviewer handoff
- downgrading real contract failures into optional suggestions

## Correction / delta lifecycle examples

### Approved / correct correction lifecycle

A plan that:
- labels parent artifact paths as current truth after accepted backfill
- labels correction artifact paths as historical truth
- conditions correction closure on parent backfill being complete
- either includes a `review-log` with reason (routing-controlling) or omits it
  with reason (routing does not depend on multi-round rework)
- declares any round cap as explicit topic policy only
- keeps creator `Implementation Steps` free of reviewer-owned tasks
- keeps detailed correction schema in reference / examples, not the workflow body

Typical verdict:

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

### Needs-rework / correction lifecycle contract violations

A plan that:
- uses vague labels like "merged implementation" or "correction folder" for
  artifact paths
- declares `review-log` as required for every review pass
- copies the three-round cap from a sample topic without declaring it as topic
  policy
- includes reviewer verdict logging inside creator `Implementation Steps`

Typical verdict:

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Correction artifact paths use vague labels instead of exact repo-visible paths.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Replace labels such as 'correction folder' with exact paths like 'plan/topic/topic.delta.md' and label each as historical truth."
    },
    {
      "issue": "review-log is declared as universally required rather than conditional.",
      "file": "plan/topic/topic.plan.md",
      "fix": "State review-log only when reviewer feedback controls routing or multi-round rework applies; otherwise omit with reason."
    },
    {
      "issue": "Round cap references a sample topic instead of declaring topic policy.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Either remove the round cap or declare it explicitly as policy for this topic only, without reference to other topics."
    },
    {
      "issue": "Creator Implementation Steps include reviewer-owned work (review-log authoring).",
      "file": "plan/topic/topic.plan.md",
      "fix": "Remove reviewer-owned tasks from creator steps. Review-log authoring belongs to the reviewer role."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```
