# Request Shape Priority Workflow

## Purpose

本目錄是 `request-shape-priority-workflow` topic 的 **canonical session-entry surface**。
新 session 進入此 topic 時，必須先讀這組文件，再決定是否需要回讀 `analysis/**` 或
`plan/**`。

本 topic 的目的是把 request-shape 工作從「邊抓 shape、邊改流程、邊等 review」的混合模式，
收斂成可排序、可注入、可 review、可停住的固定 workflow。

## Required entry order

新 session 的固定進場順序如下：

1. 讀 `docs/request-shape-priority-workflow/README.md`
2. 讀 `docs/request-shape-priority-workflow/standards.md`
3. 讀 `docs/request-shape-priority-workflow/checklist.md`

不得跳過上述順序。

## Entry hierarchy

- `docs/request-shape-priority-workflow/README.md`
  - 第一入口，說明此 topic 的讀取順序、artifact hierarchy 與回讀規則。
- `docs/request-shape-priority-workflow/standards.md`
  - request-shape `surface + API` 的實作標準、blocked policy、與 artifact 責任分界。
- `docs/request-shape-priority-workflow/checklist.md`
  - session resume checklist template 與全域 surface/API implementation board。

## Non-entry artifacts

以下 artifacts 是 workflow 工件，不是新 session 的 primary entry：

- `analysis/request-shape-priority-workflow/requirements.md`
- `analysis/request-shape-priority-workflow/technical-spec.md`
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
- `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`

只有在 session-entry docs 明確要求，或需要處理 planning / review / audit 時，才回讀這些檔案。

## Topic scope

本 topic 只負責：

- 凍結 request-shape `surface + API` 實作順序
- 把 queue 單位固定成明確的 base API surface，而不是抽象 family 名稱
- 凍結 session-entry contract
- 凍結全域 implementation board 的角色與用途
- 凍結 `checklist.md` 與 `*.step.md` 的責任分界

本 topic 不負責：

- `src/**` 實作
- request-contract tests 的功能擴張
- response / error contract
- release workflow

## Shared-file warning

`docs/request-shape-priority-workflow/checklist.md` 是共享文件。

- 其中的 session resume checklist 只是一份 **template**
- 不得直接在共享文件上打勾，避免多個 session 互相污染狀態
- 若當前 session 需要勾選 resume checklist，必須先複製到自己的 topic-local notes、handoff、
  或 session artifact，再在複本上操作

## When to read workflow artifacts

若 session 需要：

- 補寫或修正業務需求基線，回讀 `analysis/request-shape-priority-workflow/requirements.md`
- 判斷實作面與 artifact 責任，回讀 `analysis/request-shape-priority-workflow/technical-spec.md`
- 審查或執行 topic plan，回讀 `plan/request-shape-priority-workflow/request-shape-priority-workflow.plan.md`
- 檢查本 topic 自己的 completion gate，回讀 `plan/request-shape-priority-workflow/request-shape-priority-workflow.step.md`

## Missing-doc rule

若 `README.md`、`standards.md`、`checklist.md` 任一缺失：

- 直接標記為 planning insufficiency
- 不得把 `plan/**` 或 `analysis/**` 自動升格為新的 session entry
- 必須先補齊 session-entry docs，再繼續後續 workflow
