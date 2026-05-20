# mlops-async

Async Python library scaffold for SAS Viya REST API operations.

## Status

This repository is currently a **project scaffold**. The package layout, tooling,
quality gates, and agent-governance files are in place; the public client API is
not implemented yet.

As of **v0.9.3**, the repository improves the readability of request-contract
tests for the `models_request_gate` topic.

v0.9.3 新增 **request-contract-review-readability** 主題，把
`tests/unit/request_contract/models_request_gate/` 的測試改寫成以
`EndpointContractCase` 為核心的 inline readable contract 形式：reviewer
不需進入 fixture 即可一眼讀出 method、path、query、headers 與
source-observed evidence linkage。新增 `contract_case.py` 的 5 個
frozen dataclasses（`EndpointContractCase`、`RequestShape`、`FakeResponse`、
`SessionSpec`、`SourceObservedFixture`）與 `SasctlContractHarness` harness，
並保留既有 JSON fixture linkage 與舊 harness 向後相容性。

As of **v0.9.2**, the repository backfills the merged
`core-concrete-client-minimal` parent artifacts so the parent requirements,
technical spec, plan, and step tracker all reflect the final accepted #10
contract. 它也保留 `core-concrete-client-delta-backfill` topic artifacts 作為
repo-visible decision trail 與 creator/reviewer workflow sample，避免 correction /
delta artifacts 成為唯一的 final contract 載體。

v0.9.2 新增 **core-concrete-client-delta-backfill** 主題，將 nominal inheritance、
object type-hint keep/tighten 規則、`request_json()` 對 `NaN` / `Infinity` /
`-Infinity` 的 invalid-body 邊界、以及 correction artifact lifecycle 回補到
parent artifacts，讓 execution-facing source of truth 與已合併實作一致。

As of **v0.9.1**, the repository installs project-local `python-naming` and
`python-async-planning` skills, and refreshes `python-plan-authoring` plus
`python-plan-review` so async-triggered topics can carry explicit async-planning
status, planner inputs, review checks, and examples inside the repo. 它也同步校正
`.github/copilot-instructions.md` 的 installed skill inventory，讓 `python-naming`
signpost 不再落到未安裝 skill。

v0.9.1 新增 **python-naming-async-planning-migration** 主題，將
`python-naming`、`python-async-planning` 及其必要的 supporting refresh
（`python-plan-authoring` / `python-plan-review`）落地到專案工作流表面，讓後續
async topic 可以直接在 repo 內走 planning / review gate，而不需要依賴外部技能狀態。

As of **v0.9.0**, the repository includes the first internal concrete transport
substrate for the repo-owned client contract: `transport/http_client.py` now
implements the internal `Client` boundary with layered transport exceptions,
success-only raw/JSON request paths, and focused tests that keep transport
integration out of `core/`. 它也同步補上 nominal inheritance tightening 與
object type-hint correction artifacts，讓 internal contract 的 reviewer
evidence、typing boundary 與 correction history 一併固定下來。

v0.9.0 新增 **core-concrete-client-minimal** 主題，建立 internal-only minimal
`HttpClient` 的 concrete transport substrate：新增
`src/mlops_async/transport/http_client.py`、`transport/exceptions.py`、對應的
unit tests、以及 repo-visible analysis / plan / correction artifacts，正式把
第三方 transport integration 與 `core/` contract 層切開，同時禁止 root
exception re-export、alias / transition layer、以及 auth / retry scope creep。

As of **v0.8.2**, the repository includes the workflow foundation for
contract-first API porting, including migration-map integration, gated
implementation, review, and evidence-ledger guidance, as well as the project
goal and guidelines documents as the governance baseline. 它也加入了
pre-commit guard，用來阻擋提交機器本機的絕對路徑，同時允許文件中保留僅供
本機參考的 placeholder 值。開發工具鏈亦納入 `tach`，讓 Python 模組邊界能隨著
套件成長維持明確，並新增 `plan-creator`、`plan-reviewer`、`worktree-manager`
三個 repo workflow 技能來強化 topic handoff 與 worktree 管理。

v0.8.2 新增 **models-request-gate** 主題，為 `model-repository/models` read-only
family 固化 request-only gate 證據：新增 repo-visible plan / analysis artifacts、
`list_models` 與 `get_model` direct identifier branch 的 request-contract fixtures /
tests，以及 `analysis/testing_boundary_decision_draft.md`，明確區分 Layer 1
request-shape 證據與 Layer 2 integration / E2E 證據，避免把目前分支誤讀成
auth、refresh、或 real transport proof。

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
