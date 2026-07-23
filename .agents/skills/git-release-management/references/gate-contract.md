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
   the qualified non-author reviewer inventory is exactly empty.
2. An independent Reviewer agent approves the latest PR head exact SHA with
   machine-consumable evidence that records dispatcher-verifiable,
   non-opaque canonical actor/run identities for both the Implementer and
   Reviewer. Both identities must exist and must not resolve to the same
   actor/run.

Do not infer sole-maintainer eligibility from chat, historical snapshots, PR
author claims, or a ruleset approval count of `0`. If current evidence is
unavailable, ambiguous, stale, or shows a qualified non-author reviewer, this
path is `BLOCKED`.

Minimum topology evidence:

```json
{
  "repository": "<owner/name>",
  "observed_at": "<current-observation-timestamp>",
  "evidence_source": "<current-github-permission-or-collaborator-source>",
  "pr_author": "<login>",
  "write_qualified_maintainer_inventory": ["<login>"],
  "qualified_non_author_reviewer_inventory": [],
  "sole_maintainer_verified": true
}
```

Minimum independent agent review evidence:

```json
{
  "reviewer_kind": "independent-agent",
  "implementer_run_id": "/root/<canonical-implementer-run-identity>",
  "reviewer_run_id": "/root/<canonical-reviewer-run-identity>",
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

`reviewed_commit_sha` must equal the latest PR head SHA. Any implementation,
rework, or base synchronization that changes the head SHA invalidates the old
review and requires a new independent Reviewer run.

`non_live_ci_contract_verified=true` means only that the Reviewer checked the CI
contract. It does not prove or replace actual latest-head GitHub `python-ci`
success.

Independent agent review is not GitHub `APPROVED`. It does not authorize merge
or tag creation.

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

- Missing or ambiguous topology evidence: refresh current GitHub permission and
  collaborator evidence; do not infer sole-maintainer status.
- Qualified non-author reviewer exists: use the collaborative GitHub
  `APPROVED` path.
- Agent review is stale, malformed, or not independent: dispatch an independent
  Reviewer against the latest PR head exact SHA.
- Any independent hard gate is missing or failing: repair and re-run that gate;
  neither reviewer path nor emergency may bypass it.
- Conversation resolution (unresolved review threads exactly 0) is not proven:
  an unresolved-thread count above 0 or an ambiguous signal is `BLOCKED`.
