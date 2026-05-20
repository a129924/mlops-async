# Plan Reviewer Checklist

Use this checklist when reviewing a repo-visible topic plan before later
execution begins.

- [ ] The plan path is `plan/<topic>/<topic>.plan.md`.
- [ ] The review uses all four contract sources:
  - [ ] `plan/agent-handoff-workflow.md`
  - [ ] `.github/skills/plan-creator/reference.md`
  - [ ] `.github/skills/plan-creator/checklist.md`
  - [ ] `.github/skills/plan-creator/templates/topic-plan-template.md`
- [ ] All workflow-required plan sections are present, using the canonical section list from `plan/agent-handoff-workflow.md` (case-insensitive title matching is acceptable):
  - [ ] `Goal / outcome`
  - [ ] `Scope`
  - [ ] `Locked decisions`
  - [ ] `Boundaries / exclusions`
  - [ ] `Status / allowed transitions`
  - [ ] `Artifact paths`
  - [ ] `Implementation steps`
  - [ ] `Validation / acceptance checks`
  - [ ] `Reviewer handoff`
  - [ ] `Post-merge / release actions`
  - [ ] `Open questions / unresolved items`
- [ ] `Status / Allowed Transitions` uses canonical workflow transitions only.
- [ ] The current status matches the actual topic state.
- [ ] `Artifact Paths` are exact, bounded, repo-visible, and role-labeled.
- [ ] Stable-library intent is explicit:
  - [ ] clearly absent for non-stable topics, or
  - [ ] declared with `Stable library metadata` when stable surfaces are involved.
- [ ] `Reviewer Handoff` is one machine-consumable JSON object.
- [ ] `Post-merge / release actions` match the actual scope and timing.
- [ ] Planning actor, creator, reviewer, and Main Agent responsibilities are not mixed.
- [ ] No unsafe placeholders such as `TBD`, `later`, or `follow normal process` remain where the workflow needs an explicit contract.
- [ ] The final output is exactly one JSON verdict object with no trailing prose.
- [ ] If the topic uses correction or delta artifacts:
  - [ ] Parent artifact paths are labeled as current truth after accepted backfill and are exact repo-visible paths.
  - [ ] Correction artifact paths are labeled as historical truth and are exact repo-visible paths.
  - [ ] Correction closure is explicitly conditioned on parent sync / backfill being complete.
  - [ ] A `review-log` artifact path is present only if reviewer feedback controls routing or multi-round rework is declared; its absence is stated when relevant.
  - [ ] Any round cap wording is scoped to this topic only and does not imply a repository-wide rule.
  - [ ] Creator `Implementation Steps` contain no reviewer-owned work (no review-log authoring, no verdict logging, no acceptance evaluation).
  - [ ] The workflow body does not embed detailed correction artifact schema or long correction examples.
