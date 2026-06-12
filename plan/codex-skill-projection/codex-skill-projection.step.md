# Codex Skill Projection Workflow Steps

## Implementation Steps

- [X] Freeze the 32-skill same-name scope and exclusion set in the analysis layer.
- [X] Rewrite the analysis, plan, step, checklist, and audit artifacts to the
  `.agents/skills/` target model.
- [X] Create or update `AGENTS.md` to declare `.agents/skills/` as the repo-local
  discovery surface.
- [X] Create `plan/codex-skill-projection/codex-skill-projection.corrective-prompt.md`.
- [X] Audit source existence for all 32 names under `source repo/.codex/skills/`.
- [X] Audit target existence for all 32 names under `.agents/skills/`.
- [X] Create or refresh `plan/codex-skill-projection/codex-skill-projection.audit.md`
  against the `.agents/skills/` target.
- [X] Create missing target skill roots for the frozen 32 names under
  `.agents/skills/`.
- [X] Remove topic-managed `.codex/skills/<name>` copies from the branch.
- [X] Re-run recursive verification and confirm all 32 target skill roots under
  `.agents/skills/` align with source.
- [X] Update `plan/codex-skill-projection/codex-skill-projection.checklist.md`
  and this step tracker to reflect completed creator work.
- [ ] Run reviewer verification for target alignment, `AGENTS.md`, and audit
  accuracy.
- [ ] Run planner final gate and stop at wait-human-check.

## Workflow Stages

These stage markers are informational only. Completion gates must read only
`## Implementation Steps`.

- [X] Analysis rewrite
- [X] Discovery-contract and migration execution
- [ ] Reviewer gate
- [ ] Planner final gate
- [ ] Human check
