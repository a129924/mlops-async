# mlops-async

Async Python library scaffold for SAS Viya REST API operations.

## Status

This repository is currently a **project scaffold**. The package layout, tooling,
quality gates, and agent-governance files are in place; the public client API is
not implemented yet.

As of **v0.11.7**, the repository closes `PR #35`: the repo now includes the
`jobExecution/jobs/{jobId}/state` (`get_job_state`) bounded request-only /
shape-only request gate, while the broader polling / state-machine workflow
remains intentionally separated from this release surface.

v0.11.7 補齊 `PR #35` 的 final release：
repo 現已納入 `jobExecution/jobs/{jobId}/state` (`get_job_state`) 的 bounded
request-only / shape-only request gate；較大的 polling / state-machine
workflow 仍維持為獨立邊界，不併入本次 release surface。

As of **v0.11.6**, the repository closes `PR #34`: the repo now includes the
request-only / shape-only request gate for
`modelRepository/models/content` (`get_model_content`), and the shared
`request-shape-priority-workflow` board is synchronized to that merged current
truth.

v0.11.6 補齊 `PR #34` 的 final release：
repo 現已納入 `modelRepository/models/content` (`get_model_content`) 的
request-only / shape-only request gate，並將 shared
`request-shape-priority-workflow` board 同步到 merged current truth。

As of **v0.11.5**, the repository closes `PR #31`, `PR #32`, and `PR #33`:
the repo now includes request-only / shape-only request gates for
`jobExecution/jobRequests/jobs` (`start_job`),
`modelRepository/projects/champion` (`get_champion_model`), and
`jobExecution/jobs` (`get_job`), while the shared
`request-shape-priority-workflow` board is synchronized to that merged current
truth.

v0.11.5 補齊 `PR #31`、`PR #32`、`PR #33` 的 final release：
repo 現已納入 `jobExecution/jobRequests/jobs` (`start_job`)、
`modelRepository/projects/champion` (`get_champion_model`) 與
`jobExecution/jobs` (`get_job`) 的 request-only / shape-only request gates，
並將 shared `request-shape-priority-workflow` board 同步到 merged current
truth。

As of **v0.11.4**, the repository closes the `PR #30`
request-shape-priority-workflow merge: the repo now adds a docs-first
session-entry trio under `docs/request-shape-priority-workflow/`, normalizes the
request-shape queue into an explicit `surface + API` board, and aligns the
analysis / plan artifacts with the new blocked / out-of-scope workflow contract.

v0.11.4 補齊 `PR #30` 的 request-shape-priority-workflow 合併：
repo 現已新增 `docs/request-shape-priority-workflow/` 下的 docs-first
session-entry trio，將 request-shape queue 正規化為明確的 `surface + API`
board，並把相關 analysis / plan artifacts 對齊到新的 blocked /
out-of-scope workflow contract。

As of **v0.11.0**, the repository closes the `PR #26` same-name skill migration:
32 frozen agent skills are now materialized under the repo-local `.agents/skills/`
discovery surface, `AGENTS.md` declares that surface explicitly, and the
`codex-skill-projection` topic artifacts plus audit ledger remain available as the
repo-visible delivery trail.

As of **v0.11.1**, the repository closes the `PR #27` codex-skill-blockers merge:
the repo now includes neutral `api-client-porting-planner` /
`api-client-porting-implementer` skills under `.agents/skills/`, a
Codex-specific `.codex/agents/api-client-porting-workflow.toml` orchestration
surface, and aligned implementation topic artifacts that preserve contract-first
porting governance while keeping tracker and instruction dependencies explicit.

As of **v0.11.3**, the repository closes the combined `PR #29`
model-repository governance and request-contract alignment merge: the repo now
adds the shared `plan/topic-plan-contract.md` authority for topic-plan shape,
clarifies how extra `Inputs` / `Prerequisites` sections coexist with canonical
required sections, and tightens `models_request_gate` request-contract tests to
request-only / shape-only assertions.

v0.11.3 補齊 combined `PR #29` 的 governance / request-contract 對齊：
repo 現已新增 shared `plan/topic-plan-contract.md` 作為 topic-plan shape 的
repo-visible authority，明確允許 `Inputs` / `Prerequisites` 等額外章節與
canonical required sections 並存，並把 `models_request_gate` request-contract
tests 收斂為 request-only / shape-only 驗證。

As of **v0.11.2**, the repository closes the `PR #28` custom-agent-codex-compat
merge: the repo now adds repo-local `python-implementation-workflow` and
`workflow-artifact-contract` skills, aligns the Codex `planner`,
`implementer`, and `reviewer` agent surfaces under `.codex/agents/`, preserves
the `custom-agent-codex-compat` analysis / plan delivery trail, and includes a
baseline test that validates the custom-agent artifact contract against the
current repo state.

v0.11.2 補齊 `PR #28` 的 custom-agent-codex-compat 合併後整理：
repo 現已新增 repo-local `python-implementation-workflow` 與
`workflow-artifact-contract` skills，並對齊 `.codex/agents/` 下的 Codex
`planner`、`implementer`、`reviewer` agent surfaces；同時保留
`custom-agent-codex-compat` 的 analysis / plan 交付軌跡，並納入會依目前
repo 狀態驗證 custom-agent artifact contract 的 baseline test。

v0.11.1 補齊 `PR #27` 的 codex-skill-blockers 合併後整理：
repo 現已新增中立化的 `api-client-porting-planner` /
`api-client-porting-implementer` skills 到 `.agents/skills/`，並新增
Codex-specific 的 `.codex/agents/api-client-porting-workflow.toml`
orchestration surface；相關 implementation topic artifacts 也已對齊，保留
contract-first porting governance，同時將 tracker 與 instruction 依賴明確化。

v0.11.0 補齊 `PR #26` 的 same-name skill migration：
32 個 frozen agent skills 已正式更新到 repo-local `.agents/skills/` discovery
surface，`AGENTS.md` 也已明確宣告該 surface，且
`codex-skill-projection` 的 topic artifacts 與 audit ledger 仍保留為
repo-visible 交付軌跡。

As of **v0.10.10**, the repository closes the `PR #25` review-comment follow-up:
the tests-only scope guard now derives changed paths from the actual git diff state,
helper-style attribute calls are rejected, and the topic docs stay aligned with the
delivered scope.

v0.10.10 補齊 `PR #25` review comments 的後續整理：
tests-only scope guard 改為依實際 git diff/state 判定；
helper-style attribute call 也會被拒絕，且 topic 文件已與交付範圍對齊。

As of **v0.10.8**, the repository closes the `tests-importlib-plan-review`
post-merge follow-up: tests now remove non-essential `importlib` module-loading
helpers in favor of absolute imports, while preserving importability assertions
that explicitly validate module discovery behavior.

v0.10.8 補齊 `tests-importlib-plan-review` 合併後的後續整理：
`tests/` 中非必要 `importlib` 載入輔助已改為絕對引入；
僅保留真正用於 importability 驗證的 `importlib` 斷言路徑，
以維持測試語意與契約一致。

As of **v0.10.7**, the repository closes the `request-gate-projects-tables`
post-merge follow-up: the projects request gate plan, step tracker, and
request-contract tests are merged, while `model-repository/tables` remains
BLOCKED by HATEOAS conditional endpoint selection for a future topic.

v0.10.7 補齊 `request-gate-projects-tables` 合併後的後續整理：
projects request gate 的 plan / step / tests 已併入主線，
而 `model-repository/tables` 仍因 HATEOAS conditional endpoint selection
保留 BLOCKED，留待後續獨立 topic。

As of **v0.10.6**, the repository closes the `token-manager-test-rigor-review`
post-merge follow-up: the TokenManager rigor-review gaps are now covered by unit
tests, and the audit trail stays aligned with the current analysis artifacts.

v0.10.6 補齊 `token-manager-test-rigor-review` 合併後的後續整理：
TokenManager 嚴謹度缺口已由單元測試關閉，且分析工件仍與當前狀態對齊。

As of **v0.10.5**, post-merge docs/contracts are aligned for the
`coverage-agent-simplification` correction: step-tracker validation now uses the
canonical command form
`check_impl_steps_succeeded coverage-agent-simplification`, avoiding false failures
from file-path invocation examples in planning specs.

v0.10.5 補齊 `coverage-agent-simplification` 合併後的文件一致性：步驟追蹤驗證
指令統一為 `check_impl_steps_succeeded coverage-agent-simplification`，不再使用
錯誤的檔案路徑呼叫範例。

As of **v0.10.4**, the repository enforces a **90% test-coverage gate** via
`pyproject.toml` (`fail_under = 90`) and the dedicated `coverage-check` pre-commit
hook. pytest-cov writes `.coverage-reports/coverage.json` plus `term-missing` output;
Agents use that JSON evidence to identify uncovered files, functions, and lines, then
triage gaps against the current topic Test Plan or escalate human feedback when scope
or stop-condition evidence is insufficient.

v0.10.4 的 **coverage-agent** current truth 已校正為 90% 覆蓋率門檻與
pytest-cov JSON evidence workflow。`.coverage-reports/coverage.json` 提供檔案、函式
與行號層級的 missing-line 資訊；Agent / human 依目前 topic 的 Test Plan 判斷是否補
語義正確的測試，若超出 scope 或觸發 stop condition，則回報人工審查而不自動寫入測試。

As of **v0.10.3**, the repository now includes a reusable request-contract session
context for sasctl / legacy source work: `docs/standards/request-contract-testing.md`
now acts as the explicit source of truth for request-contract gate semantics, and
`.github/prompts/request-contract-testing-context.prompt.md` provides a directly
injectable new-session entry point that routes Agents back to that standard and
requires stop-on-drift behavior.

v0.10.3 新增 **request-contract-session-context** 主題，固定「新 session 如何恢復
request-contract gate 上下文」的雙工件模式：standards doc 保留完整標準，prompt
只作為注入入口。這次變更不觸碰 `src/**` 或 `tests/**`，而是把既有 request-contract
testing 基線變成更容易重用的 session entry contract。

As of **v0.10.2**, the repository now includes a minimal `tach` guardrail for the
auth / request boundary: `mlops_async.transport` may depend on
`mlops_async.core`, while `mlops_async.core` remains forbidden from depending on
`mlops_async.transport`. `README.md` and `.github/CONTRIBUTING.md` now reflect
that narrower, machine-checkable governance boundary without widening `tach`
into a repo-wide module reorganization.

v0.10.2 新增 **http-client-auth-boundary-tach-guard** 主題，將 auth/request
boundary 的最小結構護欄正式寫入 `tach.toml`，並同步校正 current-state 文件。
這次變更不觸碰 `src/**` 或 `tests/**`，而是把既有文件基線進一步變成可由
`uv run tach check` 驗證的結構規則。

As of **v0.10.1**, the repository now includes a repo-visible auth / request
boundary context document for future planning and review work.
`docs/standards/http-client-auth-boundary.md` is the first-read source of truth
for the dependency diagrams, component responsibilities, Authorization
collision policy, refresh / expiry / lock contract, and mismatch-stop rule,
while `docs/ARCHITECTURE.md` now links to it as the overview entry point. 這讓
後續 auth-boundary 相關 topic 不必再重複口頭對齊同一套設計。

v0.10.1 新增 **http-client-auth-boundary-context-doc** 主題，將
`HttpClient` / `Requester` / auth collaborators / future `MlopsAsyncClient`
facade 的邊界固定到 `docs/standards/http-client-auth-boundary.md`，並在
`docs/ARCHITECTURE.md` 補上 discoverability 入口。這次變更不觸碰
`src/**`、`tests/**` 或 `tach.toml`，而是把依賴圖、職責與非職責、以及
doc/code/guardrail 衝突時必須停下交人工的規則固定成後續 Agent 可優先引用的
文件基線。

As of **v0.10.0**, the repository includes the first internal auth / request
composition baseline above the pure transport layer: `HttpClient` remains a
transport-only substrate, `Requester` owns managed request-header composition,
and the new auth collaborators (`TokenManager`, `AuthProvider`,
`TokenFetcher`, `TokenStorage`) establish the token lifecycle boundary that
future `MlopsAsyncClient` and domain clients can depend on. 它也把 token
fetch-vs-refresh decision、Authorization conflict policy、以及 in-process
refresh coordination 一起固定到程式碼、測試與架構文件，避免後續 facade /
domain topics 重新定義這條邊界。

v0.10.0 新增 **http-client-auth-boundary** 主題，建立 internal auth / request
composition baseline：新增 `src/mlops_async/core/auth.py`、
`core/requester.py`、`core/token_storage.py` 與 `core/headers.py`，讓
`Requester` 成為唯一的 request composition layer，並讓 `TokenManager` 負責
token expiry、fetch / refresh decision、`asyncio.Lock` 與 double-check
locking。這次也同步補上對應 unit tests、`docs/ARCHITECTURE.md`，以及
repo-visible analysis / plan / spec / step artifacts，作為後續 public facade
與 domain client topic 的共同依賴基線。

As of **v0.9.4**, the repository aligns its local workflow and planning surfaces
with the released `agent-skills` `0.58.0` correction / delta lifecycle
contract. 它把 correction lifecycle / routing 規則正式落到
`plan/agent-handoff-workflow.md`、本地 `plan-creator` / `plan-reviewer` surfaces，
以及 `.github/agents/python-implementation-workflow.agent.md`，讓 parent
artifacts / correction artifacts / conditional review-log / topic-scoped round
cap / role separation 不再只靠 `v0.9.2` sample topic 隱含推斷。

v0.9.4 新增 **correction-delta-lifecycle-contract-alignment** 主題，將本地
workflow body 保持為精簡的 lifecycle / routing contract，並把 detailed
correction artifact guidance 下放到 reference / examples。這次變更不觸碰
`src/**`、`tests/**` 或 sample payload 本體，而是補齊 planner / creator /
reviewer / Main Agent 在 correction / delta workflow 上的共同治理契約。

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

目前的設定刻意維持最小範圍：先治理 `mlops_async._repo_hooks`，以及
auth/request boundary 相關的 `mlops_async.core` / `mlops_async.transport` 單向依賴；
其他子模組仍保留給未來 topic 逐步收緊，而不是過早鎖死整體架構。

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
