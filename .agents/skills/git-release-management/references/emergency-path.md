# Emergency path

## Boundary from the normal sole-maintainer path

A verified sole-maintainer repository is not automatically an emergency.

When current GitHub repository permission and collaborator evidence proves that
the qualified non-author reviewer inventory is empty, the normal
sole-maintainer reviewer path uses an independent Reviewer agent's structured
approval for the latest PR head exact SHA. That evidence:

- is not GitHub `APPROVED`
- must come from a Reviewer separate from the Implementer
- becomes stale after any implementation, rework, or base synchronization
  changes the head SHA
- does not replace actual latest-head `python-ci`, conversation resolution,
  base synchronization, or any other hard gate
- does not authorize merge or post-merge tag creation

Do not use a ruleset approval count of `0`, chat, historical evidence, or a PR
author claim as proof of sole-maintainer eligibility. If current GitHub topology
evidence is unavailable, ambiguous, stale, or shows a qualified non-author
reviewer, the normal sole-maintainer path is `BLOCKED`; it is not silently
converted to emergency.

## Allowed bypass

Emergency mode may bypass only one gate condition:

- missing pre-release reviewer evidence

It may not bypass:

- actual latest-head GitHub `python-ci`
- unresolved review threads exactly `0`
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
- Sole-maintainer topology unverified: `BLOCKED`; refresh current GitHub
  evidence rather than misclassifying the repository as emergency.
- Reviewer evidence stale after a head-SHA change: `BLOCKED`; obtain a new
  independent review for the exact latest head or use the fully evidenced
  emergency path.
