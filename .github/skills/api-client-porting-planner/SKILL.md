---
name: api-client-porting-planner
description: Analyze source SDK APIs and endpoint families before implementation, producing request-contract evidence, risk classification, porting order, and stop flags without editing production code.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
inputs:
  - source SDK or legacy client repository path
  - endpoint family or source function set to analyze
  - source commit, tag, package version, or other traceable version evidence
  - target project context and any known porting constraints
outputs:
  - endpoint family map
  - source API list with file, line range, and version evidence
  - request contract draft
  - risk classification and stop flags
  - porting order and same-family batch recommendations
  - human-review notes for implementer handoff
use_when:
  - planning a source SDK API or endpoint-family port before implementation begins
  - extracting request behavior from sasctl, a legacy SDK, or another source client
  - deciding whether a family is safe for sequential implementation or needs human review
do_not_use_when:
  - writing target async client methods, tests, schemas, or production code
  - reviewing already-written implementation against a plan
  - porting behavior without source file and version evidence
  - batching APIs across unrelated endpoint families
---

# Purpose
Create a review-ready pre-implementation plan for porting source SDK APIs into a target client by extracting source evidence, drafting request contracts, classifying risk, ordering work, and identifying stop flags.

# Trigger / When to use
Use this skill when:
- an agent must analyze source SDK APIs before writing target client code
- a source function set needs an endpoint family map and request contract draft
- future implementation depends on evidence from `sasctl`, a legacy SDK, or another SDK-like source
- a handoff artifact is needed for an implementer agent

Do not use this skill when:
- the task asks to implement production client methods, tests, models, or runtime code
- the source API behavior is already frozen in an approved planner output
- the task is response-schema implementation after the request contract gate
- the desired output is a broad architecture redesign rather than endpoint-family planning

# Inputs
- Source SDK name and location, such as an installed package, repository path, or file path.
- Endpoint family or source function set to inspect.
- Source commit, tag, package version, or other traceable version identifier.
- Target repository constraints, including paths that must not be modified.
- Any known auth, session, transport, or compatibility constraints.
- Optional prior ledger entries or planner outputs for the same endpoint family.

# Process
1. Confirm the task is planning-only. If asked to edit production code, tests, schemas, or dependencies, mark the task `BLOCKED` for this skill and route to the correct implementation workflow.
2. Identify endpoint family boundaries from source modules, paths, route names, or resource concepts. Do not merge unrelated endpoint families for convenience.
3. Discover source APIs. For each candidate, record SDK, module, function, file, line range, and commit/version evidence.
4. Extract request behavior from source code and nearby call paths. Draft method, path, required headers, query params, body, and auth behavior.
5. Classify each API as `low`, `medium`, or `high` risk using `reference.md`.
6. Mark stop flags for upload/download, streaming, polling/job wait, retry, pagination expansion, global session side effects, conditional endpoint selection, unclear source behavior, and non-wrapper complex behavior.
7. Build the endpoint family map using `templates/family-map.md`.
8. Propose porting order: simplest low-risk wrappers first, then related medium-risk wrappers, and high-risk or unclear APIs last with human review.
9. Recommend same-family batch candidates only after enough request contract evidence exists. Never batch across endpoint families.
10. Add human-review notes wherever evidence is missing, behavior is inferred, or an implementer might otherwise overreach.
11. Output the planner result and workflow state contract.

# Examples
- Positive: Analyze `sasctl` model-repository functions, cite each function's module/file/line range/version, draft request method/path/query/body/auth fields, classify pagination as a stop flag, and recommend only same-family follow-up candidates.
- Negative: Implement `AsyncModelsClient.create_model()` from memory, infer paths without source lines, or batch model, folder, and job APIs together because they share the same host.

# Outputs
- Endpoint family map grouped by source family and request pattern.
- Source API list with SDK, module, function, file, line range, and commit/version.
- Request contract draft for each API: method, path, required headers, query params, body, and auth behavior.
- Risk classification: `low`, `medium`, or `high`.
- Stop flags and human-review notes.
- Porting order and same-family batch candidate recommendations when supported by evidence.
- Workflow state fields: `current_step`, `next_step`, and `status`.

# Validation

## Required Checks
- The output does not include production code, target client methods, tests, dependency changes, or runtime configuration edits.
- Every source API entry includes SDK, module, function, file, line range, and commit/version evidence.
- Every request contract draft includes method, path, required headers, query params, body, and auth behavior, even if some fields are marked `unknown` with notes.
- Risk classification is one of `low`, `medium`, or `high`.
- Stop flags are explicitly checked for every API.
- Same-family batch recommendations are absent unless request contract evidence supports them.
- No recommendation batches across endpoint families.

## Quality Checks (best effort)
- Family boundaries are explained using source paths, modules, route patterns, or resource concepts.
- Human-review notes identify exactly what evidence is missing or ambiguous.
- Porting order starts with APIs that have the clearest request contracts and lowest stop-flag burden.
- Request contract drafts avoid response-schema or implementation assumptions.

## On Soft Fail
- Mark status as `INCOMPLETE` when useful planning output exists but some non-blocking evidence is missing.
- Preserve known source facts and mark uncertain fields as `unknown` rather than inventing values.
- List missing files, versions, line ranges, or behavior details in human-review notes.

# Failure Handling

## Missing Context
- Mark status as `BLOCKED` when no source location, endpoint family, or traceable version is available.
- Mark status as `INCOMPLETE` when a source set is partly available but some functions or line ranges cannot be confirmed.
- State the missing input needed before implementation can safely begin.

## Ambiguous Requirement
- If ambiguity changes family boundaries, risk classification, or porting order, mark status as `BLOCKED` and request human clarification.
- If ambiguity is local to one API, continue with other APIs and mark that API `needs-human-review`.
- Do not resolve unclear source behavior by guessing target client design.

## Execution Limitation
- State when source files, package metadata, or version information cannot be inspected in the current environment.
- Do not fabricate source evidence, request paths, auth behavior, or compatibility claims.
- Do not downgrade a stop flag because implementation would be inconvenient.

# Workflow State Contract
When participating in a multi-agent porting workflow, include:
- `current_step`: the current planner process step or `planner-output-complete`
- `next_step`: the next handoff, usually `implementation-planning`, `human-review`, or `DONE`
- `status`: `IN_PROGRESS`, `COMPLETE`, `INCOMPLETE`, or `BLOCKED`

# Boundaries
- This skill plans; it does not write production code, tests, Pydantic schemas, target client methods, or dependency changes.
- This skill does not approve implementation readiness when source evidence is missing.
- This skill does not define final target module hierarchy, class names, or public Python APIs.
- This skill does not make live service calls or require network access.
- This skill does not batch across endpoint families.
- This skill does not treat global session side effects from a source SDK as acceptable target behavior.
- This skill stops at planner handoff; implementer workflows own request tests, minimal implementation, response contracts, error contracts, and ledger updates.

# Local references
- `reference.md`: risk rules, required evidence fields, stop flags, and batching constraints for planner decisions.
- `examples.md`: detailed positive and negative planner-output patterns for routine source SDK analysis.
- `templates/family-map.md`: reusable output template for endpoint family maps and implementer handoff notes.
- `templates/`: local templates used only by this skill to structure planner outputs.
