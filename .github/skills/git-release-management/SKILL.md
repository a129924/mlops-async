---
name: git-release-management
description: Enforce a strict release gate for PR readiness, version-source synchronization, tagging safety, emergency exceptions, and release repair guidance without bypassing core quality checks.
---

# Purpose
Decide whether a change is safe to release, and provide the exact blocking reasons or safe tagging guidance.

# Trigger / When to use
Use this skill when:
- the user is preparing a PR gate, release, tag, or hotfix
- the agent detects `gh pr create`, release-tag intent, or a milestone that should trigger release checks
- the user asks whether the branch is safe to merge or tag
- a release process needs repair guidance after a failed gate

Do not use this skill when:
- the main task is drafting a commit message or naming a normal development branch
- the request is only to browse tags without judging release readiness
- the user wants to bypass core quality gates without human approval or without recording the exception

# Inputs
- the target branch, PR, tag, or release version
- the current workspace state, including whether uncommitted changes exist
- the project's current version sources such as `pyproject.toml`, `__version__.py`, or `package.json`
- the pass/fail signals from testing, strict typing, lint, CI, reviewer approval, and documentation updates
- whether the change includes API or contract changes that require synced documentation
- whether an emergency marker and human confirmation exist

# Process
1. Detect release context first: normal path or emergency path.
2. Inspect the repository structure with a current-state-first rule. If version files exist, include them in the release check. If no version files exist anywhere relevant, degrade to tag-only mode.
3. If multiple version sources exist, require them to agree with each other and with the intended Git tag before release proceeds.
4. Derive the recommended bump direction from accumulated commit semantics: breaking changes outrank features, and features outrank fixes or maintenance.
5. For the normal path, require the full gate: reviewer approval, CI green, base tests passing, strict type checks passing, lint passing, documentation updated where contracts changed, versions synchronized, a clean workspace, and no tag conflict.
6. Treat `python-type-hints-strict` and `python-testing-pytest` as release-signing inputs, not as optional suggestions.
7. If the PR changes more than one ecosystem in one release path, require linked version updates for each touched release surface instead of checking only one stack.
8. For the emergency path, allow exactly one bypass: missing pre-release reviewer approval. All other gates from the normal path still apply unchanged.
9. Require concrete emergency evidence before using the emergency path: an explicit marker such as `[emergency]` or `[skip-gate]`, a recorded human confirmation in the current workflow, a short explanation of why the path is urgent, and a release-note or equivalent anomaly record.
10. Hard-block when the target tag already exists, when the workspace is dirty, when version sources conflict, or when any non-bypassable gate fails.
11. When the gate fails, report each failed condition concretely and give repair guidance. When the gate passes, provide the safe next commands, but do not auto-tag or auto-push without confirmation.

# Examples
- Positive: Block a release until `pyproject.toml`, `__version__.py`, CI, type checks, docs, and the intended tag all align, then output the exact safe tagging commands.
- Negative: Allow `[emergency]` to skip failing tests, ignore an existing tag, or release from a dirty workspace because the change "looks small."

# Outputs
- a release decision: blocked, ready for PR, ready to tag, or emergency-path pending human confirmation
- a clear normal-path or emergency-path gate result
- explicit failed-gate diagnostics and repair guidance
- safe PR or tagging commands when the release gate is satisfied
- version-bump guidance based on commit semantics

# Boundaries
- Do not invent missing reviewer approval, passing test signals, or version alignment.
- Do not auto-bypass any gate except pre-release reviewer approval on the explicit emergency path.
- Do not auto-bypass CI, tests, type checks, lint, documentation-sync checks, version sync, clean workspace, or tag uniqueness.
- Do not manage ordinary feature-branch naming or commit-body wording.
- Do not assume a fixed project layout when no version files exist; degrade only to tag-only mode.

# Local references
- `examples.md`: strict release scenarios, emergency examples, blocked-gate diagnostics, and repair commands
- `references/gate-contract.md`: the hard PR/release gate and the required PASS-style signals
- `references/version-sources.md`: current-state-first version-source detection and synchronization rules
- `references/version-bump-guidance.md`: bump-priority rules derived from commit semantics
- `references/emergency-path.md`: emergency marker, human-confirmation, and post-release follow-up rules
