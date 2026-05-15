# Models Request-Gate Proof Technical Spec

## Source requirements

本技術規格落實下列需求來源：

- `analysis/models-request-gate-proof/requirements.md`

全域 guardrails 仍來自：

- `analysis/api-client-porting-contract/requirements.md`
- `analysis/api-client-porting-contract/technical-spec.md`
- `docs/project-goal.md`
- `docs/project-guidelines.md`

## Goal

把 `models-request-gate-proof` 的 frozen business baseline 轉成 implementation-facing
technical baseline，讓後續 creator work 能在不碰 production code 與 tests 的前提下，
建立 topic-local analysis artifacts 與 step tracker，並為下一階段 planner / implementer
execution 留下可追溯的 technical contract。

## Allowed file scope

此階段只能建立或更新：

- `analysis/models-request-gate-proof/requirements.md`
- `analysis/models-request-gate-proof/technical-spec.md`
- `plan/models-request-gate-proof/models-request-gate-proof.plan.md`
- `plan/models-request-gate-proof/models-request-gate-proof.step.md`

此階段不得修改：

- `src/mlops_async/**`
- `tests/**`
- `docs/migration-map.md`
- `docs/porting-ledger.md`
- `pyproject.toml`
- `uv.lock`
- runtime dependency configuration
- `README.md`
- `VERSION`

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `requirements.md` | 凍結第一個 `model-repository/models` request-gate proof 的 business baseline |
| `technical-spec.md` | 將 frozen baseline 映射成技術工作、檔案範圍、依賴與 rollback triggers |
| `models-request-gate-proof.plan.md` | 作為本 topic 的 repo-visible execution contract |
| `models-request-gate-proof.step.md` | 作為 creator / reviewer workflow 的 completion gate |

## Requirement-to-technical mapping

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| First-family boundary freeze | 在 `requirements.md`、`technical-spec.md`、topic plan 中固定 family、source API set、out-of-scope list | 既有 session 決策、source baseline | 低：文件對齊與 drift 防護 | feasible |
| Request-gate-only completion boundary | 在 technical spec 與 step tracker 中明示只做到 request contract extraction + request tests，不擴張到 response / ledger | business baseline 已凍結 | 低：主要是 scope discipline | feasible |
| Mock-first entry gate | 明確宣告 `mock_first_no_concrete_client`，把 concrete `HttpClient` 缺席降為 deferred prerequisite，而非本 topic blocker | 既有 `core.client.Client` Protocol、planning decision | 低：文件與 gate 定義 | feasible |
| Planning-only pre-implementation gate | 將 allowed file scope 與 step tracker 鎖在 analysis / plan artifact；要求 human review 先於 execution | topic plan、worktree boundary | 低：workflow 對齊 | feasible |
| Deferred environment bootstrap rule | 在 planning docs 中固定 `defer_until_execution_topic`，避免本 topic 提前變更 dependency / lockfile | 使用者限制、planning decision | 低：文件對齊；可減少 branch 汙染 | feasible |
| Evidence-layer separation | 在 technical spec 中先定義未來 summary / raw fixture / mock-answer 三層分工 | request-contract-testing 標準 | 低到中：需要下游 topic 遵守固定路徑 | feasible |

## Required technical tasks

1. 建立 topic-local `requirements.md`，把已在對話與 session plan 中凍結的 actor、success
   signal、completion boundary、client mode、family scope、non-goals 轉成 repo-visible 基線。
2. 建立 topic-local `technical-spec.md`，把 frozen baseline 轉成：
   - 允許檔案範圍
   - artifact responsibilities
   - requirement-to-technical mapping
   - deferred prerequisites
   - validation / rollback rules
3. 建立 topic-local `step.md`，讓後續 creator / reviewer 只讀 `## Implementation Steps`
   的核取方塊。
4. 修正現有 topic plan，讓 analysis-layer routing 與 status/step-tracker alignment 不再與
   topic-local analysis files 的存在狀態矛盾。
5. 在 topic-local docs 中凍結 environment bootstrap 延後策略，避免本 planning topic
   承接 `pyproject.toml` / `uv.lock` 變更。
6. 在 topic-local docs 中定義後續 execution topic 的 mock/interception code 與 raw
   request evidence 建議落點。

## Deferred prerequisites for later phases

以下事項不是本階段 blocker，但若 topic 進入 execution，需在後續主題中明確處理：

1. light review of current planning artifacts
   - review target:
     - `plan/models-request-gate-proof/models-request-gate-proof.plan.md`
     - `analysis/models-request-gate-proof/requirements.md`
     - `analysis/models-request-gate-proof/technical-spec.md`
   - review goal:
     - confirm request-only boundary did not drift into full-port scope
     - confirm bootstrap remains deferred
     - confirm file scope remains outside `src/**`, `tests/**`, `pyproject.toml`, and `uv.lock`

2. separate execution-facing topic creation
   - 後續 request-only mock/interception work 不應直接沿用目前 planning-only topic
   - 新 topic 需正式承接：
     - `tests/**` 變更授權
     - fixture 路徑
     - mock/interception code
     - execution acceptance gate
     - environment bootstrap 決策

3. planner-ready handoff
   - source API list
   - request contract draft
   - risk classification
   - stop flags

4. executable request-gate work
    - intercepted capture strategy
    - request-flow fixture
    - mock-response answer set
    - request-contract tests
    - environment bootstrap flow recorded in the execution-facing topic plan
    - dependency selection aligned to `sasctl` 的 requests transport

5. target call-site boundary
   - 若後續 topic 需要 target runtime request tests，必須先確認是否採：
     - fake client / test double
     - concrete `HttpClient`
   - 但這不是本 planning topic 的前置條件

6. planned execution artifact layout
    - future raw request-flow fixtures:
      `tests/unit/request_contract/models_request_gate/fixtures/*.request-flow.json`
    - future mock-response answer sets:
      `tests/unit/request_contract/models_request_gate/fixtures/*.mock-responses.json`
    - future mock/interception code and derived request tests:
      `tests/unit/request_contract/models_request_gate/*.py`
    - these are planned execution paths only; they are not authorized for modification in this
      planning topic

7. execution tool routing
   - 若 follow-up topic 仍維持 request-only mock/interception 邊界，優先使用
     `python-implementation-workflow` 作為 orchestration layer
   - `api-client-porting-implementer` 保留到以下條件成立後再使用：
     - planner-ready handoff 已存在
     - request-contract evidence 已具備
     - follow-up topic 明確允許修改 `tests/**`
     - topic 不再只是 planning-only boundary

## Implement-agent readiness sequence

目前狀態：**not ready for direct `api-client-porting-implementer` execution**

原因不是 family 或 business baseline 不清楚，而是 execution prerequisites 尚未以 repo-visible
方式落檔完成。

### Required sequence before execution

1. 建立 follow-up execution-facing topic
   - 建議 topic 名稱可為：
     - `models-request-gate-execution`
     - 或 `models-request-capture-tests`
   - 該 topic 必須有自己的：
     - `plan/<topic>/<topic>.plan.md`
     - `plan/<topic>/<topic>.step.md`
     - `plan/<topic>/<topic>.spec.md` 或等價的 workflow-compatible spec artifact
     - `analysis/<topic>/requirements.md`
     - `analysis/<topic>/technical-spec.md`

2. 在 follow-up topic 內凍結 allowed file scope
   - 必須明確授權：
     - `tests/unit/request_contract/models_request_gate/**`
   - 必須明確決定：
     - 是否允許修改 `pyproject.toml`
     - 是否允許修改 `uv.lock`
   - 若未授權 `tests/**`，任何 request fixture / request test implementation 都不得開始

3. 產出 planner-ready handoff
   - 至少包含：
     - source API list
     - request contract draft
     - risk classification
     - stop flags
   - 若 method、path、headers、query semantics、body shape 任一仍需猜測，execution 必須阻擋

4. 在 follow-up topic 內凍結 request-only completion gate
   - 明確寫出本輪只做到：
     - intercepted capture / mock strategy
     - request-flow fixtures
     - mock-response answer sets
     - request-contract tests
   - 明確排除：
     - response / error contract
     - `docs/migration-map.md`
     - `docs/porting-ledger.md`
     - `src/mlops_async/**` production implementation

5. 選 execution orchestrator
   - 若上述 follow-up topic 已存在，且目標仍是 request-only 邊界：
     - 優先使用 `python-implementation-workflow`
   - 若後續 topic 明確擴張到 minimal implementation、migration-map、ledger：
     - 再評估是否進 `api-client-porting-implementer`

### Agent entry decision

| Agent / Skill | Ready now? | Why |
| --- | --- | --- |
| `python-implementation-workflow` | not yet | 它需要既存的 execution topic plan；若缺 `plan/<topic>/<topic>.spec.md`，TDD gate 也可能先阻擋 |
| `api-client-porting-implementer` | no | 目前缺 execution topic file scope 與 planner-ready handoff；而且當前目標仍是 request-only |

### Minimum handoff package for the next agent

下一個 agent 在開始前，至少應被提供：

- current approved planning baseline:
  - `plan/models-request-gate-proof/models-request-gate-proof.plan.md`
  - `analysis/models-request-gate-proof/requirements.md`
  - `analysis/models-request-gate-proof/technical-spec.md`
- target of the next topic:
  - request-only mock/interception execution for `list_models` and `get_model`
- fixed boundaries:
  - no response/error contract
  - no migration-map / ledger
  - no production implementation in `src/mlops_async/**`
- required follow-up outputs:
  - execution-facing topic plan/spec/step docs
  - planner-ready handoff
  - explicit bootstrap decision

## Cost-of-realization assessment

### Workstream 1 — Topic-local analysis freeze

- Complexity: 低
- Sequencing burden: 低；可直接根據已凍結的 session decisions 落檔
- Integration burden: 低；主要與既有 global porting governance 對齊
- Operational overhead: 低；維護成本主要來自後續 topic 若 drift 時需回補

### Workstream 2 — Request-gate execution readiness

- Complexity: 中
- Sequencing burden: 中；必須等待 source evidence、planner handoff 與 capture strategy 對齊
- Integration burden: 中；涉及 `sasctl` / legacy source、mock artifacts、test strategy 與
  execution-topic bootstrap 決策
- Operational overhead: 中；後續需維護 fixture 與 source baseline traceability

### Workstream 3 — Concrete client readiness

- Complexity: 中到高
- Sequencing burden: 高；若未來要驗證 target runtime call path，需額外 topic 補 fake 或
  concrete client
- Integration burden: 高；會牽涉 `src/mlops_async/**` 與 tests
- Operational overhead: 中；需維護 internal client boundary 與測試 double 策略
- Current topic status: deferred

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo workflow boundary | fits existing architecture | 本 topic 僅建立 analysis / plan artifacts，符合現階段治理導向 |
| Async-first rule | fits existing architecture | 本 topic 不新增 sync fallback 或 runtime code |
| Dependency boundary | fits existing architecture | 本 topic 不新增 runtime dependencies，也不修改 `src/mlops_async/**`、`pyproject.toml`、`uv.lock` |
| Porting governance | fits existing architecture | 與 global porting contract、migration-map-first / ledger-second 規則一致 |
| Stable-library surfaces | fits existing architecture | 本 topic 明確不影響 `README.md`、`VERSION`、release timing |
| Target runtime boundary | fits with prerequisites | 後續若要進 request tests / implementation，仍需 topic 化處理 fake 或 concrete client 問題 |

## Conflicts and rollback-to-alignment triggers

1. **若後續人員把 topic 擴成 full first port**
   - Failing business assumption: 第一個 topic 只需 request-gate proof
   - Technical fact: response / error / ledger work 會改變 artifact scope、測試責任與 stop risk
   - Required action: 回到 business alignment，重新決定 completion boundary

2. **若後續 execution 堅持沒有 concrete client 就不能進行**
   - Failing business assumption: mock-first 足以支撐 request-gate proof
   - Technical fact: 那代表 topic 已漂移到 target runtime verification，而非 planning/request-gate boundary
   - Required action: 回到 alignment，改題或拆出 client-enablement topic

3. **若後續需要修改 `src/mlops_async/**` 或 `tests/**` 才能完成本 topic**
   - Failing business assumption: 本 topic 是 planning-only
   - Technical fact: 這已超出 allowed file scope
   - Required action: 停止並修正 plan / technical spec，不得直接擴 scope

4. **若有人想在本 topic 內先做 `uv add --dev ...` 或修改 `uv.lock`**
   - Failing business assumption: environment bootstrap 已延後到 execution topic
   - Technical fact: dependency / lockfile 變更會讓本 topic 超出 planning-only 邊界
   - Required action: 停止，並把 bootstrap 流程寫入下一個 execution topic plan

## Validation

必要檢查：

1. 下列檔案存在：
   - `analysis/models-request-gate-proof/requirements.md`
   - `analysis/models-request-gate-proof/technical-spec.md`
   - `plan/models-request-gate-proof/models-request-gate-proof.plan.md`
   - `plan/models-request-gate-proof/models-request-gate-proof.step.md`
2. `requirements.md` 明確記錄：
   - actor
   - success signal
   - completion boundary
   - mock-first decision
   - non-goals
3. `technical-spec.md` 明確記錄：
   - allowed file scope
   - requirement traceability
   - deferred prerequisites
   - architecture-compliance results
   - rollback triggers
   - deferred environment bootstrap strategy
   - planned execution artifact layout for mock/interception and fixtures
4. `plan/models-request-gate-proof/models-request-gate-proof.plan.md` 的 analysis-layer routing
   必須與 topic-local analysis files 的存在狀態一致。

建議指令：

```bash
test -f analysis/models-request-gate-proof/requirements.md
test -f analysis/models-request-gate-proof/technical-spec.md
test -f plan/models-request-gate-proof/models-request-gate-proof.plan.md
test -f plan/models-request-gate-proof/models-request-gate-proof.step.md
```

## Stop conditions

若出現以下情況，必須停止並回到 alignment 或 plan repair：

- topic 被要求直接進 implementation
- 有人主張本 topic 必須先補 concrete `HttpClient` implementation
- execution scope 漂移到 `src/mlops_async/**`、`tests/**`、`docs/migration-map.md`、或
  `docs/porting-ledger.md`
- 對 completion boundary、client mode、或 family scope 出現新的矛盾
