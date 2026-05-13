# Agent Handoff Workflow Contract

## Purpose

Define the canonical topic-plan contract used by creator/reviewer workflow gates.

## Required plan sections

Every `plan/<topic>/<topic>.plan.md` must contain these sections:

1. `Goal / Outcome`
2. `Scope`
3. `Locked Decisions`
4. `Boundaries / Exclusions`
5. `Status / Allowed Transitions`
6. `Artifact Paths`
7. `Implementation Steps`
8. `Validation / Acceptance Checks`
9. `Reviewer Handoff`
10. `Post-merge / release actions`
11. `Open Questions / Unresolved Items`

### Stable library metadata (conditional)

If a topic affects stable-library surfaces (`README.md`, `VERSION`, release timing, or release notes), add `## Stable library metadata` and declare README action, VERSION bump, timing, and rationale.

## Canonical status model

| Status | Meaning | Owner | Allowed next |
| --- | --- | --- | --- |
| `planned` | Topic plan is ready for execution routing | Planning actor | `creator-in-progress` |
| `creator-in-progress` | Creator is drafting or applying required fixes | Creator | `review-ready` |
| `review-ready` | Creator completed the latest draft and requests independent review | Creator | `reviewer-in-progress` |
| `reviewer-in-progress` | Reviewer is evaluating the latest draft | Reviewer | `approved`, `needs-rework` |
| `needs-rework` | Reviewer found blocking contract issues | Reviewer | `creator-in-progress` |
| `approved` | Reviewer accepted the draft | Reviewer -> Main Agent | `creator-in-progress`, `publish-in-progress` |
| `publish-in-progress` | Approved work is being committed/pushed and prepared for PR or direct merge | Main Agent | `pr-open`, `merged` |
| `pr-open` | PR is open and triage is active | Main Agent | `needs-rework`, `merged` |
| `merged` | Changes are merged | Main Agent | `released`, terminal |
| `released` | Optional release/version actions are complete | Main Agent | terminal |

## Allowed transitions (canonical)

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

Conditional rule:

- If `Post-merge / release actions` declares an actual release action, add `merged` -> `released`.

## Step-tracker alignment

- Canonical step file path: `plan/<topic>/<topic>.step.md`.
- Completion gate must read only `## Implementation Steps` checkboxes.
- Marker semantics: `[X]` done, `[ ]` pending (`[x]` is treated as pending).
- Status alignment:
  - keep `creator-in-progress` while any implementation step is pending or rework is active
  - move to `review-ready` only after implementation steps for the current creator pass are complete
  - if reviewer returns `needs-rework`, route back to `creator-in-progress`

## Reviewer handoff JSON contract

`Reviewer Handoff` must contain one machine-consumable JSON object with this shape:

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

## Post-merge / release rule

- Every topic plan must explicitly state post-merge behavior.
- If no release action is required, say so explicitly.
- If release is required, declare concrete release actions and ensure status transitions include `merged` -> `released`.
