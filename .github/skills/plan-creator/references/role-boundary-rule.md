# Role Boundary Rule

Rules for keeping planning actor, creator, reviewer, and main-agent roles distinct in a topic plan.

- Planning actor writes the topic plan.
- Creator implements inside the plan's locked boundaries.
- Reviewer evaluates the draft independently.
- Main Agent owns execution routing, branch preparation, planner alignment, PR flow, and post-merge orchestration.
- Do not collapse these roles into one blended author.
- Do not allow the reviewer handoff JSON to be authored by the creator; it is the reviewer's output contract, not a creator-authored narrative.
- Do not allow main-agent routing decisions (branch preparation, publish triggers, post-merge steps) to appear inside the creator or reviewer sections.
