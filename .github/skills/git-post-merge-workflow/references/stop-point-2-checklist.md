# STOP POINT 2 resume checklist

Use this checklist after manual merge handoff and before any post-merge cleanup or local sync work.

## Resume may start only when:
- a new human message explicitly confirms that the merge completed and asks to continue
- merge completion can be verified from repo-visible evidence

## 1. Merge confirmation
- [ ] The PR or merge path is confirmed as merged, not merely approved, queued, or awaiting review.
- [ ] The PR is closed because it merged, or equivalent merge evidence exists for the chosen workflow.
- [ ] The merge commit or merged change is visible from target-branch history (for example `git log origin/<base>` after fetch).
- [ ] If merge cannot be verified, stop and wait for clearer merge evidence or a clearer resume message.

## 2. Local sync entry checks
- [ ] Current worktree, untracked files, stashes, and preserved local edits are understood before switching branches.
- [ ] The repository default branch is detected dynamically from current repo configuration.
- [ ] The default branch can be updated with `git pull --ff-only`. If local branch has no upstream, use `git pull <detected-remote>/<default-branch> --ff-only` instead. If neither works, stop and repair divergence first.
- [ ] Any local-only state that must survive cleanup is captured or explicitly preserved before branch deletion.
- [ ] If sync would overwrite unclear local state, stop and surface the conflict.

## 3. Branch cleanup checks
- [ ] The feature branch name is known and tied to the merged work.
- [ ] Remote branch deletion is allowed by policy; if retention is required, record the exception and skip remote deletion.
- [ ] Local branch deletion with `git branch -d` succeeds, or unresolved commits are reviewed before any `git branch -D`.
- [ ] Post-cleanup verification shows no stale merged-branch state remains (for example `git branch -vv`).

## Stop conditions
- no explicit human resume message that confirms merge completion
- merged state or merge commit cannot be verified
- the default branch cannot be detected or cannot fast-forward cleanly
- local state preservation is unclear
- branch deletion would drop commits without explicit approval

## Completion signal
Proceed only after the required checks pass or an explicit, documented exception path is chosen.
