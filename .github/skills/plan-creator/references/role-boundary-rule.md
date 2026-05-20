# Role Boundary Rule

Rules for keeping planning actor, creator, reviewer, and main-agent roles distinct in a topic plan.

- Planning actor writes the topic plan.
- Creator implements inside the plan's locked boundaries.
- Reviewer evaluates the draft independently.
- Main Agent owns execution routing, branch preparation, planner alignment, PR flow, and post-merge orchestration.
- Do not collapse these roles into one blended author.
- Do not allow the reviewer handoff JSON to be authored by the creator; it is the reviewer's output contract, not a creator-authored narrative.
- Do not allow main-agent routing decisions (branch preparation, publish triggers, post-merge steps) to appear inside the creator or reviewer sections.

## Correction / delta topic boundaries

In topics that involve correction or delta artifacts, apply these additional role rules:

- Creator `Implementation Steps` must not contain reviewer-owned tasks. Prohibited
  examples: writing `review-log` entries, populating verdict fields, evaluating
  approval criteria, or logging reviewer acceptance decisions.
- Main Agent routing work — branch preparation, publish triggers, post-merge
  orchestration — must not appear inside creator or reviewer implementation steps.
- `python-implementation-workflow.agent.md` and similar workflow agents are
  consumers of the lifecycle contract defined in `plan/agent-handoff-workflow.md`.
  They must not re-derive, override, or independently own lifecycle routing
  decisions, including correction / delta trigger judgment and correction closure
  confirmation.
- Correction lifecycle refresh topics update existing workflow / planning surfaces
  only. Standalone correction skill extraction must be a separate topic with
  explicit justification; it is not a permitted side effect of a refresh topic.
