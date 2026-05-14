# mlops-async

Async Python library scaffold for SAS Viya REST API operations.

## Status

This repository is currently a **project scaffold**. The package layout, tooling,
quality gates, and agent-governance files are in place; the public client API is
not implemented yet.

As of **v0.8.1**, the repository includes the workflow foundation for
contract-first API porting, including migration-map integration, gated
implementation, review, and evidence-ledger guidance, as well as the project
goal and guidelines documents as the governance baseline. 它也加入了
pre-commit guard，用來阻擋提交機器本機的絕對路徑，同時允許文件中保留僅供
本機參考的 placeholder 值。開發工具鏈亦納入 `tach`，讓 Python 模組邊界能隨著
套件成長維持明確，並新增 `plan-creator`、`plan-reviewer`、`worktree-manager`
三個 repo workflow 技能來強化 topic handoff 與 worktree 管理。

v0.8.1 新增 **language-policy-canonical-headings** 主題，凍結 repo 的語言政策邊界：
一般敘述內文維持繁體中文為預設，同時只在 strict enumeration 下允許固定的
canonical English headings / terms 保留原文，並同步對齊 AI 與 contributor
兩個正式政策來源。

v0.8.0 新增 **client-interface-contract** 主題的 internal client contract，
固定 `Client` `Protocol`、request options、response envelope 與 HTTP error
context 的 repo-owned 邊界，並補齊對應 unit tests，作為後續 async API porting
的共同基底。

v0.7.0 新增 **request-contract-testing** 主題的規範與計畫產物，定義了
「Fully Intercepted Baseline Capture → Contract Fixture → Target Request Test」
工作流，供後續 implementation topic 使用。包括 capture gate 的通過條件、
auth divergence 處理政策、endpoint snapshot、mock response 答案集、
以及 stop conditions 等規範定義。

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
uv run tach check
```

## Structural guardrails

此 repository 使用 `tach` 對 `src/mlops_async/` 內部進行漸進式的依賴邊界檢查。

- 設定檔位於 `tach.toml`
- 可執行 `uv run tach check` 在本機驗證模組邊界
- `pre-commit` 也會在 commit 前執行 `tach check`

目前的設定刻意維持最小範圍：只約束既有的 `mlops_async` 套件與內部
`_repo_hooks` 子模組，讓未來套件成長時可以逐步收緊規則，而不是過早鎖死架構。

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
