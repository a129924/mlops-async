# Plan creator checklist

Use this checklist when drafting or sanity-checking a topic plan before handing
it to reviewer or main-agent execution.

- [ ] The topic plan is repo-visible at `plan/<topic>/<topic>.plan.md`.
- [ ] `Goal / Outcome`, `Scope`, `Locked Decisions`, and `Boundaries / Exclusions` are explicit.
- [ ] `Status / Allowed Transitions` uses canonical workflow transitions only.
- [ ] The current status matches the actual workflow phase.
- [ ] `Artifact Paths` are exact repo-visible paths, not catch-all labels.
- [ ] Stable-library intent is explicit:
  - [ ] clearly absent for non-stable topics, or
  - [ ] declared with timing when stable-library surfaces are involved
- [ ] `Reviewer Handoff` is a single JSON object contract.
- [ ] `Post-merge / release actions` match the actual topic scope and timing.
- [ ] Planning actor, creator, reviewer, and main-agent roles are not mixed.
- [ ] No placeholder wording remains where workflow needs a real contract.
