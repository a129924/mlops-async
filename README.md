# mlops-async

Async Python library scaffold for SAS Viya REST API operations.

## Status

This repository is currently a **project scaffold**. The package layout, tooling,
quality gates, and agent-governance files are in place; the public client API is
not implemented yet.

As of **v0.2.0**, the repository includes the workflow foundation for
contract-first API porting, including planning, gated implementation, review,
and evidence-ledger guidance.

## Goals

- Use `httpx.AsyncClient` for all HTTP operations
- Validate API payloads with Pydantic v2
- Keep strict typing with Pyright
- Separate unit tests from integration tests
- Provide a reusable library for downstream projects

## API porting workflow

本專案使用 contract-first workflow，把 `sasctl` 與 legacy SDK 的行為
平移成 async client code。未來進行 API porting 時，必須先抽出 source
request contract、撰寫 request-contract tests、定義 response / error
boundaries，並更新 `docs/porting-ledger.md`，之後才能宣告 compatibility。

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
- `analysis/` — repo-visible requirements and technical specs for governed topics
- `plan/` — repo-visible implementation plans and step trackers
- `.github/skills/` — installed project skills
- `.github/agents/` — installed custom workflow agents
- `docs/` — human-facing reference documents

## References

- `blueprint.md` — project contract and acceptance criteria
- `.github/copilot-instructions.md` — AI coding control plane
- `.github/CONTRIBUTING.md` — development workflow and contribution rules
- `docs/ARCHITECTURE.md` — design intent and skill map
- `docs/porting-ledger.md` — evidence ledger for contract-first API porting
- `.github/agents/` — reusable workflow orchestration agents for planning and implementation
