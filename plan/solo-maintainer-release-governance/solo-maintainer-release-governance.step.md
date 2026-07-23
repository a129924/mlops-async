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
> 本輪 pre-publish observation：PR #52 head
> `f4a40cb74e0261dab3b98e3a2a6b2894a966bc8b` 的 `python-ci` success，complete
> thread inventory為 unresolved `15`；PR body count `13` 已 stale。
> Threads #14／#15使 planning workflow先依 canonical `review-ready` ->
> `reviewer-in-progress` -> `needs-rework`記錄 blockers，再依 human-authorized
> Option A authoring走 `needs-rework` -> `creator-in-progress` -> `review-ready`。
> Final plan Current與本檔 phase均為 pre-publish `review-ready`；不構成 reviewer
> approval或 publish後 current truth。
> 後續 Tester回報 single P1 `FAIL`：pagination minimum JSON缺少 deduplicated
> `total_entries`及`page_count`／`total_retrieved`／`total_entries`
> reconciliation gate。本次只修改 plan／step的 bounded fix已依 canonical
> reviewer／test gate -> `needs-rework` -> `creator-in-progress` ->
> `review-ready`完成；final兩檔仍為 pre-publish `review-ready`。
> Plan-Reviewer其後回報 single `needs-rework`：plan current truth仍將 threads
> #14／#15 substantive implementation／local validation列為 pending。本次只同步
> plan／step，依 `reviewer-in-progress` -> `needs-rework` ->
> `creator-in-progress` -> `review-ready`完成；final兩檔仍為 pre-publish
> `review-ready`。
> #1至#13內容已 addressed但仍 unresolved；#14／#15的 bounded contract
> implementation與validation已完成。Publish後 allowlisted external GitHub App／bot
> exact-new-head review、new-head CI與全部15 threads reply／resolve仍為 pending。
> Local subagent Reviewer結果只能標示 `preflight_only=true`並作 advisory，不得
> 映射為 authoritative GitHub actor／review／approval。
> Comment fix／reply／resolve已獲授權；merge、tag與 release未獲授權。
> 只有實際完成並有 evidence 的項目才可標記為 `[X]`。

## Implementation Steps

- [X] 1. 更新 `.agents/skills/git-release-management/SKILL.md`，將 verified
  sole-maintainer path改為 human-authorized Option A external GitHub App／bot review
  object，保留 collaborative path、current topology sensing、exact-head freshness
  與 blocked failure handling。
- [X] 2. 更新
  `.agents/skills/git-release-management/references/gate-contract.md`，定義 dual
  normal reviewer gate、complete-pagination topology proof、external GitHub
  App／bot minimum schema與其他獨立 hard gates。
- [X] 3. 更新
  `.agents/skills/git-release-management/references/emergency-path.md`，明確區分
  sole-maintainer normal path與 emergency reviewer-evidence bypass，保留所有既有
  emergency evidence與 non-bypassable gates。
- [X] 4. 收斂既有三個 core contract surfaces：local preflight只能
  `preflight_only=true`；actual `COMMENTED`不得稱為 GitHub `APPROVED`；不以
  ruleset approvals `0` 推定 sole maintainer，也不弱化其他 hard gates。
- [X] 5. 僅更新 `.agents/skills/git-release-management/examples.md` 的 emergency
  example，明確加入 conversation resolution exact `0` 與 head up to date with
  base；保留所有其他 emergency hard gates。
- [X] 6. 完成 Option A exact六檔 bounded diff、contract scenario checks、
  `git diff --check`與 applicable repository hygiene checks後才記錄 evidence。
- [X] 7. Plan／step已鎖定 pre-publish `review-ready` snapshot boundary；commit後
  GitHub dynamic truth不得回填到同一 commit。
- [X] 8. 在 `SKILL.md`與`gate-contract.md`完成 authoritative external GitHub
  App／bot provenance schema；移除 authoritative local run mapping，保留 actual
  state並分開記錄 semantic verdict。
- [X] 9. 在既有 exact六檔 surfaces完成 thread #14 complete pagination contract：
  strategy、per-page／cursor、`page_count`、`total_retrieved`、deduplicated
  `total_entries`、每頁 URL／cursor／next evidence、terminal-next-absent與
  `pagination_complete`；三個 counts必須 reconciliation，且`total_entries` exact
  等於 deduplicated complete inventory count。Unknown／incomplete／page failure／
  cursor loop／truncation／cross-page contradiction或 count mismatch均`BLOCKED`，
  只有 reconciled complete inventory可產生 derived lists。
- [X] 10. 對 threads #14／#15完成 exact六檔 scenario、schema、scope、
  `git diff --check`與 applicable repository hygiene validation；不得新增 workflow、
  signing、key、secret、attestation artifact、settings change或 self-hash ledger。
- [X] 11. 既有 single-P1 topology predicate／derivation bounded rework與 historical
  validation已完成；不構成 Option A authoritative reviewer evidence。
- [X] 12. 在 existing exact六檔 surfaces完成 human-authorized Option A rework；
  初始 allowlist exact為`chatgpt-codex-connector[bot]`／`type=Bot`，reviewer不得是
  PR author，local preflight只能`preflight_only=true`。

## PR Rework Checklist

- [X] #1至#13的 substantive content已 addressed；GitHub尚未 resolve，因此 complete
  inventory仍將它們計入 unresolved。
- [X] 本輪 planning authoring已依
  `review-ready` -> `reviewer-in-progress` -> `needs-rework` ->
  `creator-in-progress` -> `review-ready`完成；plan Current與 step phase final均為
  pre-publish `review-ready`。
- [X] Thread #14 complete collaborator pagination contract已完成 bounded
  implementation與validation：
  `PRRT_kwDOSTt_386TT3Io`／`PRRC_kwDOSTt_387Y8IP5`／`DB3639641081`。
- [X] Thread #15 Option A authoritative external reviewer identity boundary已完成
  bounded implementation與validation：
  `PRRT_kwDOSTt_386TT3Iq`／`PRRC_kwDOSTt_387Y8IP8`／`DB3639641084`。
- [ ] Publish後取得 allowlisted
  `chatgpt-codex-connector[bot]`／`type=Bot`對 actual exact new PR head的可擷取
  GitHub review object；reviewer不得是 PR author，object body semantic verdict須為
  `approved`且 blocking issues為空。Actual `COMMENTED`必須維持`COMMENTED`，不得
  稱為 GitHub `APPROVED`。Local `preflight_only=true`結果不能替代。
- [ ] 確認 actual new PR head的 `python-ci` success；現有 success只綁定本輪
  pre-publish observed head，不能預先覆蓋 publish後 head。
- [ ] 逐項 reply並 resolve complete inventory中的全部15 threads，再以完整 pagination
  重取 authoritative inventory確認 unresolved exact `0`；PR body count `13`已
  stale，需 external update。
- [ ] Merge與 tag各自取得新的 explicit human authorization；本次 comment
  review／fix／reply／resolve授權不涵蓋兩者。

## Implementation Evidence

- Topic base：`59cc292e10fdc0144d9caf9d343dd264a8cff9b5`。
- Historical local Plan／Implementation Reviewer結果只保留為
  `preflight_only=true` workflow history，不得作為 authoritative reviewer gate
  evidence或映射成 GitHub actor／review／approval。
- Scenario contract assertions：`27/27 PASS`，涵蓋 collaborative、
  sole-maintainer valid／invalid identity、fully evidenced emergency、
  missing evidence／hard gate、exact-head stale與 conversation exact 0；此為
  threads #14／#15前的 baseline，不能證明 Option A delta。
- Topology baseline schema validation為 historical PASS；complete pagination與
  external GitHub App／bot reviewer schema已由本輪 delta validation補齊。
- Threads #14／#15 delta scenario與contract assertions：`30/30 PASS`。Pagination
  覆蓋 multi-page／terminal-next success、middle-page failure、cursor loop、
  truncation、count mismatch、incomplete、missing terminal proof及 cross-page
  dedup conflict；external review覆蓋 valid allowlisted bot
  `COMMENTED`＋semantic-approved body、PR author、wrong actor／type／repo／PR、
  stale SHA／base-sync、state wording mismatch、missing body、non-approved verdict、
  nonempty blockers與 unretrievable object。
- Threads #14／#15 scope與hygiene assertions：`29/29 PASS`；包含 topic-base exact
  六檔、non-ignored untracked exact `0`、四個 JSON blocks parse、
  no dual authoritative local-run schema、emergency/hard-gate retention、
  merge-marker、500 KiB與`git diff --check`。
- Pagination total-entry delta assertions：`12/12 PASS`；`total_retrieved`與逐頁
  retrieved count總和一致，`total_entries`與 consistent dedup後完整 inventory長度
  一致，positive multi-page example明確覆蓋跨頁相同 login的一致 dedup。
- Tester single-P1 `FAIL`指出 plan topology minimum JSON與 acceptance尚未宣告
  deduplicated `total_entries`及三個 count reconciliation；本次 bounded plan／step
  fix已補齊，並依 `needs-rework` -> `creator-in-progress` -> `review-ready`回到
  pre-publish review boundary。此記錄不構成 Tester retest PASS。
- Plan-Reviewer後續 single `needs-rework`指出 plan pending boundary與 step evidence
  不一致；本次已將 threads #14／#15 substantive implementation與 local validation
  同步為 complete。External exact-new-head review、new-head CI與全部15 threads
  reply／resolve未完成，仍是唯一 external pending gates；此 bounded fix不構成
  Plan-Reviewer re-review approval。
- Current exact-six repository local-path guard：PASS；使用既有 worktree Python
  environment執行，未讀取 secret、未執行 live E2E或 external mutation。
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
  只可作 `preflight_only=true` advisory，不等於 authoritative external review
  object或 GitHub `APPROVED`。
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
  self-referential planning approval claim。該 review與 CI只屬歷史 evidence，
  不涵蓋本次 planning rework或未來 snapshot commit。
- Bounded rework Implementer（2026-07-23）完成當時 scope；local actor identity
  不屬於 Option A authoritative external reviewer schema。
- Thread #8 bounded fix Implementer（2026-07-23）：
  `/root/solo_governance_rework_implementer`；僅修改 emergency positive／proceed
  example與本 step evidence，plan保持 ReadOnly。Example現明確要求
  `conversation resolution (unresolved review threads exactly 0)`、head up to
  date with base、完整 emergency evidence與所有 independent hard gates。
- Thread #8 bounded validation（2026-07-23）：example／contract／JSON／scope／
  merge-marker／500 KiB assertions `35/35 PASS`；相對 topic base tracked diff
  exact六檔、non-ignored untracked `0`、`git diff --check`與 repository local-path
  guard均 PASS。
- Thread #8 targeted emergency example assertions：`21/21 PASS`。
- Final exact-six working-tree review（2026-07-23）：
  `/root/solo_governance_impl_reviewer` 回報 `APPROVED`、
  `blocking_issues=[]`。
- Final exact-six working-tree test（2026-07-23）：
  `/root/solo_governance_tester` 回報 `PASS`；full assertions `35/35 PASS`，
  targeted emergency example assertions `21/21 PASS`。
- 上述 review／test run只覆蓋當時 uncommitted exact-six diff，且不替代
  authoritative external exact committed-head review object。
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
  authoritative review evidence；只可標示為`preflight_only=true` advisory。
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
- Threads #11至#13 bounded validation（2026-07-23）：當時兩個 gate JSON schema均
  parse，review URL／surface／repo／PR／SHA／timestamp／retrieval與 topology
  nonempty permission entries／freshness／contradiction正反例 assertions
  `70/70 PASS`；相對 topic base tracked diff exact六檔，`git diff --check` PASS。
  此 baseline已被 threads #14／#15的新 pagination與 Option A schema要求擴充。
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
  pre-publish `review-ready`；threads #14／#15 bounded
  implementation／validation已完成，但 external publish或15 conversations
  reply／resolve尚未完成。
- 本次 planning rework尚未 commit；observed head的 review與`python-ci`均不涵蓋
  publish後 new head。Publish後必須由 allowlisted external GitHub App／bot取得
  exact-new-head review object，並重新確認 actual new-head `python-ci`。
- 所有舊 SHA review均 stale，不涵蓋 current planning diff或後續 rework SHA。
- Rework完成項目：
  1. PASS／Required Checks已採 normal route或 fully evidenced emergency route的
     互斥判定，且所有 hard gates無條件保留；
  2. phase drift已收斂，並經 `needs-rework` -> `creator-in-progress` 到達
     `review-ready`；
  3. Human Option A已取代 local actor／run mapping作為 authoritative evidence；
     local Reviewer只能`preflight_only=true`；
  4. 三個 core contract surfaces已統一使用
     `conversation resolution (unresolved review threads exactly 0)` naming；
  5. Topic plan已鎖定 external GitHub App／bot minimum schema、actual state與
     semantic verdict分離，以及 PR author／local preflight exclusion；
  6. Plan／step不承載 self-approval，並鎖定 external exact committed-head evidence
     requirement；不新增 ledger。
- Prior thread inventory history：
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
  - previous #7 reviewer schema：
    `PRRT_kwDOSTt_386TO1VR`／`PRRC_kwDOSTt_387Y1BPR`；
  - #1至#13內容已 addressed、outdated或 duplicate，但在 GitHub reply／resolve前
    仍計入 current unresolved inventory。
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
  bounded implementation與 validation，不是 authoritative review approval。
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
  1. Publish後由 allowlisted external GitHub App／bot取得 actual exact new-head
     review object；
  2. Actual new-head `python-ci` success；
  3. Complete inventory中全部15 threads reply／resolve，再確認 unresolved exact
     `0`；
  4. Merge與 tag各自取得新的 explicit human authorization。
- Human已明確授權 PR #52 comment review／fix／reply／resolve全部 unresolved
  actionable threads；merge與 tag仍是獨立 human boundary。
- PR body unresolved count `13` 已 stale；current complete inventory observed
  exact `15`。External update仍 pending，不得由本 repo-local step宣稱完成；
  snapshot commit後的 actual count只能在 PR body或 comment更新。
