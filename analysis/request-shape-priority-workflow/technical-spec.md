# Request Shape Priority Workflow Technical Spec

## Source requirements

本技術規格落實下列需求來源：

- `analysis/request-shape-priority-workflow/requirements.md`

全域 workflow / planning guardrails 來自：

- `AGENTS.md`
- `docs/project-guidelines.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`

## Goal

把 docs-first session-entry model、cross-family dispatch board、family queue 與
Observer / Dispatcher routing rules 轉成 repo-visible technical contract，使後續 session 能在
不回溯歷史對話的前提下，按固定入口與 phase/gate 進行 request-shape 工作。

## Current state summary

目前 repo 已有：

- `tests/unit/request_contract/models_request_gate/**` 作為 shape-only 模板
- `tests/unit/request_contract/projects_request_gate/**` 作為下一批 family
- `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md` 對 `tables` 提供 `BLOCKED` precedent

但目前缺少一組 docs-first session-entry surface，讓新 session 可以不先翻 `plan/**` /
`analysis/**` 就恢復：

- family queue
- blocked family policy
- Observer / Dispatcher 邊界
- cross-family dispatch board 的用途

## Allowed file scope

後續 implementation 只允許新增或更新：

- `docs/request-shape-priority-workflow/README.md`
- `docs/request-shape-priority-workflow/standards.md`
- `docs/request-shape-priority-workflow/checklist.md`
- `analysis/request-shape-priority-workflow/requirements.md`
- `analysis/request-shape-priority-workflow/technical-spec.md`
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`

下列路徑在本 topic 中不得修改：

- `src/**`
- `tests/**`
- `pyproject.toml`
- `uv.lock`
- `README.md`
- `VERSION`

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `docs/request-shape-priority-workflow/README.md` | 作為新 session 第一入口，定義讀取順序與 artifact hierarchy |
| `docs/request-shape-priority-workflow/standards.md` | 編碼 Observer / Dispatcher 的角色、dispatch 規則、phase / gate 邊界與 stop conditions |
| `docs/request-shape-priority-workflow/checklist.md` | 作為跨 family dispatch board 與 resume checklist，不承擔 topic-local completion gate |
| `requirements.md` | 凍結 docs-first session-entry、queue、blocked policy、與角色邊界的業務基線 |
| `technical-spec.md` | 將需求映射成 exact artifact roles、entry precedence、queue data model、與 drift handling |
| `plan.md` | 提供本 topic 的 repo-visible execution contract |
| `step.md` | 只追蹤本 topic 自己的 artifact 建立與 review completion |

## Requirement-to-technical mapping

| Requirement | Technical realization | Dependencies | Status |
| --- | --- | --- | --- |
| Canonical session-entry artifacts freeze | 建立 `docs/request-shape-priority-workflow/{README,standards,checklist}.md` 三件組，並在 docs / analysis / plan 中一致宣告其 requiredness | `AGENTS.md`, `plan/topic-plan-contract.md` | feasible |
| README requiredness | 將 `README.md` 設為新 session 第一入口，明寫缺件時不得以 `plan/**` / `analysis/**` 補位 | docs trio | feasible |
| Fixed entry order | 在 `README.md` 與 `standards.md` 重複固定的 1-2-3 讀取順序 | docs trio | feasible |
| Workflow artifacts are not primary entry | 在 `README.md`、requirements、technical-spec、plan 中一致聲明 `analysis/**` / `plan/**` 是 secondary workflow artifacts | existing analysis / plan surfaces | feasible |
| Checklist as cross-family dispatch board | `checklist.md` 只記錄 family queue、phase、next dispatch、blocked reason、resume checks；不得出現 implementation-step completion gate | `plan/agent-handoff-workflow.md` for contrast with `*.step.md` | feasible |
| Family queue freeze | 在 docs / analysis / plan 鎖定 `models -> projects -> tables(BLOCKED)` | existing models/projects/tables precedents | feasible |
| Observer / Dispatcher role boundary | `standards.md` 收錄使用者提供的 dispatch prompt 規則，轉成 repo-visible contract | user-supplied prompt | feasible |
| Primary request-shape surface freeze | 在 `standards.md` 與 technical-spec 明確把 `tests/unit/request_contract/**` 定義為主面，`tests/contracts` 定位為 guard surface | current repo test layout | feasible |

## Required technical tasks

1. **建立 docs-first session-entry surface**
   - 新增 `README.md`、`standards.md`、`checklist.md`
   - 讓 `README.md` 承擔第一入口與 artifact hierarchy
   - 讓 `standards.md` 承擔正式 dispatch contract
   - 讓 `checklist.md` 承擔 cross-family queue / phase board

2. **凍結 artifact precedence**
   - 在 docs / analysis / plan 中一致聲明：
     - docs trio = primary entry
     - `analysis/**` / `plan/**` = workflow artifacts
   - 明寫 session 只有在 docs trio 指示時才回讀 workflow artifacts

3. **編碼 family queue 與 blocked policy**
   - 在 docs / analysis / plan 中一致記錄：
     - `models` first
     - `projects` second
     - `tables` blocked
   - 明寫 `tables` 不得自動解鎖

4. **分離 dispatch board 與 step tracker**
   - `docs/.../checklist.md` 只處理 queue / resume / next dispatch
   - `plan/.../*.step.md` 只處理本 topic completion gate
   - 兩者不得互相替代

5. **將使用者 prompt 轉成 repo-visible dispatch contract**
   - 將 role、allowed subAgents、禁止事項、dispatch 規則、output structure 寫入 `standards.md`
   - 讓後續 session 不需要重新依賴聊天訊息

## Deferred prerequisites and explicit non-work

以下事項不在本 topic：

1. `models` / `projects` request-contract tests 內容改寫
2. `tables` family 解鎖或新規格制定
3. `src/**` 或 dependency 檔變更
4. release / publish automation

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo language default | fits existing architecture | docs / analysis / plan 以繁體中文撰寫 |
| Session-entry hierarchy | compatible | docs-first 不取代既有 analysis / plan，只重排進場順序 |
| Step-tracker contract | compatible | `checklist.md` 不接管 `*.step.md` 的 completion gate |
| Existing family precedents | compatible | `models`、`projects`、`tables` 的排序與 blocked state 都有 repo-visible precedent |
| Production boundary | compatible | 不觸碰 `src/**` 或 tests 行為 |

## Conflicts and rollback-to-alignment triggers

1. **若後續工作要求新 session 直接從 `plan/**` / `analysis/**` 起步**
   - Required action: 停止，回到 docs-first entry order

2. **若 `checklist.md` 被要求承載單一 topic implementation steps**
   - Required action: 停止，改回該 topic 的 `*.step.md`

3. **若 `tables` 被要求在無人工決策下納入 queue**
   - Required action: 停止並升級 `human-check`

4. **若 `tests/contracts` 被要求升格為主 request-shape surface**
   - Required action: 停止並回到既有 `tests/unit/request_contract/**` baseline

## Validation

必要檢查：

1. 下列文件存在：
   - `docs/request-shape-priority-workflow/README.md`
   - `docs/request-shape-priority-workflow/standards.md`
   - `docs/request-shape-priority-workflow/checklist.md`
   - `analysis/request-shape-priority-workflow/requirements.md`
   - `analysis/request-shape-priority-workflow/technical-spec.md`
   - `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
   - `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`
2. `README.md`、`standards.md`、`checklist.md` 一致記錄：
   - fixed entry order
   - docs-first hierarchy
   - queue / blocked policy
3. `technical-spec.md`、`plan.md`、`step.md` 沒有把 checklist 當作 topic-local completion gate
4. `tests/contracts` 沒有被描述為主 request-shape surface

建議檢查指令：

```bash
test -f docs/request-shape-priority-workflow/README.md
test -f docs/request-shape-priority-workflow/standards.md
test -f docs/request-shape-priority-workflow/checklist.md
test -f analysis/request-shape-priority-workflow/requirements.md
test -f analysis/request-shape-priority-workflow/technical-spec.md
test -f plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md
test -f plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md
```

## Stop conditions

若出現以下情況，必須停止並回到 `human-check`：

- 要求跳過 docs-first session entry
- 要求在本 topic 內解鎖 `tables`
- 要求重開 family queue 順序
- 要求把 `checklist.md` 改成 topic-local step tracker
- 要求本 topic 擴張到 `src/**`、tests 內容、或 release surface
