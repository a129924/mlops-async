---
name: git-post-merge-workflow
description: Run post-merge cleanup and local sync safely after a PR is merged, including STOP POINT 2 resume checks, branch deletion defaults, fast-forward-only sync, and final status verification.
complexity: medium
risk_profile:
  - destructive_action     # deletes local and remote feature branches
  - multi_agent_handoff    # STOP POINT 2 is an explicit resume gate in multi-step workflows
  - external_tooling       # calls git CLI for sync, branch deletion, and status verification
use_when:
  - a pull request or equivalent merge path is already merged on GitHub
  - a new explicit human resume message confirms the merge completed and asks to continue
  - the next job is post-merge local sync, branch cleanup, or branch-retention exception handling
  - the workflow needs a portable STOP POINT 2 checklist before cleanup starts
do_not_use_when:
  - the human is still deciding whether to merge
  - the latest message only says 請繼續, continue, or equivalent without explicit merge confirmation
  - the PR is still open, only approved, or closed without merge
  - the main task is release gating, branch naming, or commit message drafting
inputs:
  - explicit human resume message that confirms merge completion and requests post-merge follow-up
  - merged PR reference or equivalent merge target
  - feature branch name
  - repository default branch name (detected dynamically, not hardcoded)
  - whether remote branch retention is required by policy
  - local workspace cleanliness, preserved local state, and ahead/behind status
outputs:
  - go / blocked post-merge decision tied to STOP POINT 2 entry conditions
  - post-merge action plan with runnable cleanup and sync commands
  - exception guidance when branch retention, divergence, or unsafe local state blocks the normal path
  - final verification summary of branch and workspace state
---

# Purpose
Standardize post-merge cleanup and local synchronization after a PR is merged and the workflow is explicitly resumed.

# Trigger / When to use
Use this skill when:
- a pull request or equivalent merge path is already merged on GitHub
- a new explicit human resume message confirms the merge completed and asks to continue
- the next job is post-merge local sync, branch cleanup, or branch-retention exception handling
- the workflow needs a portable STOP POINT 2 checklist before cleanup starts

Do not use this skill when:
- the human is still deciding whether to merge
- the latest message only says `請繼續`, `continue`, or equivalent without explicit merge confirmation
- the PR is still open, only approved, or closed without merge
- the main task is release gating, branch naming, or commit message drafting

# Inputs
- an explicit human resume message that confirms merge completion and asks to continue
- a merged PR reference or equivalent merge target
- the feature branch name
- the repository default branch name (dynamic, not hardcoded)
- whether remote branch retention is required by policy
- local workspace cleanliness, preserved local state, and ahead/behind status

# Process
1. Validate STOP POINT 2 entry conditions with `references/stop-point-2-checklist.md`.
2. Start only when both are true: merge completion can be verified and a new explicit human resume message requests post-merge follow-up. If either is missing, stop with a no-op handoff and wait.
3. Inspect the current worktree, untracked files, and any preserved local state before switching branches. If sync or cleanup would overwrite unclear local state, stop and surface the conflict first.
4. Detect the repository default branch dynamically, then switch to it.
5. Detect the repository's remote and default branch dynamically. Sync the default branch with `git pull <remote>/<default-branch> --ff-only` to ensure FF-only semantics; if upstream is configured, `git pull --ff-only` is acceptable; otherwise use explicit remote+branch form.
6. Verify local workspace status and ahead/behind state after sync.
7. Delete the remote feature branch by default after confirmed merge; keep it only when policy or audit retention explicitly requires it.
8. Delete the local feature branch with `git branch -d`; use `-D` only when explicitly required and after warning about commit-loss risk.
9. Verify no stale post-merge branch state remains (for example with `git branch -vv`) and report any exception path that was used.

# Examples
- **Positive**: User says `I merged PR #42; continue with post-merge cleanup`, merge is verifiable, then sync the default branch with `git pull --ff-only`, delete the merged feature branch, and report final status.
- **Negative**: Continue after STOP POINT 2 because the user only says `請繼續`, or delete branches before verifying merge completion and default-branch sync.

# Outputs
- a go / blocked post-merge decision tied to STOP POINT 2 entry conditions
- a post-merge action plan with runnable cleanup and sync commands
- exception guidance when branch retention, divergence, or unsafe local state blocks the normal path
- a final verification summary of branch and workspace state

# Verification
- Require both a verified merge and an explicit human resume message before cleanup starts.
- Use the local STOP POINT 2 checklist before branch deletion or post-merge release follow-up.
- Treat fast-forward sync, workspace safety, and branch-cleanup verification as completion criteria, not optional polish.

# Red Flags
- merge is assumed from PR approval, silence, or a short `continue` message
- the default branch is hardcoded instead of detected
- `git pull` would require merge or rebase instead of `--ff-only`
- local branch deletion would discard unreviewed or unpreserved commits
- remote branch retention policy is unclear but deletion is attempted anyway

# Validation
**PASS**: merge completion is explicitly confirmed in the resume message AND the STOP POINT 2 entry conditions in `references/stop-point-2-checklist.md` are met. Proceed with sync and cleanup.

**SOFT FAIL**: workspace state is unclean or ahead/behind status is ambiguous, but the ambiguity is resolvable by inspection. Mark the affected step as INCOMPLETE, surface the conflict to the user, and wait for confirmation before continuing. Do not delete branches while any local state is unresolved.

**BLOCKED**: resume message does not confirm merge (e.g., bare `請繼續` or `continue`), the PR is not confirmed merged, or local state would be silently overwritten by a branch switch or pull. Stop with a no-op handoff and state exactly what confirmation is needed before proceeding.

Do not use `BLOCKED` for retention-policy ambiguity alone; default to keeping the remote branch and ask for the policy instead.

# Failure Handling
- **ff-only sync fails**: the default branch has diverged and cannot be fast-forwarded. Do not force a merge or rebase. Surface the divergence, explain the options (rebase vs. merge), and wait for explicit user instruction before proceeding.
- **branch retention policy is unclear**: default to keeping the remote branch intact. Report the ambiguity and ask whether retention is required before deletion.
- **local branch deletion would lose commits**: `git branch -d` will refuse if unmerged commits exist. Surface the warning to the user; do not escalate to `-D` without explicit confirmation and a commit-loss warning.
- **workspace is unclean before branch switch**: stash, commit, or discard any untracked or modified files before switching to the default branch. If none of those options is safe, stop and surface the conflict rather than silently proceeding.
- **STOP POINT 2 entry conditions are not fully met**: do not begin cleanup. Report which condition is missing and wait.

# Boundaries
- Do not start post-merge work before STOP POINT 2 is explicitly resumed.
- Do not poll GitHub, wait in the background, or infer merge completion from silence or indirect signals.
- Do not decide release readiness, tag policy, or version synchronization gates.
- Do not auto-run destructive branch deletion without explicit confirmation or policy support.
- Do not assume a fixed default branch name.
- Do not manage branch naming or commit message wording.

# Local references
- `examples.md`: normal paths, anti-patterns, exception handling, and verification-oriented command playbooks
- `references/stop-point-2-checklist.md`: portable STOP POINT 2 resume checklist for merge confirmation, local sync entry conditions, and branch cleanup checks
