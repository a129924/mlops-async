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
