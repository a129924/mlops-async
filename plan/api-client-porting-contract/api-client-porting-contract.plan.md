# API Client Porting Contract Workflow

## Goal

Create repo-visible contract-first API porting artifacts for `mlops-async` so future agents can port `sasctl` and legacy SDK APIs by extracting request contracts, testing first, defining response/error boundaries, updating a ledger, and stopping on high-risk ambiguity.

## Non-goals

- This change will not implement SAS Viya production client methods in `src/mlops_async/`.
- This change will not decide final client class names, module hierarchy, or resource layout.
- This change will not create a complete endpoint family mapping for all SAS Viya APIs.
- This change will not add runtime dependencies or change package configuration.
- This change will not run live SAS Viya integration tests.

## Current Context

`mlops-async` is currently a scaffold with strict Python tooling, 26 installed Agent Skills, and one `python-implementation-workflow` custom agent. The public client API is not implemented yet. The next phase needs a project-specific behavior contract before agents begin translating `sasctl` and legacy `sas-api` behavior into async-first code.

The source-of-truth requirements are:

- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`

## Requirements

1. Add repo-visible analysis and plan artifacts for the API porting contract workflow.
2. Add `api-client-porting-planner` as a project skill that analyzes source SDK APIs but does not implement code.
3. Add `api-client-porting-implementer` as a project skill that performs gated request-test-first implementation from planner output.
4. Add `docs/porting-ledger.md` with a reusable ledger entry schema and empty initial ledger.
5. Update control docs so future API porting starts from the analysis artifacts, planner skill, implementer skill, and ledger.
6. Keep this topic documentation/skill-authoring only; do not touch `src/mlops_async/**`.

## Decisions

- Module/package placement: no production module placement in this phase; new skills live under `.github/skills/`.
- New public API: no.
- Interface changes: no Python runtime interface changes.
- Breaking changes allowed: no.
- New dependencies: no.
- Error handling strategy: no runtime error handling changes; skill failure handling uses `INCOMPLETE`, `BLOCKED`, `needs-human-review`, and `blocked` labels.
- Typing strategy: no Python typing changes; future code must continue following strict Pyright rules.

## Public Contract / API Changes

No public Python API changes.

This topic adds workflow contracts only:

- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`
- `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
- `plan/api-client-porting-contract/api-client-porting-contract.step.md`
- `.github/skills/api-client-porting-planner/`
- `.github/skills/api-client-porting-implementer/`
- `docs/porting-ledger.md`

## Affected Files / Modules

Likely affected files:

- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`
- `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
- `plan/api-client-porting-contract/api-client-porting-contract.step.md`
- `.github/skills/api-client-porting-planner/SKILL.md`
- `.github/skills/api-client-porting-planner/reference.md`
- `.github/skills/api-client-porting-planner/examples.md`
- `.github/skills/api-client-porting-planner/templates/family-map.md`
- `.github/skills/api-client-porting-implementer/SKILL.md`
- `.github/skills/api-client-porting-implementer/reference.md`
- `.github/skills/api-client-porting-implementer/examples.md`
- `.github/skills/api-client-porting-implementer/templates/porting-result.md`
- `docs/porting-ledger.md`
- `docs/ARCHITECTURE.md`
- `.github/copilot-instructions.md`
- `.github/CONTRIBUTING.md`
- `README.md`

Candidate files to inspect:

- `blueprint.md`
- `pyproject.toml`
- `.github/agents/python-implementation-workflow.agent.md`
- `.github/skills/python-implementation-review/SKILL.md`
- `.github/skills/python-code-review/SKILL.md`
- `.github/skills/python-serialization-boundaries/SKILL.md`

## Implementation Steps

1. Create `analysis/api-client-porting-contract/requirements.md` to freeze contract-first porting requirements.
2. Create `analysis/api-client-porting-contract/technical-spec.md` to map requirements to concrete files and validation.
3. Create `plan/api-client-porting-contract/api-client-porting-contract.plan.md` with the 13-section implementation contract.
4. Create `plan/api-client-porting-contract/api-client-porting-contract.step.md` with implementation-only checkbox steps.
5. Create `.github/skills/api-client-porting-planner/` with `SKILL.md`, `reference.md`, `examples.md`, and `templates/family-map.md`.
6. Create `.github/skills/api-client-porting-implementer/` with `SKILL.md`, `reference.md`, `examples.md`, and `templates/porting-result.md`.
7. Create `docs/porting-ledger.md` with ledger schema, labels, and an empty initial ledger.
8. Update `docs/ARCHITECTURE.md` to list the new skills and ledger.
9. Update `.github/copilot-instructions.md` to route source SDK API porting through analysis artifacts, planner skill, implementer skill, and ledger.
10. Update `.github/CONTRIBUTING.md` with porting workflow handoff and ledger rules.
11. Update `README.md` with a concise contract-first porting workflow note.
12. Review the new skill folders against required sections, examples, local references, and boundaries.

## Test Plan

No production code or scripts are added in this topic.

Validation cases:

- Happy path: all planned analysis, plan, skill, ledger, and routing files exist.
- Invalid input: each skill states missing source evidence or missing request contract is `BLOCKED` or `INCOMPLETE`.
- Edge case: batch porting rules forbid cross-family automation and require stop flags for high-risk behaviors.
- Regression: existing scaffold status is not overstated as implemented client functionality.
- Backward compatibility: no changes to public Python API, package dependencies, or test layout.

## Validation Commands

Use existing filesystem and text checks for documentation artifacts:

```bash
test -f analysis/api-client-porting-contract/requirements.md
test -f analysis/api-client-porting-contract/technical-spec.md
test -f plan/api-client-porting-contract/api-client-porting-contract.plan.md
test -f plan/api-client-porting-contract/api-client-porting-contract.step.md
test -f .github/skills/api-client-porting-planner/SKILL.md
test -f .github/skills/api-client-porting-implementer/SKILL.md
test -f docs/porting-ledger.md
```

Runtime validation such as `pytest`, `pyright`, or `ruff` is not required unless this topic unexpectedly adds Python code.

## Risks

- The workflow may become too broad if planner and implementer responsibilities are merged into one skill.
- The control docs may overstate readiness if they imply production client APIs already exist.
- If ledger requirements are too loose, future endpoint porting may lose source evidence or compatibility decisions.
- If stop conditions are not explicit, agents may batch-port risky SDK behavior without human review.

## Rollback Plan

Revert the files created or modified by this topic:

- `analysis/api-client-porting-contract/**`
- `plan/api-client-porting-contract/**`
- `.github/skills/api-client-porting-planner/**`
- `.github/skills/api-client-porting-implementer/**`
- `docs/porting-ledger.md`
- `docs/ARCHITECTURE.md`
- `.github/copilot-instructions.md`
- `.github/CONTRIBUTING.md`
- `README.md`

## Open Questions

None.
