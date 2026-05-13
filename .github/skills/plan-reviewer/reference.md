# Plan Reviewer Reference

Use this file to keep repo-visible topic-plan review aligned with the repository workflow.

## Review basis

Review topic plans against all four contract sources together:

1. `plan/agent-handoff-workflow.md`
2. `.github/skills/plan-creator/reference.md`
3. `.github/skills/plan-creator/checklist.md`
4. `.github/skills/plan-creator/templates/topic-plan-template.md`

Do not treat any one source as sufficient by itself. The workflow defines the
canonical execution contract, while `plan-creator` materials define the expected
plan shape and the common failure signals.

## What counts as blocking

Treat these as blocking issues:

- missing required sections
- invalid or non-canonical transitions
- vague or drifting `Artifact Paths`
- undeclared or mixed stable-library intent
- non-JSON reviewer handoff
- wrong post-merge or release timing
- mixed role ownership
- placeholders where the workflow needs an explicit contract

Do not raise blocking issues for tone, phrasing, or layout preferences that do
not change contract meaning.

## Workflow position

`plan-reviewer` runs after a repo-visible topic plan exists and before later
execution begins under `plan/agent-handoff-workflow.md`.

Typical operating sequence:

1. `plan-creator` authors `plan/<topic>/<topic>.plan.md`
2. Main Agent routes the plan to an independent reviewer, typically via `/fleet`
3. required fixes are applied
4. only then does branch preparation or later execution continue

This skill is a planning-contract gate. It does not replace the existing
implementation-review step in Phase 4, and it does not create a new numbered
phase by itself.

## Output rule

Return exactly one JSON object with:

- `verdict`
- `blocking_issues`
- `copilot_feedback_triage`
  - `ADDRESS`
  - `DISCUSS`
  - `SKIP`

Keep all reasoning inside structured fields. Do not append prose before or
after the JSON object.
