# Formal CI Topic Plan

> **Semantic warning — optional analysis layer absent**：
> `analysis/formal-ci/requirements.md` 與 `analysis/formal-ci/technical-spec.md`
> 均不存在。本 plan 依 Planner 已核准的 bounded contract、locked base 與 repository
> current truth authoring；沒有可優先套用的 optional analysis layer。此警告不代表
> implementation、CI run 或 GitHub approval 已完成。

## Goal / Outcome

- 在 targeting `dev` 的 pull request 與 `dev` push 建立正式 GitHub Actions CI。
- workflow 只提供一個穩定且可供後續 ruleset 引用的 check context：`python-ci`。
- CI 以 frozen dependency state 執行 Ruff format／lint、Pyright、Tach、明確排除 live
  E2E 的 pytest coverage gate，以及未被前述 gates 重複涵蓋的 pre-commit hygiene。
- Repository-visible implementation result 是 `.github/workflows/ci.yml`。CI PR 的實際
  green run 與 qualified non-author GitHub `APPROVED` review 是 human／GitHub boundary，
  不得由 plan 或 local validation 代替。

## Scope

- **In scope**：
  - 建立 `.github/workflows/ci.yml`。
  - trigger 僅限 targeting `dev` 的 `pull_request` 與 `dev` 的 `push`。
  - 建立單一 `python-ci` job／check context並執行本 plan 鎖定的 Python gates。
  - 維護本 topic 的 plan 與 step tracker。
- **Out of scope**：
  - GitHub ruleset、branch protection、required check 或 approval policy 的實際寫入。
  - release PR 的版本、branch、tag、release notes、發版內容或建立／合併。
  - `README.md`、`VERSION`、`pyproject.toml`、`uv.lock` 的修改。
  - secrets、live E2E、live integration 與 `config/.env.test` 的讀取或使用。
  - 測試、production code、dependencies、repository hooks 或其他 workflow 的修改。

## Locked Decisions

- Base SHA：`fbbae8678eb75cf008d66c191f0595b645efc0d8`。
- Branch：`ci/andrew/formal-ci`。
- Managed worktree：`D:\code\python\mlops-async.worktrees\agent-20260722-formal-ci`。
- 本 topic 不涉及 stable-library surfaces；不修改 `README.md`、`VERSION`、release
  metadata，也不執行 release。
- Workflow triggers 固定為 targeting `dev` 的 `pull_request` 與 `dev` 的 `push`。
- Top-level permissions 固定為 `contents: read`，不得增加 write permission。
- Concurrency 以同 workflow 與 ref 分組，並設定 `cancel-in-progress: true`。
- Runner 固定為 `ubuntu-24.04`；只允許一個 job，job id 與顯示名稱均為
  `python-ci`，使 required check context 穩定為 `python-ci`。
- Actions 必須以完整 commit SHA pin：
  - `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1`（`v7.0.1`）。
  - `astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9`（`v9.0.0`）。
- `setup-uv` 同時管理 uv 與 Python，固定 `version: "0.11.31"`、
  `python-version: "3.10"`。
- 不使用 `actions/setup-python`。若 `setup-uv` 無法提供鎖定的 Python 3.10，停止並
  回報 blocker；經另行明確討論後才能改變此決策，不得自行加入 setup-python。
- Dependency install 固定使用 `uv sync --frozen`；所有 `uv run` gates 加上
  `--frozen`，不得更新 `uv.lock` 或動態解鎖 dependency resolution。
- 明確 gates 與命令固定為：
  - `uv run --frozen python -m ruff format --check .`
  - `uv run --frozen python -m ruff check .`
  - `uv run --frozen python -m pyright`
  - `uv run --frozen python -m tach check`
  - `uv run --frozen python -m pytest -m "not viya_e2e" --cov=src/mlops_async --cov-fail-under=90 --cov-report=term-missing --cov-report=json:.coverage-reports/coverage.json`
- Pre-commit hygiene 固定使用
  `uv run --frozen python -m pre_commit run --all-files --show-diff-on-failure`；該 step
  的 `SKIP` exact hook IDs 是
  `ruff,ruff-format,tach-check,pytest,coverage-check,pyright-strict`。這些 hooks 只能因
  等價或更嚴格的 explicit gates 已在同一 job 先行執行而 skip；這是去除重複執行，
  不是 gate bypass。其餘 `check-local-absolute-paths`、`trailing-whitespace`、
  `end-of-file-fixer`、`check-yaml`、`check-merge-conflict`、
  `check-added-large-files` 必須實際執行。
- Ruff、Pyright、Tach、pytest 與 pre-commit 固定使用 `python -m` launcher。
- CI 不注入 secrets，不設定 live E2E opt-in，不讀 `config/.env.test`，pytest 明確以
  `-m "not viya_e2e"` 排除 live E2E。
- CI PR 必須取得 GitHub 上實際的 `python-ci` green run；local gates 不能替代。
- Qualified non-author reviewer 的 GitHub `APPROVED` 是 approval requirement 的必要
  human evidence；author self-review、comment、local reviewer verdict 或 plan
  `approved` 均不能替代。

## Boundaries / Exclusions

- Planning actor 只 author 本 plan 與 step tracker，不建立 workflow、不 commit、不 push、
  不開 PR，也不修改 GitHub settings。
- Implementer 只可建立 `.github/workflows/ci.yml` 並依 tracker 記錄 creator work；
  不得修改 scope 外檔案。
- Reviewer 獨立核對 workflow，且不得把尚未發生的 GitHub run 或 approval 標示完成。
- Main Agent 擁有 publish、PR routing 與 post-merge orchestration；workflow merge 後若要
  寫入 GitHub ruleset，必須另取得 explicit human authorization。
- Ruleset bootstrap 前必須確認有 qualified non-author reviewer 可提供 GitHub
  `APPROVED`；不得用 topic author 或 agent verdict 假冒此 requirement。
- Release version、release branch、release tag 與 release PR payload 完全屬另一 topic。
- 不讀取、不列印、不 diff、不 stage `config/.env.test`；不執行 live E2E。
- 若 implementation 需要任何未列於 `Artifact Paths` 的 repo-visible 寫入，停止並交
  Main Agent 重新對齊，不得自行擴張。

## Status / Allowed Transitions

- **Current**：`review-ready`。
- **Execution model**：目前只有 planning artifacts 完成，可進入獨立 plan review；
  此狀態不代表 workflow 已實作、CI 已 green、PR 已批准、ruleset 已啟用或 release
  已準備。Plan review 通過後以 canonical `approved` -> `creator-in-progress` 路由實作。
- **Allowed transitions**：
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes：

- 本 topic 不宣告 `merged` -> `released`，因為沒有 release action。
- Plan approval 後先回到 `creator-in-progress`；implementation steps 全部完成後，才能
  再次進入 `review-ready`。
- CI PR 的實際 `python-ci` green run 與 GitHub `APPROVED` 是 publish／merge boundary，
  不屬於 planning artifact authoring evidence。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/formal-ci/formal-ci.plan.md` | Planning actor | Repo-visible execution contract |
| Topic step tracker | `plan/formal-ci/formal-ci.step.md` | Planning actor，後續由 Implementer 更新 | Implementation completion gate 與 workflow evidence |
| Formal CI workflow | `.github/workflows/ci.yml` | Implementer | `dev` PR／push 的單一 `python-ci` check implementation |

- 上表是本 topic 唯一 executable artifact inventory。
- 本 topic 不修改 `README.md`、`VERSION` 或 `.github/copilot-instructions.md`。
- GitHub ruleset 是 external setting，不是 repo-visible artifact；任何寫入都必須在
  workflow merge 後另取 explicit authorization。
- 任何其他 path 的寫入都屬 plan-alignment blocker。

## Implementation Steps

1. 建立 `.github/workflows/ci.yml`，設定 exact `dev` PR／push triggers、
   `contents: read`、cancel-in-progress concurrency、單一 `python-ci` job 與
   `ubuntu-24.04` runner。
2. 以鎖定的完整 action SHAs checkout，並由 `setup-uv` 安裝 uv `0.11.31` 與 Python
   `3.10`；不得加入 `actions/setup-python`。
3. 以 `uv sync --frozen` 同步 frozen environment，依 Locked Decisions 的 exact
   `python -m` commands 執行 Ruff format／lint、Pyright、Tach 與明確排除
   `viya_e2e` 的 coverage >= 90 pytest gate。
4. 所有 explicit gates 成功後執行 selective pre-commit hygiene，只以 exact `SKIP`
   hook IDs 去除同 job 已執行 gates 的重複工作；保留其餘 hygiene hooks 實際執行。
5. 更新 `plan/formal-ci/formal-ci.step.md` 的 implementation checkboxes並交付 bounded
   diff；不得宣稱尚未發生的 GitHub run、approval、ruleset 或 release evidence。

## Validation / Acceptance Checks

- Diff 只包含 `Artifact Paths` 的 exact paths；沒有 secret、E2E、release 或 dependency
  surface drift。
- YAML 可解析，trigger exact 為 targeting `dev` 的 `pull_request` 與 `dev` push。
- Top-level permissions exact 為 `contents: read`；沒有 write permission。
- Concurrency 啟用 `cancel-in-progress: true`，group 同時區分 workflow 與 ref。
- 只有一個 job，job id／顯示名稱／check context 均為 `python-ci`；runner 是
  `ubuntu-24.04`。
- Actions 使用 Locked Decisions 的完整 SHA；uv 與 Python exact pin `0.11.31`、
  `3.10`，且沒有 `actions/setup-python`。
- `uv sync --frozen` 與每個 `uv run --frozen` gate 不改寫 lock state。
- Ruff format／lint、Pyright、Tach 與 non-E2E pytest coverage >= 90 均以鎖定的
  `python -m` command 存在；pytest 明確排除 `viya_e2e`。
- Pre-commit `SKIP` 只含
  `ruff,ruff-format,tach-check,pytest,coverage-check,pyright-strict`，且在對應 explicit
  gates 後執行；其他 configured hygiene hooks 沒有被 skip。
- Workflow 沒有 secret reference、live E2E opt-in 或 `config/.env.test` access。
- CI PR 上實際出現且通過 `python-ci`；未取得前不得稱 CI green。
- CI PR merge 前取得 qualified non-author GitHub `APPROVED`；未取得前不得稱 approval
  requirement 滿足。
- Workflow merge 後，ruleset 寫入仍是未授權 human boundary，不得自動執行。
- 本 topic 不修改 stable-library surfaces，不建立 release version／branch／tag。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- CI topic 本身不需要 release action；merge 後以 `merged` terminal 結束，不更新
  `VERSION`、`README.md`，不建立 tag 或 release。
- Workflow merge 到 `dev` 後，Main Agent 必須先確認 qualified non-author reviewer
  boundary，再向 human 取得另一份 explicit authorization，才可寫入 GitHub ruleset
  以要求 `python-ci` 與 approval policy。
- Ruleset bootstrap 是 external GitHub write，未授權前保持 pending。
- Release PR 的建立、版本、branch、tag、實際 `python-ci` run 與 GitHub `APPROVED`
  由後續 release workflow 處理，不屬於本 topic completion claim。

## Open Questions / Unresolved Items

- None。GitHub CI run、qualified non-author approval 與 ruleset explicit authorization 是
  尚待未來執行的 human gates，不是未決設計問題。
