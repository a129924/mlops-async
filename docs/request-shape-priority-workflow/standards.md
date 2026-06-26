# Request Shape Priority Workflow Standards

## Purpose

本文件定義 `request-shape-priority-workflow` 的 **實作標準**。

它負責固定：

- session-entry 後的 artifact precedence
- `surface + API` 實作順序
- blocked surface policy
- `checklist.md` 與 `*.step.md` 的責任分界
- request-shape 主測試面

本文件不是 workflow handoff prompt，也不是角色扮演腳本。

## Session-entry and artifact precedence

新 session 進入本 topic 時，固定先讀：

1. `docs/request-shape-priority-workflow/README.md`
2. `docs/request-shape-priority-workflow/standards.md`
3. `docs/request-shape-priority-workflow/checklist.md`

`analysis/**` 與 `plan/**` 是 workflow artifacts，不是 primary entry。

只有在下列情況才回讀 workflow artifacts：

- 需要理解需求基線：讀 `analysis/request-shape-priority-workflow/requirements.md`
- 需要理解技術責任：讀 `analysis/request-shape-priority-workflow/technical-spec.md`
- 需要審查或套用 topic plan：讀 `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
- 需要判斷本 topic completion gate：讀 `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`

## Implementation sequencing rules

### Surface naming rule

workflow board 的 queue 單位固定為 `surface + API`。

規則：

- `surface` 必須使用明確的 base API namespace，不得使用抽象 family 名稱
- `tables` 不得單獨當作 queue 單位；必須明寫是哪一套 surface
- `modelRepository/projects -> tables-link surface` 與 `casManagement/.../tables` 必須視為不同 surface

範例：

- `modelRepository/models`
- `modelRepository/projects`
- `modelRepository/projects/champion`
- `modelRepository/projects -> tables-link surface`
- `jobExecution/jobRequests/jobs`
- `jobExecution/jobs`
- `casManagement/dataSources/tables`

### Surface order

request-shape queue 順序以共享 board 內的 `Order` 欄位為準。

目前固定採用下列 surface 流向：

1. `modelRepository/models`
2. `modelRepository/models/content`
3. `modelRepository/projects`
4. `modelRepository/projects/champion`
5. `modelRepository/projects -> tables-link surface`
6. `jobExecution/jobRequests/jobs`
7. `jobExecution/jobs`
8. `jobExecution/jobs/state`

### API order

API 級順序與建議注入內容以 `docs/request-shape-priority-workflow/checklist.md` 的
`Global surface/API implementation board` 為準。

規則：

- session 需要選擇下一個實作接口時，必須從 board 由上而下判讀
- 若前一列仍未完成、仍 blocked、或仍待人工決策，不得任意跳到下一列
- 若需要把 queue 切得更細，應在 board 新增 API 列，而不是繞過既有順序

### Blocked policy

Blocked surfaces remain `BLOCKED` until a new human decision is recorded:

- `modelRepository/projects -> tables-link surface`

Do not automatically:

- unlock a blocked surface
- rewrite the HATEOAS / fixed-path strategy for `modelRepository/projects -> tables-link surface`
- expand `jobExecution/jobs/state` from its bounded request-only / shape-only lane into a polling / state-machine gate
- treat the completed `jobExecution/jobs/state` request gate as permission to redefine broader polling semantics
- move a blocked surface back into the general ready queue

下列 surface 必須保留為 `OUT-OF-SCOPE`，除非人類重新定義 workflow 範圍：

- `casManagement/dataSources/tables`
- `casManagement/caslibs/tables/state`
- `SASLogon/oauth/token`

## Board and step-tracker boundaries

### `checklist.md`

`docs/request-shape-priority-workflow/checklist.md` 只有兩個用途：

1. `Session resume checklist template`
2. `Global surface/API implementation board`

規則：

- shared `checklist.md` 中的 resume checklist 不得直接打勾
- 若 session 需要勾選，必須先複製到自己的 topic-local artifact
- implementation board 是共享真值表面，可用來表示 `surface + API` 的進度與注入 hint

### `*.step.md`

各 topic 的 `plan/<topic>/<topic>.step.md` 仍是唯一的 topic-local completion gate。

規則：

- `*.step.md` 用來追蹤單一 topic 的 implementation steps
- `checklist.md` 不得承擔 topic-local completion gate
- implementation board 也不得取代 `*.step.md`

## Request-shape scope law

request-shape 主測試面固定為：

- `tests/unit/request_contract/**`

`tests/contracts` 只保留：

- import / contract policy guard
- 非主要 request-shape implementation surface

不得把 `tests/contracts` 升格成目前 workflow 的 request-shape 主戰場。

## Injection-hint usage

`checklist.md` 中每個 API 列都可提供 `Injection hint`。

這些 hint 的用途是：

- 指定新 session 應優先注入哪些 artifacts / 語意
- 降低多 session 在同一 `surface + API` 上重新摸索的成本
- 讓人類能明確點名下一個要做的接口

`Injection hint` 是提示，不是 completion gate，也不是架構重定義 surface。

## Stop conditions

出現以下任一條件，必須停止並回到 `human-check`：

- session-entry docs 缺件
- `surface + API` queue 被要求跳步
- `modelRepository/projects -> tables-link surface` 被要求在無人工決策下直接推進
- `jobExecution/jobs/state` is expanded into polling / state-machine workflow without a new human decision
- `tests/contracts` 被要求升格成主 request-shape surface
- `checklist.md` 被要求改成 topic-local gate
- 工作漂移到 `src/**`、request-contract tests 內容、或 release surface
