---
topic: job-execution-family
type: correction-step
parent_correction: plan/job-execution-family/job-execution-family.post-merge.correction-plan.md
created: 2026-08-10
status: approved
---

# Job Execution Family — Post-merge Correction Step Tracker

## PR #66 Review-Fix Evidence

- [X] ADDRESS: modeled raw `error`, `jobRequest`, and `links` containers now use an
  iterative defensive copy; no nested raw-container validation was added.
- [X] ADDRESS: modeled numeric fields reject non-finite values, including an
  `elapsedTime` decoded as infinity from JSON `1e400`.
- [X] Family unit regressions cover a deeply nested modeled raw object and
  non-finite `elapsedTime` values.
- [ ] Independent focused WSL verification, commit, push, and review-thread
  resolution remain owned by their respective workflow roles.

本 tracker 只追蹤 `job-execution-family` 的 post-merge correction。它不改變
`job-execution-family.plan.md` 與 `.step.md` 的已合併歷史。

## Workflow Stages

- [X] correction-authoring
- [X] correction-review
- [X] creator-alignment
- [X] evidence-check
- [X] human-check: WSL linked-worktree environment exception accepted
- [X] correction-closed

## Correction Steps

- [X] 0. Planning actor 在 Plan-Reviewer `approved` 後、任何 Creator code/test/gate 修改前，完成
  `job-execution-family.post-merge.correction-plan.md` 所定義的 bounded parent-sync closure。
  - 僅可改 parent plan 的 `Current` 為 `merged` 與同 section 的 PR #64/correction-artifact
    historical routing note。
  - parent step tracker 必須保持不變；獨立 Reviewer 未確認 exact diff 前不得進行 Step 1。

- [X] 1. 在 `client.py` 修正 `get_job_state()` 的 request headers。
  - `Accept: text/plain`、`Delegate-Domain: ""` 與 `Content-Type: application/json` 必須同時存在。
  - 保留一個 request、`params={}`、無 body、無 polling/retry/timeout。

- [X] 2. 在 `value_objects.py` 實作 state/stateDetails conjunction。
  - non-null `stateDetails` 沒有合法 `JobState` 時 raise `JobExecutionResponseError`。
  - 不改 `JobState` 六值、public signature 或其他 Job field policy。

- [X] 3. 在 `client.py` 收斂 JSON success decoder 的 recursion boundary。
  - 不遞迴掃描 raw nested containers。
  - 保留 JSON syntax/UTF-8 failure 的 family-local translation 與 modeled shallow parser checks。

- [X] 4. 在兩個 family-local unit-test modules 補三項 correction regression evidence。
  - state request 的 exact headers、text/plain/JobState exact parsing。
  - `stateDetails` without valid state rejection。
  - deep raw nested JSON payload 不觸發 client recursive validator 的 failure/leak。

- [X] 5. 僅更新 listed state request gate local files。
  - mock response 改為 `200 text/plain` text body。
  - assertion 改為 `JobState`；不使用 JSON response oracle。
  - 不修改 shared harness、header family 或 request-flow fixture。

- [X] 6. 以 correction plan 列出的 WSL commands 完成 pytest、Ruff format/check、Pyright 與 Tach。
  - diff 必須只包含 correction plan 所列 writable paths。
  - 將證據交給獨立 Reviewer；不得自行宣告 review approval、commit、push、PR、tag、release 或 cleanup。

## Completed Evidence / Human Acceptance

- 獨立 Reviewer verdict：`approved-with-human-check`。唯一未綠的項目是 WSL 無法解析 Windows
  linked-worktree `.git` pointer 的 shared policy guard；它不是 Job Execution implementation、
  test 或 request-gate failure。
- Human 已明確接受此 WSL linked-worktree environment exception；shared policy guard 的修正
  屬 scope 外，未修改 shared harness。
- 已完成證據：511 passed、coverage 95.76%；Ruff format、Ruff lint、Pyright、Tach 與
  `git diff --check` 均通過。
- `correction-closed` 僅表示 correction 的 creator-alignment、review 與 human-check
  lifecycle 已完整回填；不表示已 commit、push、open PR、merge、tag、release 或 cleanup。

## Closure Condition

parent-sync closure 已由獨立 Reviewer 確認，三個 ADDRESS 已完整處理，無
scope/contract/workflow drift，且 human 已接受唯一 WSL linked-worktree environment exception。
因此此 correction 的 planning lifecycle 已 closed，Main Agent 可另行 route 已授權的
publish/PR；該 action 尚未執行。此 correction merge 後仍不進入 release 或 cleanup。

## Historical Retention Note

本 tracker 為 retained correction audit trail；closure 後不得刪除，亦不得取代 parent artifacts。
