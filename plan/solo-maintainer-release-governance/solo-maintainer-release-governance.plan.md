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
- Topology proof必須包含可重新取得的 GitHub collaborator／permission query
  provenance，minimum contract為：

  ```json
  {
    "repository_full_name": "<owner/repository>",
    "evidence_url": "<retrievable-github-api-endpoint>",
    "observed_at_utc": "<iso-8601-utc>",
    "freshness_max_age_seconds": "<positive-integer>",
    "query_scope": "<collaborator-and-permission-scope>",
    "pr_author_login": "<pr-author-login>",
    "write_qualification_predicate": "role_name in [admin, maintain, write] OR permissions.admin == true OR permissions.maintain == true OR permissions.push == true",
    "permission_bearing_entries": [
      {
        "login": "<pr-author-login>",
        "role_name": "admin",
        "permissions": {
          "admin": true,
          "maintain": true,
          "push": true
        }
      }
    ],
    "write_qualified_maintainers": ["<pr-author-login>"],
    "qualified_non_author_reviewers": [],
    "sole_maintainer_verified": true
  }
  ```

- `pr_author_login` 必須是 exact current PR author。
  `permission_bearing_entries` 必須 nonempty並涵蓋 query scope內所有 retrieved
  collaborators；每個 entry必須有 login、recognized `role_name`，以及 boolean
  `admin`、`maintain`、`push` permissions。
- `write_qualification_predicate` 固定為：`role_name`是 `admin`、`maintain`或
  `write`，或 boolean `permissions.admin`、`permissions.maintain`、
  `permissions.push`任一為 `true`時才 write-qualified；`triage`與 `read` alone
  不合格。不得修改或以自述 predicate取代。
- `write_qualified_maintainers` 必須由全部 `permission_bearing_entries`依固定
  predicate導出；`qualified_non_author_reviewers`必須再由前者排除 exact
  `pr_author_login`導出。兩個 inventories都不得接受 self-asserted input。
- Sole-maintainer topology只在 provenance可擷取、fresh且 scope正確、entries
  nonempty且 fully classifiable、derived `write_qualified_maintainers` exact一人且
  等於 `pr_author_login`、derived `qualified_non_author_reviewers`為空，以及
  `sole_maintainer_verified=true`與全部 derived values一致時通過。
  Arbitrary string、empty entries加 self-asserted boolean、missing／mismatched PR
  author、zero或multiple write-qualified maintainers、unknown／missing／non-boolean
  role或permissions、stale／unretrievable provenance、query scope不明、self-asserted
  inventories或任何 derived mismatch一律 `BLOCKED`。Repo examples只可使用
  placeholders，不得寫入真實 private collaborator inventory、token或 secret。
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
    "repository_full_name": "<owner/repository>",
    "pull_request_number": "<positive-integer>",
    "evidence_surface": "pr-body|pr-comment",
    "evidence_url": "<retrievable-pr-body-or-comment-url>",
    "published_at_utc": "<iso-8601-utc>",
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
- Review evidence provenance必須可從 `evidence_url`重新取得，且該 PR body或
  comment內容必須同時綁定同一 `repository_full_name`、
  `pull_request_number`與 exact `reviewed_commit_sha`。Missing、unretrievable、
  non-PR-visible evidence surface、repository／PR／SHA mismatch，或
  `published_at_utc`缺失時一律 `BLOCKED`。
- Repo-visible plan／step是 commit前的 `review-ready` snapshot，不承載 publish後
  動態 GitHub truth。Snapshot commit後，actual `pr-open`／current head／CI／review／
  conversation state只發布於 PR-visible body或 comment，不回填到同一 commit；此
  boundary避免 published-head self-reference。
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

- **Current**：`review-ready`。
- **Execution model**：本 repo-visible plan／step只表示 commit前的
  `review-ready` snapshot。外部 PR review在 observed head
  `dbe86b96c0b403b24e24dfddd5fa0520049b027e` 找到 threads #11至#13後，workflow
  依 canonical `pr-open` -> `needs-rework` -> `creator-in-progress` ->
  `review-ready` 完成本輪 planning authoring。上述 SHA只是在本輪 rework前觀測到的
  historical／pre-publish head，不得稱為本 snapshot publish後的 current PR head。
  Snapshot commit後，actual `pr-open`、head、CI、review與conversation state只能
  發布在 PR body或 comment，不回填到同一 commit。Bounded implementation完成後，
  獨立 Implementation Reviewer指出單一 P1：topology contract遺漏既有 locked
  PR author、write-qualified maintainer inventory與 explicit qualification
  predicate。Workflow已依 canonical `reviewer-in-progress` -> `needs-rework`
  返回 bounded implementation修正邊界。Bounded Implementer完成單一 P1並提供
  predicate／derivation validation evidence後，workflow再依
  `needs-rework` -> `creator-in-progress` -> `review-ready`前進；此狀態仍是
  pre-publish snapshot，不構成 review approval。後續 planning consistency
  Reviewer指出兩項 drift：P1 plan topology minimum JSON／acceptance未完整對齊
  locked implemented contract；P2 step將 pre-P1 hash與 `needs-rework`誤寫成 current
  truth。兩項 bounded fix已依 `reviewer-in-progress` -> `needs-rework` ->
  `creator-in-progress` -> `review-ready`完成，未改變 locked contract。
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
- Publish後 PR head變更會使任何先前 evidence stale；必須在 PR-visible surface對
  new exact committed head重新取得 Reviewer verdict。
- 本 topic 不需要 repo-visible review-log，也不宣告 round cap；review routing 使用
  standard workflow contract。
- Pre-publish external observation（historical trigger only）：
  - repository／PR：`a129924/mlops-async`／`#52`；
  - observed head：`dbe86b96c0b403b24e24dfddd5fa0520049b027e`；
  - observed `python-ci`：success；
  - verdict：`needs-rework`；
  - observed unresolved conversations：`13`。
- Current actionable threads：
  - #11 published-head self-reference：
    `PRRT_kwDOSTt_386TSiGc`／`PRRC_kwDOSTt_387Y6PeK`／`DB3639146378`，
    source為 plan lines 149-151；
  - #12 PR-visible review evidence provenance：
    `PRRT_kwDOSTt_386TSiGi`／`PRRC_kwDOSTt_387Y6PeS`／`DB3639146386`，
    source為 gate-contract lines 61-71；
  - #13 independently verifiable topology proof：
    `PRRT_kwDOSTt_386TSiGn`／`PRRC_kwDOSTt_387Y6PeX`／`DB3639146391`，
    source為 gate-contract lines 47-55。
- #1至#10 substantive status保持既有判定：內容已 addressed、outdated或仍依
  external evidence pending；在 GitHub reply／resolve前，observed inventory仍全部
  unresolved。
- 尚未滿足的 boundaries：
  1. 單一 P1 bounded implementation已由
     `/root/solo_governance_rework_implementer`完成；49/49、50/50與12/12 checks
     PASS，且 locked requirement未變更。仍須由獨立 Implementation Reviewer對
     最新 exact六檔 diff複審；
  2. Snapshot commit後，獨立 Reviewer必須審查 actual exact committed PR head，
     並把合格 provenance evidence發布至 PR body或 comment；
  3. observed unresolved `13`尚待 authorized reply／resolve；PR body中 count `10`
     已 stale，external update仍 pending；
  4. merge與 tag仍需新的 explicit human authorization。
- Human已明確授權 PR #52 comment review／fix／reply／resolve全部 unresolved
  actionable threads；此授權不包含 merge或 tag，兩者仍是獨立 human boundary。

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

Current bounded rework additions（plan review通過後執行）：

7. 在 `.agents/skills/git-release-management/SKILL.md` 與
   `.agents/skills/git-release-management/references/gate-contract.md` 鎖定
   repo-visible plan／step是 pre-publish `review-ready` snapshot；snapshot commit後的
   actual PR head、CI、review與 conversation state只能更新於 PR body或 comment，
   不得回填到同一 commit形成 published-head self-reference。
8. 在上述兩個 primary contract surfaces加入 PR-visible independent review
   provenance contract：evidence必須可擷取，且其
   `repository_full_name`、`pull_request_number`與 `reviewed_commit_sha` 必須綁定
   同一 repository、同一 PR與 exact committed head。僅在需要保持既有語意一致時
   更新 `emergency-path.md`；不得擴張 emergency bypass。
9. 在上述兩個 primary contract surfaces加入可獨立驗證的 topology proof：
   GitHub collaborator／permission query provenance必須可擷取、fresh、scope明確，
   並含 nonempty permission-bearing entries；由其導出 qualified non-author
   reviewer inventory與 sole-maintainer verdict。`examples.md`只使用 placeholders，
   不得包含 private inventory、token或 secret。
10. 僅在 exact六檔 artifact contract內執行 scenario、schema、scope與 repository
    hygiene validation；在 `.step.md`保留 threads #11至#13的 external
    reply／resolve為 pending，直到獨立 review、publish後 exact-head evidence與
    GitHub reply／resolve都實際完成。
11. 依 Implementation Reviewer單一 P1執行 bounded rework：由 Implementer更新
    `SKILL.md`與 `gate-contract.md`，使 topology contract明確包含既有 locked
    PR author、write-qualified maintainer inventory與 explicit qualification
    predicate；`examples.md`只在需要時加入無 private data的 placeholders，
    `emergency-path.md`只做一致性修正。不得新增 artifact或改變 locked requirement。

## Validation / Acceptance Checks

Contract checks：

- 三個 core contract surfaces 對 normal reviewer gate 的語意一致：collaborative path
  需要 qualified non-author GitHub `APPROVED`；sole-maintainer path 需要 current
  GitHub topology proof 與 latest-head independent agent review evidence。
- 無法取得或無法判定 current maintainer inventory 時，結果為 `BLOCKED`，不得從聊天、
  ruleset approval count 或歷史 evidence 推定 sole-maintainer eligibility。
- Topology proof必須提供可擷取的 GitHub collaborator／permission query provenance，
  包含 repository、evidence URL或 API endpoint、observation UTC、正整數 freshness
  limit、query scope、exact `pr_author_login`、fixed
  `write_qualification_predicate`與 nonempty permission-bearing entries；每個 entry
  必須包含 login、recognized role，以及 boolean `admin`／`maintain`／`push`
  permissions。
- 只依 fixed predicate將 role `admin`／`maintain`／`write`，或 boolean
  permission `admin`／`maintain`／`push`為 `true`的 entry導出為
  `write_qualified_maintainers`；`triage`／`read` alone不合格。
  `qualified_non_author_reviewers`必須由 derived write-qualified inventory排除
  exact PR author導出，不得接受 self-asserted inventory。
- Sole-maintainer topology PASS必須同時滿足：provenance current、retrievable且
  repository scope正確；entries nonempty且 fully classifiable；derived
  `write_qualified_maintainers` exact一人且等於 `pr_author_login`；derived
  `qualified_non_author_reviewers`為空；`sole_maintainer_verified=true`與所有
  derived values一致。
- Arbitrary string、empty entries加 self-asserted boolean、missing／mismatched PR
  author、zero／multiple qualified maintainers、unknown／missing／non-boolean
  role或permissions、self-asserted inventories、stale／unretrievable provenance，
  或 derived inventory／verdict矛盾，一律 `BLOCKED`。Repo examples不得揭露
  private collaborator inventory、token或 secret。
- Agent evidence 包含 locked minimum fields與 reviewer run/session identifier；
  `reviewed_commit_sha` 必須 equal latest PR head SHA，否則為 stale 並 `BLOCKED`。
- Independent review evidence發布於 PR body或 comment，且
  `repository_full_name`、`pull_request_number`與 `reviewed_commit_sha`必須分別
  exact綁定同一 repository、PR與 committed current PR head；`evidence_url`必須可
  擷取並指向該 PR body或 comment，`published_at_utc`必須有效。Missing、
  unretrievable、non-PR-visible或任一 binding mismatch均 `BLOCKED`；plan／step
  content hash、working-tree hash或 repo-local self-approval claim不能替代 external
  evidence。
- Repo-visible plan／step只表示 pre-publish `review-ready` snapshot。Snapshot
  commit後的 actual PR head、CI、review與 conversation state由 PR body或 comment
  承載，不得回填到同一 commit宣稱 published-head truth。
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
   任意字串、空 inventory加 boolean、不可擷取或與 permission-bearing entries
   矛盾的 evidence也同樣 BLOCKED。
5. Agent review SHA與 latest PR head不一致，或 rework 後未重審：BLOCKED。
6. Agent JSON 宣告 `non_live_ci_contract_verified=true`，但 actual GitHub
   `python-ci`缺失／失敗：BLOCKED。
7. Unresolved thread 非零、workspace dirty、version sources不同步或 target tag已存在：
   BLOCKED，且不得用任一 reviewer path bypass。
8. Missing reviewer evidence 改走 emergency，但缺少 marker、human confirmation、
   urgency explanation 或 anomaly record 任一項：BLOCKED。
9. Emergency evidence齊全，但 unresolved review threads非 `0`或 head落後 base：
   BLOCKED；example不得把任一條件表達為 optional。
10. Independent review evidence存在，但 URL不可擷取、不是 PR body／comment，
    或 repository／PR／SHA任一不匹配：BLOCKED。
11. Snapshot commit後 PR head或 conversation state改變：repo snapshot不得自稱
    current；PR-visible evidence必須針對 actual exact head重新發布。

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
