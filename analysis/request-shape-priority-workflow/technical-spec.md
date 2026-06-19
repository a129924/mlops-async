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

把 docs-first session-entry model、session resume checklist template、global surface/API
implementation board、與 implementation standards 轉成 repo-visible technical contract，使後續
session 能在不回溯歷史對話的前提下，恢復實作順序、共享接口狀態、與注入提示。

## Current state summary

目前 repo 已有：

- `tests/unit/request_contract/models_request_gate/**` 作為 shape-only 模板
- `tests/unit/request_contract/projects_request_gate/**` 作為 `modelRepository/projects` precedent
- `plan/request-gate-projects-tables/request-gate-projects-tables.plan.md` 對 `modelRepository` 的 HATEOAS tables 提供 `BLOCKED` precedent
- `docs/api-endpoints/swagger-spec/openapi-complete.yaml` 與 markdown reference 顯示 repo 真實 surface 至少包含 `SASLogon`、`modelRepository`、`casManagement`、`jobExecution`

但現有 docs surface 仍有三個 drift：

1. `checklist.md` 把 session resume checklist 寫成共享可勾選區
2. `checklist.md` 仍用抽象 family 名稱，缺少 `surface + API` 級 implementation board 與注入 hint
3. `standards.md` 偏成 workflow handoff prompt，而不是 implementation standards

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
| `docs/request-shape-priority-workflow/README.md` | 作為新 session 第一入口，定義讀取順序、artifact hierarchy 與共享文件警告 |
| `docs/request-shape-priority-workflow/standards.md` | 記錄 implementation sequencing rules、surface naming rules、artifact precedence、blocked policy、board / step 分工與 request-shape scope |
| `docs/request-shape-priority-workflow/checklist.md` | 同時承擔 session resume checklist template 與 global surface/API implementation board；不承擔 topic-local completion gate |
| `requirements.md` | 凍結 docs-first entry、template-only resume policy、surface board、與 implementation standards 的業務基線 |
| `technical-spec.md` | 將需求映射成 exact artifact roles、board schema、entry precedence、與 drift handling |
| `plan.md` | 提供本 topic 的 repo-visible execution contract |
| `step.md` | 只追蹤本 topic 自己的 artifact correction completion 與 review readiness |

## Requirement-to-technical mapping

| Requirement | Technical realization | Dependencies | Status |
| --- | --- | --- | --- |
| Canonical session-entry artifacts freeze | 保留 `docs/request-shape-priority-workflow/{README,standards,checklist}.md` 三件組，並在 docs / analysis / plan 中一致宣告其 requiredness | `AGENTS.md`, `plan/topic-plan-contract.md` | feasible |
| README requiredness | 將 `README.md` 設為新 session 第一入口，明寫缺件時不得以 `plan/**` / `analysis/**` 補位 | docs trio | feasible |
| Fixed entry order | 在 `README.md` 與 `standards.md` 固定相同的 1-2-3 讀取順序 | docs trio | feasible |
| Workflow artifacts are not primary entry | 在 `README.md`、requirements、technical-spec、plan 中一致聲明 `analysis/**` / `plan/**` 是 secondary workflow artifacts | existing analysis / plan surfaces | feasible |
| Shared resume checklist must be template-only | 將 resume checklist 改寫為可複製模板，不在共享文件直接勾選 | `checklist.md` | feasible |
| Global surface/API implementation board | 在 `checklist.md` 新增 API 級 board，固定欄位為 `state`、`surface`、`api`、`order`、`injection hint`、`notes` | current repo surface truth | feasible |
| Surface / API queue freeze | 在 docs / analysis / plan 鎖定具名 surface queue，並把 blocked / out-of-scope surface 明確列入 board | tests, swagger, and plan precedents | feasible |
| Standards must stay implementation-focused | 把 `standards.md` 改寫成 implementation standards，移除 persona / allowed-subAgent / output-style prompt 語氣 | user correction baseline | feasible |
| Primary request-shape surface freeze | 在 `standards.md` 與 technical-spec 明確把 `tests/unit/request_contract/**` 定義為主面，`tests/contracts` 定位為 guard surface | current repo test layout | feasible |

## Required technical tasks

1. **修正 README artifact 描述**
   - 把 `standards.md` 的角色改成 implementation standards
   - 把 `checklist.md` 的角色改成 template + global board
   - 補上共享勾選污染警告

2. **重構 `checklist.md`**
   - 把 `Session resume checklist` 改成 template-only 區塊
   - 明寫複製到 session-local artifact 的使用方式
   - 新增 `Global surface/API implementation board`
   - 對 `modelRepository`、`jobExecution`、`casManagement`、`SASLogon` 的實際 API 寫入狀態、queue、與 injection hint
   - 把 `modelRepository/projects -> tables-link surface` 與 `casManagement/.../tables` 明確拆開

3. **重寫 `standards.md`**
   - 移除 prompt / persona / allowed-subAgent / output-preference 內容
   - 保留實作順序、artifact precedence、board / step 邊界、blocked policy、request-shape scope

4. **同步修正 analysis layer**
   - `requirements.md` 與 `technical-spec.md` 都要反映：
     - template-only resume policy
     - `surface + API` 級 board
     - implementation-focused `standards.md`
     - `tables` 不再作為抽象 queue 單位

5. **同步修正 plan / step**
   - `plan.md` 與 `step.md` 的 implementation steps、artifact roles、validation wording 必須和修正後的 docs/analysis 一致
   - 由於本輪修正尚未重新獨立 review，`step.md` 的 `Independent review` 應回到未完成

## Deferred prerequisites and explicit non-work

以下事項不在本 topic：

1. `models` / `projects` request-contract tests 內容改寫
2. `modelRepository/projects -> tables-link surface` 解鎖或新規格制定
3. `src/**` 或 dependency 檔變更
4. release / publish automation

## Architecture-compliance self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo language default | fits existing architecture | docs / analysis / plan 以繁體中文撰寫 |
| Session-entry hierarchy | compatible | docs-first 不取代既有 analysis / plan，只重排進場順序 |
| Shared board model | compatible | `checklist.md` 提供共享排序與注入提示，但不接管 `*.step.md` |
| Existing surface precedents | compatible | `modelRepository/models`、`modelRepository/projects` 與 HATEOAS tables blocked state 都有 repo-visible precedent |
| Production boundary | compatible | 不觸碰 `src/**` 或 tests 行為 |

## Conflicts and rollback-to-alignment triggers

1. **若後續工作要求新 session 直接從 `plan/**` / `analysis/**` 起步**
   - Required action: 停止，回到 docs-first entry order

2. **若共享 `checklist.md` 被直接當成勾選真值**
   - Required action: 停止，改回 template-only policy

3. **若 `checklist.md` 被要求承載單一 topic implementation steps**
   - Required action: 停止，改回該 topic 的 `*.step.md`

4. **若 `standards.md` 被重新寫成 prompt / persona**
   - Required action: 停止，改回 implementation standards

5. **若 `modelRepository/projects -> tables-link surface` 或 `jobExecution/jobs/state` 被要求在無人工決策下納入 ready queue**
   - Required action: 停止並升級 `human-check`

6. **若 `tests/contracts` 被要求升格為主 request-shape surface**
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
   - template-only resume policy
   - `surface + API` 級 implementation board
   - `tables` 不再作為抽象 queue 單位
3. `standards.md` 不再包含 persona、subAgent 名單、或 output-preference prompt wording
4. `technical-spec.md`、`plan.md`、`step.md` 沒有把 checklist 當作 topic-local completion gate
5. `tests/contracts` 沒有被描述為主 request-shape surface

建議檢查指令：

```bash
test -f docs/request-shape-priority-workflow/README.md
test -f docs/request-shape-priority-workflow/standards.md
test -f docs/request-shape-priority-workflow/checklist.md
rg -n "subAgent|Observer / Dispatcher|Output preference" docs/request-shape-priority-workflow/standards.md
```

## Stop conditions

若出現以下情況，必須停止並回到 `human-check`：

- 要求跳過 docs-first session entry
- 要求在本 topic 內解鎖 `modelRepository/projects -> tables-link surface` 或 `jobExecution/jobs/state`
- 要求重開 `surface + API` queue 順序
- 要求把共享 template 改成共享勾選真值
- 要求把 `standards.md` 改回 handoff prompt
- 要求本 topic 擴張到 `src/**`、tests 內容、或 release surface
