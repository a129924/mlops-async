# Emergency path

## Boundary from the normal sole-maintainer path

A verified sole-maintainer repository is not automatically an emergency.

When retrievable, fresh GitHub collaborator and permission query provenance
contains the exact PR author plus nonempty, fully classifiable
permission-bearing entries, the normal sole-maintainer reviewer path derives
write-qualified maintainers using the fixed `admin`／`maintain`／`write` or
`admin`／`maintain`／`push` permission predicate. It passes topology only when
exactly one write-qualified maintainer exists, that login is the PR author, and
excluding the author leaves no qualified non-author reviewer. The path then
uses an independent Reviewer agent's structured approval for the latest PR
head exact SHA. The structured review must be published to and re-retrieved
from the same PR body or comment, with matching repository, PR, SHA, complete
payload, and valid publication timestamp. That evidence:

- is not GitHub `APPROVED`
- must record dispatcher-verifiable, non-opaque canonical
  `implementer_run_id` and `reviewer_run_id` identities that exist and are not
  equal
- becomes stale after any implementation, rework, or base synchronization
  changes the head SHA
- does not replace actual latest-head `python-ci`, conversation resolution
  (unresolved review threads exactly 0), base synchronization, or any other
  hard gate
- does not authorize merge or post-merge tag creation

Do not use a ruleset approval count of `0`, chat, historical evidence, or a PR
author claim as proof of sole-maintainer eligibility. If current GitHub topology
evidence is unavailable, unretrievable, ambiguous, stale, contains no valid
permission-bearing entries, omits the PR author, contains missing or unknown
roles/permissions, does not derive exactly one write-qualified maintainer equal
to the PR author, contradicts its derived inventories or verdict, or shows a
qualified non-author reviewer, the normal sole-maintainer path is `BLOCKED`; it
is not silently converted to emergency. The same applies when review evidence
is missing, unretrievable, non-PR-visible, stale, incomplete, or mismatched.

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
  collaborator and permission evidence, validate nonempty permission-bearing
  entries, the exact PR author, and the fixed write-qualified predicate, then
  re-derive both inventories rather than misclassifying the repository as
  emergency.
- Reviewer evidence stale after a head-SHA change: `BLOCKED`; obtain a new
  independent review for the exact latest head, publish it to the applicable PR
  body or comment, and re-retrieve it; alternatively, use the fully evidenced
  emergency path, which still satisfies every independent hard gate.
