# Architecture

## Purpose

`mlops-async` is intended to become an async Python client library for selected
SAS Viya REST API endpoints, built on `httpx.AsyncClient` and Pydantic v2.

## Design principles

- Async-first I/O only
- Strict typing by default
- Import-safe modules with no side effects
- Clear separation between public API, endpoint transport, and data models

## Planned package shape

- `src/mlops_async/` — public package root
- `tests/unit/` — isolated tests
- `tests/integration/` — live-environment tests

The blueprint currently names these future-facing public modules:

- `client.py`
- `models.py`
- `endpoints.py`

They are design targets, not implemented files yet.

## Internal client contract — `core/...` + `transport/...` placement

The internal client contract remains split between protocol/value-object modules in
`src/mlops_async/core/` and the concrete transport implementation in
`src/mlops_async/transport/`:

- `core/client.py` — internal-only `Client` `Protocol`
- `core/request_options.py` — `RequestTimeouts` and `ClientRequestOptions` value objects
- `core/types.py` — `JSONScalar`, `JSONValue`, `HttpMethod`, `ResponseHeaders`, `RawClientResponse`
- `transport/http_client.py` — internal-only concrete `HttpClient` backed by `httpx.AsyncClient`
- `exceptions.py` — root `MlopsAsyncBaseException` only
- `transport/exceptions.py` — `HttpErrorContext` and transport-local exception hierarchy

This placement is **internal-only**: none of these `core/...` or `transport/...` types are
re-exported from the package root (`src/mlops_async/__init__.py`), and this topic does not add a
public facade. The top-level `client.py` named in the blueprint remains a **future public design
target**. If `Client` is promoted to a public stable API, that requires a separate topic; the
current internal contract is not a drop-in substitute for it.

## Skill map

This repository includes 35 project skills. They guide implementation rather
than replace normal source files.

### Async and API design

- `python-async-await`
- `python-api-signature`
- `python-error-handling`
- `python-serialization-boundaries`
- `python-type-hints-strict`

### Library structure

- `python-library-architecture`
- `python-module-boundaries`
- `python-package-layout`
- `python-class-design`
- `python-data-model-methods`
- `python-model-selection`
- `python-context-management`
- `python-docstrings`
- `python-naming`

### Testing and environment

- `python-testing-pytest`
- `sense-env-scaffold`
- `copilot-instructions-init`

### Planning and implementation workflow

- `api-client-porting-planner`
- `api-client-porting-implementer`
- `python-plan-authoring`
- `python-plan-review`
- `python-tdd-test-authoring`
- `plan-step-tracker`
- `python-implementation-review`
- `python-code-review`
- `python-async-planning`

### Git and release workflow

- `git-commit-convention`
- `git-branch-naming`
- `git-post-merge-workflow`
- `git-release-management`

## Custom agents

This repository includes 1 custom workflow agent.

- `python-implementation-workflow` — orchestrates plan review, TDD assessment,
  implementation gating, implementation review, and code review for one topic

## Control documents

- `README.md` — human entry point
- `.github/CONTRIBUTING.md` — development workflow
- `.github/copilot-instructions.md` — AI control plane
- `docs/project-goal.md` — project mission, success criteria, non-goals, and phase boundary
- `docs/project-guidelines.md` — project execution rules, stop conditions, and topic git workflow
- `blueprint.md` — initialization and acceptance contract
- `analysis/api-client-porting-contract/requirements.md` — frozen API porting behavior requirements
- `analysis/api-client-porting-contract/technical-spec.md` — technical mapping for API porting workflow artifacts
- `plan/api-client-porting-contract/api-client-porting-contract.plan.md` — implementation contract for the porting workflow
- `docs/migration-map.md` — centralized source-to-target migration map for endpoint families
- `docs/porting-ledger.md` — evidence ledger for each ported source SDK API
