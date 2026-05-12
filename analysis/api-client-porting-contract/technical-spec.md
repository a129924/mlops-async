# API Client Porting Contract Technical Spec

## Source Requirements

This technical spec implements `analysis/api-client-porting-contract/requirements.md`.

The requirements freeze a contract-first workflow for porting `sasctl` and legacy SDK APIs into `mlops-async`. This spec maps those requirements to repository artifacts, skill files, templates, ledger schema, routing rules, and validation steps.

## Allowed File Scope

This phase may create or update only:

- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`
- `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
- `plan/api-client-porting-contract/api-client-porting-contract.step.md`
- `.github/skills/api-client-porting-planner/**`
- `.github/skills/api-client-porting-implementer/**`
- `docs/porting-ledger.md`
- `docs/ARCHITECTURE.md`
- `.github/copilot-instructions.md`
- `.github/CONTRIBUTING.md`
- `README.md`

This phase must not modify `src/mlops_async/**`, `tests/**`, or runtime dependency configuration.

## Artifact Responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | Freezes business/workflow intent for contract-first API porting. |
| `technical-spec.md` | Maps the frozen requirements to files, schemas, validation, and routing. |
| `api-client-porting-contract.plan.md` | Implementation contract for creating the workflow artifacts. |
| `api-client-porting-contract.step.md` | Checkbox tracker for implementation completion gates. |
| `api-client-porting-planner` skill | Analyzes source SDK APIs and produces family maps, request contract drafts, risk classifications, and porting order. |
| `api-client-porting-implementer` skill | Executes gated porting from planner output: request test first, minimal implementation, response/error contracts, ledger update. |
| `docs/porting-ledger.md` | Repo-visible evidence ledger for each ported API. |
| Control docs | Route future API porting work through the analysis artifacts, skills, and ledger. |

## Skill Shape

Both skills must follow the local Agent Skill contract:

- folder name is lowercase kebab-case
- `SKILL.md` includes YAML frontmatter with `name`, `description`, and `complexity`
- `SKILL.md` includes Purpose, Trigger / When to use, Inputs, Process, Examples, Outputs, Validation, Failure Handling, Boundaries, and Local references
- each `SKILL.md` includes at least one concise positive and one concise negative example
- each optional file or folder is named in Local references with its role

Because both skills affect downstream implementation behavior and may be consumed by other agents, both should be at least `complexity: high` with:

- `ambiguity_sensitive`
- `multi_agent_handoff`

`api-client-porting-planner` should not use `code_modification` unless its actual workflow directly edits code, tests, configuration, or generated artifacts. Its default responsibility is analysis-only.

`api-client-porting-implementer` should use `code_modification` because it directly governs future source, test, schema, and ledger edits. It may also use `external_tooling` when it instructs agents to run tests or inspect source SDKs through local commands.

## Planner Skill Requirements

`api-client-porting-planner` must:

1. Trigger only for pre-implementation analysis of source SDK APIs or endpoint families.
2. Produce family maps and request contract drafts.
3. Require source module/function/file/line range/version evidence.
4. Classify risk as low, medium, or high.
5. Mark stop flags for upload/download, streaming, polling, retry, pagination expansion, global session side effects, conditional endpoint selection, unclear request behavior, and complex non-wrapper logic.
6. Avoid writing production code, tests, or target client methods.

Required local files:

- `SKILL.md`
- `reference.md`
- `examples.md`
- `templates/family-map.md`

## Implementer Skill Requirements

`api-client-porting-implementer` must:

1. Trigger only when a planner output or equivalent source/request contract exists.
2. Block implementation when source evidence or request contract is missing.
3. Require request tests before minimal implementation.
4. Keep request tests semantic: method, path, required header subset, query key-values, and body shape.
5. Avoid brittle request tests for query ordering, transport headers, host, content length, or connection headers.
6. Define response and error contracts after the request contract gate.
7. Apply Pydantic schema policy from requirements.
8. Update or emit a porting ledger entry for each API.
9. End with `continue`, `stable`, `needs-human-review`, or `blocked`.

Required local files:

- `SKILL.md`
- `reference.md`
- `examples.md`
- `templates/porting-result.md`

## Porting Ledger Schema

`docs/porting-ledger.md` must define an entry shape with:

- source SDK, module, function, file, line range, commit/version
- request method, path, headers, query params, body, auth behavior, status
- target module/class/method and async status
- response status codes, schema model, extra policy, transformations, status
- compatibility labels for request, response, error, and session behavior
- tests added
- known divergences
- human-review notes
- decision label

The ledger must allow blank initial state because no endpoint has been ported in this topic.

## Routing Rules

`.github/copilot-instructions.md` must state that API porting tasks start from:

1. `analysis/api-client-porting-contract/requirements.md`
2. `analysis/api-client-porting-contract/technical-spec.md`
3. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
4. `api-client-porting-planner`
5. `api-client-porting-implementer`
6. `docs/porting-ledger.md`

`docs/ARCHITECTURE.md`, `.github/CONTRIBUTING.md`, and `README.md` must mention the contract-first porting workflow without overstating production client readiness.

## Validation

This phase is documentation/skill-authoring focused. Validation should check:

- required files exist
- both skill folders contain required local files
- both `SKILL.md` files include required sections and examples
- control docs route future porting work through the new artifacts
- `docs/porting-ledger.md` includes compatibility and decision labels

No runtime tests are required unless a script or production code is added. This phase should not add scripts or production code.

## Stop Conditions

Stop and request human review if:

- the user asks to implement real endpoint client methods in this same phase
- source SDK behavior must be inferred without source evidence
- a skill would mix planner and implementer responsibilities into one broad skill
- an artifact outside the allowed file scope appears necessary
- changes to `src/mlops_async/**` or runtime dependencies become necessary
