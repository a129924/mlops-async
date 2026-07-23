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
- Repository-visible outcome 是四個 `git-release-management` governance surfaces
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
  - 更新 `.agents/skills/git-release-management/examples.md` 的 emergency example，
    明確要求 conversation resolution exact `0` 與 head up to date with base。
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
- Written artifact set exact 為六檔：
  `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.plan.md`、
  `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.step.md`、
  `.agents/skills/git-release-management/SKILL.md`、
  `.agents/skills/git-release-management/references/gate-contract.md`、
  `.agents/skills/git-release-management/references/emergency-path.md`、
  `.agents/skills/git-release-management/examples.md`。Deleted：None。
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
- 合格 independent review evidence必須針對 exact committed PR head SHA，並發布於
  PR body或 PR comment，形成 external、可稽核且非自我參照的 evidence。
  `plan.md`／`step.md` 不得以自身 content hash聲稱已 approved；本 topic不新增
  review ledger file。缺少 external exact committed-head evidence時 reviewer gate
  維持 pending／`BLOCKED`。
- Sole-maintainer agent review evidence 至少使用下列 machine-consumable contract；
  `reviewer_run_id` 記錄可追溯的 reviewer run 或 session identifier：

  ```json
  {
    "reviewer_kind": "independent-agent",
    "implementer_run_id": "<canonical-implementer-actor-or-run-id>",
    "reviewer_run_id": "<reviewer-run-or-session-id>",
    "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
    "verdict": "approved",
    "blocking_issues": [],
    "scope_verified": true,
    "version_sources_verified": true,
    "non_live_ci_contract_verified": true
  }
  ```

- `implementer_run_id` 與 `reviewer_run_id` 必須是 dispatcher execution record可核對
  的 canonical actor／run identity；兩者都必須存在、可追溯、non-opaque且不相等。
  任一 identity缺失、unverifiable、只提供 opaque label，或兩者指向 same actor／run
  時，independent agent evidence一律 `BLOCKED`。
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

- **Current**：`pr-open`。
- **Execution model**：planning、bounded governance implementation、pre-commit
  review／test 與 publish 已完成，PR #52 曾合法進入 `pr-open`。Current-head
  `40d09aeac922c7ed95374b4e7a661e54780d28c9` 的 exact-head Reviewer回傳
  `needs-rework`，blocking issues是 emergency example缺少兩個 hard gates，以及
  planning artifacts使用 self-referential hash approval claims。Planning rework與
  thread #8 bounded implementation／validation已完成，現依 canonical
  `needs-rework` -> `creator-in-progress` -> `review-ready` 等待獨立 review。
  Latest working-tree Reviewer只因 thread inventory仍寫 `9` 而回傳
  `needs-rework`；本次 inventory correction依
  `reviewer-in-progress` -> `needs-rework` -> `creator-in-progress` ->
  `review-ready` 收斂。Current exact-six working-tree review／test通過後，再依
  `review-ready` -> `reviewer-in-progress` -> `approved` ->
  `publish-in-progress` -> `pr-open` 完成 final bookkeeping。
  Thread #9要求的 external exact committed-head evidence只能在 commit後產生，仍
  pending。
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
- PR #52 current-head evidence：
  - reviewed SHA：
    `40d09aeac922c7ed95374b4e7a661e54780d28c9`；
  - verdict：`needs-rework`；
  - blocking issues：thread #8 emergency example hard-gate omission；thread #9
    self-referential planning hash approval；
  - actual current-head `python-ci`：success，但只滿足 CI gate，不代表 overall
    reviewer／conversation／merge gate通過。
- Historical internal plan reviews保留為 workflow history，但不構成 external
  reviewer gate evidence；所有以 plan／step自身 content hash表達 approval的 claims
  已移除。只有 PR body或 comment中針對 exact committed PR head SHA的獨立 review
  evidence可供 current reviewer gate使用。
- Current working-tree rework evidence：
  - Implementer run：`/root/solo_governance_rework_implementer`；
  - emergency example SHA256：
    `CA691C00D92ECBDEBC9C6EE22962AA3B513D43704FA4918BA5DB3CCFA3767664`；
  - Implementer-delivered pre-bookkeeping step snapshot SHA256：
    `44E4CC762C187723FCF517727EFA786F8D05BFAE1B30374303B3BCD9D0684989`；
  - contract／JSON／scope／hygiene assertions：`35/35 PASS`；
  - emergency example targeted assertions：`21/21 PASS`；
  - tracked diff exact六檔、non-ignored untracked `0`。
- 上述 hashes只識別 Implementer-delivered artifacts／snapshot，不構成 review
  approval，也不能替代 commit後發布於 PR body或 comment的 external exact-head
  evidence。
- Final exact-six working-tree gates：
  - Reviewer run：`/root/solo_governance_impl_reviewer`；
  - Reviewer verdict：`APPROVED`，blocking issues `[]`；
  - Tester run：`/root/solo_governance_tester`；
  - Tester verdict：`PASS`；
  - full contract／scope assertions：`35/35 PASS`；
  - targeted emergency example assertions：`21/21 PASS`。
- 上述 run verdicts只覆蓋 current uncommitted exact-six working-tree diff；沒有使用
  plan／step self-content hash，也不建立 ledger，不能替代 commit後發布於 PR body
  或 comment的 external exact committed-head review。
- Latest working-tree Reviewer verdict：
  - verdict：`needs-rework`；
  - single blocker：unresolved count／thread inventory drift；
  - substantive governance／examples contract blocker：None。
- Current thread inventory exact 為 `10`，由
  `/root/pr52_comment_reviewer` 的 thread-aware inventory證明；所有 thread在
  GitHub resolve前仍算 unresolved：
  - thread #10 second stale audit-trace hash assertion：
    `PRRT_kwDOSTt_386TPTpn`／`PRRC_kwDOSTt_387Y1rV9`／`DB3637949821`，
    source為 plan lines 190-192；此 thread current actionable，與 thread #9同屬
    self-hash cluster但不是 pure duplicate。既有移除全部 self-referential approval
    claims的修正已 substantive address其內容，但 GitHub resolve前仍 unresolved；
  - thread #8 emergency example：
    `PRRT_kwDOSTt_386TPHWi`／`PRRC_kwDOSTt_387Y1aJg`；
  - thread #9 external exact committed-head review evidence：
    `PRRT_kwDOSTt_386TPHWl`／`PRRC_kwDOSTt_387Y1aJk`；
  - previous #6 phase/state thread：
    `PRRT_kwDOSTt_386TO1VJ`／`PRRC_kwDOSTt_387Y1BPI`；
  - previous #7 reviewer-schema／`implementer_run_id` thread：
    `PRRT_kwDOSTt_386TO1VR`／`PRRC_kwDOSTt_387Y1BPR`；
  - previous #1 至 #5 threads內容已 addressed、outdated或 duplicate，但尚未在 GitHub
    reply／resolve：
    - emergency：
      `PRRT_kwDOSTt_386TOHa-`／`PRRC_kwDOSTt_387Y0A3Z`；
    - identity：
      `PRRT_kwDOSTt_386TOHa2`／`PRRC_kwDOSTt_387Y0A3T`；
    - canonical naming：
      `PRRT_kwDOSTt_386TOHvQ`／`PRRC_kwDOSTt_387Y0BTt`；
    - phase：
      `PRRT_kwDOSTt_386TOHbG`／`PRRC_kwDOSTt_387Y0A3g`；
    - duplicate phase：
      `PRRT_kwDOSTt_386TOHuq`／`PRRC_kwDOSTt_387Y0BS7`。
- Prior addressed planning rework history：
  1. Topic plan的 independent agent evidence JSON加入
     `implementer_run_id`／`reviewer_run_id`，並鎖定 canonical、traceable、
     non-opaque、different-actor hard-block語意；
  2. Earlier phase drift曾同步至 `review-ready`；current head的新 review已另依
     `pr-open` -> `needs-rework` 記錄，不沿用舊 phase。
- Current rework completion：
  1. Thread #8 emergency example已加入 conversation resolution exact `0` 與 head
     up to date with base；
  2. Exact六檔 bounded validation已通過；
  3. Workflow依 `needs-rework` -> `creator-in-progress` -> `review-ready` 前進。
  4. Thread #10 substantive內容已由 existing removal of all self-referential
     approval claims處理，inventory已從 `9` 更正為 `10`。
- 尚未滿足的 PR boundaries：
  1. Bounded fix commit後，必須由獨立 Reviewer審查 new exact PR head SHA，且
     evidence須發布至 PR body或 comment；不得使用 plan／step self-hash claim。
  2. `conversation resolution (unresolved review threads exactly 0)` 尚未通過；
     current unresolved exact為 `10`；
  3. 本次 working-tree planning diff尚待獨立 review，不得以
     `40d09aeac922c7ed95374b4e7a661e54780d28c9` 的 review或 CI代替。
- Human已明確授權 PR #52 comment review／fix／reply／resolve全部 unresolved
  actionable threads；此授權不包含 merge或 tag，兩者仍是獨立 human boundary。
- PR body中 unresolved count `9` 已 stale；external PR body／comment update仍
  pending，必須改為 current exact `10`，且不得由本 repo-local bookkeeping假稱完成。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.plan.md` | Planning actor | Repo-visible execution contract |
| Topic step tracker | `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.step.md` | Planning actor，後續由 Implementer 更新 | Creator completion gate 與 bounded implementation evidence |
| Release skill contract | `.agents/skills/git-release-management/SKILL.md` | Implementer | Normal reviewer-path sensing、gate decision 與 failure handling |
| Release gate reference | `.agents/skills/git-release-management/references/gate-contract.md` | Implementer | Dual normal reviewer gate 與 hard-gate contract |
| Emergency reference | `.agents/skills/git-release-management/references/emergency-path.md` | Implementer | Sole-maintainer normal path與 emergency bypass boundary |
| Release examples | `.agents/skills/git-release-management/examples.md` | Implementer | Emergency example的 conversation-resolution與 base up-to-date hard gates |

Artifact path notes：

- 上表是本 topic 唯一 executable write inventory，exact 六檔；Deleted：None。
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
4. 對既有三個 core contract surfaces執行一致性收斂：不得把 agent review稱為 GitHub
   `APPROVED`，不得以 ruleset approvals `0` 推定 sole maintainer，不得弱化
   `python-ci`、conversation resolution 或任何既有 non-bypassable gate。
5. 僅更新 `.agents/skills/git-release-management/examples.md` 的 emergency example，
   明確加入 `conversation resolution (unresolved review threads exactly 0)` 與
   release PR head up to date with base，且不得弱化其他 emergency hard gates。
6. 更新
   `plan/solo-maintainer-release-governance/solo-maintainer-release-governance.step.md`
   的 implementation checkboxes；只在 exact 六檔 bounded diff、contract checks 與
   applicable repository hygiene checks實際完成後標示完成。

## Validation / Acceptance Checks

Contract checks：

- 三個 core contract surfaces 對 normal reviewer gate 的語意一致：collaborative path
  需要 qualified non-author GitHub `APPROVED`；sole-maintainer path 需要 current
  GitHub topology proof 與 latest-head independent agent review evidence。
- 無法取得或無法判定 current maintainer inventory 時，結果為 `BLOCKED`，不得從聊天、
  ruleset approval count 或歷史 evidence 推定 sole-maintainer eligibility。
- Agent evidence 包含 locked minimum fields與 reviewer run/session identifier；
  `reviewed_commit_sha` 必須 equal latest PR head SHA，否則為 stale 並 `BLOCKED`。
- Independent review evidence發布於 PR body或 comment，且
  `reviewed_commit_sha` exact等於 committed current PR head；plan／step content
  hash、working-tree hash或 repo-local self-approval claim不能替代 external evidence。
- Reviewer／Implementer 角色分離；rework 或 base sync 改變 SHA 後必須重新 review。
- 文案明確區分 independent agent approval 與 GitHub `APPROVED`，且 agent evidence
  不授權 merge／tag。
- Actual latest-head `python-ci`、conversation resolution exact `0`、up-to-date、
  tests、strict typing、lint、docs、version sync、clean workspace 與 tag uniqueness
  均保持獨立 hard gates，不得由 agent JSON 欄位替代。
- Emergency contract保持現有單一 bypass boundary；sole-maintainer path 不要求或產生
  emergency marker，emergency 也不能 bypass其他 hard gates。
- `examples.md` 的 emergency example明確包含 conversation resolution
  （unresolved review threads exact `0`）與 head up to date with base，且其餘
  hard gates與 emergency evidence requirements保持不變。
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
9. Emergency evidence齊全，但 unresolved review threads非 `0`或 head落後 base：
   BLOCKED；example不得把任一條件表達為 optional。

Repository checks：

- `git diff --check` 通過。
- 相對 topic base 的 tracked diff 與 non-ignored untracked file union exact 等於
  `Artifact Paths` 的六檔；沒有 source、tests、CI、config、其他 reference、release
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
