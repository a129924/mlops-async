## Project Overview

**mlops-async** is a Python async library for SAS Viya REST API operations. It provides non-blocking access to 12+ OpenAPI endpoints (Models, Projects, Tables, Jobs, Authentication) using pure `httpx.AsyncClient` and Pydantic v2 response models. Intended as a dependency for downstream services such as `sas-model-serving`.

**Baseline goals:**
- Governed async Python library structure with minimal filesystem layout
- Pure async I/O via `httpx.AsyncClient` (no thread-based fallback)
- Type-safe response models via Pydantic v2
- Comprehensive test coverage (≥90%) with pytest and pytest-asyncio
- Strict type checking and linting via Pyright and Ruff
- Ready to be consumed as an importable package

## Required Skills

- sense-env-scaffold: Acceptance verification runner
- python-testing-pytest: Pytest unit-testing baseline
- python-type-hints-strict: Strict typing baseline
- python-async-await: Async/await code governance
- python-library-architecture: Library package structure and boundaries

## Toolchain Expectation

- python @ 3.10: Runtime baseline (pinned from 3.12 environment)
- package_manager @ uv: Dependency and lock workflow
- linter @ ruff: Linting and formatting surface
- formatter @ ruff: Code formatting
- tester @ pytest: Test execution with pytest-asyncio
- type_checker @ pyright: Strict type checking (--strict mode)

## Structural Invariants

- package: mlops_async
- path: src/mlops_async
- path: tests
- path: docs (optional, for API reference if needed)
- entrypoint: src/mlops_async/__init__.py
- public_modules: src/mlops_async/client.py, src/mlops_async/models.py, src/mlops_async/endpoints.py
- runtime_deps: httpx>=0.25.0, pydantic>=2.0
- dev_deps: pytest, pytest-asyncio, ruff, pyright, pytest-cov

## Quality Thresholds

- coverage: >=90
- type_checking: pyright --strict passes
- lint_pass: ruff check passes without warnings
- test_pass: pytest passes with pytest-asyncio
- test_async: all async fixtures use pytest-asyncio event_loop_policy

## Acceptance Criteria

```yaml [sensing-assertions]
- kind: path_exists
  target: pyproject.toml
  expected: "true"
- kind: path_exists
  target: src/mlops_async/__init__.py
  expected: "true"
- kind: path_exists
  target: tests
  expected: "true"
- kind: path_type
  target: src/mlops_async
  expected: "directory"
- kind: command_available
  target: uv
  expected: "true"
- kind: command_available
  target: pyright
  expected: "true"
- kind: command_available
  target: ruff
  expected: "true"
- kind: file_contains
  target: pyproject.toml
  expected: 'name = "mlops-async"'
- kind: file_contains
  target: pyproject.toml
  expected: 'requires-python = "==3.10"'
- kind: file_contains
  target: pyproject.toml
  expected: 'dependencies = ['
- kind: file_contains
  target: pyproject.toml
  expected: 'pytest'
```

Acceptance should pass after greenfield init completes. All path assertions validate directory and file structure. All command assertions verify toolchain availability. Pyproject assertions confirm package metadata and dependency declarations.
