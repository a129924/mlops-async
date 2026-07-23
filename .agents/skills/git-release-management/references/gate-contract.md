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
- Independent agent review does not replace GitHub `APPROVED` when a qualified
  non-author reviewer exists.

### Verified sole-maintainer repository path

This path passes only when both topology proof and independent review evidence
are valid:

1. Current GitHub repository permission and collaborator evidence proves that
   exactly one write-qualified maintainer exists, that login is the exact PR
   author, and excluding that author derives no qualified non-author reviewer.
2. An independent Reviewer agent approves the latest PR head exact SHA with
   machine-consumable evidence that records dispatcher-verifiable,
   non-opaque canonical actor/run identities for both the Implementer and
   Reviewer. Both identities must exist and must not resolve to the same
   actor/run.

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

Retrieve `evidence_url` and verify that it is a GitHub collaborator or
permission API endpoint for `repository_full_name`. `observed_at_utc` must be a
valid UTC timestamp whose age does not exceed the positive
`freshness_max_age_seconds`. `query_scope` must state the collaborator and
permission population queried. `pr_author_login` must be the exact current PR
author. `permission_bearing_entries` must be nonempty and represent the
retrieved collaborators; every entry must have a login, a recognized
`role_name`, and boolean `admin`, `maintain`, and `push` permission values.

The write-qualified predicate is fixed:

- write-qualified when `role_name` is `admin`, `maintain`, or `write`; or
- write-qualified when `permissions.admin`, `permissions.maintain`, or
  `permissions.push` is `true`;
- `triage` and `read` alone are not write-qualified.

Missing role or permission values, unknown roles, non-boolean permission
values, or contradictory role/permission data are `BLOCKED`.

Derive `write_qualified_maintainers` from all retrieved
`permission_bearing_entries` using that predicate. Derive
`qualified_non_author_reviewers` by excluding the exact `pr_author_login` from
`write_qualified_maintainers`. Do not accept either inventory as a
self-asserted input.

The sole-maintainer topology gate passes only when:

1. provenance is current, retrievable, and scoped to the declared repository;
2. permission-bearing collaborator entries are nonempty and fully classifiable;
3. `write_qualified_maintainers` contains exactly one login;
4. that exact login equals `pr_author_login`;
5. `qualified_non_author_reviewers` is empty; and
6. `sole_maintainer_verified=true` agrees with every derived value.

Arbitrary strings, empty entries plus a self-asserted boolean, missing PR
author, a PR author different from the sole write-qualified maintainer, zero or
multiple write-qualified maintainers, stale or unretrievable provenance,
unclear query scope, malformed or unknown permissions, a self-asserted empty
non-author inventory, or any derived mismatch make this path `BLOCKED`. When a
qualified non-author reviewer exists, select the collaborative GitHub
`APPROVED` path instead.

Minimum independent agent review evidence:

```json
{
  "reviewer_kind": "independent-agent",
  "implementer_run_id": "<canonical-implementer-actor-or-run-id>",
  "reviewer_run_id": "<reviewer-run-or-session-id>",
  "repository_full_name": "<owner/repository>",
  "pull_request_number": "<positive-integer>",
  "evidence_surface": "pr-body|pr-comment",
  "evidence_url": "<retrievable-pr-body-or-comment-url>",
  "published_at_utc": "<iso-8601-utc>",
  "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
  "verdict": "approved",
  "blocking_issues": [],
  "scope_verified": true,
  "version_sources_verified": true,
  "non_live_ci_contract_verified": true
}
```

`implementer_run_id` and `reviewer_run_id` must map to canonical actor/run
identities in the dispatcher execution record. A UUID, label, or session token
without that mapping is opaque-only and does not prove separation. Missing,
unverifiable, opaque-only, or equal identities make the normal
sole-maintainer route `BLOCKED`.

Retrieve `evidence_url` and verify that it resolves to the declared
`evidence_surface`, which must be the applicable PR body or PR comment. The
retrieved surface must belong to the same `repository_full_name` and positive
`pull_request_number`, contain the complete reviewer payload, bind
`reviewed_commit_sha` to the latest PR head exact SHA, and carry a valid
`published_at_utc` within the applicable freshness policy.

Missing or unretrievable evidence, a non-PR URL, an invalid or stale timestamp,
an omitted reviewer payload, or any repository, PR, or SHA mismatch makes the
normal sole-maintainer route `BLOCKED`.

`reviewed_commit_sha` must equal the latest PR head SHA. Any implementation,
rework, or base synchronization that changes the head SHA invalidates the old
review and requires a new independent Reviewer run.

`non_live_ci_contract_verified=true` means only that the Reviewer checked the CI
contract. It does not prove or replace actual latest-head GitHub `python-ci`
success.

Independent agent review is not GitHub `APPROVED`. It does not authorize merge
or tag creation.

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
  validate the exact PR author, query scope, recognized roles, and boolean
  permission-bearing entries, then re-derive `write_qualified_maintainers`,
  `qualified_non_author_reviewers`, and the verdict; do not infer
  sole-maintainer status.
- Qualified non-author reviewer exists: use the collaborative GitHub
  `APPROVED` path.
- Agent review is stale, malformed, unretrievable, non-PR-visible, mismatched,
  or not independent: dispatch an independent Reviewer against the latest PR
  head exact SHA, publish the complete payload to that PR's body or comment,
  and re-retrieve it.
- Any independent hard gate is missing or failing: repair and re-run that gate;
  neither reviewer path nor emergency may bypass it.
- Conversation resolution (unresolved review threads exactly 0) is not proven:
  an unresolved-thread count above 0 or an ambiguous signal is `BLOCKED`.
