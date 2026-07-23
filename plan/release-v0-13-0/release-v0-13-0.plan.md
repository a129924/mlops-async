# v0.13.0 Release Topic Plan

> **Semantic warning — optional analysis layer absent**：
> `analysis/release-v0-13-0/requirements.md` 與
> `analysis/release-v0-13-0/technical-spec.md` 均不存在。本 plan 依 human 已凍結的
> release contract、locked release range 與 repository current truth authoring；沒有
> 可優先套用的 optional analysis layer。此警告不代表 release implementation、PR
> gates、merge、tag 或 GitHub Release 已完成。

## Goal / Outcome

- 建立 `v0.13.0` release PR，將 `v0.12.0` 之後至 locked base
  `39a40a22a1255c1c358cfb95312b0d8996e399d4` 的已合併內容，以 bounded
  stable-library metadata promotion 發布。
- Repository-visible outcome 只包含本 topic 的兩個 planning artifacts、
  `README.md` release status entries，以及 `VERSION`、`pyproject.toml`、`uv.lock`
  三處一致的 `0.13.0`。
- Release PR 固定以 `dev` 為 base、`chore/andrew/release-v0-13-0` 為 head；merge
  前必須有實際 CI success、qualified non-author approval、零 unresolved review
  threads 與 up-to-date 證據。
- Merge 後的 annotated tag `v0.13.0` 必須另取新的 human authorization；是否建立
  GitHub Release 保持 post-merge human check，不由本 plan 預先假定。

## Scope

- **In scope**：
  - 建立 `plan/release-v0-13-0/release-v0-13-0.plan.md` 與
    `plan/release-v0-13-0/release-v0-13-0.step.md`。
  - 在 `README.md` 的 `Status` 區段新增 `v0.13.0` 英文與繁體中文 release entries，
    摘要 PR #47 至 PR #50 已落地的 explicit TLS trust、guarded Viya password-token
    E2E、workflow launcher 修正與 formal CI gates。
  - 將 `VERSION` 與 `pyproject.toml` 的 project version 更新為 `0.13.0`。
  - 只為 root package version synchronization 更新 `uv.lock` 至 `0.13.0`，不得產生
    dependency graph drift。
  - 執行 locked non-live-E2E local validations，並由 GitHub 驗證 release PR gates。
- **Out of scope**：
  - 修改 source code、tests、CI workflow、dependencies、pre-commit hooks 或 upstream
    API specs。
  - 執行 live Viya E2E、讀取 secret config，或以 live evidence 作為本 release 的必要
    local validation。
  - 修改既有 `formal-ci`、`viya-password-token-e2e` 或 `http-client-tls-trust`
    planning artifacts。
  - 在本 topic 內處理 `formal-ci` topic 的 branch／worktree cleanup、GitHub
    ruleset、branch protection、ACL 或 approval-policy mutation。
  - 自動 merge PR、建立或 push tag、建立 GitHub Release、修改 GitHub settings，或
    清理其他 topic 的 branch／worktree。

## Locked Decisions

- Human-locked release version 是 `0.13.0`；tag name 固定為 `v0.13.0`。
- Release range 固定為 `v0.12.0` at `916934d` exclusive 至
  `39a40a22a1255c1c358cfb95312b0d8996e399d4` inclusive；release evidence range
  exact 為 `916934d..39a40a22a1255c1c358cfb95312b0d8996e399d4`。
- Release planning／implementation base 固定為
  `39a40a22a1255c1c358cfb95312b0d8996e399d4`。
- Branch 固定為 `chore/andrew/release-v0-13-0`；managed worktree 固定為
  `D:\code\python\mlops-async.worktrees\agent-20260723-release-v0-13-0`。
- Release PR 固定為 base `dev`、head `chore/andrew/release-v0-13-0`。
- Written artifact set exact 為六檔：
  `plan/release-v0-13-0/release-v0-13-0.plan.md`、
  `plan/release-v0-13-0/release-v0-13-0.step.md`、`README.md`、`VERSION`、
  `pyproject.toml`、`uv.lock`。
- `README.md` 必須新增兩個相鄰 `v0.13.0` status entries：
  - 英文 entry 說明 release closes PR #47、#48、#49、#50，並摘要 explicit
    `bool | ssl.SSLContext` TLS trust、process-only guarded password-token E2E、
    Python-module workflow launchers 與 single-context formal `python-ci` gates；
  - 繁體中文 entry 表達同一 release surface 與明確排除 live E2E 的 CI boundary；
  - 兩者均不得宣稱 insecure-mode evidence 驗證了 TLS trust。
- `VERSION`、`project.version` 與 `uv.lock` root package version 必須 exact
  `0.13.0`；`uv.lock` 除 root package version 外不得有 dependency、source 或
  resolution drift。
- 既有 formal CI、E2E 與 TLS topic artifacts 是 read-only current／historical
  evidence，不在 release topic 內修正、回填或重開其 decisions。
- `formal-ci` topic 的 branch／worktree cleanup 與 GitHub ruleset／ACL mutation 是
  兩條獨立 lanes，且各自需要適用的 human authorization；release approval、release
  PR merge 或 tag authorization 均不得被解讀為授權這些動作。
- Local validation 不執行 live E2E，不設定 `RUN_VIYA_E2E=1`，pytest 必須明確使用
  `-m "not viya_e2e"`。
- Release PR merge gate 必須同時具備實際 `python-ci` success、qualified non-author
  reviewer 的 GitHub `APPROVED`、unresolved review threads exact `0`，以及 head
  已與最新 `dev` up to date 且更新後 required checks 仍成功。
- PR merge 不授權 post-merge tag。Annotated tag `v0.13.0` 的建立與 push 必須在 merge
  後取得一份新的 human authorization，且 tag target 必須是該 release PR 的實際 merge
  commit。
- GitHub Release 是否建立、其 title／notes／artifact payload 均未被 human 鎖定；
  merge／tag 後必須停在 human check，未取得明確決定前不得建立或假定完成。

## Boundaries / Exclusions

- Planning actor 只 author 本 plan 與 step tracker；不修改四個 stable-library files，
  不執行 tests，不 commit、不 push、不開 PR、不 merge、不 tag。
- Implementer 只可修改 `Artifact Paths` 列出的六檔，執行本 plan 的 local
  validations，並更新 step tracker；不得修改 release range 內既有 topic artifacts。
- Reviewer 獨立核對 release contract、version consistency、bounded diff 與 non-live-E2E
  gates；不得把 local result 當成 GitHub `python-ci`、approval 或 thread evidence。
- Main Agent 擁有 commit／push、PR routing、merge 與 post-merge orchestration；tag
  authorization 與 GitHub Release human check 不得由 plan／reviewer verdict 取代。
- 下列既有 artifacts 全部 read-only，不得在本 topic 寫入：
  - `plan/formal-ci/formal-ci.plan.md`
  - `plan/formal-ci/formal-ci.step.md`
  - `plan/viya-password-token-e2e/viya-password-token-e2e.plan.md`
  - `plan/viya-password-token-e2e/viya-password-token-e2e.spec.md`
  - `plan/viya-password-token-e2e/viya-password-token-e2e.step.md`
  - `plan/viya-password-token-e2e/viya-password-token-e2e.tdd-test-authoring.yaml`
  - `plan/http-client-tls-trust/http-client-tls-trust.plan.md`
  - `plan/http-client-tls-trust/http-client-tls-trust.spec.md`
  - `plan/http-client-tls-trust/http-client-tls-trust.step.md`
  - `plan/http-client-tls-trust/http-client-tls-trust.tdd-test-authoring.yaml`
- `config/.env.test` 與 `reference/get_token.py` 不得讀取、列印、diff、stage 或作為
  validation input。
- 若 implementation 需要任何未列於 `Artifact Paths` 的 repo-visible 寫入，停止並交
  Main Agent 重新對齊；不得自行擴張。

## Status / Allowed Transitions

- **Current**：`review-ready`。
- **Execution model**：release planning artifacts 已完成
  `review-ready` -> `reviewer-in-progress` -> `approved`，並依
  `approved` -> `creator-in-progress` 進入 bounded implementation；stable-library
  metadata 與完整 non-live-E2E local validation 均已完成，現已依
  `creator-in-progress` -> `review-ready` 進入 implementation review boundary。
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
  - `merged` -> `released`
  - `released` -> terminal

Routing notes：

- 本輪 current `review-ready` 代表 plan review 已 approved、bounded implementation
  與完整 non-live-E2E local validation 已完成；不代表 implementation review 或任何
  GitHub gate 已滿足。
- Reviewer `needs-rework` 時，只能由 Plan-Creator bounded 修正兩個 planning
  artifacts，再交獨立 Plan-Reviewer 複審。
- Plan approval 後先路由 creator implementation，再路由 implementation／code review；
  publish 只能在 bounded diff 與 local gates 都通過後開始。
- `pr-open` 期間任何 review rework、`dev` 更新或 check rerun 都必須維持相同六檔
  write ACL。
- `merged` -> `released` 只在新 human authorization 下成功建立並 push annotated
  `v0.13.0` tag 後成立；GitHub Release 仍依 human check 決定。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/release-v0-13-0/release-v0-13-0.plan.md` | Planning actor | Repo-visible release execution contract |
| Topic step tracker | `plan/release-v0-13-0/release-v0-13-0.step.md` | Planning actor，後續由 Implementer 更新 | Plan-review phase 與 implementation／external gate evidence |
| Release status documentation | `README.md` | Implementer | `v0.13.0` 英文與繁體中文 stable-library release entries |
| Canonical version file | `VERSION` | Implementer | Human-locked release version `0.13.0` |
| Package metadata | `pyproject.toml` | Implementer | Project version synchronization 至 `0.13.0` |
| Frozen lock metadata | `uv.lock` | Implementer | Root package version synchronization 至 `0.13.0`，不得 dependency drift |

Artifact path notes：

- 上表是本 topic 唯一 executable write inventory，exact 六檔。
- 本 topic 明確修改 `README.md` 與 `VERSION`，不修改
  `.github/copilot-instructions.md`。
- Formal CI、E2E、TLS plans 僅供 read-only release evidence，不是可寫 artifacts。
- 任何其他 path 的寫入均為 plan-alignment blocker。

## Stable library metadata

- `README row`：在 `README.md` 的 `Status` 區段、既有 `v0.12.0` entry 之前新增相鄰的
  `As of **v0.13.0**` 英文 entry 與 `v0.13.0` 繁體中文 entry；兩者依 Locked
  Decisions 摘要 PR #47 至 PR #50 的 TLS trust、guarded E2E、launcher 與 formal CI
  release surface。
- `VERSION bump`：`0.12.0` -> `0.13.0`（MINOR），並同步
  `VERSION`、`pyproject.toml` 與 `uv.lock` root package metadata。
- `timing`：stable-library file changes 在 `creator-in-progress` 完成，經 review 後於
  `publish-in-progress` 進入 release PR；annotated tag 在 PR merge 後、取得新 human
  authorization 時執行。
- `rationale`：相較 `v0.12.0`，本 release 新增可配置 TLS trust contract、anti-fake-
  success 的真實 Viya password-token E2E guard、穩定 workflow launchers 與正式
  `python-ci` quality gates，因此 human 鎖定 MINOR release `0.13.0`。
- `release notes`：repository release notes 由 `README.md` 的雙語 status entries
  承載；是否另建 GitHub Release 與其 notes 內容由 post-merge human check 決定。

## Implementation Steps

1. 在 `README.md` 的 `Status` 區段新增 Locked Decisions 定義的兩個相鄰
   `v0.13.0` release entries，保持既有 `v0.12.0` 與更早 release history 不變。
2. 將 `VERSION` 與 `pyproject.toml` 的 version exact 更新為 `0.13.0`。
3. 執行 `uv lock` 只同步 `uv.lock` 的 root `mlops-async` package version，確認
   dependency、source 與 resolution 沒有 drift。
4. 執行 Validation / Acceptance Checks 的 exact local commands；所有 pytest 均明確
   排除 `viya_e2e`，不得讀取 secret config 或執行 live network E2E。
5. 更新 `plan/release-v0-13-0/release-v0-13-0.step.md` 的 implementation
   checkboxes，只標示實際完成且有 evidence 的項目，並交付 exact 六檔 bounded diff。

## Validation / Acceptance Checks

Local creator／reviewer commands 必須 exact 執行：

1. `uv lock --check`
2. `uv sync --frozen`
3. `uv run --frozen python -m ruff format --check .`
4. `uv run --frozen python -m ruff check .`
5. `uv run --frozen python -m pyright`
6. `uv run --frozen python -m tach check`
7. `uv run --frozen python -m pytest -m "not viya_e2e" --cov=src/mlops_async --cov-fail-under=90 --cov-report=term-missing --cov-report=json:.coverage-reports/coverage.json`
8. 設定 environment
   `SKIP=ruff,ruff-format,tach-check,pytest,coverage-check,pyright-strict` 後執行
   `uv run --frozen python -m pre_commit run --all-files --show-diff-on-failure`。
9. `git diff --check`
10. 在未執行 `git add` 或其他 staging mutation 的情況下，執行下列 exact
    PowerShell gate。它將 locked base 起算的 tracked diff 與所有 non-ignored
    untracked files 合併，將 path separator 正規化為 `/`，去重排序後與宣告的六檔
    exact set 比對：

    ```powershell
    $expected = @(
        'README.md'
        'VERSION'
        'plan/release-v0-13-0/release-v0-13-0.plan.md'
        'plan/release-v0-13-0/release-v0-13-0.step.md'
        'pyproject.toml'
        'uv.lock'
    ) | Sort-Object -Unique
    $tracked = git diff --name-only 39a40a22a1255c1c358cfb95312b0d8996e399d4 --
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to collect tracked diff paths from locked base.'
    }
    $untracked = git ls-files --others --exclude-standard
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to collect non-ignored untracked paths.'
    }
    $actual = @($tracked; $untracked) |
        ForEach-Object { $_ -replace '\\', '/' } |
        Where-Object { $_ -ne '' } |
        Sort-Object -Unique
    $delta = Compare-Object -ReferenceObject $expected -DifferenceObject $actual
    if ($delta) {
        $delta | Format-Table -AutoSize
        throw 'Release write set does not match the declared exact six paths.'
    }
    ```

Acceptance criteria：

- Locked-base tracked diff 與 non-ignored untracked files 的 normalized union exact
  等於 Artifact Paths 宣告的六檔；不得依賴 staging state，也沒有 source、tests、
  workflow、dependency、existing plan、secret surface 或其他 untracked drift。
- `VERSION`、`pyproject.toml` 的 `project.version` 與 `uv.lock` root
  `mlops-async` package version 全部 exact 為 `0.13.0`。
- `uv.lock` 除 root package version `0.12.0` -> `0.13.0` 外沒有其他 package、
  source、dependency 或 resolution 變化。
- `README.md` 有相鄰雙語 `v0.13.0` entries，release range 與 PR #47 至 PR #50
  摘要正確，且沒有把 insecure-mode success 誤稱為 TLS trust verified。
- Ruff format／lint、Pyright、Tach、non-live-E2E pytest coverage >= 90 與剩餘
  pre-commit hygiene 均成功；沒有設定 `RUN_VIYA_E2E=1`，沒有執行 live E2E。
- Release range exact 為 `v0.12.0`（`916934d`）exclusive 至
  `39a40a22a1255c1c358cfb95312b0d8996e399d4` inclusive。
- Release PR exact base/head 為 `dev` /
  `chore/andrew/release-v0-13-0`。
- Merge 前 GitHub evidence 同時證明最新 head 的 required `python-ci` 成功、
  qualified non-author reviewer 已提交 GitHub `APPROVED`、unresolved review threads
  exact `0`、head 與最新 `dev` up to date，且同步後 required check 仍成功。
- PR merge 後不得沿用 merge authorization 建立 tag；必須取得新的 human
  authorization，建立 annotated `v0.13.0` 並使其 exact 指向 release PR merge commit，
  成功 push 後才能標記 `released`。
- GitHub Release 未被本 plan 鎖定；tag 完成後停在 human check，依 human 明確決定
  建立或不建立，不得假冒 completed evidence。
- `formal-ci` cleanup 與 GitHub ruleset／ACL lane 保持獨立，不得因 release 成功而自動
  執行或標記完成。

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

- Main Agent 必須先以 GitHub current truth 確認 release PR 已 merge，並取得實際 merge
  commit；不得以 local branch tip 或 plan base SHA 代替 merge commit。
- PR merge authorization 在 merge 完成時耗盡。建立與 push annotated tag
  `v0.13.0` 前，Main Agent 必須向 human 取得新的明確 authorization。
- 經新 authorization 後，annotated tag `v0.13.0` 必須 exact 指向 release PR merge
  commit；push 成功後才可將 topic transition `merged` -> `released`。
- Tag 完成後，Main Agent 必須執行 GitHub Release human check。Human 尚未鎖定是否
  建立 GitHub Release、title、notes 或 assets；未取得明確決定前不得建立，也不得因
  annotated tag 存在而宣稱 GitHub Release 已完成。
- Release topic 自身的 branch／worktree cleanup 由 Main Agent 在 release truth
  verification 後另行路由；不得順帶清理 formal CI、E2E 或 TLS topic。
- `formal-ci` branch／worktree cleanup 與 GitHub ruleset／ACL mutation 各自保持獨立
  authorization boundary，不由 release 的 plan approval、PR merge、tag authorization
  或 GitHub Release decision 擴權。

## Open Questions / Unresolved Items

- None。是否建立 GitHub Release 已被明確路由為 tag 後的 human check，而不是留給
  Implementer 或 Reviewer 猜測的設計問題；在 human 決定前該 external action保持
  pending。
