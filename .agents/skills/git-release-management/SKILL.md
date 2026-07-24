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
  - retrievable current GitHub collaborator and permission query provenance with complete pagination plus exact PR author identity when sole-maintainer eligibility is evaluated
  - repository full name, pull request number, latest PR head SHA, and a retrievable allowlisted external GitHub App or bot review object
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
  policy-owned `review_freshness_max_age_seconds=3600`, evidence
  `freshness_max_age_seconds=3600`, query scope exact
  `repository-wide permission-bearing collaborator population`, complete page
  or cursor traversal, exact PR author identity, and permission-bearing
  collaborator entries
- the repository full name, pull request number, latest PR head SHA, and
  retrievable allowlisted external GitHub App or bot review object
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
     policy-owned exact 3600-second freshness maximum, evidence freshness value
     exact 3600, query scope exact
     `repository-wide permission-bearing collaborator population`, and complete
     page-number or cursor traversal through the authoritative
     terminal-next-absent signal. The observation timestamp must exist, must not
     be in the future, and must have age from 0 through 3600 seconds inclusive
     at evaluation time. Record the exact PR author. Deduplicate a repeated
     login only when its role and permissions are identical on every page;
     contradictory duplicates are `BLOCKED`. Only after pagination is proven
     complete, treat a collaborator as write-qualified when its known role is
     `admin`, `maintain`, or `write`, or its boolean GitHub permissions grant
     `admin`, `maintain`, or `push`; `triage` and `read` alone are not
     write-qualified. Derive `write_qualified_maintainers` from the complete
     deduplicated inventory, then derive `qualified_non_author_reviewers` by
     excluding the exact PR author. The sole-maintainer path is eligible only
     when exactly one write-qualified maintainer remains, that login is the PR
     author, the derived non-author list is empty, and the evidence is
     internally consistent.
6. Do not infer sole-maintainer eligibility from chat, historical evidence,
   arbitrary strings, empty inventory plus a self-asserted boolean, PR-author
   claims, or a ruleset approval count of `0`. Hard-block the sole-maintainer
   path when topology evidence is unavailable, unretrievable, ambiguous, stale,
   scoped incorrectly, uses PR participants, known maintainers, one team, or
   any caller-selected or partial sample instead of the repository-wide
   permission-bearing collaborator population, incompletely paginated,
   truncated, contradictory,
   contains a failed page, repeats a cursor, lacks authoritative terminal-next
   evidence, has page-count or total mismatch, contains no permission-bearing
   entries, omits the PR author, contains missing or unknown role/permission
   values, derives zero or multiple write-qualified maintainers, derives a sole
   write-qualified maintainer other than the PR author, or shows a qualified
   non-author reviewer. Use the collaborative path when a qualified non-author
   reviewer exists.
7. On the verified sole-maintainer path, require an API-retrievable GitHub review
   object submitted by the allowlisted external reviewer
   `chatgpt-codex-connector[bot]` with actor `type` exactly `Bot`. The canonical
   reviewer login must differ from the exact PR author. The object must bind the
   same repository and PR, positive review id, retrievable review URL, valid
   submission UTC, valid evaluation UTC, policy-owned
   `review_freshness_max_age_seconds=3600`, exact latest PR head SHA, actual
   GitHub review state, and exact review body. The review age is
   `evaluated_at_utc - submitted_at_utc` and must be from 0 through 3600 seconds
   inclusive. The body must machine-parse to semantic verdict `approved` and
   `blocking_issues=[]`.
8. Preserve the API object's actual `github_review_state` literally and allow
   only exact `COMMENTED` or `APPROVED`. An actual `COMMENTED` review remains
   `COMMENTED` and must never be described as GitHub `APPROVED`; Option A relies
   on the parseable semantic verdict in the body, not on a fabricated GitHub
   approval state. `CHANGES_REQUESTED`, `DISMISSED`, every other unallowlisted
   state, and a missing state are `BLOCKED` even when the body says approved.
   A wrong or non-bot actor, PR-author actor, mismatched repository, PR, review
   id, URL, timestamp, SHA, state, or body, missing or future timestamp,
   evidence-supplied freshness override, age above 3600 seconds, missing
   semantic verdict, nonempty blockers, stale or unretrievable object is
   `BLOCKED`. A PR-author body or comment that repeats the same JSON is not a
   GitHub review object and cannot qualify.
   Any implementation, rework, or base synchronization that changes the PR
   head invalidates the prior object and requires a new review of the new exact
   SHA.
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
    - verified sole-maintainer repository: retrievable GitHub topology proof
      whose policy and evidence freshness maximums are both exact 3600 seconds,
      whose query covers the repository-wide permission-bearing collaborator
      population, and whose complete pagination yields the exact PR author and
      a nonempty, consistently deduplicated permission-bearing collaborator
      inventory; the explicit predicate derives exactly one write-qualified
      maintainer equal to that PR author and an empty
      `qualified_non_author_reviewers` list; plus an API-retrievable review
      object from allowlisted
      `chatgpt-codex-connector[bot]` with `type=Bot`, a reviewer login different
      from the PR author, actual state exact `COMMENTED` or `APPROVED`, age from
      0 through 3600 seconds inclusive, and a body whose semantic verdict is
      `approved` with `blocking_issues=[]` for the latest PR head exact SHA.
  - **Emergency route**: all four emergency evidence items are present and the
    only bypassed condition is missing pre-release reviewer evidence.
- On the normal route, the applicable reviewer evidence is current and any
  changed head SHA has been re-reviewed.
- On the normal sole-maintainer route, every topology page was retrieved through
  authoritative terminal-next absence; page counts, totals, cursors, and
  consistent cross-page deduplication have been validated before deriving the
  maintainer inventories or verdict. The query scope is exact
  `repository-wide permission-bearing collaborator population`; PR
  participants, known maintainers, a team, or another partial sample do not
  qualify.
- On the normal sole-maintainer route, the retrieved GitHub review object
  belongs to the same repository and PR, contains the allowlisted non-author
  `Bot` actor, positive review id, review URL, exact body, valid submission and
  evaluation timestamps, policy-owned exact 3600-second freshness maximum,
  literal actual GitHub state exact `COMMENTED` or `APPROVED`, review age from
  0 through 3600 seconds inclusive, and exact latest-head SHA.
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
  unretrievable, ambiguous, stale, has a missing or future observation
  timestamp, does not use policy and evidence freshness values both exact
  `3600`, is scoped to anything other than the repository-wide
  permission-bearing collaborator population, uses PR participants, known
  maintainers, one team, or another partial sample, has empty or malformed
  permission-bearing entries, has unknown or incomplete pagination, a failed
  page, cursor loop, truncation, missing terminal-next-absent evidence,
  page-count or total mismatch, contradictory duplicate logins, omits the exact
  PR author, has missing or unknown roles or permissions, derives anything
  other than exactly one write-qualified maintainer equal to the PR author, or
  contradicts its derived maintainer inventory, non-author reviewer list, or
  sole-maintainer verdict.
- On a normal route, the applicable latest-head reviewer evidence is absent,
  stale, or malformed.
- On a normal sole-maintainer route, reviewer evidence is missing,
  unretrievable, not a GitHub review object, submitted by an actor outside the
  exact allowlist or whose `type` is not `Bot`, submitted by the PR author,
  lacks a positive review id, retrievable review URL, valid submission
  timestamp, valid evaluation timestamp, policy-owned exact 3600-second
  freshness maximum, exact body, literal actual GitHub state exact `COMMENTED`
  or `APPROVED`, semantic verdict `approved`, or empty `blocking_issues`; has a
  missing or future timestamp, negative or greater-than-3600-second age,
  evidence-supplied freshness override, `CHANGES_REQUESTED`, `DISMISSED`, a
  missing or other unallowlisted state; or mismatches the repository, PR, or
  latest-head SHA.
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
- An actual GitHub `COMMENTED` review is described as GitHub `APPROVED`;
  `CHANGES_REQUESTED`, `DISMISSED`, a missing state, or another unallowlisted
  state is accepted because its body says approved; or any reviewer evidence is
  treated as merge or tag authorization.
- A local Reviewer result is used as authoritative gate evidence instead of
  being labeled `preflight_only=true`, or is mapped to a GitHub actor, review,
  or approval.
- A PR-author body or comment carrying the same JSON is accepted as the
  allowlisted external GitHub App or bot review object.
- Repo-local plan or step content is treated as authoritative evidence for
  publish-time PR head, CI, review, or conversation state.
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
     policy-owned `review_freshness_max_age_seconds=3600`, evidence
     `freshness_max_age_seconds=3600`, timestamp age from 0 through 3600 seconds
     inclusive, query scope exact
     `repository-wide permission-bearing collaborator population`, pagination
     strategy, per-page or initial cursor, page count, total retrieved,
     deduplicated total entries, every page evidence URL, request and next
     value, next evidence, and authoritative terminal-next absence. Reject PR
     participants, known maintainers, a team, or any other caller-selected or
     partial population. Require every page to succeed and reject loops,
     truncation, or count mismatch. Deduplicate repeated logins only when role
     and permissions are identical; require total entries to match the
     resulting complete inventory; verify the exact PR author and known
     role/permission values from that inventory; apply the explicit
     write-qualified predicate;
     derive `write_qualified_maintainers`; exclude the exact PR author to derive
     `qualified_non_author_reviewers`; require exactly one write-qualified
     maintainer equal to the PR author and an empty non-author list; then
     retrieve the allowlisted external GitHub App or bot review object for the
     latest head exact SHA.
4. For the normal route, confirm applicable reviewer-evidence freshness and
   re-review after every implementation, rework, or base-sync head-SHA change.
   For the sole-maintainer path, confirm the API-retrieved object has the same
   repository and PR, positive review id, retrievable review URL, allowlisted
   canonical reviewer `chatgpt-codex-connector[bot]`, actor `type=Bot`, reviewer
   login different from the exact PR author, valid submission and evaluation
   UTC, policy-owned `review_freshness_max_age_seconds=3600`, review age from 0
   through 3600 seconds inclusive, exact latest-head SHA, literal actual GitHub
   review state exact `COMMENTED` or `APPROVED`, and exact body that parses to
   semantic verdict `approved` with `blocking_issues=[]`. An actual `COMMENTED`
   state must remain `COMMENTED`; `CHANGES_REQUESTED`, `DISMISSED`, a missing
   state, and every other unallowlisted state are `BLOCKED`; a PR body or
   comment is not a qualifying review object.
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
- If collaborative-path GitHub `APPROVED` or the verified sole-maintainer
  allowlisted external GitHub review object is missing, malformed, or stale:
  mark the reviewer gate BLOCKED and identify the exact missing or stale
  evidence.
- If CI, conversation resolution (unresolved review threads exactly 0),
  base-sync, test, type-check, lint, or docs-sync signal is absent: mark that
  gate as UNCONFIRMED; do not count an absent signal as PASS.
- If the user cannot supply the signal: mark the overall release decision as BLOCKED and list the missing signals explicitly.

## Sole-Maintainer Evidence Failure
- BLOCKED when GitHub collaborator or permission provenance is unavailable,
  unretrievable, ambiguous, stale, has a missing or future observation
  timestamp, has policy or evidence freshness other than exact 3600 seconds,
  is scoped to anything other than the repository-wide permission-bearing
  collaborator population, substitutes PR participants, known maintainers, one
  team, or another caller-selected or partial sample, contains no valid
  permission-bearing collaborator entries, has unknown or incomplete
  pagination, a page retrieval failure, cursor loop, truncation, missing
  authoritative terminal-next-absent evidence, page-count or total mismatch,
  or contradictory cross-page duplicate login, omits the exact PR author,
  contains missing or unknown role/permission values, derives zero or multiple
  write-qualified maintainers, derives a sole write-qualified maintainer other
  than the PR author, contradicts its derived inventories or verdict, or shows
  any qualified non-author reviewer.
- Report the repository, evidence URL or API endpoint, UTC observation time,
  policy and evidence freshness values, evaluated age, exact query scope,
  pagination strategy, page count, total retrieved, deduplicated total entries,
  page evidence and terminal proof, PR author, cross-page
  deduplication result, permission-entry validation result, write-qualified
  predicate, derived `write_qualified_maintainers`,
  `qualified_non_author_reviewers`, and sole-maintainer verdict when available.
  Do not copy private collaborator inventory or credentials into repo examples.
- Repair guidance: refresh retrievable GitHub topology evidence and re-derive
  every page through authoritative terminal-next absence, validate consistent
  cross-page deduplication, then re-derive both inventories and the verdict from
  known GitHub roles and permissions; if a qualified non-author reviewer
  exists, use the collaborative GitHub `APPROVED` path.

## Stale or Invalid External GitHub Review
- BLOCKED on the normal sole-maintainer route when `reviewed_commit_sha` differs
  from the latest PR head; when `reviewer_kind`, `reviewer_login`, `type`,
  `repository_full_name`, `pull_request_number`, `review_id`, `review_url`,
  `submitted_at_utc`, `evaluated_at_utc`,
  `review_freshness_max_age_seconds`, `github_review_state`, or exact review
  body is missing or invalid; when either timestamp is in the future, review
  age is negative or above 3600 seconds, the freshness value is not
  policy-owned exact `3600`, or evidence attempts to override it; when actual
  state is not exact `COMMENTED` or `APPROVED`; when the object or URL is
  unretrievable; when the reviewer is not exact allowlisted
  `chatgpt-codex-connector[bot]` with `type=Bot`, equals the PR author, or the
  repository, PR, review id, URL, timestamp, SHA, state, or body mismatches;
  when the body does not parse to
  `semantic_verdict=approved`; or when `blocking_issues` is missing or nonempty.
- Preserve the object's actual GitHub state literally. An actual `COMMENTED`
  review is not GitHub `APPROVED`, even when its body carries the qualifying
  semantic verdict. `CHANGES_REQUESTED`, `DISMISSED`, a missing state, and all
  other unallowlisted states remain `BLOCKED` even when their body carries the
  qualifying semantic verdict. A PR-author body or comment with copied JSON is
  not a qualifying GitHub review object.
- Any implementation, rework, or base synchronization that changes the head SHA
  invalidates the prior external review object.
- Repair guidance: obtain a new review object from the allowlisted external
  GitHub App or bot against the new exact latest PR head, then retrieve the API
  object again and validate every binding plus the body semantics.
- Local Reviewer output may be retained only as separately labeled
  `preflight_only=true` advisory evidence. It cannot satisfy this gate and must
  not be mapped to a GitHub actor, review, or approval.

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
- Do not let a reviewer-evidence JSON field substitute for actual GitHub
  `python-ci`, conversation resolution (unresolved review threads exactly 0),
  base synchronization, or any other hard-gate evidence.
- Do not auto-tag or auto-push after repair; require user re-confirmation.

## Execution Limitation
- If git commands are unavailable or fail to execute: mark the overall gate as INCOMPLETE; list which checks could not be evaluated; do not issue a release decision.
- If version files cannot be read (permissions, encoding, missing filesystem access): report the inaccessible files; degrade to manual-confirm mode and require the user to supply version values explicitly.
- If CI or external gate signals cannot be retrieved: mark those signals as UNCONFIRMED and treat them as BLOCKED until the user provides them manually.

# Boundaries
- Do not invent missing reviewer evidence, sole-maintainer eligibility, passing test signals, or version alignment.
- Do not call an actual GitHub `COMMENTED` review GitHub `APPROVED`.
- Do not accept `CHANGES_REQUESTED`, `DISMISSED`, a missing state, or any
  unallowlisted GitHub review state even when its body says approved.
- Do not use local Reviewer output as authoritative normal-gate evidence. Keep
  it separately labeled `preflight_only=true`, and do not map it to a GitHub
  actor, review, or approval.
- Do not infer sole-maintainer status from ruleset approvals `0`, chat, historical snapshots, or PR-author claims.
- Do not accept arbitrary strings, empty permission-bearing entries plus a
  self-asserted boolean, a self-asserted empty non-author inventory, stale or
  unretrievable provenance, missing PR-author identity, unknown
  role/permission values, or contradictory topology data as sole-maintainer
  proof.
- Derive `write_qualified_maintainers` only from retrievable collaborator
  entries from the exact repository-wide permission-bearing collaborator
  population after all pages have been retrieved through authoritative
  terminal-next absence and repeated logins have been consistently
  deduplicated. Do not substitute PR participants, known maintainers, one team,
  or another caller-selected or partial sample. Derive
  `qualified_non_author_reviewers` only by excluding the exact PR author. Do
  not pass unless exactly one write-qualified maintainer exists and is the PR
  author.
- On the normal sole-maintainer route, require an API-retrievable review object
  from exact allowlisted `chatgpt-codex-connector[bot]` with `type=Bot`; require
  the reviewer to differ from the PR author and bind the object to the same
  repository, PR, review id, URL, submission and evaluation UTC, policy-owned
  `review_freshness_max_age_seconds=3600`, age from 0 through 3600 seconds
  inclusive, exact latest head, literal actual GitHub state exact `COMMENTED`
  or `APPROVED`, and exact body with semantic verdict `approved` and
  `blocking_issues=[]`.
- Do not accept a PR-author body or comment carrying copied reviewer JSON as a
  qualifying GitHub review object, and do not reuse a review object after the
  PR head SHA changes.
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
