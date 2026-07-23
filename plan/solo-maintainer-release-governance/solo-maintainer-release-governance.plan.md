# Sole-Maintainer Release Governance Topic Plan

> **Semantic warning — optional analysis layer absent**：
> `analysis/solo-maintainer-release-governance/requirements.md` 與
> `analysis/solo-maintainer-release-governance/technical-spec.md` 均不存在。本 plan
> 依 human 已鎖定的 dual normal reviewer gate、repository workflow contract 與
> current release-governance surfaces authoring；沒有可優先套用的 optional analysis
> layer。此警告不代表 governance implementation、review、publish、merge 或任何
> release/tag action 已完成。

## Goal / Outcome

- 將 release normal-path reviewer gate 改為兩條互斥且可稽核的合格路徑：
  - collaborative repository：取得 qualified non-author reviewer 對最新 PR head
    的 GitHub `APPROVED`；
  - 經 current GitHub repository evidence 證實的 sole-maintainer repository：
    取得獨立 Reviewer agent 對最新 PR head exact SHA 的結構化 approved evidence。
- 保留所有非 reviewer gates 的 hard-gate 性質，並使 sole-maintainer path 不會被誤稱
  為 GitHub approval、emergency bypass、merge authorization 或 tag authorization。
- Repository-visible outcome 是三個 `git-release-management` governance surfaces
  對 dual normal reviewer gate、sole-maintainer proof、stale-review invalidation 與
  emergency boundary 提供一致、可執行的合約。

## Scope

- **In scope**：
  - 更新 `.agents/skills/git-release-management/SKILL.md` 的 normal-path gate、
    current repository sensing、reviewer evidence 與 failure handling。
  - 更新
    `.agents/skills/git-release-management/references/gate-contract.md`，定義
    collaborative 與 verified sole-maintainer 兩條 normal reviewer paths。
  - 更新
    `.agents/skills/git-release-management/references/emergency-path.md`，明確區分
    sole-maintainer normal path 與只允許 bypass reviewer evidence 的 emergency path。
  - 維護本 topic 的 plan 與 step tracker。
- **Out of scope**：
  - 修改 GitHub ruleset、branch protection、required approvals、required checks 或
    repository collaborator permissions。
  - 弱化或移除 `python-ci`、conversation resolution、base tests、strict typing、
    lint、documentation sync、version sync、clean workspace 或 tag uniqueness gates。
  - 修改 source code、tests、CI workflow、dependencies、hooks、config、reference
    files、release metadata 或既有 historical planning artifacts。
  - 修改或 merge current release PR、建立或 push `v0.13.0` tag、建立 GitHub
    Release，或執行任何 release／cleanup action。
  - 把 independent agent review 描述為 GitHub `APPROVED`，或把 sole-maintainer
    repository 自動歸類為 emergency。

## Locked Decisions

- Topic base exact 為 `origin/dev` 的
  `59cc292e10fdc0144d9caf9d343dd264a8cff9b5`；topic branch 為
  `fix/andrew/solo-maintainer-release-gate`。
- 本 topic 不涉及 stable-library surfaces；不修改 `README.md`、`VERSION`、release
  notes 或 release timing，也不執行 release。
- GitHub ruleset 的 required approvals 保持 `0`；本 topic 不執行任何 settings
  mutation。`python-ci` 與 conversation resolution 仍是 required external gates。
- Normal reviewer gate 固定為二選一：
  1. **Collaborative path**：latest PR head 有 qualified non-author reviewer 提交的
     GitHub `APPROVED`。
  2. **Verified sole-maintainer path**：gate evaluation 當下的 current GitHub
     repository evidence 證明沒有可提供 qualified non-author approval 的其他
     write-qualified maintainer，且 latest PR head 有獨立 Reviewer agent 的
     structured approved evidence。
- Sole-maintainer eligibility 不得從聊天敘述、歷史快照、ruleset approval count、
  PR author 自述或先前 release 推定。每次使用此 path 都必須讀取 current GitHub
  repository permission／collaborator evidence；若證據不可取得、含糊或顯示存在合格
  non-author reviewer，sole-maintainer path 必須 hard-block。
- Sole-maintainer topology evidence 必須可機器消費，至少記錄 repository、觀測時間、
  current evidence source、PR author、write-qualified maintainer inventory、
  qualified non-author reviewer inventory 與 `sole_maintainer_verified`。只有
  qualified non-author reviewer inventory exact 為空且
  `sole_maintainer_verified=true` 時，才能評估 agent-review path。
- Independent Reviewer agent 必須與 Implementer 分離，並審查 latest PR head exact
  SHA。每次 implementation／rework／sync 造成 head SHA 改變，舊 agent review
  立即失效，必須對新 SHA 重新審查。
- Sole-maintainer agent review evidence 至少使用下列 machine-consumable contract；
  `reviewer_run_id` 記錄可追溯的 reviewer run 或 session identifier：

  ```json
  {
    "reviewer_kind": "independent-agent",
    "reviewer_run_id": "<reviewer-run-or-session-id>",
    "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
    "verdict": "approved",
    "blocking_issues": [],
    "scope_verified": true,
    "version_sources_verified": true,
    "non_live_ci_contract_verified": true
  }
  ```

- `non_live_ci_contract_verified=true` 只表示 Reviewer 已核對 CI contract；它不能取代
  GitHub 上 latest head 的實際 `python-ci` success。
- Actual `python-ci` success、unresolved review threads exact `0`、head 與 base
  up-to-date、base tests、strict typing、lint、documentation sync、version source
  synchronization、clean workspace 與 tag uniqueness 都維持獨立 hard gates。
- Agent review 只滿足 verified sole-maintainer normal path 的 reviewer evidence；
  不構成 GitHub `APPROVED`、merge authorization 或 post-merge tag authorization。
  Merge 與 tag 仍各自保留 explicit human decision boundary。
- Sole-maintainer path 不是 emergency。Existing emergency contract只允許 bypass
  normal reviewer evidence，且仍需 explicit marker、recorded human confirmation、
  urgency explanation、release-note／equivalent anomaly record 與所有其他 hard
  gates；本 topic 不擴張 emergency bypass。
- Current `release-v0-13-0` planning artifacts 與 historical `formal-ci` plan 不在
  本 topic 回填。Governance topic merge 後，current release planning contract 的
  rework 必須由另一個 bounded topic 或另行授權 phase 處理。

## Boundaries / Exclusions

- Planning actor 只 author 本 plan 與 step tracker；不修改 governance skill、
  不執行 validation、不 commit、不 push、不開 PR、不 merge、不 tag。
- Implementer 只可修改 `Artifact Paths` 列出的 Creator-owned governance files 與
  step tracker；不得寫入 GitHub settings 或 release artifacts。
- Reviewer 必須獨立於 Implementer，核對 latest diff、dual-path contract 與 exact
  reviewed SHA；不得把自己的 agent verdict 表述成 GitHub approval。
- Main Agent 擁有 branch／publish／PR／merge／post-merge routing；human 明確保留
  merge 與 tag authorization。
- `.github/workflows/ci.yml`、`plan/formal-ci/formal-ci.plan.md`、
  `plan/release-v0-13-0/release-v0-13-0.plan.md` 與
  `plan/release-v0-13-0/release-v0-13-0.step.md` 只供 read-only context，不得修改。
- `config/.env.test` 與 `reference/legacy_code/get_token.py` 不得讀取、列印、diff、
  stage、copy 或作為 validation input。
- 若 implementation 需要任何未列於 `Artifact Paths` 的 repo-visible 寫入，停止並
  交 Main Agent 重新對齊；不得自行擴張。

## Status / Allowed Transitions

- **Current**：`needs-rework`。
- **Execution model**：planning、bounded governance implementation、pre-commit
  review／test 與 publish 已完成，PR #52 曾合法進入 `pr-open`；current-head
  Reviewer 對 SHA `bc8a730ef75b332ca174c1936b0a84f4ad8896ec` 回傳
  `needs-rework`，因此依 canonical `pr-open` -> `needs-rework` route停止 publish
  progression。後續只能依 `needs-rework` -> `creator-in-progress` 交由獨立
  Implementer修正，再由 Reviewer 對新 SHA 複審。
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
- Plan review 或 implementation review 回傳 `needs-rework` 時，只能交回相應
  Creator／Implementer bounded 修正，再由獨立 Reviewer 對最新版重新審查。
- PR head 變更會使先前 agent review evidence stale；publish／PR routing 必須在新
  SHA 上重新取得 Reviewer verdict。
- 本 topic 不需要 repo-visible review-log，也不宣告 round cap；review routing 使用
  standard workflow contract。
- PR #52 current-head review evidence：
  - reviewed SHA：
    `bc8a730ef75b332ca174c1936b0a84f4ad8896ec`；
  - reviewer run：`/root/solo_governance_impl_reviewer`；
  - verdict：`needs-rework`；
  - actual current-head `python-ci`：success，但只滿足 CI gate，不代表 overall
    reviewer／conversation／merge gate通過。
- Current open blockers exact 為六項：
  1. `.agents/skills/git-release-management/SKILL.md` 的 PASS／Required Checks
     無條件要求 normal reviewer path，使 fully evidenced emergency仍不可能 PASS；
     必須由 Implementer加入 fully evidenced emergency alternative，同時保留所有
     non-bypassable hard gates。Trace：
     `PRRT_kwDOSTt_386TOHa-`／`PRRC_kwDOSTt_387Y0A3Z`。
  2. Topic plan／step 的 phase與 PR current state drift；本次 planning rework只修正
     這兩個 planning artifacts，不標示 implementation fix完成。Primary trace：
     `PRRT_kwDOSTt_386TOHbG`／`PRRC_kwDOSTt_387Y0A3g`；duplicate trace：
     `PRRT_kwDOSTt_386TOHuq`／`PRRC_kwDOSTt_387Y0BS7`。Duplicate不需要另一個
     獨立 fix。
  3. PR body中對 SHA
     `816ab30e8d1829593542da35f0024ae09b4f2a45` 的 review evidence已 stale，
     不得宣稱覆蓋 current head。
  4. PR #52 尚有 `5` 個 unresolved conversations；必須逐項 triage，必要時由
     Implementer bounded fix，經 latest-head Reviewer複審後才能 resolve。
  5. Independent actor identity linkage尚未形成可驗證 contract：
     `gate-contract.md` 與 `SKILL.md` 的 schema／gate必須記錄可由 dispatcher
     execution record核對的 Reviewer與 Implementer canonical actor／run identity；
     兩者必須存在、可追溯且不相等。Missing、unverifiable或 same actor一律
     `BLOCKED`，並繼續要求 exact-head freshness。Trace：
     `PRRT_kwDOSTt_386TOHa2`／`PRRC_kwDOSTt_387Y0A3T`。
  6. 三個 governance surfaces 的 canonical gate naming尚未一致；必須統一使用
     `conversation resolution (unresolved review threads exactly 0)` 語意，不得以
     較弱或含糊名稱替代。Trace：
     `PRRT_kwDOSTt_386TOHvQ`／`PRRC_kwDOSTt_387Y0BTt`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.plan.md` | Planning actor | Repo-visible execution contract |
| Topic step tracker | `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.step.md` | Planning actor，後續由 Implementer 更新 | Creator completion gate 與 bounded implementation evidence |
| Release skill contract | `.agents/skills/git-release-management/SKILL.md` | Implementer | Normal reviewer-path sensing、gate decision 與 failure handling |
| Release gate reference | `.agents/skills/git-release-management/references/gate-contract.md` | Implementer | Dual normal reviewer gate 與 hard-gate contract |
| Emergency reference | `.agents/skills/git-release-management/references/emergency-path.md` | Implementer | Sole-maintainer normal path與 emergency bypass boundary |

Artifact path notes：

- 上表是本 topic 唯一 executable write inventory，exact 五檔。
- 本 topic 明確不修改 `README.md`、`VERSION`、
  `.github/copilot-instructions.md`、release notes 或 release metadata。
- `.github/workflows/ci.yml`、existing release plans 與 GitHub settings 均是
  read-only context／external state，不是可寫 artifacts。
- 任何其他 path 的寫入都是 plan-alignment blocker。

## Implementation Steps

1. 更新 `.agents/skills/git-release-management/SKILL.md`，將 normal reviewer gate
   實作為 collaborative GitHub approval 與 verified sole-maintainer agent review
   兩條互斥路徑，並加入 current GitHub topology sensing、evidence freshness、
   exact-head review invalidation 與 blocked failure handling。
2. 更新
   `.agents/skills/git-release-management/references/gate-contract.md`，明確定義
   dual normal reviewer gate、sole-maintainer topology evidence、agent review
   minimum JSON fields，以及所有其他 release gates 的獨立 hard-gate地位。
3. 更新
   `.agents/skills/git-release-management/references/emergency-path.md`，明確寫出
   verified sole-maintainer 是 normal path、不是 emergency，並保留 emergency 只能
   bypass reviewer evidence 的既有 marker、human、urgency、anomaly 與 hard-gate
   requirements。
4. 對三個 governance surfaces 執行一致性收斂：不得把 agent review 稱為 GitHub
   `APPROVED`，不得以 ruleset approvals `0` 推定 sole maintainer，不得弱化
   `python-ci`、conversation resolution 或任何既有 non-bypassable gate。
5. 更新
   `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.step.md`
   的 implementation checkboxes；只在 exact 五檔 bounded diff、contract checks 與
   applicable repository hygiene checks實際完成後標示完成。

## Validation / Acceptance Checks

Contract checks：

- 三個 governance surfaces 對 normal reviewer gate 的語意一致：collaborative path
  需要 qualified non-author GitHub `APPROVED`；sole-maintainer path 需要 current
  GitHub topology proof 與 latest-head independent agent review evidence。
- 無法取得或無法判定 current maintainer inventory 時，結果為 `BLOCKED`，不得從聊天、
  ruleset approval count 或歷史 evidence 推定 sole-maintainer eligibility。
- Agent evidence 包含 locked minimum fields與 reviewer run/session identifier；
  `reviewed_commit_sha` 必須 equal latest PR head SHA，否則為 stale 並 `BLOCKED`。
- Reviewer／Implementer 角色分離；rework 或 base sync 改變 SHA 後必須重新 review。
- 文案明確區分 independent agent approval 與 GitHub `APPROVED`，且 agent evidence
  不授權 merge／tag。
- Actual latest-head `python-ci`、conversation resolution exact `0`、up-to-date、
  tests、strict typing、lint、docs、version sync、clean workspace 與 tag uniqueness
  均保持獨立 hard gates，不得由 agent JSON 欄位替代。
- Emergency contract保持現有單一 bypass boundary；sole-maintainer path 不要求或產生
  emergency marker，emergency 也不能 bypass其他 hard gates。
- GitHub ruleset required approvals 保持 `0`，本 topic沒有 settings write。

Scenario test cases：

1. Collaborative repository 有 qualified non-author GitHub `APPROVED`，且其他 hard
   gates 全部通過：normal reviewer gate PASS。
2. Collaborative repository 缺少 qualified non-author GitHub `APPROVED`：即使有
   agent review，normal reviewer gate仍 BLOCKED。
3. Current GitHub evidence 證實沒有 qualified non-author reviewer，且 independent
   agent review JSON 對 latest head exact SHA approved：sole-maintainer normal
   reviewer gate PASS，但仍需個別通過所有其他 hard gates與 human merge decision。
4. Sole-maintainer topology evidence缺失、過時或含糊：BLOCKED。
5. Agent review SHA與 latest PR head不一致，或 rework 後未重審：BLOCKED。
6. Agent JSON 宣告 `non_live_ci_contract_verified=true`，但 actual GitHub
   `python-ci`缺失／失敗：BLOCKED。
7. Unresolved thread 非零、workspace dirty、version sources不同步或 target tag已存在：
   BLOCKED，且不得用任一 reviewer path bypass。
8. Missing reviewer evidence 改走 emergency，但缺少 marker、human confirmation、
   urgency explanation 或 anomaly record 任一項：BLOCKED。

Repository checks：

- `git diff --check` 通過。
- 相對 topic base 的 tracked diff 與 non-ignored untracked file union exact 等於
  `Artifact Paths` 的五檔；沒有 source、tests、CI、config、reference、release
  metadata 或 settings drift。
- Applicable Markdown／repository hygiene checks 通過；不得讀取 secret config 或
  執行 live E2E。

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

- 本 governance topic 不需要 release action；merge 後以 `merged` terminal 結束，
  不更新 version、README、release notes，不建立 tag 或 GitHub Release。
- Merge 後 dual normal reviewer gate 才成為後續 release evaluation 的 current
  governance contract。
- Current `release-v0-13-0` planning contract 的 stale reviewer requirement 必須在
  另一個 bounded topic 或另行授權 phase 內 rework／review；不得在本 topic merge
  時自動回填。
- 本 topic merge 不授權 current release merge、annotated tag `v0.13.0` 或 cleanup。
  後續 release仍須依更新後 contract取得 exact merge evidence與新的 human tag
  authorization。

## Open Questions / Unresolved Items

- None。Sole-maintainer eligibility 的 current GitHub verification 是每次 gate
  evaluation 都必須執行的 evidence requirement，不是由 Plan-Creator 預先猜測的
  open design question。
