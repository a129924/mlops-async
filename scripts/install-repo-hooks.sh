#!/bin/sh

set -eu

repo_root="$(git rev-parse --show-toplevel)" \
    || {
        echo 'error: run this script from a Git worktree.' >&2
        exit 2
    }
hook_path="$repo_root/.githooks/pre-commit"

if [ ! -f "$hook_path" ]; then
    echo "error: version-controlled hook not found: $hook_path" >&2
    exit 2
fi

if [ ! -x "$hook_path" ]; then
    echo "error: version-controlled hook is not executable: $hook_path" >&2
    exit 2
fi

git -C "$repo_root" config core.hooksPath .githooks

configured_path="$(git -C "$repo_root" config --get core.hooksPath)"
if [ "$configured_path" != '.githooks' ]; then
    echo "error: unexpected core.hooksPath after installation: $configured_path" >&2
    exit 1
fi

printf '%s\n' 'Installed version-controlled Git hooks from .githooks.'
printf '%s\n' 'Rollback: git config --unset-all core.hooksPath'
