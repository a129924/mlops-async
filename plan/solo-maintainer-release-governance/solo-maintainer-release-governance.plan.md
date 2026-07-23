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
    取得 allowlisted external GitHub App／bot 對最新 PR head exact SHA 的可擷取
    GitHub review object，且 review body 的 semantic verdict 為 `approved`。
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
  - 新增或修改 workflow、signing、key、secret、attestation artifact或 GitHub
    settings。
  - 修改或 merge current release PR、建立或 push `v0.13.0` tag、建立 GitHub
    Release，或執行任何 release／cleanup action。
  - 把 GitHub review object 的 actual `COMMENTED` state 描述為 GitHub
    `APPROVED`，或把 sole-maintainer repository 自動歸類為 emergency。

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
     write-qualified maintainer，且 latest PR head 有 allowlisted external GitHub
     App／bot 的可擷取 review object，其 semantic verdict 為 `approved`。
- Human 已明確核准 Option A：verified sole-maintainer path 的 authoritative reviewer
  evidence 只能是 allowlisted external GitHub App／bot review object。初始 allowlist
  candidate exact 為 `chatgpt-codex-connector[bot]`，actor `type` 必須 exact 為
  `Bot`；實際 API 回傳的 canonical login／type 必須與 allowlist exact match，且
  reviewer login 必須不等於 exact PR author。PR author 的 PR body或 comment不得
  合格。
- Local subagent Reviewer只能產生獨立標示 `preflight_only=true` 的 advisory
  preflight；它不屬於 authoritative normal gate evidence，不得映射成 GitHub actor、
  GitHub review或 GitHub approval，也不得單獨使 reviewer gate PASS。
- Sole-maintainer eligibility 不得從聊天敘述、歷史快照、ruleset approval count、
  PR author 自述或先前 release 推定。每次使用此 path 都必須讀取 current GitHub
  repository permission／collaborator evidence；若證據不可取得、含糊或顯示存在合格
  non-author reviewer，sole-maintainer path 必須 hard-block。
- Sole-maintainer topology evidence 必須可機器消費，至少記錄 repository、觀測時間、
  current evidence source、PR author、write-qualified maintainer inventory、
  qualified non-author reviewer inventory 與 `sole_maintainer_verified`。只有
  qualified non-author reviewer inventory exact 為空且
  `sole_maintainer_verified=true` 時，才能評估 Option A external-review path。
- Topology proof必須包含可重新取得的 GitHub collaborator／permission query
  provenance，minimum contract為：

  ```json
  {
    "repository_full_name": "<owner/repository>",
    "evidence_url": "<retrievable-github-api-endpoint>",
    "observed_at_utc": "<iso-8601-utc>",
    "freshness_max_age_seconds": "<positive-integer>",
    "query_scope": "<collaborator-and-permission-scope>",
    "pagination": {
      "strategy": "page-number|cursor",
      "per_page_or_cursor": "<positive-integer-per-page-or-initial-cursor>",
      "page_count": "<positive-integer>",
      "total_retrieved": "<non-negative-integer>",
      "total_entries": "<non-negative-integer-deduplicated-count>",
      "page_evidence": [
        {
          "request_page_or_cursor": "<page-number-or-cursor>",
          "evidence_url": "<retrievable-page-api-endpoint>",
          "retrieved_count": "<non-negative-integer>",
          "next_page_or_cursor": "<next-value-or-null>",
          "next_evidence": "<retrievable-header-or-page-info-proof>"
        }
      ],
      "terminal_next_absent": true,
      "pagination_complete": true
    },
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

- Collaborator／permission inventory 必須完整分頁：明確記錄 pagination strategy、
  per-page／initial cursor、`page_count`、`total_retrieved`、deduplicated
  `total_entries`、每頁 evidence URL／request cursor、retrieved count、next value與
  next evidence。所有 pages／cursors 必須逐一成功，直到 authoritative next
  evidence 證明 next absent；只有
  `terminal_next_absent=true`且`pagination_complete=true`時 inventory才可使用。
  Unknown／incomplete pagination、任一 page failure、cursor loop、truncation、
  `page_count`／`total_retrieved`／`total_entries` reconciliation mismatch或缺少
  terminal-next-absent evidence一律 `BLOCKED`。
- 完整 inventory 才能餵入 derived lists。跨頁同一 login只能在 role與 permissions
  完全一致時 deduplicate；同一 login出現任何 role／permissions矛盾一律
  `BLOCKED`，不得選擇較方便的 entry。`total_entries`必須 exact等於完整分頁結果
  經允許的 consistent-login deduplication後的 inventory count。
- Gate contract與 examples必須對`total_entries`使用同一 deduplicated-count語意與
  reconciliation規則；examples只能使用 non-private placeholders，不得省略或改寫
  此欄位。
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
- Authoritative external reviewer evidence必須審查 latest PR head exact SHA。每次
  implementation／rework／sync 造成 head SHA 改變，舊 GitHub review object立即
  失效，必須由 allowlisted external GitHub App／bot對新 SHA重新審查。
- 合格 external review object必須是 GitHub API可重新取得的 exact repository／PR
  review，並由該 object本身綁定 reviewer canonical login／type、review id／URL、
  submission UTC、exact committed PR head SHA、actual GitHub review state與 exact
  review body。Review body必須可解析出 semantic verdict `approved`及
  `blocking_issues=[]`。
  `plan.md`／`step.md` 不得以自身 content hash聲稱已 approved；本 topic不新增
  review ledger file。缺少 external exact committed-head evidence時 reviewer gate
  維持 pending／`BLOCKED`。
- Sole-maintainer external GitHub App／bot reviewer evidence 至少使用下列
  machine-consumable contract：

  ```json
  {
    "reviewer_kind": "external-github-app",
    "reviewer_login": "chatgpt-codex-connector[bot]",
    "type": "Bot",
    "repository_full_name": "<owner/repository>",
    "pull_request_number": "<positive-integer>",
    "review_id": "<positive-integer>",
    "review_url": "<retrievable-github-review-url>",
    "submitted_at_utc": "<iso-8601-utc>",
    "reviewed_commit_sha": "<exact-latest-pr-head-sha>",
    "github_review_state": "<actual-github-review-state>",
    "semantic_verdict": "approved",
    "blocking_issues": []
  }
  ```

- External reviewer evidence不得包含或宣稱 GitHub 可證明 local
  `implementer_run_id`、`reviewer_run_id`、dispatcher mapping或 local subagent
  identity；這些 local execution facts不是 authoritative external schema的一部分。
- Review evidence provenance必須可從 `review_url`重新取得，且 API object與 body
  必須 exact綁定同一 `repository_full_name`、`pull_request_number`、
  `review_id`、allowlisted reviewer login／`type=Bot`、exact
  `reviewed_commit_sha`、`submitted_at_utc`、actual `github_review_state`、
  semantic verdict `approved`及`blocking_issues=[]`。Missing、unretrievable、
  repository／PR／author／type／SHA／time／body mismatch一律 `BLOCKED`。
- `github_review_state` 必須保留 GitHub API 的 actual state；若 actual state為
  `COMMENTED`，contract與 evidence仍必須寫 `COMMENTED`，不得稱為 GitHub
  `APPROVED`。此時只有 review body的 `semantic_verdict=approved`滿足 Option A，
  不會產生 GitHub approval state。
- Repo-visible plan／step是 commit前的 `review-ready` snapshot，不承載 publish後
  動態 GitHub truth。Snapshot commit後，actual `pr-open`／current head／CI／review／
  conversation state只發布於 PR-visible body或 comment，不回填到同一 commit；此
  boundary避免 published-head self-reference。
- Actual `python-ci` success、unresolved review threads exact `0`、head 與 base
  up-to-date、base tests、strict typing、lint、documentation sync、version source
  synchronization、clean workspace 與 tag uniqueness 都維持獨立 hard gates。
- Option A external review object只滿足 verified sole-maintainer normal path 的
  reviewer evidence；actual `COMMENTED`不構成 GitHub `APPROVED`，且任何 review
  state或 semantic verdict都不構成 merge authorization 或 post-merge tag
  authorization。
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
- Local Reviewer只核對 latest diff與 dual-path contract，輸出必須標為
  `preflight_only=true`且只作 advisory；authoritative normal gate由 allowlisted
  external GitHub App／bot review object獨立滿足。不得把 local verdict映射成
  GitHub actor、review或 approval。
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
  `review-ready` snapshot。PR review在 head
  `f4a40cb74e0261dab3b98e3a2a6b2894a966bc8b` 新增 threads #14與#15後，本輪
  planning state先依 canonical `review-ready` -> `reviewer-in-progress` ->
  `needs-rework`記錄 review blockers，再由 human-authorized Option A authoring依
  `needs-rework` -> `creator-in-progress` -> `review-ready`完成 bounded plan／step
  rework。Final plan Current與 step phase均為 pre-publish `review-ready`；這不構成
  reviewer approval、publish後 current GitHub truth、merge authorization或 tag
  authorization。Snapshot commit後，actual `pr-open`、head、CI、review與
  conversation state只能發布在 PR body或 comment，不得回填到同一 commit。其後
  Tester對 plan／step回報 single P1：pagination minimum JSON缺少 deduplicated
  `total_entries`及三個計數 reconciliation gate；本 bounded fix再依 canonical
  reviewer／test gate -> `needs-rework` -> `creator-in-progress` -> `review-ready`
  完成。其後 Plan-Reviewer回報 single current-truth fix：plan仍將 threads #14／#15
  substantive implementation／local validation列為 pending；本次同步已依
  `reviewer-in-progress` -> `needs-rework` -> `creator-in-progress` ->
  `review-ready`完成。Final status仍為 pre-publish `review-ready`。
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
- Publish後 PR head變更會使任何先前 authoritative external review object stale；
  必須由 allowlisted external GitHub App／bot對 new exact committed head重新提交
  可擷取 review object。Local `preflight_only=true`結果只能作 advisory。
- 本 topic 不需要 repo-visible review-log，也不宣告 round cap；review routing 使用
  standard workflow contract。
- Pre-publish external observation（本輪 trigger only）：
  - repository／PR：`a129924/mlops-async`／`#52`；
  - observed head：`f4a40cb74e0261dab3b98e3a2a6b2894a966bc8b`；
  - observed `python-ci`：success；
  - verdict：`needs-rework`；
  - observed unresolved conversations：`15`；
  - PR body unresolved count：`13`，已 stale且待 external update。
- Current actionable threads：
  - #14 complete collaborator pagination contract：
    `PRRT_kwDOSTt_386TT3Io`／`PRRC_kwDOSTt_387Y8IP5`／`DB3639641081`；
  - #15 authoritative external reviewer identity boundary：
    `PRRT_kwDOSTt_386TT3Iq`／`PRRC_kwDOSTt_387Y8IP8`／`DB3639641084`。
- #1至#13內容均已 addressed，但在 GitHub reply／resolve前仍全部 unresolved；
  只有完整分頁後取得的 current thread inventory可以提供 derived count。
- Threads #14／#15的 substantive implementation與 local validation已在 existing
  exact六檔 surfaces完成；這不等於 external exact-new-head reviewer evidence、
  new-head CI或 GitHub thread resolution已完成。
- 尚未滿足的 boundaries：
  1. Snapshot commit後，allowlisted external GitHub App／bot必須審查 actual exact
     new PR head並提交合格、可擷取的 GitHub review object；
  2. new exact head的 actual `python-ci` success仍 pending；
  3. observed unresolved `15`均待 authorized reply／resolve；PR body count `13`
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
   實作為 collaborative GitHub approval 與 verified sole-maintainer Option A
   external GitHub App／bot review object兩條互斥路徑，並加入 current GitHub
   topology sensing、evidence freshness、exact-head review invalidation 與 blocked
   failure handling。
2. 更新
   `.agents/skills/git-release-management/references/gate-contract.md`，明確定義
   dual normal reviewer gate、完整分頁的 sole-maintainer topology evidence、
   external GitHub App／bot review minimum JSON fields，以及所有其他 release
   gates 的獨立 hard-gate地位。
3. 更新
   `.agents/skills/git-release-management/references/emergency-path.md`，明確寫出
   verified sole-maintainer 是 normal path、不是 emergency，並保留 emergency 只能
   bypass reviewer evidence 的既有 marker、human、urgency、anomaly 與 hard-gate
   requirements。
4. 對既有三個 core contract surfaces執行一致性收斂：不得把 local subagent
   preflight當作 authoritative evidence；actual `COMMENTED`不得稱為 GitHub
   `APPROVED`；不得以 ruleset approvals `0` 推定 sole maintainer；不得弱化
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
8. 在上述兩個 primary contract surfaces加入 authoritative external GitHub
   App／bot review provenance contract：review object必須可擷取，且 exact綁定
   repository、PR、allowlisted canonical reviewer login／`type=Bot`、review id、
   review URL、submission UTC、exact committed head、actual GitHub review state
   與 body semantic verdict。移除 authoritative schema中的 local
   implementer／reviewer run mapping；僅在需要保持既有語意一致時更新
   `emergency-path.md`，不得擴張 emergency bypass。
9. 在上述兩個 primary contract surfaces加入可獨立驗證的 topology proof：
   GitHub collaborator／permission query provenance必須可擷取、fresh、scope明確，
   且完整分頁到 authoritative next absent；unknown／incomplete／page failure／cursor
   loop／truncation／cross-page contradiction均 `BLOCKED`。`page_count`、
   `total_retrieved`與 deduplicated `total_entries`必須完整 reconciliation；只有完成
   分頁且一致 deduplicate後的 inventory可導出 qualified non-author reviewer
   inventory與 sole-maintainer verdict。`examples.md`只使用 placeholders，不得
   包含 private inventory、token或 secret。
10. 僅在 exact六檔 artifact contract內執行 scenario、schema、scope與 repository
    hygiene validation；在 `.step.md`記錄 threads #14／#15 substantive
    implementation與 local validation已完成，並只將 external review、new-head CI
    與全部15 threads reply／resolve保留為 pending，直到各項實際完成。
11. 依 Implementation Reviewer單一 P1執行 bounded rework：由 Implementer更新
    `SKILL.md`與 `gate-contract.md`，使 topology contract明確包含既有 locked
    PR author、write-qualified maintainer inventory與 explicit qualification
    predicate；`examples.md`只在需要時加入無 private data的 placeholders，
    `emergency-path.md`只做一致性修正。不得新增 artifact或改變 locked requirement。
12. 依 human-authorized Option A在既有 exact六檔 surfaces完成 threads #14／#15：
    planning actor只更新 plan／step contract；Implementer只更新四個
    `git-release-management` contract files及 step completion evidence。不得新增
    workflow、signing、key、secret、attestation artifact或 GitHub settings變更。

## Validation / Acceptance Checks

Contract checks：

- 三個 core contract surfaces 對 normal reviewer gate 的語意一致：collaborative path
  需要 qualified non-author GitHub `APPROVED`；sole-maintainer path 需要 current
  GitHub topology proof 與 latest-head allowlisted external GitHub App／bot review
  object。Local `preflight_only=true`結果只能是 advisory。
- 無法取得或無法判定 current maintainer inventory 時，結果為 `BLOCKED`，不得從聊天、
  ruleset approval count 或歷史 evidence 推定 sole-maintainer eligibility。
- Topology proof必須提供可擷取的 GitHub collaborator／permission query provenance，
  包含 repository、evidence URL或 API endpoint、observation UTC、正整數 freshness
  limit、query scope、pagination strategy、per-page／initial cursor、`page_count`、
  `total_retrieved`、deduplicated `total_entries`、每頁 evidence URL／request
  cursor／retrieved count／next evidence、`terminal_next_absent=true`、
  `pagination_complete=true`、exact `pr_author_login`、fixed
  `write_qualification_predicate`與 nonempty permission-bearing entries；每個 entry
  必須包含 login、recognized role，以及 boolean `admin`／`maintain`／`push`
  permissions。
- 所有 pages／cursors必須 success直到 authoritative next absent。Unknown／incomplete
  pagination、page failure、cursor loop、truncation或缺少 terminal evidence一律
  `BLOCKED`。`page_count`必須等於成功 page evidence數；`total_retrieved`必須等於
  所有 pages的 retrieved count總和；`total_entries`必須等於完整結果經允許的
  consistent-login deduplication後的 inventory count。三者任一 reconciliation
  mismatch一律 `BLOCKED`。只有 reconciled complete inventory可進入 derivation；
  duplicate login只能在 role／permissions一致時 deduplicate，任何 contradiction
  一律 `BLOCKED`。
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
- External evidence minimum schema exact包含
  `reviewer_kind=external-github-app`、`reviewer_login`、`type`、
  `repository_full_name`、`pull_request_number`、`review_id`、`review_url`、
  `submitted_at_utc`、`reviewed_commit_sha`、actual `github_review_state`、
  `semantic_verdict=approved`與`blocking_issues=[]`；不得包含 authoritative local
  run mapping。
- `review_url`必須可重新取得 GitHub review object；object與 body必須 exact綁定
  repository、PR、review id、allowlisted canonical login／`type=Bot`、非 PR author、
  latest committed head SHA、submission time、actual state與 semantic body。
  初始 allowlist candidate exact為`chatgpt-codex-connector[bot]`。任何 missing、
  unretrievable或 repository／PR／author／type／SHA／time／body mismatch均
  `BLOCKED`。
- Actual `COMMENTED`必須保持`COMMENTED`且不得稱為 GitHub `APPROVED`；只有 body的
  semantic verdict `approved`可滿足 Option A。PR author body／comment與 local
  subagent preflight均不合格。Plan／step content hash、working-tree hash或
  repo-local self-approval claim也不能替代 external review object，且不新增
  self-hash ledger。
- Repo-visible plan／step只表示 pre-publish `review-ready` snapshot。Snapshot
  commit後的 actual PR head、CI、review與 conversation state由 PR body或 comment
  承載，不得回填到同一 commit宣稱 published-head truth。
- Rework 或 base sync 改變 SHA 後，舊 external review object立即 stale，必須由
  allowlisted external GitHub App／bot重新 review exact new head。
- 文案明確區分 semantic verdict、actual GitHub state與 GitHub `APPROVED`；external
  review object不授權 merge／tag。
- Actual latest-head `python-ci`、conversation resolution exact `0`、up-to-date、
  tests、strict typing、lint、docs、version sync、clean workspace 與 tag uniqueness
  均保持獨立 hard gates，不得由 external review object欄位替代。
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
   local preflight或 non-allowlisted review，normal reviewer gate仍 BLOCKED。
3. Complete current GitHub evidence證實沒有 qualified non-author reviewer，且
   allowlisted external GitHub App／bot review object exact綁定 latest head，
   semantic verdict為`approved`且 blocking issues為空：sole-maintainer normal
   reviewer gate PASS，但仍需個別通過所有其他 hard gates與 human merge decision。
4. Sole-maintainer topology evidence缺失、過時或含糊：BLOCKED。
   任意字串、空 inventory加 boolean、不可擷取或與 permission-bearing entries
   矛盾的 evidence也同樣 BLOCKED。
5. Pagination unknown／incomplete、page failure、cursor loop、truncation、跨頁同一
   login role／permissions矛盾，或 `page_count`／`total_retrieved`／
   `total_entries` reconciliation mismatch：BLOCKED；`total_entries`必須 exact
   等於 deduplicated complete inventory count。
6. External review object SHA與 latest PR head不一致，或 rework後未重審：
   BLOCKED。
7. Unresolved thread 非零、workspace dirty、version sources不同步或 target tag已存在：
   BLOCKED，且不得用任一 reviewer path bypass。
8. Missing reviewer evidence 改走 emergency，但缺少 marker、human confirmation、
   urgency explanation 或 anomaly record 任一項：BLOCKED。
9. Emergency evidence齊全，但 unresolved review threads非 `0`或 head落後 base：
   BLOCKED；example不得把任一條件表達為 optional。
10. External review存在，但 URL不可擷取，或 repository／PR／author／type／SHA／
    time／body任一不匹配：BLOCKED。
11. GitHub API actual state為`COMMENTED`，但 evidence稱為 GitHub `APPROVED`：
    BLOCKED；必須保留 actual state並分開記錄 semantic verdict。
12. Snapshot commit後 PR head或 conversation state改變：repo snapshot不得自稱
    current；external review object必須針對 actual exact head重新取得。

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
