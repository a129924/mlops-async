---
name: api-client-porting-implementer
description: Implement one source SDK API or safe same-family batch from planner output using request-test-first porting, minimal implementation, response and error contract checks, optional tracker updates, and an explicit final decision.
---

# Purpose
Implement one bounded API port, or a safe same-family batch, from planner output using a contract-first sequence: source evidence, request test first, minimal implementation, response and error validation, optional tracker updates, and an explicit final decision.

# Use when
- planner output or equivalent request-contract evidence already exists
- the work is to implement tested target client behavior, not endpoint-family discovery
- the task stays inside the allowed file scope

# Do not use when
- source evidence or request contract is missing
- stop flags require human review before implementation
- the task is still endpoint-family planning

# Inputs
- planner output or equivalent request contract with source SDK, module, function, file, line range, and commit/version
- source code evidence from the original SDK or legacy repository
- target module, class, method, and allowed file scope
- existing test style and local validation commands
- optional repo-local tracker artifacts when they are already in scope

# Process
1. Confirm one bounded API or safe same-family batch, the allowed files, the source evidence, and any in-scope tracker files.
2. Block if source evidence or request contract is missing. Do not infer method, path, auth, headers, query params, body, or response behavior.
3. Re-read the source evidence locally and restate the observed method, path, required headers, query semantics, body shape, auth behavior, and line range.
4. Write request contract tests before implementation.
5. Keep request tests semantic. Do not assert query order, generated headers, content length, host, or connection headers.
6. Implement the smallest target code needed to satisfy the request tests.
7. Extract response contract only after the request gate passes.
8. Apply external-boundary schema policy from [reference.md](reference.md).
9. Add response and error tests based on observed or documented behavior.
10. If a migration map and ledger are both in scope, update the migration map before the ledger. If either tracker is absent or out of scope, emit tracker-ready content in the task output instead of inventing a new path.
11. End with exactly one decision label: `continue`, `stable`, `needs-human-review`, or `blocked`.

# Outputs
- request contract test(s)
- minimal target implementation
- response and error contract tests when evidence is available
- typed schema artifacts or schema updates when needed
- tracker-ready migration rows or ledger-ready output when tracker files are absent or out of scope
- final decision label plus workflow state fields

# Validation
- source evidence includes SDK, module, function, file, line range, and commit/version
- request contract exists before implementation
- request tests are written before minimal implementation
- request tests assert only semantic request behavior
- compatibility uses only `equivalent`, `normalized`, `intentionally_changed`, `not_supported`, or `unknown`
- final decision uses only `continue`, `stable`, `needs-human-review`, or `blocked`
- tracker files are updated only when they are already in scope

# Failure handling
- mark `BLOCKED` when source evidence or request contract is missing
- mark `needs-human-review` when ambiguity affects response schema, compatibility, batching safety, or tracker completeness
- do not fabricate request, response, error, or compatibility data

# Boundaries
- this skill implements from planner output; it does not redo broad endpoint-family discovery
- this skill does not require repo-local tracker artifacts or repo-local instruction artifacts to exist at runtime
- this skill does not batch across endpoint families
- this skill does not modify files outside the active plan's allowed implementation scope

# Local references
- [reference.md](reference.md): request gates, schema policy, compatibility labels, stop conditions, and final decisions
- [examples.md](examples.md): positive and negative implementation patterns
- [templates/porting-result.md](templates/porting-result.md): reusable tracker-ready implementation result template
