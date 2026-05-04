# mlops-async

Async Python library scaffold for SAS Viya REST API operations.

## Status

This repository is currently a **project scaffold**. The package layout, tooling,
quality gates, and agent-governance files are in place; the public client API is
not implemented yet.

## Goals

- Use `httpx.AsyncClient` for all HTTP operations
- Validate API payloads with Pydantic v2
- Keep strict typing with Pyright
- Separate unit tests from integration tests
- Provide a reusable library for downstream projects

## Requirements

- Python `3.10`
- `uv`

## Install

```bash
uv sync
```

## Development quick start

```bash
uv run pytest
uv run pyright
uv run ruff check .
uv run ruff format .
```

## Repository layout

- `src/mlops_async/` — package source
- `tests/unit/` — pure unit tests
- `tests/integration/` — integration tests
- `.github/skills/` — installed project skills
- `docs/` — human-facing reference documents

## References

- `blueprint.md` — project contract and acceptance criteria
- `.github/copilot-instructions.md` — AI coding control plane
- `.github/CONTRIBUTING.md` — development workflow and contribution rules
- `docs/ARCHITECTURE.md` — design intent and skill map
