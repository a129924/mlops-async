---
name: api-client-porting-implementer
description: Implement one source SDK API or a safe same-family batch from planner output using request-test-first API client porting, response/error contract extraction, and ledger-backed stop decisions.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
  - code_modification
  - external_tooling
inputs:
  - planner output or equivalent source/request contract
  - source SDK evidence with module, function, file, line range, and commit or version
  - target module, class, method, and allowed file scope
  - local test command or validation expectations
  - current porting ledger location
outputs:
  - request contract tests
  - minimal target implementation
  - response and error contract tests
  - Pydantic request, response, and error schemas when needed
  - updated or emitted porting ledger entry
  - final decision label
use_when:
  - porting a source SDK API into an async-first API client after planning is complete
  - implementing a safe same-family batch with stable request patterns and no stop flags
  - converting source request/response behavior into tested target client behavior
  - updating the porting ledger for implemented APIs
do_not_use_when:
  - source evidence or request contract is missing
  - the task is only endpoint discovery or family mapping
  - the request involves upload/download, streaming, polling, retry, pagination expansion, global session side effects, or unclear source behavior
  - the task asks to infer source behavior without evidence
---

# Purpose
Implement one API, or a safe same-family API batch, from planner output using a contract-first sequence: source evidence, request test first, minimal implementation, response/error tests, ledger update, and explicit stop/continue decision.

# Trigger / When to use
Use this skill when:
- a planner output, source evidence, and request contract already exist for a source SDK API
- the target work is to implement tested async client behavior, not merely analyze an endpoint family
- the implementation can stay within the allowed files for the active task or plan
- a same-family batch has at least two APIs with passing request contract tests and no stop flags

Do not use this skill when:
- source module, function, file, line range, or commit/version evidence is missing
- request contract fields are incomplete or depend on guesses
- the work is endpoint-family planning; use `api-client-porting-planner` instead
- any stop condition requires human review before implementation

# Inputs
- Planner output or equivalent request contract, including source SDK, module, function, file, line range, and commit/version.
- Source code evidence from the original SDK, commonly `sasctl` or another locally available legacy SDK checkout such as `<path-to-legacy-sas-api-checkout>`, but not limited to those SDKs.
- Target async client location, method name, public contract, and allowed files from the active plan.
- Existing test style and local validation commands.
- Ledger path, normally `docs/porting-ledger.md`, or another task-specific ledger path.

# Process
1. Confirm scope: identify the single API or safe same-family batch, allowed files, source evidence, target method, and ledger path.
2. Block if source evidence or request contract is missing. Do not infer method, path, auth, headers, query params, body, or response behavior.
3. Re-read source evidence locally and record the observed method, path, required header subset, query parameter semantics, body shape, auth behavior, and source line range.
4. Write request contract tests before implementation. Assert HTTP method, endpoint path, required header subset, query param key-value semantics, and request body shape.
5. Keep request tests semantic. Do not assert query parameter order, transport-generated headers, content length, host, or connection headers.
6. Implement the smallest target code needed to satisfy the request tests while preserving the planned async-first boundary and avoiding unrelated refactors.
7. Extract response contract only after the request gate passes. Record success status codes, schema model, extra policy, nullable/optional fields, aliases, transformations, pagination, and empty-response behavior.
8. Apply Pydantic external schema policy: request models default to `extra="forbid"`; response models default to `extra="ignore"` or `extra="allow"`; error response models default to `extra="allow"`.
9. Add response tests for the observed success behavior and compatibility label. If raw SDK output is converted into typed Pydantic schema, mark response compatibility as `normalized`, not `equivalent`.
10. Add error tests for observed or documented error response shape without overfitting unknown service internals.
11. Run the relevant local validation commands for the changed files or explain why they could not run.
12. Update or emit the ledger entry using `templates/porting-result.md`, including compatibility decisions, tests added, divergences, human-review notes, and final decision.
13. End with exactly one decision label: `continue`, `stable`, `needs-human-review`, or `blocked`.

# Examples
- Positive: Given planner output for `sasctl.foo.get_bar` with file, line range, commit, method `GET`, path `/foo/{id}`, required accept header, query keys, and stable JSON fixture, first add a request test for method/path/header subset/query key-values, implement the minimal async method, add tolerant response and error tests, update the ledger, and finish with `continue`.
- Negative: Do not implement `list_all_jobs` by guessing pagination, polling, retry, or response schema from endpoint naming; mark `needs-human-review` or `blocked` until source behavior and response evidence are clear.

# Outputs
- Request contract test(s) created before target implementation.
- Minimal target async implementation for one API or an explicitly safe same-family batch.
- Response contract test(s) and error contract test(s), when response/error evidence is available.
- Pydantic models or schema updates with external-boundary `extra` policy documented.
- Ledger entry updated or emitted for every ported API.
- Final decision label: `continue`, `stable`, `needs-human-review`, or `blocked`.

# Validation

## Required Checks
- Source evidence includes SDK, module, function, file, line range, and commit/version.
- Request contract exists before implementation and includes method, path, required headers, query params, body, and auth behavior.
- Request tests are written before minimal implementation.
- Request tests assert only semantic request behavior: method, path, required header subset, query key-values, and body shape.
- Request tests do not assert query order, transport-generated headers, content length, host, or connection headers.
- Pydantic schema policy is applied and documented for request, response, and error models.
- Compatibility labels use only `equivalent`, `normalized`, `intentionally_changed`, `not_supported`, or `unknown`.
- Final decision uses only `continue`, `stable`, `needs-human-review`, or `blocked`.
- The ledger is updated or an explicit ledger entry is emitted before handoff.

## Quality Checks (best effort)
- The minimal implementation does not introduce unrelated module restructuring or broad abstractions.
- Tests follow existing repository style and avoid brittle transport details.
- Response schema remains tolerant at the external API boundary unless stable behavior is proven.
- Human-review notes explain any unknowns, divergences, fixture gaps, or source limitations.

## On Soft Fail
- Mark workflow status as `INCOMPLETE` when non-blocking evidence is incomplete but the request contract remains safe.
- Continue only with explicitly stated assumptions that do not change request behavior or public semantics.
- List missing response fixtures, validation commands not run, and any uncertain compatibility labels.

# Failure Handling

## Missing Context
- If source evidence or request contract is missing, mark status `BLOCKED` and do not implement.
- If target file scope is unclear, mark status `INCOMPLETE` or `BLOCKED` depending on whether implementation would risk unrelated edits.

## Ambiguous Requirement
- Mark `needs-human-review` when ambiguity affects response schema, compatibility label, batching safety, or ledger completeness.
- Mark `blocked` when ambiguity affects method, path, auth behavior, request body, required headers, or source behavior.

## Execution Limitation
- State any local tool, test, or source-inspection limitation explicitly.
- Do not fabricate request, response, error, or compatibility data to fill gaps.

# Workflow State Contract
When participating in a multi-agent workflow, include:
- current_step: <step name from Process>
- next_step: <next step or DONE>
- status: IN_PROGRESS | COMPLETE | INCOMPLETE | BLOCKED

# Red Flags
- Upload/download, streaming, polling or job wait, retry behavior, pagination expansion, global session side effects, conditional endpoint selection, unclear response schema, or unclear source behavior.
- A same-family batch proposed before two APIs have passing request contract tests.
- A response compatibility label of `equivalent` when target code normalizes raw SDK output into typed Pydantic schema.
- Ledger update omitted because tests already passed.

# Common Rationalizations
- "The endpoint name makes the path obvious" is not source evidence.
- "Query order passed locally" is not a stable request contract.
- "Strict response models are cleaner" is not valid at an unstable external API boundary.
- "This API is similar enough to another family" does not justify cross-family batching.

# Boundaries
- This skill implements from planner output; it does not perform broad endpoint-family discovery.
- Do not infer missing source behavior or skip source re-reading.
- Do not skip request-test-first even for small methods.
- Do not skip response or error evidence when claiming compatibility.
- Do not batch across endpoint families.
- Do not modify files outside the active plan's allowed implementation scope.
- Do not bypass the ledger or final decision label.
- Do not claim the result is stable unless request, response, error, validation, and ledger evidence all support `stable`.

# Local references
- `reference.md`: compact rule reference for request gates, schema policy, compatibility labels, stop conditions, and final decisions.
- `examples.md`: detailed positive and negative implementation patterns, including safe batching and blocked cases.
- `templates/porting-result.md`: reusable ledger/handoff template for each implemented API or safe same-family batch.
