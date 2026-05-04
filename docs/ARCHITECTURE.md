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

## Skill map

This repository includes 19 project skills. They guide implementation rather
than replace normal source files.

### Async and API design

- `python-async-await`
- `python-api-signature`
- `python-error-handling`
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

### Testing and environment

- `python-testing-pytest`
- `sense-env-scaffold`
- `copilot-instructions-init`

### Git and release workflow

- `git-commit-convention`
- `git-branch-naming`
- `git-post-merge-workflow`
- `git-release-management`

## Control documents

- `README.md` — human entry point
- `.github/CONTRIBUTING.md` — development workflow
- `.github/copilot-instructions.md` — AI control plane
- `blueprint.md` — initialization and acceptance contract
