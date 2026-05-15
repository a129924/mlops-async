# Models Request-Gate Execution Requirements

## Purpose

本文件凍結 `models-request-gate-execution` 的 execution-facing 業務基線，讓後續
`python-implementation-workflow` 只能在 request-only boundary 內推進 `model-repository/models`
family 的 request gate，而不把 topic 擴張成 full port、response/error contract、或 production
implementation。

## Scope

本需求只涵蓋 follow-up execution topic 的 request-only 邊界：

- family 固定為 read-only `model-repository/models`
- source API 固定為：
  - `sasctl.ModelRepository.list_models`
  - `sasctl.ModelRepository.get_model`
  - `legacy src/sas_api/utils/_api/get_model.py::get_all_models`
  - `legacy src/sas_api/utils/_api/get_model.py::get_one_model`
- execution-facing in scope：
  - mock/interception strategy
  - intercepted request capture design
  - request-flow fixtures
  - mock-response answer sets
  - request-contract tests

本需求不涵蓋：

- response / error contract
- `docs/migration-map.md` 更新
- `docs/porting-ledger.md` 更新
- `src/mlops_async/**` production implementation
- auth implementation
- 任何 full-port compatibility 宣告

## Actors and ownership

- Workflow orchestrator: `python-implementation-workflow`
- Executor: future creator / test authoring agent
- Human reviewer: unresolved request-contract semantics 仲裁者

Ownership model:

- `workflow-gated with fixed bootstrap boundary`

## Measurable requirements

1. **Allowed file scope freeze**
   - Condition: execution topic 準備開始 TDD 與 implementation 時
   - Required outcome: 至少明確授權 `tests/unit/request_contract/models_request_gate/**`；topic-local
     analysis / plan artifacts 也可更新；任何超出此範圍的寫入都必須先被文件化授權
   - Acceptance signal: `plan.md`、`spec.md`、`technical-spec.md` 都列出相同 allowed file scope
   - Failure meaning: 若 executor 需要在未授權路徑寫入，request-only boundary 會失真

2. **Bootstrap gate fixed to existing dependencies only**
   - Condition: executor 需要 mock/interception 能力才能完成 request-only work 時
   - Required outcome: `pyproject.toml` 與 `uv.lock` 在本 topic 一律不得修改；execution 只能使用 repo
     既有 dependencies；若既有 dependencies 不足，workflow 必須回報 `BLOCKED`，不得擴張 bootstrap
     scope
   - Acceptance signal: `plan.md`、`spec.md`、`technical-spec.md` 都明確記錄 `pyproject.toml` / `uv.lock`
     forbidden，且要求既有依賴不足時直接阻擋
   - Failure meaning: 若 bootstrap 被重新打開，topic 會從 request-only boundary 漂移到 dependency/topic
     enablement work

3. **Planner-ready handoff must be repo-visible**
   - Condition: execution topic 進入 TDD authoring 前
   - Required outcome: 至少凍結 source API list、request contract draft、risk classification、stop flags
   - Acceptance signal: `technical-spec.md` 內有可引用的 handoff matrix，並區分 confirmed vs unresolved
   - Failure meaning: 若 request contract draft 仍靠對話記憶，後續測試會開始猜測 request semantics

4. **Request-only execution boundary**
   - Condition: topic 進入實作時
   - Required outcome: 只處理 mock/interception、fixtures、mock answers、request tests；不得進入
     response/error contract、migration evidence、或 `src/mlops_async/**`
   - Acceptance signal: step tracker 與 spec 的 acceptance criteria 只指向 tests-side artifacts
   - Failure meaning: 若 topic 漂移到 full port，將違反已核准 planning baseline

5. **Planned artifact layout freeze**
   - Condition: executor 建立 raw request evidence 與測試時
   - Required outcome: fixture 與 tests 路徑固定落在：
     - `tests/unit/request_contract/models_request_gate/fixtures/*.request-flow.json`
     - `tests/unit/request_contract/models_request_gate/fixtures/*.mock-responses.json`
     - `tests/unit/request_contract/models_request_gate/*.py`
   - Acceptance signal: 新增 artifacts 均落在上述 layout
   - Failure meaning: 若 raw evidence 分散到其他位置，reviewer 無法穩定追蹤 request contract

6. **Execution acceptance gate covers both APIs**
   - Condition: topic 宣稱 request-only execution 完成時
   - Required outcome: `list_models` 與 `get_model` 都必須進入 request-only gate；其中
     `get_model` 只允許宣告 repo-visible evidence 已確認的 direct request branch
   - Acceptance signal: 對兩個 API 都存在 request-flow fixture、mock-response answer set、與 request tests
   - Failure meaning: 若只完成其中一個 API，topic 不算完成；若把未證實 branch 混入完成宣告，topic 會誤導下游

7. **Semantic request assertions only**
   - Condition: request-contract tests 撰寫時
   - Required outcome: 只比對 method、path、required header subset、query key/value semantics、body shape
   - Acceptance signal: spec 與 tests 均明確排除 query order、host、content-length、connection headers、transport-generated headers
   - Failure meaning: 若引入脆弱 transport assertions，request gate 會變成不穩定的 snapshot test

8. **Workflow-compatible spec contract**
   - Condition: topic 交由 `python-implementation-workflow` 執行前
   - Required outcome: `plan/<topic>/<topic>.spec.md` 必須足以作為 Phase 2 的 primary behavior contract
   - Acceptance signal: spec 內具備 acceptance criteria、behavioral scenarios、error/edge cases，且明示 blockers
   - Failure meaning: 若只留下 analysis docs，workflow 會在 plan/TDD gate 缺少可執行 contract

## Contradictions surfaced and resolved

1. `topic-level definition of done 要求 migration-map/ledger` vs `本 follow-up topic 固定為 request-only execution`
   - Resolution: 本 topic 不宣告 full port done；只驗證 request-only gate，migration-map/ledger 留待後續 topic

2. `mock-first 可先推進` vs `bootstrap scope 不得擴張`
   - Resolution: mock/interception 仍在 scope 內，但只能使用既有 repo dependencies；若不足則阻擋，不得修改 `pyproject.toml` / `uv.lock`

3. `source API 名稱已凍結` vs `repo-visible evidence 對部分 request semantics 尚未完整`
   - Resolution: 允許在 handoff 中把未確認欄位標為 unresolved 與 stop flags；禁止用推測補齊

4. `兩個 API 都要進 gate` vs `sasctl.get_model` 可能含非 direct-request variants`
   - Resolution: 本 topic 只允許執行已由 repo-visible evidence 證實的 direct request branch；其他 variants 以 stop flags 保留，需人工決策後另擴 scope

## Extreme-boundary checks

1. **Dependency drift**
   - 若 executor 需要新增 interception 套件、修改 `pyproject.toml`、或更新 `uv.lock` 才能前進，必須立即 BLOCKED

2. **Evidence drift**
   - 若 source review 或 capture design 顯示 `get_model` 會依輸入型別走不同 request path，且與本 spec 的 direct-request 範圍衝突，必須停止並升級人工

3. **Scope drift**
   - 若 execution 需要修改 `src/mlops_async/**`、`docs/migration-map.md`、或 `docs/porting-ledger.md`，視為超出本 topic

4. **Assertion drift**
   - 若測試開始比對 host、transport headers、或 query order，視為違反 request semantics boundary

5. **Partial completion**
   - 若只完成 `list_models` 或只完成 `get_model`，topic 不算完成

## Assumptions

- `plan/models-request-gate-proof/models-request-gate-proof.plan.md`、
  `analysis/models-request-gate-proof/requirements.md`、
  `analysis/models-request-gate-proof/technical-spec.md` 是本 topic 的已核准 planning baseline。
- repo-visible docs `docs/api-endpoints/swagger-spec/*.yaml` 與 markdown reference 可作為目前 handoff 的主要 request evidence。
- auth 行為仍屬 out of scope；若 capture 觀察到 auth steps，應保留為 observed flow，但不把 auth implementation 拉進本 topic。
- 未來 executor 會在 `tests/unit/request_contract/models_request_gate/**` 內完成 request-only work，而不是修改 production code。

## Non-goals

- 不在此 topic 中修改 `src/mlops_async/**`
- 不在此 topic 中建立 response / error contract
- 不在此 topic 中更新 `docs/migration-map.md`
- 不在此 topic 中更新 `docs/porting-ledger.md`
- 不在此 topic 中宣告 full-port compatibility 或 stable-library 變更
- 不在此 topic 中自動解決 `sasctl.get_model` 非 direct branch 的 request semantics
- 不在此 topic 中修改 `pyproject.toml` 或 `uv.lock`
- 不在此 topic 中新增 dependency

## Blockers

本需求目前在已鎖定的 execution scope 內無未決 blocker；若 execution 需要超出既有依賴、direct `get_model` branch、或已確認的 `list_models` query semantics，必須依 stop conditions 回報 `BLOCKED`。

## Freeze status

Status: `FROZEN`
