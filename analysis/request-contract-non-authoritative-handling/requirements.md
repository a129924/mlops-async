# request-contract-non-authoritative-handling requirements

## Goal

- 建立一個可執行的 current-truth handling 規則，避免 `tests/unit/request_contract/**`
  中的 non-authoritative surfaces 被後續 `src` implementation 誤讀成 upstream
  endpoint truth。
- 先處理會誤導 implementation 的訊息，不先處理 release、publish、或歷史 worktree
  cleanup。

## Required outcomes

- `projects_tables_link_request_gate` 必須被明確降級為 historical superseded surface，
  不可再作為 current endpoint truth。
- `internal-wrapper-shape-only` 與 `custom-client-shape-only` topics 必須保留為
  repo-local shape baseline，且明確標示不得當 upstream truth。
- repo-visible docs 必須能讓 implementer 先讀到 authority boundary，再決定哪些
  request-contract tests 可以拿來當 shape baseline。
- 若某個 topic 是 pseudo-endpoint 或 pseudo-contract，repo-visible artifacts
  必須能阻止它繼續被當成 implementation baseline。

## Constraints

- 本 topic 必須在新的 managed worktree 上完成，不得在 `dev` 上落地任何 topic
  變更。
- 本 topic 走 implementation workflow lane：
  `create worktree -> plan-finalization -> plan-review -> plan-fix -> final-gate -> implementation -> independent review -> human check`
- 仍有 repo-local shape 價值的 tests 不可直接刪除；只能標示、隔離、或列為
  `delete-candidate`。
- 不得修改 upstream raw spec 檔案。
- 不得實作 `src/mlops_async/**` runtime endpoint。

## Non-goals

- 不清理舊 `request-gate-projects-tables-fixed-path-mvp` worktree。
- 不做 release、commit、push、PR、merge。
- 不全面重寫 repo-local normalized specs。
- 不在本 topic 直接刪除 historical tests 或 plans。

## Deliverables

- 一份 repo-visible non-authoritative handling policy / ledger。
- 更新後的 `request-contract-evidence-matrix.md`，可直接指出 authority class、
  allowed use、與 implementation consumption boundary。
- 受影響 request-contract topics 的明確 non-authoritative metadata 與必要的
  collection / routing guardrails。
