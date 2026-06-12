# Corrective Prompt For `codex-skill-projection`

You are updating the `codex-skill-projection` topic for `mlops-async`.

## Topic

- topic: `codex-skill-projection`
- source repo: `agent-skills`
- target repo: `mlops-async`

## Corrected Direction

Do not use `.codex/skills/` as the final discovery target.

This topic must treat:

- source root: `source repo/.codex/skills/<name>/`
- target root: `target repo/.agents/skills/<name>/`

`.codex/skills/` may be legal as a compatibility surface, but it is not the
discovery path for this corrected topic.

## Scope

Only process these 32 same-name skills:

- business-intent-alignment
- business-to-technical-translation
- git-branch-naming
- git-commit-convention
- git-post-merge-workflow
- git-release-management
- plan-creator
- plan-reviewer
- plan-step-tracker
- python-api-signature
- python-async-await
- python-async-planning
- python-class-design
- python-code-review
- python-context-management
- python-data-model-methods
- python-docstrings
- python-error-handling
- python-implementation-review
- python-library-architecture
- python-model-selection
- python-module-boundaries
- python-naming
- python-package-layout
- python-plan-authoring
- python-plan-review
- python-serialization-boundaries
- python-tdd-test-authoring
- python-testing-pytest
- python-type-hints-strict
- sense-env-scaffold
- worktree-manager

## Explicit Exclusions

- copilot-instructions-init
- api-client-porting-implementer
- api-client-porting-planner
- .github/agents/*
- non-same-name skills
- whole-library projection
- mlops-async/skills/*
- README.md
- VERSION
- release / publish routing

## Required Work

1. Audit each same-name skill:
   - source exists?
   - target exists?
   - is it already migrated?
   - is there a recursive diff?
2. Write the audit to
   `plan/codex-skill-projection/codex-skill-projection.audit.md`
3. Materialize missing targets under `.agents/skills/<name>/`
4. If target exists and differs, overwrite it from source and remove target-only
   drift
5. Re-run recursive verification and confirm source / target alignment
6. Update
   `plan/codex-skill-projection/codex-skill-projection.step.md`
   and
   `plan/codex-skill-projection/codex-skill-projection.checklist.md`

## Output Rule

The topic only answers:

- has this same-name skill been migrated?
- does this same-name skill have a diff?
- if there is a diff, should source overwrite target?

Do not expand scope to `.github/agents/*`, blockers, `.github/skills/*`, or
canonical `skills/*`.
