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

### Positive: complete topology and an external GitHub review object

```json
{
  "repository_full_name": "<owner/repository>",
  "evidence_url": "<retrievable-github-collaborator-or-permission-api-endpoint>",
  "observed_at_utc": "<fresh-iso-8601-utc>",
  "freshness_max_age_seconds": "<positive-integer>",
  "query_scope": "<collaborator-and-permission-scope>",
  "pagination": {
    "strategy": "page-number",
    "per_page_or_cursor": "<positive-integer-per-page>",
    "page_count": 2,
    "total_retrieved": 2,
    "total_entries": 1,
    "page_evidence": [
      {
        "request_page_or_cursor": 1,
        "evidence_url": "<retrievable-page-1-api-endpoint>",
        "retrieved_count": 1,
        "next_page_or_cursor": 2,
        "next_evidence": "<retrievable-link-header-proof-for-page-2>"
      },
      {
        "request_page_or_cursor": 2,
        "evidence_url": "<retrievable-page-2-api-endpoint>",
        "retrieved_count": 1,
        "next_page_or_cursor": null,
        "next_evidence": "<retrievable-link-header-proof-that-next-is-absent>"
      }
    ],
    "terminal_next_absent": true,
    "pagination_complete": true
  },
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
  "reviewer_kind": "external-github-app",
  "reviewer_login": "chatgpt-codex-connector[bot]",
  "type": "Bot",
  "repository_full_name": "<owner/repository>",
  "pull_request_number": "<positive-integer>",
  "review_id": "<positive-integer>",
  "review_url": "<retrievable-github-review-url>",
  "submitted_at_utc": "<fresh-iso-8601-utc>",
  "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
  "github_review_state": "COMMENTED",
  "review_body": "{\"semantic_verdict\":\"approved\",\"blocking_issues\":[]}",
  "semantic_verdict": "approved",
  "blocking_issues": []
}
```

- Retrieve both URLs before deciding the gate.
- Verify the topology endpoint belongs to the declared repository, the
  permission-bearing collaborator entries are nonempty and fresh, and every
  page is retrieved through authoritative terminal-next absence. Verify page
  counts, totals, next evidence, and absence of failure, cursor loop, or
  truncation before using the inventory.
- Deduplicate a login repeated across pages only when its role and permissions
  are identical. A contradiction blocks the path.
- Apply the explicit predicate: `admin`, `maintain`, or `write`, or boolean
  `admin`, `maintain`, or `push` permission means write-qualified; `triage` and
  `read` alone do not. Derive exactly one write-qualified maintainer equal to
  the PR author, then exclude that author to derive an empty
  `qualified_non_author_reviewers` list.
- Retrieve the GitHub review object and verify the same repository and PR,
  positive review id, exact allowlisted reviewer
  `chatgpt-codex-connector[bot]`, exact `type=Bot`, reviewer different from the
  PR author, valid submission time, exact latest PR head, literal actual state,
  and exact body. Parse the body to semantic verdict `approved` and
  `blocking_issues=[]`.
- This positive placeholder deliberately records the actual state as
  `COMMENTED`. It satisfies Option A only through the body semantics and must
  not be described as GitHub `APPROVED`.
- These placeholder examples do not disclose an actual private collaborator
  inventory, token, or secret.

### Negative: invalid provenance is blocked

```text
Blocked sole-maintainer reviewer gate:
- topology evidence is an arbitrary string, or has empty permission-bearing
  entries plus `sole_maintainer_verified=true`
- topology endpoint is missing, unretrievable, stale, scoped ambiguously, or
  contradicts the derived write-qualified or non-author inventory
- pagination is unknown or incomplete, a middle page fails, a cursor loops,
  results are truncated, page counts or totals mismatch, or authoritative
  terminal-next-absent evidence is missing
- the same login has conflicting roles or permissions across pages
- PR author is missing or differs from the sole write-qualified maintainer
- zero or multiple write-qualified maintainers are derived
- a collaborator role or required permission is missing, unknown, non-boolean,
  or contradicts the other permission data
- an empty `qualified_non_author_reviewers` list is self-asserted instead of
  derived by excluding the exact PR author
- review object or URL is missing or unretrievable
- reviewer is not exact allowlisted `chatgpt-codex-connector[bot]`, actor type
  is not `Bot`, or reviewer equals the PR author
- review object belongs to another repository or PR, or its review id,
  submission time, literal state, or exact body mismatches
- reviewed commit differs from the latest PR head
- review body is missing or unparseable, semantic verdict is not `approved`, or
  `blocking_issues` is missing or nonempty
- a PR-author body or comment copies the same JSON but no qualifying GitHub
  review object exists
```

- Refresh and re-retrieve GitHub topology evidence, validate the exact PR
  author, complete pagination, consistent deduplication, and known
  role/permission values, then re-derive both inventories and the verdict.
- Obtain a new allowlisted external GitHub App or bot review object for the
  exact latest head and retrieve the object again.
- A local Reviewer result may be retained only as separately labeled
  `preflight_only=true` advisory evidence; it cannot satisfy the gate.
- Do not describe an actual `COMMENTED` object as GitHub `APPROVED`.

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
- Missing pre-release reviewer evidence is the only bypass. An incomplete
  topology query is not proof of sole-maintainer status and is not silently
  converted into this route.

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
