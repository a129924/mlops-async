# Git release management examples

Use these examples after `SKILL.md` has already narrowed the task to PR gating, version synchronization, or tagging safety.

## Normal release gate

### Block until all release inputs align
```text
Blocked release:
- `pyproject.toml` says `1.4.0`
- `package.json` says `1.3.9`
- intended tag is `v1.4.0`
- `python-type-hints-strict` still reports one failing check

Repair:
1. align Python and Node release versions for this PR
2. fix the strict typing failure
3. rerun CI
4. retry release gating
```

- This is a hard block, not a warning.
- Multi-ecosystem changes must release coherently when they travel in one PR.

### Safe next commands after a clean pass
```bash
git checkout main && git pull origin main
git tag v1.4.0
git push origin v1.4.0
```

- Only present commands like these after the gate is actually green.
- Do not auto-run them.

## No version files present

### Degrade to tag-only mode only when the repo truly has no tracked version source
```text
No version files detected in the release surface.
Continuing in tag-only mode.
Still required:
- clean workspace
- CI green
- tests/type/lint green
- target tag absent
```

- This is the one allowed downgrade path.
- Absence of version files does not waive the rest of the release gate.

## Dirty workspace

### Block tagging from a dirty tree
```text
Blocked release:
- uncommitted changes detected in the workspace

Repair:
- commit or stash the remaining changes
- rerun the release gate from a clean workspace
```

- Release should not guess which files belong in the tag.

## Existing tag conflict

### Stop when the intended tag already exists
```bash
git tag -l "v1.4.0"
```

```text
Blocked release:
- `v1.4.0` already exists

Repair:
- confirm whether the existing tag is the real release
- or choose the next correct version after fixing source files
```

- Do not delete or retarget tags automatically.

## API-signature or contract change

### Require synced docs for contract changes
```text
Blocked PR gate:
- public signature changed in `src/api/session.py`
- related skill/reference docs were not updated

Repair:
- update the relevant `SKILL.md` or reference material
- rerun docs-aware release gate
```

- Contract changes are not docs-optional in this release policy.

## Emergency path

### Emergency can bypass reviewer timing, not core quality gates
```text
PR title: [emergency] restore partner-login callback
Human confirmation: present
Release note exception entry: present
CI: green
Tests: green
Typing: green
Lint: green
Workspace: clean
```

- This can proceed without waiting for ordinary reviewer timing.
- It still fails if any core gate is red.

### Emergency does not excuse failing tests
```text
Blocked emergency release:
- marker present
- reviewer timing bypass requested
- core behavior tests still failing
```

- `[emergency]` is not a license to ship broken behavior.

## Post-release follow-up

### Record what was bypassed and remind later
```text
Emergency release note:
- reviewer timing bypassed
- post-release action: complete retrospective review and document operator timeline
```

- The agent should surface this follow-up in the next relevant conversation, not let it vanish.

## Anti-pattern summary

- tagging from a dirty workspace
- ignoring a mismatched `pyproject.toml` and `__version__.py`
- pretending CI green implies typing and tests passed when the actual skill signals say otherwise
- using `[skip-gate]` to bypass broken core checks
