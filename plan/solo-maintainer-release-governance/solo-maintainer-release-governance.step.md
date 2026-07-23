---
topic: solo-maintainer-release-governance
phase: review-ready
created: 2026-07-23
---

# solo-maintainer-release-governance — Step Tracking

> Completion gate 只讀取 `## Implementation Steps`。
> 本文件是 repo-visible pre-publish `review-ready` snapshot；它不宣稱 snapshot
> commit後的 actual PR head、CI、review或 conversation state。這些 dynamic facts
> 只能發布於 PR body或 comment，不得回填到同一 commit形成 self-reference。
> Historical／pre-publish observation：PR #52 observed head
> `dbe86b96c0b403b24e24dfddd5fa0520049b027e`、observed `python-ci` success、
> observed unresolved conversations `13`。Threads #11至#13使 workflow依
> canonical `pr-open` -> `needs-rework` -> `creator-in-progress` ->
> `review-ready`返回 planning review boundary。
> 既有 Implementation Steps與 threads #11至#13的 `[X]`只代表先前有 evidence的
> bounded work；publish後 exact-head review evidence、PR body count更新與全部
> 13 threads reply／resolve仍是 pending。
> Bounded implementation後，獨立 Implementation Reviewer回報單一 P1：
> topology contract遺漏既有 locked PR author、write-qualified maintainer
> inventory與 explicit qualification predicate。Workflow已依
> `reviewer-in-progress` -> `needs-rework`返回 bounded Implementer修正邊界。
> `/root/solo_governance_rework_implementer`完成該 P1且 validation通過後，workflow
> 依 `needs-rework` -> `creator-in-progress` -> `review-ready`回到獨立
> Implementation Reviewer boundary；此 pre-publish狀態不構成 approval。
> 後續 planning consistency Reviewer指出 P1 plan topology schema／acceptance drift
> 與 P2 stale pre-P1 hash／phase current-truth drift；兩項已依
> `reviewer-in-progress` -> `needs-rework` -> `creator-in-progress` ->
> `review-ready`完成 bounded planning correction，locked contract未改變。
> Comment fix／reply／resolve已獲授權；merge、tag與 release未獲授權。
> 只有實際完成並有 evidence 的項目才可標記為 `[X]`。

## Implementation Steps

- [X] 1. 更新 `.agents/skills/git-release-management/SKILL.md`，建立
  collaborative GitHub approval 與 verified sole-maintainer agent review 兩條
  normal reviewer paths，包含 current topology sensing、exact-head freshness與
  blocked failure handling。
- [X] 2. 更新
  `.agents/skills/git-release-management/references/gate-contract.md`，定義 dual
  normal reviewer gate、sole-maintainer topology proof、minimum agent review JSON
  與其他獨立 hard gates。
- [X] 3. 更新
  `.agents/skills/git-release-management/references/emergency-path.md`，明確區分
  sole-maintainer normal path與 emergency reviewer-evidence bypass，保留所有既有
  emergency evidence與 non-bypassable gates。
- [X] 4. 收斂既有三個 core contract surfaces 的語意，確認不把 agent review稱為 GitHub
  `APPROVED`、不以 ruleset approvals `0` 推定 sole maintainer，也不弱化
  `python-ci`、conversation resolution或其他 release hard gates。
- [X] 5. 僅更新 `.agents/skills/git-release-management/examples.md` 的 emergency
  example，明確加入 conversation resolution exact `0` 與 head up to date with
  base；保留所有其他 emergency hard gates。
- [X] 6. 完成 exact六檔 bounded diff、contract scenario checks、
  `git diff --check` 與 applicable repository hygiene checks後，記錄實際 evidence；
  不執行 settings mutation、release、tag、live E2E或 secret access。

## PR Rework Checklist

- [X] 修正 `.agents/skills/git-release-management/SKILL.md` 的 PASS／Required
  Checks，使 fully evidenced emergency可作為 normal reviewer path以外的合法
  alternative，同時保留所有 non-bypassable hard gates。Trace：
  `PRRT_kwDOSTt_386TOHa-`／`PRRC_kwDOSTt_387Y0A3Z`。
- [X] 完成 plan／step phase drift修正後，依 `needs-rework` ->
  `creator-in-progress` -> `review-ready` 完成 bounded planning authoring；plan
  Current與 step phase均已同步。Primary trace：
  `PRRT_kwDOSTt_386TOHbG`／`PRRC_kwDOSTt_387Y0A3g`；duplicate trace：
  `PRRT_kwDOSTt_386TOHuq`／`PRRC_kwDOSTt_387Y0BS7`，不需新增另一個獨立 fix。
- [ ] 將 PR body中 SHA
  `816ab30e8d1829593542da35f0024ae09b4f2a45` 的 independent review明確標示
  stale，並在 publish後更新 new exact-head review；不得宣稱舊 evidence覆蓋
  current head或後續 rework SHA。
- [ ] 對 PR #52 observed `13` 個 unresolved conversations逐項 triage；需要修改時交由
  Implementer bounded fix，完成 latest-head Reviewer複審後才可回覆並 resolve。
- [X] 在 `gate-contract.md` 與 `SKILL.md` 加入 independent actor identity
  linkage：記錄可由 dispatcher execution record核對的 Reviewer與 Implementer
  canonical actor／run identity；兩者必須存在、可追溯且不相等。Missing、
  unverifiable、opaque-only或 same actor必須 `BLOCKED`；exact-head freshness仍
  required。
  Trace：`PRRT_kwDOSTt_386TOHa2`／`PRRC_kwDOSTt_387Y0A3T`。
- [X] 在 topic plan的 independent agent evidence JSON加入
  `implementer_run_id` 與 `reviewer_run_id`；兩者必須能由 dispatcher execution
  record核對、存在、可追溯、non-opaque且不相等。Missing、unverifiable、
  opaque-only或 same actor／run一律 `BLOCKED`；`reviewed_commit_sha` 與原
  verification fields保持不變。Trace：
  `PRRT_kwDOSTt_386TO1VR`／`PRRC_kwDOSTt_387Y1BPR`。
- [X] 將三個 core contract surfaces 的 gate naming統一為
  `conversation resolution (unresolved review threads exactly 0)` 語意。
  Trace：`PRRT_kwDOSTt_386TOHvQ`／`PRRC_kwDOSTt_387Y0BTt`。
- [X] Prior phase-drift rework曾將 plan Current與 step phase同步為
  `review-ready`，並記錄 canonical `needs-rework` -> `creator-in-progress` ->
  `review-ready`；後續 historical head review曾另回到 `needs-rework`，不代表本
  snapshot current phase。Trace：
  `PRRT_kwDOSTt_386TO1VJ`／`PRRC_kwDOSTt_387Y1BPI`。
- [X] 修正 `.agents/skills/git-release-management/examples.md` 的 emergency
  example，使 conversation resolution exact `0` 與 head up to date with base
  都是明確 hard gates。Trace：
  `PRRT_kwDOSTt_386TPHWi`／`PRRC_kwDOSTt_387Y1aJg`。
- [ ] 在 bounded fix commit後取得 independent Reviewer對 exact committed PR head
  SHA的 review，並將 evidence發布到 PR body或 comment；不得用 plan／step自身
  content hash宣稱 approved，也不新增 review ledger file。Trace：
  `PRRT_kwDOSTt_386TPHWl`／`PRRC_kwDOSTt_387Y1aJk`。
- [X] 修正 published-head self-reference：repo plan／step只保留 pre-publish
  `review-ready` snapshot；commit後 actual PR head、CI、review與 conversation
  state只更新於 PR body或 comment。Trace：
  `PRRT_kwDOSTt_386TSiGc`／`PRRC_kwDOSTt_387Y6PeK`／`DB3639146378`。
- [X] 在 primary contract surfaces加入 PR-visible review evidence provenance：
  `repository_full_name`、`pull_request_number`、`evidence_surface`、
  `evidence_url`、`published_at_utc`必須可擷取並綁定同 repo／PR／exact
  `reviewed_commit_sha`；missing、unretrievable、non-PR-visible或 mismatch均
  `BLOCKED`。Trace：
  `PRRT_kwDOSTt_386TSiGi`／`PRRC_kwDOSTt_387Y6PeS`／`DB3639146386`。
- [X] 在 primary contract surfaces加入 independently verifiable topology proof：
  GitHub collaborator／permission query provenance必須可擷取、fresh、scope明確，
  含 nonempty permission-bearing entries，並可導出 qualified non-author reviewer
  inventory與 sole-maintainer verdict；arbitrary strings、empty inventory加
  boolean、stale／unretrievable或 contradictory evidence均 `BLOCKED`。Examples
  只可使用 placeholders，不得含 private inventory或 secrets。Trace：
  `PRRT_kwDOSTt_386TSiGn`／`PRRC_kwDOSTt_387Y6PeX`／`DB3639146391`。
- [X] 依 Implementation Reviewer單一 P1執行 bounded fix：在 `SKILL.md`與
  `gate-contract.md`明確加入既有 locked PR author、write-qualified maintainer
  inventory與 explicit qualification predicate；`examples.md`依需要使用
  non-private placeholders，`emergency-path.md`只做 consistency alignment。
  修改範圍保持 exact六檔，不得新增 artifact、重新定義或弱化 locked requirement。

## Implementation Evidence

- Topic base：`59cc292e10fdc0144d9caf9d343dd264a8cff9b5`。
- Historical internal Plan-Reviewer runs只保留為 workflow history；先前以
  plan／step自身 content hash表達 approval的 claims已移除，且不得作為 reviewer
  gate evidence。合格 evidence必須由獨立 Reviewer對 exact committed PR head SHA
  產生並發布於 PR body或 comment。
- Scenario contract assertions：`27/27 PASS`，涵蓋 collaborative、
  sole-maintainer valid／invalid identity、fully evidenced emergency、
  missing evidence／hard gate、exact-head stale與 conversation exact 0。
- Topology 與 independent Reviewer evidence JSON schema：兩個 JSON examples均可
  parse，required fields PASS。
- Tracked diff 與 non-ignored untracked union：相對 topic base exact六檔，PASS。
- `git diff --check`、merge-marker 與 500 KiB file-size checks：PASS。
- Repository local-path guard：以 portable `uv run --no-project` 執行，PASS。
- Tester evidence顯示 ignored `.venv` 在 test time已存在；它不屬於 tracked／
  repo-visible artifact contract。Current rework Tester未建立該目錄，且 offline
  no-project guard執行前後 timestamp未變；其 provenance unknown，不歸因於本
  topic。未執行 live E2E 或任何 external mutation。
- Pre-commit topic implementation review（2026-07-23）：
  `/root/solo_governance_impl_reviewer` 回報 `APPROVED`，blocking findings
  `None`、scope `PASS`、contract scenarios `15/15 PASS`。此為 historical
  working-tree review，不是 external exact committed-head evidence。
- Pre-commit topic implementation test（2026-07-23）：
  `/root/solo_governance_tester` 回報 `PASS`，scope 為 exact five approved
  paths；scenario、schema與 hygiene checks全部 PASS，無 implementation或
  environment blocker。
- 上述 review／test evidence 僅證明本 topic 的 pre-commit implementation；
  不等於未來 release PR 的 exact-head independent review evidence，也不等於
  GitHub `APPROVED`。
- READY PR：[#52](https://github.com/a129924/mlops-async/pull/52)。
- PR 建立時 head：`816ab30e8d1829593542da35f0024ae09b4f2a45`。
- Historical／pre-publish observed PR head：
  `dbe86b96c0b403b24e24dfddd5fa0520049b027e`。
- Historical／pre-publish observed GitHub `python-ci`：success；此結果只描述
  observed SHA，且不取代 reviewer verdict、conversation resolution或其他 hard
  gates。
- Historical review lineage（2026-07-23）：
  earlier exact-head Reviewer曾對
  `40d09aeac922c7ed95374b4e7a661e54780d28c9` 回報 `needs-rework`；blocking
  issues是 thread #8 emergency example hard-gate omission與 thread #9
  self-referential planning hash approval。該 review與 CI只屬歷史 evidence，
  不涵蓋本次 planning rework或未來 snapshot commit。
- Bounded rework Implementer（2026-07-23）：
  `/root/solo_governance_rework_implementer`；此 canonical run identity與前述
  Reviewer identity不同。
- Thread #8 bounded fix Implementer（2026-07-23）：
  `/root/solo_governance_rework_implementer`；僅修改 emergency positive／proceed
  example與本 step evidence，plan保持 ReadOnly。Example現明確要求
  `conversation resolution (unresolved review threads exactly 0)`、head up to
  date with base、完整 emergency evidence與所有 independent hard gates。
- Thread #8 bounded validation（2026-07-23）：example／contract／JSON／scope／
  merge-marker／500 KiB assertions `35/35 PASS`；相對 topic base tracked diff
  exact六檔、non-ignored untracked `0`、`git diff --check`與 repository local-path
  guard均 PASS。Example SHA256：
  `CA691C00D92ECBDEBC9C6EE22962AA3B513D43704FA4918BA5DB3CCFA3767664`。
- Implementer-delivered pre-bookkeeping step snapshot SHA256：
  `44E4CC762C187723FCF517727EFA786F8D05BFAE1B30374303B3BCD9D0684989`。
  此 hash只識別 Implementer evidence snapshot，不構成 review approval，也不替代
  external exact committed-head evidence。
- Thread #8 targeted emergency example assertions：`21/21 PASS`。
- Final exact-six working-tree review（2026-07-23）：
  `/root/solo_governance_impl_reviewer` 回報 `APPROVED`、
  `blocking_issues=[]`。
- Final exact-six working-tree test（2026-07-23）：
  `/root/solo_governance_tester` 回報 `PASS`；full assertions `35/35 PASS`，
  targeted emergency example assertions `21/21 PASS`。
- 上述 review／test run只覆蓋 current uncommitted exact-six diff；未使用
  plan／step self-content hash、未建立 ledger，且不替代 external exact
  committed-head evidence。
- Bounded rework validation（2026-07-23）：contract／JSON／scope／merge-marker／
  500 KiB assertions `27/27 PASS`；`git diff --check`與 repository local-path
  guard PASS。
- Current bounded rework test（2026-07-23）：
  `/root/solo_governance_tester` first verdict `FAIL`；唯一 finding是 step曾錯誤宣稱
  worktree `.venv`未建立，並非 governance contract、scope或其他 validation
  failure。Bounded evidence correction已完成，phase回到 `review-ready`；不得由
  `.venv`存在推定建立者或將 ignored environment納入本 topic scope。
- Bounded rework implementation review（2026-07-23）：
  `/root/solo_governance_impl_reviewer` 對 bounded working-tree diff回報
  `APPROVED`；此結果不是 GitHub `APPROVED`，也不是 publish後 new exact head的
  independent review evidence。
- Bounded rework Tester retest（2026-07-23）：
  `/root/solo_governance_tester` 回報 `PASS`，contract／JSON／scope／hygiene
  assertions `27/27 PASS`；first-verdict evidence mismatch已完成 bounded
  correction，無 remaining test blocker。
- Threads #11至#13 bounded implementation（2026-07-23）：
  `/root/solo_governance_rework_implementer` 僅更新核准的 existing contract
  surfaces與本 step evidence。Thread #11的 pre-publish `review-ready` snapshot
  boundary由 Plan-Creator完成且已驗證；threads #12／#13分別加入可擷取的
  PR-visible review evidence provenance與 GitHub collaborator／permission
  topology proof。Emergency route仍只可 bypass missing pre-release reviewer
  evidence，所有 hard gates保持不變。
- Threads #11至#13 bounded validation（2026-07-23）：兩個 gate JSON schema均
  parse，review URL／surface／repo／PR／SHA／timestamp／retrieval與 topology
  nonempty permission entries／freshness／contradiction正反例 assertions
  `70/70 PASS`；相對 topic base tracked diff exact六檔，`git diff --check` PASS。
  Locked plan SHA256維持
  `A9D3359B134AED874787D53C704E7170F1B56250D80240E3DA2DF9AD06D6783B`。
- Single-P1 bounded fix（2026-07-23）：
  `/root/solo_governance_rework_implementer` 在既有 contract surfaces加入 exact
  `pr_author_login`、固定 write-qualified predicate、derived
  `write_qualified_maintainers`與 derived
  `qualified_non_author_reviewers`。Predicate只接受 GitHub role
  `admin`／`maintain`／`write`，或 boolean permission
  `admin`／`maintain`／`push`；`triage`／`read` alone不合格。Sole path只在
  exactly one write-qualified maintainer等於 PR author且 derived non-author list
  為空時成立；第二位 qualified actor改走 collaborative path，missing／unknown／
  stale／unretrievable／contradictory／self-asserted evidence均 `BLOCKED`。
- Single-P1 bounded validation（2026-07-23）：topology schema／predicate／synthetic
  derivation正反例 assertions `49/49 PASS`；既有 review provenance、snapshot、
  emergency hard gates、exact六檔 scope與 hygiene assertions `50/50 PASS`。
  先前 pre-P1 bookkeeping snapshot與當時 `needs-rework`狀態均是 historical、
  non-current且不構成 approval。Current step phase與 plan Current均為
  pre-publish `review-ready`；未完成 external publish或 13 conversations
  reply／resolve。
- 本次 planning rework尚未 commit；historical observed review與 `python-ci`均不
  涵蓋此 working-tree diff。必須由獨立 Reviewer複審，publish後再以 actual exact
  head取得 PR-visible review evidence與 `python-ci`。
- PR body針對
  `816ab30e8d1829593542da35f0024ae09b4f2a45` 的 independent review已 stale，
  不涵蓋 current head或後續 rework SHA。
- Rework完成項目：
  1. PASS／Required Checks已採 normal route或 fully evidenced emergency route的
     互斥判定，且所有 hard gates無條件保留；
  2. phase drift已收斂，並經 `needs-rework` -> `creator-in-progress` 到達
     `review-ready`；
  3. Reviewer／Implementer canonical actor／run identity已加入可核對、必須不同的
     hard-block contract；
  4. 三個 core contract surfaces已統一使用
     `conversation resolution (unresolved review threads exactly 0)` naming；
  5. Topic plan evidence JSON已加入 `implementer_run_id`／`reviewer_run_id` 與
     non-opaque、traceable、different-actor requirement；
  6. Plan／step的 self-referential content-hash approval claims已移除，並鎖定
     external exact committed-head evidence requirement。
- Historical／pre-publish observed thread inventory：
  - exact unresolved：`13`；
  - thread #11 published-head self-reference：
    `PRRT_kwDOSTt_386TSiGc`／`PRRC_kwDOSTt_387Y6PeK`／`DB3639146378`，
    source為 plan lines 149-151；
  - thread #12 PR-visible review evidence provenance：
    `PRRT_kwDOSTt_386TSiGi`／`PRRC_kwDOSTt_387Y6PeS`／`DB3639146386`，
    source為 gate-contract lines 61-71；
  - thread #13 independently verifiable topology proof：
    `PRRT_kwDOSTt_386TSiGn`／`PRRC_kwDOSTt_387Y6PeX`／`DB3639146391`，
    source為 gate-contract lines 47-55；
  - thread #10 second stale audit-trace hash assertion：
    `PRRT_kwDOSTt_386TPTpn`／`PRRC_kwDOSTt_387Y1rV9`／`DB3637949821`，
    source為 plan lines 190-192；current actionable，與 thread #9同 cluster但不是
    pure duplicate。Existing removal of all self-referential approval claims已
    substantive address此 finding，但 GitHub resolve前仍 unresolved；
  - thread #8 emergency example：
    `PRRT_kwDOSTt_386TPHWi`／`PRRC_kwDOSTt_387Y1aJg`；
  - thread #9 external exact committed-head review：
    `PRRT_kwDOSTt_386TPHWl`／`PRRC_kwDOSTt_387Y1aJk`；
  - previous #6 phase/state：
    `PRRT_kwDOSTt_386TO1VJ`／`PRRC_kwDOSTt_387Y1BPI`；
  - previous #7 reviewer schema／`implementer_run_id`：
    `PRRT_kwDOSTt_386TO1VR`／`PRRC_kwDOSTt_387Y1BPR`；
  - #1至#7內容已 addressed、outdated或 duplicate，但在 GitHub reply／resolve前
    仍計入 unresolved。
- Historical bounded Implementation Reviewer verdict：`needs-rework`；single P1是
  topology contract遺漏 locked PR author、write-qualified maintainer inventory與
  explicit qualification predicate。已記錄 canonical
  `reviewer-in-progress` -> `needs-rework`；不得由 Plan-Creator直接修改 skill或
  reference implementation。
- Single-P1 bounded implementation：
  `/root/solo_governance_rework_implementer`回報完成；qualification predicate與
  topology derivation contract已補齊，locked requirement未變更。Validation
  evidence為 full assertions `49/49 PASS`、targeted assertions `50/50 PASS`與
  additional predicate／derivation assertions `12/12 PASS`。此 run／verdict只證明
  bounded implementation與 validation，不是 review approval，亦未使用 self-hash
  approval claim。
- Planning consistency findings已完成 bounded correction：
  1. P1：plan topology minimum JSON與 acceptance已對齊 locked／implemented
     `pr_author_login`、fixed `write_qualification_predicate`、derived
     `write_qualified_maintainers`、derived
     `qualified_non_author_reviewers`及 exact derivation／BLOCKED rules；
  2. P2：移除 stale pre-P1 hash的 current-truth claim，並將當時
     `needs-rework`明確標示為 historical、non-current、non-approval。
  Workflow記錄為 `reviewer-in-progress` -> `needs-rework` ->
  `creator-in-progress` -> `review-ready`。
- Pending boundaries：
  1. 上述 single-P1 exact六檔修正仍須交由獨立 Implementation Reviewer複審；
  2. Bounded fix commit後仍須取得 external exact committed-head independent
     review evidence，並發布到 PR body或 comment；不得使用 self-hash claim；
  3. PR body舊 SHA review仍須明確標示 stale，並在 publish後更新 new exact-head
     review；
  4. PR #52 observed unresolved conversations exact `13`，仍待獨立
     triage／review／reply／resolve；
  5. 本次 exact六檔 working-tree diff仍待獨立 Reviewer複審，不得以任何
     historical head的 review evidence取代。
- Human已明確授權 PR #52 comment review／fix／reply／resolve全部 unresolved
  actionable threads；merge與 tag仍是獨立 human boundary。
- PR body unresolved count `10` 已 stale；external update至 observed exact `13`
  仍 pending，不得由本 repo-local step宣稱完成。Snapshot commit後的 actual
  count只能在 PR body或 comment更新。
