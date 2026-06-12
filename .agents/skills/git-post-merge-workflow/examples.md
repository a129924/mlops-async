# Git post-merge workflow examples

Use these examples after `SKILL.md` has already narrowed the task to post-merge cleanup and local synchronization.

## Normal path

### Merged PR and standard cleanup
```bash
remote_name=$(git remote | head -n 1)
current_branch=$(git branch --show-current)
tracking_remote=$(git config --get "branch.$current_branch.remote" || true)

if [ -n "$tracking_remote" ]; then
	remote_name="$tracking_remote"
fi

if [ -z "$remote_name" ]; then
	echo "Blocked cleanup: no git remote found"
	exit 1
fi

default_branch=$(git symbolic-ref "refs/remotes/$remote_name/HEAD" 2>/dev/null | sed "s@^refs/remotes/$remote_name/@@")

if [ -z "$default_branch" ]; then
	default_branch=$(git remote show "$remote_name" | sed -n '/HEAD branch/s/.*: //p')
fi

if [ -z "$default_branch" ]; then
	echo "Blocked cleanup: cannot detect default branch for remote '$remote_name'"
	exit 1
fi

git checkout "$default_branch"
git pull --ff-only "$remote_name" "$default_branch"
git push "$remote_name" --delete feat/andrew/post-merge-workflow
git branch -d feat/andrew/post-merge-workflow
git branch -vv
```

- Use dynamic default-branch detection, not hardcoded names.
- Prefer branch-tracking remote first, then fall back to first configured remote.
- Remote deletion is default after confirmed merge.

## Safety checks

### Stop when PR was not merged
```text
Blocked cleanup:
- PR is closed without merge

Repair:
1. keep branch state as-is
2. decide whether to reopen PR or create a new one
3. run post-merge cleanup only after an actual merge
```

- Cleanup deletion is merge-dependent.

### Stop when fast-forward sync is not possible
```bash
git pull --ff-only origin "$default_branch"
```

```text
Blocked sync:
- local branch cannot fast-forward to origin

Repair:
1. inspect divergence with `git log --oneline --graph --decorate --all -n 30`
2. decide team-approved reconciliation path (rebase or merge)
3. rerun post-merge cleanup after default branch is synchronized
```

- Do not silently fall back to non-fast-forward pull.

### Failure example: Non-FF divergence on default branch
```text
Blocked sync:
- local `main` has 2 commits not present on `origin/main`
- remote `origin/main` has 5 new commits

Repair guidance:
1. this is an abnormal state; default branch should not receive direct local commits
2. inspect the extra local commits with `git log --oneline --graph --decorate --all -n 30`
3. if this was accidental, realign with `git reset --hard origin/main`
4. if these commits are intentional, move them to a dedicated feature branch with cherry-pick
```

- Resolve divergence deliberately before rerunning post-merge cleanup.

## Exception path

### Keep remote branch for audit retention
```text
Exception applied:
- merged PR confirmed
- policy requires temporary remote branch retention for audit

Actions:
1. skip `git push origin --delete <branch>`
2. document retention reason and expected cleanup date
3. still sync default branch and verify local state
```

- Retention must be explicit and time-bounded.

### Local branch still has unpushed commits
```text
Blocked local deletion:
- `git branch -d` rejected because branch has unmerged commits

Repair:
1. inspect commits and decide whether they should be cherry-picked or discarded
2. only use `git branch -D` after explicit confirmation
3. record the reason for force deletion
```

- `-D` is a last resort, not a default.

## Anti-pattern summary

- deleting remote or local branches before merge confirmation
- hardcoding `main` or `dev` instead of detecting repository default branch
- replacing `--ff-only` with implicit merge pull in a safety-first flow
- force-deleting local branches without commit-loss review
