# mlops-async

Async Python library scaffold for SAS Viya REST API operations.

## Status

This repository is currently a **project scaffold**. The package layout, tooling,
quality gates, and agent-governance files are in place; the public client API is
not implemented yet.

As of **v0.3.0**, the repository includes the workflow foundation for
contract-first API porting, including migration-map integration, gated
implementation, review, and evidence-ledger guidance.

## Goals

- Use `httpx.AsyncClient` for all HTTP operations
- Validate API payloads with Pydantic v2
- Keep strict typing with Pyright
- Separate unit tests from integration tests
- Provide a reusable library for downstream projects

## Project governance

在開始任何新 topic 前，請先閱讀：

- `docs/project-goal.md` — 專案目標、成功定義、非目標與階段邊界
- `docs/project-guidelines.md` — contract-first 執行準則、migration evidence 順序、
  stop conditions、以及 topic 的 Git workflow

## API porting workflow

本專案使用 contract-first workflow，把 `sasctl` 與 legacy SDK 的行為
平移成 async client code。未來進行 API porting 時，必須先抽出 source
request contract、撰寫 request-contract tests、定義 response / error
boundaries，並同步更新 `docs/migration-map.md` 與 `docs/porting-ledger.md`，
之後才能宣告 compatibility。

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
- `docs/project-goal.md` — 專案 GOAL（Mission / Success criteria / Non-goals）
- `docs/project-guidelines.md` — 專案準則（contract-first / migration-map-first / stop rules）
- `docs/migration-map.md` — source API 到 target async API 的集中遷移對照表
- `docs/porting-ledger.md` — evidence ledger for contract-first API porting
- `.github/agents/` — reusable workflow orchestration agents for planning and implementation
