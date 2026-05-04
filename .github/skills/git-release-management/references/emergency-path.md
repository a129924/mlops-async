# Emergency path

## Allowed bypass

Emergency mode may bypass only one gate condition:

- missing pre-release reviewer approval

It may not bypass:

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

## Aftercare

Emergency releases must produce a follow-up reminder for the skipped pre-release reviewer approval and any linked administrative follow-up.
