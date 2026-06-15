---
name: api-client-porting-planner
description: Plan a source SDK API client port before implementation by collecting source evidence, drafting request contracts, classifying risk and stop flags, and preparing implementer handoff output for one endpoint family or safe same-family batch.
---

# Purpose
Create a planning-only handoff for porting source SDK APIs into a target client without editing production code. The planner freezes source evidence, request-contract facts, risk, stop flags, batching limits, and implementer handoff notes.

# Use when
- source SDK or legacy client behavior must be analyzed before implementation
- an endpoint family or source function set needs request-contract evidence
- an implementer needs a bounded, reviewable handoff

# Do not use when
- the task is to write target client methods, tests, schemas, or production code
- the source request behavior is already frozen in planner output and the work is implementation-only
- the task would require guessing source behavior without file and version evidence

# Inputs
- source SDK or repository path
- endpoint family or source function set
- source commit, tag, package version, or other traceable version evidence
- target repository context and allowed file scope
- optional repo-local tracker artifacts when they are already in scope

# Process
1. Confirm the task is planning-only. If the request is really implementation, stop and route to the implementation workflow.
2. Identify one endpoint family boundary from source modules, route patterns, or resource concepts. Do not merge unrelated families for convenience.
3. Record source evidence for every candidate API: SDK, module, function, file, line range, and commit/version.
4. Draft one request contract per API with method, path, required headers, query params, body, and auth behavior.
5. Classify risk as `low`, `medium`, or `high` using [reference.md](reference.md).
6. Check mandatory stop flags for every API.
7. Build the family map with [templates/family-map.md](templates/family-map.md).
8. If a migration map or similar tracker is in scope, draft tracker-ready rows. If not, keep the rows in the planner output so a downstream workflow can apply them later.
9. Recommend porting order and same-family batch candidates only when request-contract evidence supports them.
10. Add human-review notes anywhere evidence is missing, inferred, or likely to cause implementer overreach.
11. End with workflow state fields and a bounded handoff for the implementer.

# Outputs
- source API list with SDK, module, function, file, line range, and commit/version evidence
- request contract draft for each API
- endpoint family map
- tracker-ready migration rows or equivalent handoff table
- risk classification, stop flags, human-review notes, and porting order
- same-family batch recommendations only when evidence supports them
- workflow state fields: `current_step`, `next_step`, `status`

# Validation
- every source API includes SDK, module, function, file, line range, and commit/version evidence
- every request contract includes method, path, required headers, query params, body, and auth behavior, even when some fields are explicitly `unknown`
- stop flags are checked for every API
- same-family batch recommendations are absent unless request-contract evidence shows a shared pattern
- no output includes target production code, tests, schemas, or dependency edits

# Failure handling
- mark `BLOCKED` when no source location, endpoint family, or traceable version is available
- mark `INCOMPLETE` when some evidence exists but line ranges, versions, or local behavior remain unconfirmed
- do not invent paths, auth behavior, compatibility, or batching safety

# Boundaries
- this skill plans; it does not implement
- this skill does not require repo-local tracker artifacts or repo-local instruction artifacts to exist at runtime
- this skill does not batch across endpoint families
- this skill stops at implementer handoff or human-review escalation

# Local references
- [reference.md](reference.md): required evidence, risk, stop flags, and batching rules
- [examples.md](examples.md): positive and negative planner-output patterns
- [templates/family-map.md](templates/family-map.md): reusable family-map and handoff template
