# Release gate contract

A release or PR is green only when exactly one mutually exclusive route is
confirmed against current evidence:

- a normal route with exactly one applicable normal reviewer path; or
- a fully evidenced emergency route that bypasses only missing pre-release
  reviewer evidence.

Every independent hard gate remains mandatory on both routes.

## Normal reviewer gate

Select exactly one path from current GitHub repository truth.

### Collaborative repository path

This path passes only when a qualified non-author reviewer has submitted GitHub
`APPROVED` for the latest PR head.

- The approval must apply to the current latest PR head.
- A stale or dismissed approval does not pass.
- Local `preflight_only=true` review does not replace GitHub `APPROVED` when a
  qualified non-author reviewer exists.

### Verified sole-maintainer repository path

This path passes only when both complete topology proof and authoritative
external GitHub review evidence are valid:

1. Current GitHub repository permission and collaborator evidence proves that
   exactly one write-qualified maintainer exists, that login is the exact PR
   author, and excluding that author derives no qualified non-author reviewer.
   The policy and evidence freshness maximums are both exact 3600 seconds, the
   observation age is from 0 through 3600 seconds inclusive, and query scope is
   exact `repository-wide permission-bearing collaborator population`.
   The inventory may be derived only after all pages or cursors are retrieved
   through authoritative terminal-next absence and cross-page duplicate logins
   are consistently deduplicated.
2. An allowlisted external GitHub App or bot submits an API-retrievable GitHub
   review object for the latest PR head exact SHA. The initial exact allowlist
   is `chatgpt-codex-connector[bot]` with actor `type=Bot`; that canonical login
   must differ from the exact PR author. The exact review body must parse to
   semantic verdict `approved` with `blocking_issues=[]`.

Do not infer sole-maintainer eligibility from chat, historical snapshots, PR
author claims, or a ruleset approval count of `0`. If current evidence is
unavailable, ambiguous, stale, or shows a qualified non-author reviewer, this
path is `BLOCKED`.

Minimum topology evidence uses placeholders in repo artifacts; runtime evidence
must be retrieved from the stated GitHub API endpoint:

```json
{
  "repository_full_name": "<owner/repository>",
  "evidence_url": "<retrievable-github-api-endpoint>",
  "observed_at_utc": "<iso-8601-utc>",
  "review_freshness_max_age_seconds": 3600,
  "freshness_max_age_seconds": 3600,
  "query_scope": "repository-wide permission-bearing collaborator population",
  "pagination": {
    "strategy": "page-number|cursor",
    "per_page_or_cursor": "<positive-integer-per-page-or-initial-cursor>",
    "page_count": "<positive-integer>",
    "total_retrieved": "<non-negative-integer>",
    "total_entries": "<non-negative-integer-after-consistent-deduplication>",
    "page_evidence": [
      {
        "request_page_or_cursor": "<page-number-or-cursor>",
        "evidence_url": "<retrievable-page-api-endpoint>",
        "retrieved_count": "<non-negative-integer>",
        "next_page_or_cursor": "<next-value-or-null>",
        "next_evidence": "<retrievable-header-or-page-info-proof>"
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

Retrieve `evidence_url` and verify that it is a GitHub collaborator or
permission API endpoint for `repository_full_name`. `observed_at_utc` must be a
valid UTC timestamp that is not in the future. The policy-owned
`review_freshness_max_age_seconds` and evidence
`freshness_max_age_seconds` must both be exact `3600`; evidence producers and
callers cannot override or widen either value. Observation age at evaluation
must be from 0 through 3600 seconds inclusive.

`query_scope` must be exact
`repository-wide permission-bearing collaborator population`. It must query the
repository-wide population from which GitHub repository permissions can be
derived. PR participants, known-maintainer lists, one team, caller-selected
subsets, partial samples, or any other narrower population are `BLOCKED`.

`pagination` must record the page-number or cursor strategy, positive per-page
size or initial cursor, positive `page_count`, non-negative `total_retrieved`,
non-negative deduplicated `total_entries`, and one `page_evidence` entry for
every successful request. `total_retrieved` must equal the sum of page
`retrieved_count` values; `total_entries` must equal the length of the complete,
consistently deduplicated permission-bearing inventory. Each page entry must
bind its request page or cursor to a retrievable evidence URL, retrieved count,
next page or cursor value, and authoritative next evidence such as a response
header or page-info object. Follow every authoritative next value until the
final page proves next absent. Only
`terminal_next_absent=true` and `pagination_complete=true`, with page counts and
retrieved totals matching the evidence, may supply the inventory.

Unknown or incomplete pagination, a failed middle or terminal page, a repeated
cursor, truncation, missing next evidence, missing terminal-next-absent proof,
or a page-count or total mismatch is `BLOCKED`. A source-side cap or result
limit is truncation unless authoritative pagination evidence proves the
complete repository-wide permission-bearing collaborator population was
traversed.

`pr_author_login` must be the exact current PR author.
`permission_bearing_entries` must be nonempty and represent the complete
retrieved collaborator inventory. When a login appears on more than one page,
deduplicate it only if its `role_name` and all required permissions are
identical. A contradictory role or permission for the same login is `BLOCKED`;
do not choose a preferred entry. Every deduplicated entry must have a login, a
recognized `role_name`, and boolean `admin`, `maintain`, and `push` permission
values.

The write-qualified predicate is fixed:

- write-qualified when `role_name` is `admin`, `maintain`, or `write`; or
- write-qualified when `permissions.admin`, `permissions.maintain`, or
  `permissions.push` is `true`;
- `triage` and `read` alone are not write-qualified.

Missing role or permission values, unknown roles, non-boolean permission
values, or contradictory role/permission data are `BLOCKED`.

Derive `write_qualified_maintainers` from the complete, consistently
deduplicated `permission_bearing_entries` using that predicate. Derive
`qualified_non_author_reviewers` by excluding the exact `pr_author_login` from
`write_qualified_maintainers`. Do not accept either inventory as a
self-asserted input.

The sole-maintainer topology gate passes only when:

1. provenance is current, retrievable, and scoped to the declared repository;
2. policy and evidence freshness maximums are both exact 3600 seconds, the
   observation timestamp is present and not in the future, and its age is from
   0 through 3600 seconds inclusive;
3. query scope is exact
   `repository-wide permission-bearing collaborator population`;
4. pagination is complete through authoritative terminal-next absence, with no
   failed page, loop, truncation, or count mismatch;
5. permission-bearing collaborator entries are nonempty, consistently
   deduplicated, and fully classifiable;
6. `write_qualified_maintainers` contains exactly one login;
7. that exact login equals `pr_author_login`;
8. `qualified_non_author_reviewers` is empty; and
9. `sole_maintainer_verified=true` agrees with every derived value.

Arbitrary strings, empty entries plus a self-asserted boolean, missing PR
author, a PR author different from the sole write-qualified maintainer, zero or
multiple write-qualified maintainers, stale or unretrievable provenance,
freshness values other than exact 3600 seconds, a missing or future observation
timestamp, age outside 0 through 3600 seconds, query scope other than the exact
repository-wide permission-bearing collaborator population, use of PR
participants, known maintainers, one team, a caller-selected subset, or another
partial sample, incomplete pagination, failed pages, cursor loops, truncation,
count mismatch, contradictory duplicate logins, malformed or unknown
permissions, a self-asserted empty non-author inventory, or any derived
mismatch make this path `BLOCKED`. Only the complete inventory may derive the
lists and verdict. When a qualified non-author reviewer exists, select the
collaborative GitHub `APPROVED` path instead.

Minimum authoritative external GitHub review evidence:

```json
{
  "reviewer_kind": "external-github-app",
  "reviewer_login": "chatgpt-codex-connector[bot]",
  "type": "Bot",
  "repository_full_name": "<owner/repository>",
  "pull_request_number": "<positive-integer>",
  "review_id": "<positive-integer>",
  "review_url": "<retrievable-github-review-url>",
  "submitted_at_utc": "<iso-8601-utc>",
  "evaluated_at_utc": "<iso-8601-utc>",
  "review_freshness_max_age_seconds": 3600,
  "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
  "github_review_state": "COMMENTED",
  "review_body": "{\"semantic_verdict\":\"approved\",\"blocking_issues\":[]}",
  "semantic_verdict": "approved",
  "blocking_issues": []
}
```

Retrieve `review_url` through the GitHub API and validate the review object
itself. It must belong to the same `repository_full_name` and positive
`pull_request_number`; carry a positive `review_id`; bind the canonical
`reviewer_login` exactly to the allowlisted
`chatgpt-codex-connector[bot]` with actor `type` exactly `Bot`; and prove that
the reviewer is not the exact PR author. It must also carry a valid
`submitted_at_utc`, valid `evaluated_at_utc`, policy-owned exact
`review_freshness_max_age_seconds=3600`, the exact latest
`reviewed_commit_sha`, literal actual `github_review_state`, and exact
`review_body`. Review age is `evaluated_at_utc - submitted_at_utc` and must be
from 0 through 3600 seconds inclusive. Missing or future timestamps, negative
age, age above 3600 seconds, or an evidence-supplied freshness override are
`BLOCKED`.

Parse the body rather than trusting copied top-level claims. The parsed body
must yield `semantic_verdict=approved` and `blocking_issues=[]`, and those
values must match the recorded derived fields. Missing body, unparseable or
missing verdict, any non-approved verdict, missing or nonempty blockers, or any
repository, PR, review id, URL, actor, type, timestamp, SHA, state, body, or
derived-field mismatch makes the normal sole-maintainer route `BLOCKED`.

Preserve the actual GitHub state literally and allow only exact `COMMENTED` or
`APPROVED`. If the API object says `COMMENTED`, record `COMMENTED` and never
call it GitHub `APPROVED`. The semantic verdict in the review body satisfies
this Option A path without creating GitHub approval state. Actual state
`CHANGES_REQUESTED`, `DISMISSED`, missing, or any other unallowlisted state is
`BLOCKED` even when the body parses to semantic verdict `approved` with
`blocking_issues=[]`.

A PR-author body or comment containing the same JSON is not a GitHub review
object and cannot qualify. Local Reviewer output may exist only as separately
labeled `preflight_only=true` advisory evidence; it cannot satisfy the gate and
must not be mapped to a GitHub actor, review, or approval.

`reviewed_commit_sha` must equal the latest PR head SHA. Any implementation,
rework, or base synchronization that changes the head SHA invalidates the old
review object and requires the allowlisted external GitHub App or bot to review
the new exact SHA.

The external review object does not authorize merge or tag creation and does
not replace actual latest-head GitHub `python-ci` success or any other
independent hard gate.

## Pre-publish snapshot boundary

Repo-visible plan and step artifacts are a pre-publish `review-ready` snapshot.
They may record clearly labeled historical or pre-publish observations, but
they must not claim authoritative state for the snapshot commit's later PR
head, CI, review, or conversation state.

After the snapshot is committed, publish actual current PR head, CI, review,
and conversation evidence only to the applicable PR body or PR comments.
Writing those dynamic facts back into the same commit creates a
published-head self-reference and is invalid evidence.

## Independent hard gates

Both the normal and emergency routes are green only when all of these are
independently confirmed:

- actual latest-head GitHub `python-ci` success
- conversation resolution (unresolved review threads exactly 0)
- latest PR head up-to-date with the target base
- base tests passing
- strict type checks passing
- lint passing
- relevant documentation updated
- versions synchronized across existing release sources and the intended tag
- clean workspace
- target tag does not already exist
- linked version updates for every touched release surface in a
  multi-ecosystem PR

No reviewer evidence field substitutes for any hard gate. Human merge decision
and post-merge tag authorization remain separate explicit boundaries after all
gates pass.

## Emergency path

The fully evidenced emergency route may bypass exactly one normal-path
condition:

- missing pre-release reviewer evidence

Verified sole-maintainer review is a normal reviewer path, not an emergency.

The emergency route still requires all independent hard gates plus:

- explicit emergency marker
- recorded human confirmation
- short urgency explanation
- release-note or equivalent anomaly record

## Skill-signature rule

Treat upstream skills as explicit gate signals.

- `python-testing-pytest`: PASS means test expectations are satisfied for
  release gating
- `python-type-hints-strict`: PASS means strict typing is satisfied for release
  gating

Do not substitute intuition, partial logs, topology claims, or reviewer JSON for
those outcomes when the workflow already exposes them.

## Failure reporting

When the gate fails, name each failed condition directly and give the shortest
useful repair path.

- Missing, stale, unretrievable, empty, unknown, or contradictory topology
  evidence: refresh the GitHub collaborator and permission API evidence,
  enforce policy and evidence freshness values exact 3600 seconds and age from
  0 through 3600 seconds inclusive, require exact repository-wide
  permission-bearing collaborator population scope, traverse every page
  through authoritative terminal-next absence, reject partial populations,
  page failures, loops, truncation, count mismatches, and contradictory
  duplicate logins, then validate the exact PR author, recognized roles, and
  boolean permission-bearing entries before re-deriving
  `write_qualified_maintainers`, `qualified_non_author_reviewers`, and the
  verdict; do not infer sole-maintainer status.
- Qualified non-author reviewer exists: use the collaborative GitHub
  `APPROVED` path.
- External GitHub review is stale, malformed, unretrievable, from the wrong
  actor or type, authored by the PR author, mismatched, has timestamps or
  policy freshness outside the exact 3600-second contract, has actual state
  other than exact `COMMENTED` or `APPROVED`, lacks a parseable approved
  semantic verdict, or has blockers: obtain a new allowlisted external GitHub
  App or bot review object against the latest PR head exact SHA and re-retrieve
  it through the GitHub API.
- Any independent hard gate is missing or failing: repair and re-run that gate;
  neither reviewer path nor emergency may bypass it.
- Conversation resolution (unresolved review threads exactly 0) is not proven:
  an unresolved-thread count above 0 or an ambiguous signal is `BLOCKED`.
