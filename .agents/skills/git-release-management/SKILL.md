---
name: git-release-management
description: Enforce a strict release gate for PR readiness, version-source synchronization, tagging safety, emergency exceptions, and release repair guidance without bypassing core quality checks.
complexity: high
risk_profile:
  - destructive_action
  - ambiguity_sensitive
  - external_tooling
inputs:
  - target branch, PR, tag, or release version
  - current workspace state including whether uncommitted changes exist
  - project version sources such as pyproject.toml, __version__.py, or package.json
  - pass/fail signals from testing, strict typing, lint, CI, the applicable normal reviewer path, and documentation updates
  - current GitHub repository permission and collaborator evidence when sole-maintainer eligibility is evaluated
  - latest PR head SHA and machine-consumable reviewer evidence
  - whether the change includes API or contract changes that require synced documentation
  - whether an emergency marker and human confirmation exist
outputs:
  - release decision — blocked, ready for PR, ready to tag, or emergency-path pending human confirmation
  - normal-path or emergency-path gate result with explicit failed-gate diagnostics
  - repair guidance for each failed gate condition
  - safe PR or tagging commands when all gates are satisfied
  - version-bump guidance based on commit semantics
use_when:
  - preparing a PR gate, release, tag, or hotfix
  - the agent detects gh pr create, release-tag intent, or a milestone that should trigger release checks
  - the user asks whether the branch is safe to merge or tag
  - a release process needs repair guidance after a failed gate
do_not_use_when:
  - the main task is drafting a commit message or naming a normal development branch
  - the request is only to browse tags without judging release readiness
  - the user wants to bypass core quality gates without human approval or without recording the exception
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
- the pass/fail signals from testing, strict typing, lint, CI, the applicable normal reviewer path, and documentation updates
- current GitHub repository permission and collaborator evidence when sole-maintainer eligibility is evaluated
- the latest PR head SHA and machine-consumable reviewer evidence
- whether the change includes API or contract changes that require synced documentation
- whether an emergency marker and human confirmation exist

# Process
1. Detect release context first: normal path or emergency path.
2. Inspect the repository structure with a current-state-first rule. If version files exist, include them in the release check. If no version files exist anywhere relevant, degrade to tag-only mode.
3. If multiple version sources exist, require them to agree with each other and with the intended Git tag before release proceeds.
4. Derive the recommended bump direction from accumulated commit semantics: breaking changes outrank features, and features outrank fixes or maintenance.
5. For the normal path, select exactly one reviewer path from current repository truth:
   - **Collaborative repository**: require a qualified non-author reviewer to submit GitHub `APPROVED` for the latest PR head.
   - **Verified sole-maintainer repository**: require current GitHub repository permission and collaborator evidence proving that the qualified non-author reviewer inventory is empty, then require an independent Reviewer agent's structured approved evidence for the latest PR head exact SHA.
6. Do not infer sole-maintainer eligibility from chat, historical evidence, PR-author claims, or a ruleset approval count of `0`. If current GitHub topology evidence is unavailable, ambiguous, stale, or shows a qualified non-author reviewer, hard-block the sole-maintainer path.
7. Require the independent Reviewer agent to be separate from the Implementer. Invalidate its evidence whenever implementation, rework, or base synchronization changes the PR head SHA; review the new exact SHA before continuing.
8. Keep the reviewer path independent from every other hard gate: actual latest-head `python-ci` success, unresolved review threads equal to `0`, head up-to-date with the base, base tests, strict typing, lint, documentation sync, version synchronization, clean workspace, and tag uniqueness.
9. Treat `python-type-hints-strict` and `python-testing-pytest` as release-signing inputs, not as optional suggestions.
10. If the PR changes more than one ecosystem in one release path, require linked version updates for each touched release surface instead of checking only one stack.
11. For the emergency path, allow exactly one bypass: missing pre-release reviewer evidence. Verified sole-maintainer review is a normal path, not an emergency. All other gates from the normal path still apply unchanged.
12. Require concrete emergency evidence before using the emergency path: an explicit marker such as `[emergency]` or `[skip-gate]`, a recorded human confirmation in the current workflow, a short explanation of why the path is urgent, and a release-note or equivalent anomaly record.
13. Hard-block when the target tag already exists, when the workspace is dirty, when version sources conflict, or when any non-bypassable gate fails.
14. When the gate fails, report each failed condition concretely and give repair guidance. When the gate passes, provide the safe next commands, but do not merge, tag, or push without explicit human authorization.

# Examples

- **Positive**: Block a release until `pyproject.toml`, `__version__.py`, CI, type checks, docs, and the intended tag all align, then output the exact safe tagging commands.
- **Negative**: Allow `[emergency]` to skip failing tests, ignore an existing tag, or release from a dirty workspace because the change "looks small."

# Outputs
- a release decision: blocked, ready for PR, ready to tag, or emergency-path pending human confirmation
- a clear normal-path or emergency-path gate result
- explicit failed-gate diagnostics and repair guidance
- safe PR or tagging commands when the release gate is satisfied
- version-bump guidance based on commit semantics

# Validation

## PASS (all gates satisfied — safe to provide tagging commands)
All of the following must be confirmed positive:
- Exactly one normal reviewer path is satisfied:
  - collaborative repository: qualified non-author GitHub `APPROVED` for the latest PR head; or
  - verified sole-maintainer repository: current topology proof and independent Reviewer agent approved evidence for the latest PR head exact SHA
- The reviewer evidence is current, the Reviewer is independent from the Implementer, and any changed head SHA has been re-reviewed
- All other required gate signals are independently present and confirmed: actual latest-head `python-ci`, unresolved review threads exactly `0`, head up-to-date with base, base tests, strict type checks, lint, documentation sync, version sync, clean workspace, and tag uniqueness
- All version sources agree with the intended tag
- No uncommitted changes in the workspace
- The target tag does not yet exist in the repository
- For multi-ecosystem PRs: all touched release surfaces have linked version updates
- Human merge and post-merge tag authorization remain separate decisions; reviewer evidence does not supply either authorization

## Hard-Block Conditions (BLOCKED — do not proceed)
- The target tag already exists in the repository — overwriting a tag is destructive and forbidden.
- The workspace has uncommitted changes — a dirty workspace produces an unreliable release artifact.
- Two or more version sources disagree with each other or with the intended Git tag.
- Current GitHub topology evidence is unavailable, ambiguous, stale, or inconsistent with the selected reviewer path.
- The latest-head reviewer evidence is absent, stale, malformed, or produced by the Implementer.
- Any non-bypassable gate is failing: actual latest-head `python-ci`, conversation resolution, base synchronization, base tests, strict type checks, lint, documentation sync, version sync, clean workspace, or tag uniqueness.

## Red Flags — Treat as Immediate BLOCKED
- The user invokes `[emergency]` or `[skip-gate]` to bypass tests, a dirty workspace, or an existing tag conflict. The emergency path allows only one bypass: missing pre-release reviewer evidence. All other gates remain hard requirements.
- A ruleset approval count of `0`, a chat statement, a PR-author claim, or historical evidence is used as proof of sole-maintainer eligibility.
- Independent agent review is described as GitHub `APPROVED`, or is treated as merge or tag authorization.
- Agent evidence claims `non_live_ci_contract_verified=true` while actual latest-head `python-ci` is absent or failing.
- Version sources are present but have not been compared. Version synchronization must be confirmed before any tagging command is provided.
- A commit in the release range includes a breaking change but the proposed bump is `patch` or `minor`. Bump direction must be re-derived from accumulated commit semantics.
- The user asks for safe tagging commands before CI or type-check signals have been provided. Do not provide tag commands under incomplete signal.
- The emergency path is invoked without all four required evidence items: explicit marker, recorded human confirmation, short urgency explanation, and release-note or anomaly record.

## Required Checks Before Gate Decision
1. Confirm release path: normal or emergency.
2. Confirm version-source inventory: list all found version files; verify mutual agreement and agreement with the intended tag.
3. Confirm the normal reviewer path from current GitHub repository truth:
   - collaborative path: qualified non-author GitHub `APPROVED` on latest head; or
   - verified sole-maintainer path: current topology evidence plus independent Reviewer agent evidence on the latest head exact SHA.
4. Confirm evidence freshness, Reviewer/Implementer separation, and re-review after every head-SHA change.
5. Confirm independent hard-gate signals: actual latest-head `python-ci`, unresolved threads exactly `0`, base synchronization, tests, type checks, lint, docs sync, version sync, clean workspace, and tag uniqueness.
6. For multi-ecosystem PRs: confirm linked version updates exist for every touched release surface.

## On Soft Fail (SOFT FAIL — proceed with explicit limitation)
- A version file is absent entirely — degrade to tag-only mode; state the degradation explicitly before continuing.
- A gate signal is ambiguous or unconfirmed — list it as UNCONFIRMED and require the user to confirm before providing safe tagging commands.

## Quality Checks (best effort — SOFT FAIL if absent)
- A release-note or changelog entry exists for the intended version.
- PR description or commit messages reference the version bump rationale.
- Commit messages in the release range follow semantic-commit conventions (feat/fix/chore/etc.).
- Migration notes are present when any breaking change is included in the release range.

# Failure Handling

## Existing Tag Conflict
- BLOCKED — hard stop; do not provide tagging commands.
- Report the exact tag name and the commit it currently points to.
- Repair guidance: create a new tag with an incremented patch or pre-release suffix; do not delete or move the existing tag without explicit human decision and a documented reason.

## Dirty Workspace
- BLOCKED — hard stop; do not provide tagging or push commands.
- Repair guidance: `git status` to list changes; `git stash` or `git commit` to clean the workspace before proceeding.

## Version Source Conflict
- BLOCKED — halt gate evaluation; do not produce a release decision until all version sources agree.
- Report each conflicting file and its current value.
- Repair guidance: update the lagging sources to match the intended release version, then re-run the gate.

## Missing or Ambiguous Gate Signals
- If current GitHub topology evidence cannot establish the applicable reviewer path: mark the reviewer gate BLOCKED. Do not infer sole-maintainer status from chat, history, or ruleset configuration.
- If collaborative-path GitHub `APPROVED` or verified sole-maintainer agent evidence is missing, malformed, or stale: mark the reviewer gate BLOCKED and identify the exact missing or stale evidence.
- If CI, conversation-resolution, base-sync, test, type-check, lint, or docs-sync signal is absent: mark that gate as UNCONFIRMED; do not count an absent signal as PASS.
- If the user cannot supply the signal: mark the overall release decision as BLOCKED and list the missing signals explicitly.

## Sole-Maintainer Evidence Failure
- BLOCKED when current GitHub repository permission and collaborator evidence is unavailable, ambiguous, stale, or shows any qualified non-author reviewer.
- Report the evidence source, observation time, PR author, write-qualified maintainer inventory, and qualified non-author reviewer inventory when available.
- Repair guidance: refresh current GitHub topology evidence; if a qualified non-author reviewer exists, use the collaborative GitHub `APPROVED` path.

## Stale or Invalid Agent Review
- BLOCKED when `reviewed_commit_sha` differs from the latest PR head, the reviewer run/session identifier is absent, required structured fields are missing, or Reviewer and Implementer are not separate.
- Any implementation, rework, or base synchronization that changes the head SHA invalidates prior agent review evidence.
- Repair guidance: dispatch an independent Reviewer against the new exact latest PR head and record a fresh structured verdict.

## Emergency Path Misuse
- If the emergency path is invoked but any required evidence item is missing: BLOCKED — do not allow the bypass.
- Report which evidence items are absent.
- Repair guidance: supply the missing evidence or revert to the normal path.
- Do not route verified sole-maintainer review through emergency; it is a normal reviewer path.

## Multi-Ecosystem Missing Version Update
- BLOCKED for the affected release surface — flag each ecosystem whose version file was not updated.
- Repair guidance: update each lagging version file and re-run the gate.

## Failed Normal-Gate Condition
- Report each failed condition with its current value and the required value.
- Provide targeted repair commands for each failure (e.g., `git stash`, bump command, lint fix reference).
- Do not let an agent-review JSON field substitute for actual GitHub `python-ci`, conversation resolution, base synchronization, or any other hard-gate evidence.
- Do not auto-tag or auto-push after repair; require user re-confirmation.

## Execution Limitation
- If git commands are unavailable or fail to execute: mark the overall gate as INCOMPLETE; list which checks could not be evaluated; do not issue a release decision.
- If version files cannot be read (permissions, encoding, missing filesystem access): report the inaccessible files; degrade to manual-confirm mode and require the user to supply version values explicitly.
- If CI or external gate signals cannot be retrieved: mark those signals as UNCONFIRMED and treat them as BLOCKED until the user provides them manually.

# Boundaries
- Do not invent missing reviewer evidence, sole-maintainer eligibility, passing test signals, or version alignment.
- Do not call independent agent review GitHub `APPROVED`.
- Do not infer sole-maintainer status from ruleset approvals `0`, chat, historical snapshots, or PR-author claims.
- Do not let Reviewer and Implementer be the same actor, and do not reuse review evidence after the PR head SHA changes.
- Do not auto-bypass any gate except missing pre-release reviewer evidence on the explicit emergency path.
- Do not auto-bypass actual latest-head `python-ci`, conversation resolution, base synchronization, tests, type checks, lint, documentation-sync checks, version sync, clean workspace, or tag uniqueness.
- Reviewer evidence never authorizes merge or tag creation. Require explicit human merge and post-merge tag authorization.
- Do not manage ordinary feature-branch naming or commit-body wording.
- Do not assume a fixed project layout when no version files exist; degrade only to tag-only mode.

# Local references
- `examples.md`: strict release scenarios, emergency examples, blocked-gate diagnostics, and repair commands
- `references/gate-contract.md`: the hard PR/release gate and the required PASS-style signals
- `references/version-sources.md`: current-state-first version-source detection and synchronization rules
- `references/version-bump-guidance.md`: bump-priority rules derived from commit semantics
- `references/emergency-path.md`: emergency marker, human-confirmation, and post-release follow-up rules
