---
topic: release-v0-13-0
phase: review-ready
created: 2026-07-23
---

# release-v0-13-0 — Step Tracking

> Completion gate 只讀取 `## Implementation Steps`。本檔目前位於
> `review-ready`：release metadata implementation 與完整 non-live-E2E local
> validation 均已完成，等待獨立 implementation／code review。

## Planning Artifact Evidence

- [X] 已確認兩個 optional analysis artifacts 均不存在，並寫入具名 semantic warning。
- [X] 已建立 canonical 11 sections 並加入完整 `Stable library metadata`。
- [X] 已鎖定 human-selected `0.13.0`、release range
  `v0.12.0@916934d` exclusive 至 `39a40a22` inclusive、branch／worktree 與
  `dev` <- `chore/andrew/release-v0-13-0` PR routing。
- [X] 已將 executable write inventory exact 限定為兩個 planning artifacts加
  `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`，共六檔。
- [X] 已將既有 formal CI、E2E、TLS plans 鎖為 read-only，並把 formal cleanup 與
  GitHub ruleset／ACL 保持為獨立 authorization lanes。
- [X] Plan review 已依序完成 `review-ready` -> `reviewer-in-progress` ->
  `approved`，並依 `approved` -> `creator-in-progress` 進入 bounded
  implementation；creator work 與獨立 Tester validation 完成後，已依
  `creator-in-progress` -> `review-ready` 轉換，plan 與本 step 的 current
  status 均為 `review-ready`。

## Implementation Steps

- [X] 1. 在 `README.md` 的 `Status` 區段、既有 `v0.12.0` entry 之前新增相鄰的
  `v0.13.0` 英文與繁體中文 release entries，正確摘要 PR #47 至 PR #50，且不把
  insecure-mode success 誤稱為 TLS trust verified。
- [X] 2. 將 `VERSION` 與 `pyproject.toml` 的 project version exact 更新為
  `0.13.0`。
- [X] 3. 執行 `uv lock`，只將 `uv.lock` root `mlops-async` package version 同步為
  `0.13.0`；確認沒有 dependency、source 或 resolution drift。
- [X] 4. 執行 plan 鎖定的 exact local validations：`uv lock --check`、
  `uv sync --frozen`、Ruff format／lint、Pyright、Tach、明確
  `-m "not viya_e2e"` 的 pytest coverage >= 90、selective pre-commit hygiene、
  `git diff --check` 與六檔 path check；不得執行 live E2E。
- [X] 5. 交付 exact 六檔 bounded diff，並只在每項 implementation 與 validation
  實際完成後將對應 checkbox 標為 `[X]`。

## Implementation Evidence

- `uv 0.11.31` 已以 approved user-local exact binary 執行。
- `uv lock --offline` 因本機 cache 缺少 `httpx` 而停止；取得一次 online lock 的
  human authorization 後，以同一 binary 執行不含 `--upgrade`／`--refresh` 的
  `uv lock`。
- `uv.lock` 相對 locked base 的 diff exact 為 root editable `mlops-async`
  version `0.12.0` -> `0.13.0`，共一行刪除、一行新增；dependency、hash、URL、
  source 與 resolution 均無 drift。
- `uv lock --check` 已通過。
- Pre-validation bounded gate 已確認 version sources exact `0.13.0`、
  `git diff --check` 通過，且 locked-base tracked diff 與 non-ignored untracked
  union exact 為本 topic 宣告的六檔。
- 獨立 Tester 使用 exact `uv 0.11.31` 完成 lock／sync；Ruff format／lint PASS；
  Pyright `0 errors, 0 warnings`；Tach PASS；non-live-E2E pytest
  `321 passed, 9 skipped, 1 deselected`，coverage `96.25%`；清除相關 environment
  後 selective pre-commit PASS。
- Final gate 已確認 exact 六檔 write set、三個 version sources exact `0.13.0`、
  `uv.lock` 僅 root editable version 變更，且 tag `v0.13.0` 不存在。
- 本輪未執行 live E2E；External Human / GitHub Gates 全部維持 pending。
- 所有 creator-owned implementation steps 均有 evidence，phase 已依
  `creator-in-progress` -> `review-ready` 進入獨立 implementation／code review
  boundary。

## External Human / GitHub Gates

- [ ] Release implementation 已通過獨立 implementation／code review，且 reviewer
  handoff 沒有 blocking issue。
- [ ] Release changes 已 commit／push，並以 exact base `dev`、head
  `chore/andrew/release-v0-13-0` 建立 PR。
- [ ] Release PR 最新 head 的 `python-ci` 實際成功。
- [ ] Release PR 已取得 qualified non-author reviewer 的 GitHub `APPROVED`。
- [ ] Release PR unresolved review threads exact 為 `0`。
- [ ] Release PR head 已與最新 `dev` up to date，且同步後 required checks 仍成功。
- [ ] Release PR 已 merge，且 Main Agent 已確認實際 merge commit。
- [ ] Merge 後已取得一份新的 human authorization，annotated tag `v0.13.0` 已 exact
  指向 release PR merge commit 並成功 push。
- [ ] Annotated tag 完成後已執行 GitHub Release human check；只有 human 明確要求建立
  且實際建立成功時，才可另行記錄 GitHub Release completed。
- [ ] Release topic cleanup 已依 release truth 另行處理；未順帶清理 formal CI、E2E
  或 TLS topic。
- [ ] Formal CI cleanup 與 GitHub ruleset／ACL mutation 仍各自依獨立 authorization
  處理；不得用本 release 的 approval、merge 或 tag authorization 代替。
