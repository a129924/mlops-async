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
  - retrievable current GitHub collaborator and permission query provenance plus exact PR author identity when sole-maintainer eligibility is evaluated
  - repository full name, pull request number, latest PR head SHA, and retrievable PR-visible machine-consumable reviewer evidence
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
- retrievable current GitHub collaborator and permission query provenance when
  sole-maintainer eligibility is evaluated, including observation time,
  freshness limit, query scope, exact PR author identity, and
  permission-bearing collaborator entries
- the repository full name, pull request number, latest PR head SHA, and
  retrievable PR-visible machine-consumable reviewer evidence
- whether the change includes API or contract changes that require synced documentation
- whether an emergency marker and human confirmation exist

# Process
1. Detect release context first: normal path or emergency path.
2. Inspect the repository structure with a current-state-first rule. If version files exist, include them in the release check. If no version files exist anywhere relevant, degrade to tag-only mode.
3. If multiple version sources exist, require them to agree with each other and with the intended Git tag before release proceeds.
4. Derive the recommended bump direction from accumulated commit semantics: breaking changes outrank features, and features outrank fixes or maintenance.
5. For the normal path, select exactly one reviewer path from current repository truth:
   - **Collaborative repository**: require a qualified non-author reviewer to submit GitHub `APPROVED` for the latest PR head.
   - **Verified sole-maintainer repository**: retrieve current GitHub collaborator
     and permission query evidence, validate its repository, observation time,
     positive freshness limit, query scope, and nonempty permission-bearing
     collaborator entries. Record the exact PR author. Treat a collaborator as
     write-qualified only when its known role is `admin`, `maintain`, or
     `write`, or its boolean GitHub permissions grant `admin`, `maintain`, or
     `push`; `triage` and `read` alone are not write-qualified. Derive
     `write_qualified_maintainers` from the entries, then derive
     `qualified_non_author_reviewers` by excluding the exact PR author. The
     sole-maintainer path is eligible only when exactly one write-qualified
     maintainer remains, that login is the PR author, the derived non-author
     list is empty, and the evidence is internally consistent. Then require an
     independent Reviewer agent's structured approved evidence for the latest
     PR head exact SHA.
6. Do not infer sole-maintainer eligibility from chat, historical evidence,
   arbitrary strings, empty inventory plus a self-asserted boolean, PR-author
   claims, or a ruleset approval count of `0`. Hard-block the sole-maintainer
   path when topology evidence is unavailable, unretrievable, ambiguous, stale,
   scoped incorrectly, contradictory, contains no permission-bearing entries,
   omits the PR author, contains missing or unknown role/permission values,
   derives zero or multiple write-qualified maintainers, derives a sole
   write-qualified maintainer other than the PR author, or shows a qualified
   non-author reviewer. Use the collaborative path when a qualified non-author
   reviewer exists.
7. Require independent agent evidence to record both the Implementer and Reviewer
   canonical actor/run identities from the dispatcher execution record. Both
   identities must exist, be traceable, and be unequal. An opaque identifier
   without a dispatcher-record mapping is not sufficient. Invalidate the
   evidence whenever implementation, rework, or base synchronization changes the
   PR head SHA; review the new exact SHA before continuing.
8. Require sole-maintainer review evidence to be published in the applicable PR
   body or PR comment and then retrieved from its `evidence_url`. Verify that
   the retrieved PR-visible surface belongs to the same
   `repository_full_name` and `pull_request_number`, contains the complete
   reviewer payload, binds `reviewed_commit_sha` to the latest PR head, and has
   a valid `published_at_utc` within the applicable freshness policy. Missing,
   unretrievable, non-PR-visible, stale, or mismatched evidence is `BLOCKED`.
9. Treat repo-visible plan and step artifacts as a pre-publish `review-ready`
   snapshot. After that snapshot is committed, publish actual current PR head,
   CI, review, and conversation state only on the PR body or PR comments; do not
   write those dynamic facts back into the same commit as authoritative truth.
10. Keep the reviewer path independent from every other hard gate: actual
   latest-head `python-ci` success, conversation resolution (unresolved review
   threads exactly 0), head up-to-date with the base, base tests, strict typing,
   lint, documentation sync, version synchronization, clean workspace, and tag
   uniqueness.
11. Treat `python-type-hints-strict` and `python-testing-pytest` as release-signing inputs, not as optional suggestions.
12. If the PR changes more than one ecosystem in one release path, require linked version updates for each touched release surface instead of checking only one stack.
13. For the emergency path, allow exactly one bypass: missing pre-release reviewer evidence. Verified sole-maintainer review is a normal path, not an emergency. All other gates from the normal path still apply unchanged.
14. Require concrete emergency evidence before using the emergency path: an explicit marker such as `[emergency]` or `[skip-gate]`, a recorded human confirmation in the current workflow, a short explanation of why the path is urgent, and a release-note or equivalent anomaly record.
15. Hard-block when the target tag already exists, when the workspace is dirty, when version sources conflict, or when any non-bypassable gate fails.
16. When the gate fails, report each failed condition concretely and give repair guidance. When the gate passes, provide the safe next commands, but do not merge, tag, or push without explicit human authorization.

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
- Exactly one mutually exclusive release route is satisfied:
  - **Normal route**: exactly one normal reviewer path is satisfied:
    - collaborative repository: qualified non-author GitHub `APPROVED` for the
      latest PR head; or
    - verified sole-maintainer repository: retrievable, fresh GitHub topology
      proof with the exact PR author and nonempty permission-bearing
      collaborator entries; the explicit predicate derives exactly one
      write-qualified maintainer equal to that PR author and an empty
      `qualified_non_author_reviewers` list; plus retrievable PR-visible
      independent Reviewer agent approved evidence for the latest PR head exact
      SHA.
  - **Emergency route**: all four emergency evidence items are present and the
    only bypassed condition is missing pre-release reviewer evidence.
- On the normal route, the applicable reviewer evidence is current and any
  changed head SHA has been re-reviewed.
- On the normal sole-maintainer route, the dispatcher execution record proves
  that `implementer_run_id` and `reviewer_run_id` are present, traceable
  canonical actor/run identities and are not equal.
- On the normal sole-maintainer route, the retrieved reviewer surface belongs
  to the same repository and PR, contains the complete reviewer payload and
  valid publication timestamp, and exactly matches the latest PR head SHA.
- Repo-visible plan and step artifacts remain a pre-publish `review-ready`
  snapshot; publish-time PR head, CI, review, and conversation truth is carried
  only by PR-visible evidence.
- All non-bypassable gate signals are independently present and confirmed:
  actual latest-head `python-ci`, conversation resolution (unresolved review
  threads exactly 0), head up-to-date with base, base tests, strict type checks,
  lint, documentation sync, version sync, clean workspace, and tag uniqueness.
- All version sources agree with the intended tag
- No uncommitted changes in the workspace
- The target tag does not yet exist in the repository
- For multi-ecosystem PRs: all touched release surfaces have linked version updates
- Human merge and post-merge tag authorization remain separate decisions; reviewer evidence does not supply either authorization

## Hard-Block Conditions (BLOCKED — do not proceed)
- The target tag already exists in the repository — overwriting a tag is destructive and forbidden.
- The workspace has uncommitted changes — a dirty workspace produces an unreliable release artifact.
- Two or more version sources disagree with each other or with the intended Git tag.
- On a normal sole-maintainer route, GitHub topology provenance is unavailable,
  unretrievable, ambiguous, stale, scoped incorrectly, has empty or malformed
  permission-bearing entries, omits the exact PR author, has missing or unknown
  roles or permissions, derives anything other than exactly one
  write-qualified maintainer equal to the PR author, or contradicts its derived
  maintainer inventory, non-author reviewer list, or sole-maintainer verdict.
- On a normal route, the applicable latest-head reviewer evidence is absent,
  stale, or malformed.
- On a normal sole-maintainer route, reviewer evidence is missing,
  unretrievable, not a PR body or PR comment, lacks a valid publication
  timestamp, omits the reviewer payload, or mismatches the repository, PR, or
  latest-head SHA.
- On a normal sole-maintainer route, actor separation fails:
  `implementer_run_id` or `reviewer_run_id` is missing, unverifiable,
  opaque-only, or both identities resolve to the same actor/run.
- On an emergency route, any emergency evidence item is missing or the requested
  bypass exceeds missing pre-release reviewer evidence.
- Any non-bypassable gate is failing: actual latest-head `python-ci`,
  conversation resolution (unresolved review threads exactly 0), base
  synchronization, base tests, strict type checks, lint, documentation sync,
  version sync, clean workspace, or tag uniqueness.

## Red Flags — Treat as Immediate BLOCKED
- The user invokes `[emergency]` or `[skip-gate]` to bypass tests, a dirty workspace, or an existing tag conflict. The emergency path allows only one bypass: missing pre-release reviewer evidence. All other gates remain hard requirements.
- A ruleset approval count of `0`, a chat statement, a PR-author claim, or historical evidence is used as proof of sole-maintainer eligibility.
- An arbitrary string, empty permission-bearing inventory plus a boolean,
  self-asserted empty non-author list, or contradictory topology payload is
  used as proof of sole-maintainer eligibility.
- Independent agent review is described as GitHub `APPROVED`, or is treated as merge or tag authorization.
- Repo-local plan or step content is treated as authoritative evidence for
  publish-time PR head, CI, review, or conversation state.
- Agent evidence claims `non_live_ci_contract_verified=true` while actual latest-head `python-ci` is absent or failing.
- Version sources are present but have not been compared. Version synchronization must be confirmed before any tagging command is provided.
- A commit in the release range includes a breaking change but the proposed bump is `patch` or `minor`. Bump direction must be re-derived from accumulated commit semantics.
- The user asks for safe tagging commands before CI or type-check signals have been provided. Do not provide tag commands under incomplete signal.
- The emergency path is invoked without all four required evidence items: explicit marker, recorded human confirmation, short urgency explanation, and release-note or anomaly record.

## Required Checks Before Gate Decision
1. Confirm exactly one release route: normal or emergency.
2. Confirm version-source inventory: list all found version files; verify mutual agreement and agreement with the intended tag.
3. For the normal route, confirm the reviewer path from current GitHub
   repository truth:
   - collaborative path: qualified non-author GitHub `APPROVED` on latest head;
     or
   - verified sole-maintainer path: retrieve the GitHub collaborator and
     permission query provenance; verify repository, UTC observation time,
     positive freshness limit, query scope, and nonempty permission-bearing
     collaborator entries; verify the exact PR author and known role/permission
     values; apply the explicit write-qualified predicate; derive
     `write_qualified_maintainers`; exclude the exact PR author to derive
     `qualified_non_author_reviewers`; require exactly one write-qualified
     maintainer equal to the PR author and an empty non-author list; then
     retrieve independent Reviewer agent evidence from the PR body or PR
     comment for the latest head exact SHA.
4. For the normal route, confirm applicable reviewer-evidence freshness and
   re-review after every head-SHA change. For the sole-maintainer path, also
   confirm dispatcher-record actor linkage: `implementer_run_id` and
   `reviewer_run_id` are present, traceable canonical identities, and unequal;
   confirm the retrieved surface has the same repository and PR, complete
   reviewer payload, valid publication timestamp, and exact latest-head SHA.
5. For the emergency route, confirm the explicit marker, recorded human
   confirmation, urgency explanation, and anomaly record, and confirm that only
   missing pre-release reviewer evidence is bypassed.
6. Confirm independent hard-gate signals: actual latest-head `python-ci`,
   conversation resolution (unresolved review threads exactly 0), base
   synchronization, tests, type checks, lint, docs sync, version sync, clean
   workspace, and tag uniqueness.
7. For multi-ecosystem PRs: confirm linked version updates exist for every touched release surface.

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
- If CI, conversation resolution (unresolved review threads exactly 0),
  base-sync, test, type-check, lint, or docs-sync signal is absent: mark that
  gate as UNCONFIRMED; do not count an absent signal as PASS.
- If the user cannot supply the signal: mark the overall release decision as BLOCKED and list the missing signals explicitly.

## Sole-Maintainer Evidence Failure
- BLOCKED when GitHub collaborator or permission provenance is unavailable,
  unretrievable, ambiguous, stale, scoped incorrectly, contains no valid
  permission-bearing collaborator entries, omits the exact PR author, contains
  missing or unknown role/permission values, derives zero or multiple
  write-qualified maintainers, derives a sole write-qualified maintainer other
  than the PR author, contradicts its derived inventories or verdict, or shows
  any qualified non-author reviewer.
- Report the repository, evidence URL or API endpoint, UTC observation time,
  freshness limit, query scope, PR author, permission-entry validation result,
  write-qualified predicate, derived `write_qualified_maintainers`,
  `qualified_non_author_reviewers`, and sole-maintainer verdict when available.
  Do not copy private collaborator inventory or credentials into repo examples.
- Repair guidance: refresh retrievable GitHub topology evidence and re-derive
  both inventories and the verdict from known GitHub roles and permissions; if
  a qualified non-author reviewer exists, use the collaborative GitHub
  `APPROVED` path.

## Stale or Invalid Agent Review
- BLOCKED on the normal sole-maintainer route when `reviewed_commit_sha` differs
  from the latest PR head; when `repository_full_name`,
  `pull_request_number`, `evidence_surface`, `evidence_url`, or
  `published_at_utc` is missing or invalid; when the URL is unretrievable or
  does not resolve to the same PR body or PR comment; when the retrieved
  surface omits the complete reviewer payload; when repository, PR, SHA, or
  freshness mismatches; when the dispatcher execution record cannot verify
  both canonical `implementer_run_id` and `reviewer_run_id`; when either
  identity is opaque-only; or when both identities resolve to the same
  actor/run.
- Any implementation, rework, or base synchronization that changes the head SHA invalidates prior agent review evidence.
- Repair guidance: dispatch an independent Reviewer against the new exact
  latest PR head, publish the complete structured verdict to that PR's body or
  comment, and re-retrieve it for binding and freshness validation.

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
- Do not let an agent-review JSON field substitute for actual GitHub
  `python-ci`, conversation resolution (unresolved review threads exactly 0),
  base synchronization, or any other hard-gate evidence.
- Do not auto-tag or auto-push after repair; require user re-confirmation.

## Execution Limitation
- If git commands are unavailable or fail to execute: mark the overall gate as INCOMPLETE; list which checks could not be evaluated; do not issue a release decision.
- If version files cannot be read (permissions, encoding, missing filesystem access): report the inaccessible files; degrade to manual-confirm mode and require the user to supply version values explicitly.
- If CI or external gate signals cannot be retrieved: mark those signals as UNCONFIRMED and treat them as BLOCKED until the user provides them manually.

# Boundaries
- Do not invent missing reviewer evidence, sole-maintainer eligibility, passing test signals, or version alignment.
- Do not call independent agent review GitHub `APPROVED`.
- Do not infer sole-maintainer status from ruleset approvals `0`, chat, historical snapshots, or PR-author claims.
- Do not accept arbitrary strings, empty permission-bearing entries plus a
  self-asserted boolean, a self-asserted empty non-author inventory, stale or
  unretrievable provenance, missing PR-author identity, unknown
  role/permission values, or contradictory topology data as sole-maintainer
  proof.
- Derive `write_qualified_maintainers` only from retrievable collaborator
  entries using the explicit GitHub role/permission predicate. Derive
  `qualified_non_author_reviewers` only by excluding the exact PR author. Do
  not pass unless exactly one write-qualified maintainer exists and is the PR
  author.
- On the normal sole-maintainer route, require dispatcher-verifiable,
  non-opaque canonical Implementer and Reviewer actor/run identities; do not let
  them resolve to the same actor/run, and do not reuse review evidence after the
  PR head SHA changes.
- On the normal sole-maintainer route, require retrievable PR-visible review
  evidence bound to the same repository, PR, and exact latest head, with a
  valid publication timestamp and complete reviewer payload.
- Keep repo-visible plan and step artifacts as pre-publish `review-ready`
  snapshots; do not use them as authoritative publish-time PR-state evidence.
- Do not auto-bypass any gate except missing pre-release reviewer evidence on the explicit emergency path.
- Do not auto-bypass actual latest-head `python-ci`, conversation resolution
  (unresolved review threads exactly 0), base synchronization, tests, type
  checks, lint, documentation-sync checks, version sync, clean workspace, or tag
  uniqueness.
- Reviewer evidence never authorizes merge or tag creation. Require explicit human merge and post-merge tag authorization.
- Do not manage ordinary feature-branch naming or commit-body wording.
- Do not assume a fixed project layout when no version files exist; degrade only to tag-only mode.

# Local references
- `examples.md`: strict release scenarios, emergency examples, blocked-gate diagnostics, and repair commands
- `references/gate-contract.md`: the hard PR/release gate and the required PASS-style signals
- `references/version-sources.md`: current-state-first version-source detection and synchronization rules
- `references/version-bump-guidance.md`: bump-priority rules derived from commit semantics
- `references/emergency-path.md`: emergency marker, human-confirmation, and post-release follow-up rules
