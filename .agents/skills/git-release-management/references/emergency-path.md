# Emergency path

## Boundary from the normal sole-maintainer path

A verified sole-maintainer repository is not automatically an emergency.

When retrievable, fresh GitHub collaborator and permission query provenance
contains the exact PR author plus nonempty, fully classifiable
permission-bearing entries, the normal sole-maintainer reviewer path first
requires policy-owned `review_freshness_max_age_seconds=3600`, evidence
`freshness_max_age_seconds=3600`, a present non-future observation timestamp
whose age is from 0 through 3600 seconds inclusive, and query scope exact
`repository-wide permission-bearing collaborator population`. PR participants,
known maintainers, one team, caller-selected subsets, and partial samples do
not qualify. It then proves complete pagination through authoritative
terminal-next absence. Unknown or incomplete pagination, a page failure, cursor
loop, truncation, count mismatch, or contradictory cross-page duplicate login
is `BLOCKED`. Only the complete, consistently deduplicated repository-wide
inventory may derive write-qualified maintainers using the fixed
`admin`／`maintain`／`write` or `admin`／`maintain`／`push` permission predicate.
It passes topology only when exactly one write-qualified maintainer exists,
that login is the PR author, and excluding the author leaves no qualified
non-author reviewer.

The path then requires an API-retrievable GitHub review object from exact
allowlisted `chatgpt-codex-connector[bot]` with actor `type=Bot`; that reviewer
must differ from the exact PR author. The object must bind the same repository,
PR, positive review id, review URL, submission UTC, evaluation UTC,
policy-owned `review_freshness_max_age_seconds=3600`, exact latest-head SHA,
literal actual GitHub state, and exact review body. Review age is
`evaluated_at_utc - submitted_at_utc` and must be from 0 through 3600 seconds
inclusive; missing or future timestamps, negative age, stale age, or an
evidence-supplied freshness override are `BLOCKED`. The body must parse to
semantic verdict `approved` with `blocking_issues=[]`. That evidence:

- preserves an actual `COMMENTED` state literally and never calls it GitHub
  `APPROVED`
- accepts actual state only when it is exact `COMMENTED` or `APPROVED`;
  `CHANGES_REQUESTED`, `DISMISSED`, a missing state, and every other
  unallowlisted state remain `BLOCKED` even when their body says approved
- cannot be replaced by a PR-author body or comment carrying copied JSON
- cannot be replaced by local Reviewer output; local review is only separately
  labeled `preflight_only=true` advisory evidence and must not be mapped to a
  GitHub actor, review, or approval
- becomes stale after any implementation, rework, or base synchronization
  changes the head SHA
- does not replace actual latest-head `python-ci`, conversation resolution
  (unresolved review threads exactly 0), base synchronization, or any other
  hard gate
- does not authorize merge or post-merge tag creation

Do not use a ruleset approval count of `0`, chat, historical evidence, or a PR
author claim as proof of sole-maintainer eligibility. If current GitHub topology
evidence is unavailable, unretrievable, ambiguous, stale, contains no valid
permission-bearing entries, has policy or evidence freshness other than exact
3600 seconds, a missing or future observation timestamp, age outside 0 through
3600 seconds, query scope other than the repository-wide permission-bearing
collaborator population, a partial-population substitute, incomplete
pagination or any page/cursor/count failure, omits the PR author, contains
missing, unknown, or contradictory roles/permissions, does not derive exactly
one write-qualified maintainer equal to the PR author, contradicts its derived
inventories or verdict, or shows a qualified non-author reviewer, the normal
sole-maintainer path is `BLOCKED`; it is not silently converted to emergency.
The same applies when the external GitHub review object is missing,
unretrievable, stale, submitted by the wrong actor or type, submitted by the PR
author, has invalid freshness or actual state outside exact `COMMENTED` or
`APPROVED`, lacks a parseable approved semantic verdict with empty blockers, or
mismatches repository, PR, review id, URL, timestamp, SHA, state, or body.

## Allowed bypass

The fully evidenced emergency route may bypass only one gate condition:

- missing pre-release reviewer evidence

It may not bypass:

- actual latest-head GitHub `python-ci`
- conversation resolution (unresolved review threads exactly 0)
- latest PR head being up-to-date with the target base
- failing tests
- failing strict typing
- failing lint
- missing required documentation updates
- version conflicts
- dirty workspace
- existing tag conflicts

## Required markers

Require all of these:

- explicit marker such as `[emergency]` or `[skip-gate]`
- recorded human confirmation in the current workflow, such as a PR comment, PR body note, issue comment, or direct human instruction captured in the session
- release-note or equivalent anomaly record
- a short explanation of why the path is urgent

The emergency marker and evidence do not authorize merge or tag creation.
Explicit human merge decision and post-merge tag authorization remain separate.

## Aftercare

Emergency releases must produce a follow-up reminder for the skipped
pre-release reviewer evidence and any linked administrative follow-up.

## Failure handling

- Missing marker, recorded human confirmation, urgency explanation, or anomaly
  record: `BLOCKED`; supply the missing item or return to a normal reviewer path.
- Any independent hard gate missing or failing: `BLOCKED`; emergency cannot
  bypass it.
- Conversation resolution (unresolved review threads exactly 0) is `BLOCKED`
  unless that exact condition is proven.
- Sole-maintainer topology unverified: `BLOCKED`; refresh current GitHub
  collaborator and permission evidence, enforce both freshness values exact
  3600 seconds and age from 0 through 3600 seconds inclusive, require exact
  repository-wide permission-bearing collaborator population scope, retrieve
  every page through authoritative terminal-next absence, validate consistent
  deduplication, nonempty permission-bearing entries, the exact PR author, and
  the fixed write-qualified predicate, then re-derive both inventories rather
  than misclassifying the repository as emergency.
- Reviewer evidence stale after a head-SHA change: `BLOCKED`; obtain a new
  allowlisted external GitHub App or bot review object for the exact latest
  head, re-retrieve it through the GitHub API, and enforce policy-owned exact
  3600-second freshness plus actual state exact `COMMENTED` or `APPROVED`;
  alternatively, use the fully evidenced emergency path, which still satisfies
  every independent hard gate.
