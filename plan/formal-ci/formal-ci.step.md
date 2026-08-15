---
topic: formal-ci
phase: plan-review
created: 2026-07-22
---

# formal-ci — Step Tracking

> Completion gate 只讀取 `## Implementation Steps`。只有所有 implementation
> checkboxes 均為 `[X]`，才可把 implementation pass 移到 `review-ready`。

## Planning Artifact Evidence

- [X] 已確認兩個 optional analysis artifacts 均不存在。
- [X] 已依 optional analysis layer absent routing 寫入 semantic warning。
- [X] 已建立 canonical 11-section topic plan，current status 為 `review-ready`，可進入
  獨立 plan review。
- [X] 已將 artifact inventory 限定為 topic plan、step tracker 與 formal CI workflow。

## Implementation Steps

- [X] 1. 建立 `.github/workflows/ci.yml`，設定 exact `dev` PR／push triggers、
  `contents: read`、cancel-in-progress concurrency、單一 `python-ci` job 與
  `ubuntu-24.04` runner。
- [X] 2. 以鎖定的完整 SHA 使用 `actions/checkout` 與 `astral-sh/setup-uv`，由
  `setup-uv` 管理 uv `0.11.31` 及 Python `3.10`，且不加入 `actions/setup-python`。
- [X] 3. 以 frozen sync／run 執行 exact Ruff format／lint、Pyright、Tach 及明確排除
  `viya_e2e` 的 pytest coverage >= 90 gates。
- [X] 4. 在 explicit gates 後執行 selective pre-commit hygiene；`SKIP` 只含
  `ruff,ruff-format,tach-check,pytest,coverage-check,pyright-strict`，其餘 hygiene
  hooks 必須實際執行。
- [X] 5. 更新本 tracker 並交付 exact bounded diff；不得把 CI green、GitHub
  `APPROVED`、ruleset 或 release 標示為 implementation evidence。

## External Human / GitHub Gates

- [ ] CI PR 實際產生並通過 `python-ci` check。
- [ ] CI PR 取得 qualified non-author reviewer 的 GitHub `APPROVED` review。
- [ ] Workflow merge 後，如需寫入 ruleset，Main Agent 已另取 explicit authorization；
  未授權不得執行。
- [ ] 後續 release workflow 自行處理 release version／branch／tag 與 release PR；本 CI
  topic 不得代為完成或勾選。
