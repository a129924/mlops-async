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

## Verified sole-maintainer evidence

### Positive: retrievable topology and PR-visible review evidence

```json
{
  "repository_full_name": "<owner/repository>",
  "evidence_url": "<retrievable-github-collaborator-or-permission-api-endpoint>",
  "observed_at_utc": "<fresh-iso-8601-utc>",
  "freshness_max_age_seconds": "<positive-integer>",
  "query_scope": "<collaborator-and-permission-scope>",
  "pr_author_login": "<pr-author-login>",
  "write_qualification_predicate": "role_name in [admin, maintain, write] OR permissions.admin == true OR permissions.maintain == true OR permissions.push == true",
  "permission_bearing_entries": [
    {
      "login": "<pr-author-login>",
      "role_name": "admin",
      "permissions": {
        "admin": true,
        "maintain": true,
        "push": true
      }
    }
  ],
  "write_qualified_maintainers": ["<pr-author-login>"],
  "qualified_non_author_reviewers": [],
  "sole_maintainer_verified": true
}
```

```json
{
  "reviewer_kind": "independent-agent",
  "implementer_run_id": "<canonical-implementer-actor-or-run-id>",
  "reviewer_run_id": "<different-reviewer-run-or-session-id>",
  "repository_full_name": "<owner/repository>",
  "pull_request_number": "<positive-integer>",
  "evidence_surface": "pr-comment",
  "evidence_url": "<retrievable-pr-comment-url>",
  "published_at_utc": "<fresh-iso-8601-utc>",
  "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
  "verdict": "approved",
  "blocking_issues": [],
  "scope_verified": true,
  "version_sources_verified": true,
  "non_live_ci_contract_verified": true
}
```

- Retrieve both URLs before deciding the gate.
- Verify the topology endpoint belongs to the declared repository, the
  permission-bearing collaborator entries are nonempty and fresh, all
  roles/permissions are known, and the exact PR author is present.
- Apply the explicit predicate: `admin`, `maintain`, or `write`, or boolean
  `admin`, `maintain`, or `push` permission means write-qualified; `triage` and
  `read` alone do not. Derive exactly one write-qualified maintainer equal to
  the PR author, then exclude that author to derive an empty
  `qualified_non_author_reviewers` list.
- Verify the review URL resolves to the same repository and PR, contains the
  complete reviewer payload and timestamp, and names the exact latest PR head.
- These placeholder examples do not disclose an actual private collaborator
  inventory, token, or secret.

### Negative: invalid provenance is blocked

```text
Blocked sole-maintainer reviewer gate:
- topology evidence is an arbitrary string, or has empty permission-bearing
  entries plus `sole_maintainer_verified=true`
- topology endpoint is missing, unretrievable, stale, scoped ambiguously, or
  contradicts the derived write-qualified or non-author inventory
- PR author is missing or differs from the sole write-qualified maintainer
- zero or multiple write-qualified maintainers are derived
- a collaborator role or required permission is missing, unknown, non-boolean,
  or contradicts the other permission data
- an empty `qualified_non_author_reviewers` list is self-asserted instead of
  derived by excluding the exact PR author
- review evidence URL is missing, unretrievable, or not a PR body/comment URL
- review evidence belongs to another repository or PR
- reviewed commit differs from the latest PR head
- publication timestamp or complete reviewer payload is missing or stale
```

- Refresh and re-retrieve GitHub topology evidence, validate the exact PR
  author and known role/permission values, then re-derive both inventories and
  the verdict.
- Dispatch an independent Reviewer for the exact latest head, publish the full
  evidence to that PR's body or comment, and retrieve it again.
- Do not describe independent agent review as GitHub `APPROVED`.

## Emergency path

### Emergency can bypass reviewer timing, not core quality gates
```text
PR title: [emergency] restore partner-login callback
Human confirmation: present
Urgency explanation: present
Release note exception entry: present
Latest-head CI: green
Conversation resolution: unresolved review threads exactly 0
Head/base synchronization: head up to date with base
Tests: green
Typing: green
Lint: green
Documentation: synchronized
Version sources and intended tag: synchronized
Workspace: clean
Target tag: absent
```

- This can proceed without waiting for ordinary reviewer timing only after all
  emergency evidence and every independent hard gate are confirmed.
- It still fails if conversation resolution is not exact 0, the head is behind
  its base, or any other hard gate is red.

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
