---
topic: solo-maintainer-release-governance
phase: pr-open
created: 2026-07-23
---

# solo-maintainer-release-governance — Step Tracking

> Completion gate 只讀取 `## Implementation Steps`。
> Topic plan 已核准；creator-owned implementation 與 bounded validation 已完成，
> READY PR #52 曾合法進入 `pr-open`。Current-head
> `def877f0090c3057f37d4e0cfba677b880d5fc3e` 的 exact-head Reviewer回傳
> `needs-rework`，single blocker是兩組 current thread IDs 的 schema／state labels
> swapped；audit-trace correction已依 canonical `pr-open` -> `needs-rework` ->
> `creator-in-progress` -> `review-ready` -> `reviewer-in-progress` -> `approved` ->
> `publish-in-progress` -> `pr-open` 完成 authoring、Plan-Reviewer審查與
> bookkeeping。Actual current-head GitHub `python-ci` success只滿足該 SHA 的 CI
> gate；後續新 exact head仍須重新取得 independent review與 CI evidence。
> PR body與 unresolved `7` conversations維持 pending；merge、tag與 release均未執行。
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
- [X] 4. 收斂三個 governance surfaces 的語意，確認不把 agent review稱為 GitHub
  `APPROVED`、不以 ruleset approvals `0` 推定 sole maintainer，也不弱化
  `python-ci`、conversation resolution或其他 release hard gates。
- [X] 5. 完成 exact五檔 bounded diff、contract scenario checks、
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
- [ ] 對 PR #52 的 `7` 個 unresolved conversations逐項 triage；需要修改時交由
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
  verification fields保持不變。Current trace：
  `PRRT_kwDOSTt_386TO1VR`／`PRRC_kwDOSTt_387Y1BPR`。
- [X] 將三個 governance surfaces 的 gate naming統一為
  `conversation resolution (unresolved review threads exactly 0)` 語意。
  Trace：`PRRT_kwDOSTt_386TOHvQ`／`PRRC_kwDOSTt_387Y0BTt`。
- [X] 將 plan Current與 step phase同步為 `review-ready`，並記錄 canonical
  `needs-rework` -> `creator-in-progress` -> `review-ready`。Current trace：
  `PRRT_kwDOSTt_386TO1VJ`／`PRRC_kwDOSTt_387Y1BPI`。

## Implementation Evidence

- Topic base：`59cc292e10fdc0144d9caf9d343dd264a8cff9b5`。
- Current planning rework Plan-Reviewer（2026-07-23）：
  `/root/solo_governance_plan_reviewer` 對 plan SHA256
  `B255CCBC95F3B9ADB5B349467360676E79D06D4725106FE45E3F6B6BC756B4A0`
  與 step SHA256
  `2DD5F22697B06581CF5283CDA093D1005423FAA7D7EF28334EED23DBA0AE1450`
  回報 `approved`、`blocking_issues=[]`。
- Planning phase已依 `review-ready` -> `reviewer-in-progress` -> `approved` ->
  `publish-in-progress` -> `pr-open` bookkeeping；此結果不改寫
  `def877f0090c3057f37d4e0cfba677b880d5fc3e` 的 implementation exact-head
  `needs-rework`，也不完成 PR body或 conversation resolution。
- Audit-trace correction Plan-Reviewer（2026-07-23）：
  `/root/solo_governance_plan_reviewer` 對 plan SHA256
  `74055E6345E0E950AA362FD510CCD8064ECFDBCE68D2E5ECC67D3424FBE2DB3E`
  與 step SHA256
  `CFC4EC8CFDF66231480924B6F1D5354545E930DC366523B77680A98884B5F046`
  回報 `approved`、`blocking_issues=[]`。
- Audit correction已依 `needs-rework` -> `creator-in-progress` -> `review-ready` ->
  `reviewer-in-progress` -> `approved` -> `publish-in-progress` -> `pr-open`
  bookkeeping；此結果保留
  `def877f0090c3057f37d4e0cfba677b880d5fc3e` implementation exact-head
  `needs-rework` historical evidence，且 PR body與 unresolved `7` conversations
  仍 pending。
- Scenario contract assertions：`27/27 PASS`，涵蓋 collaborative、
  sole-maintainer valid／invalid identity、fully evidenced emergency、
  missing evidence／hard gate、exact-head stale與 conversation exact 0。
- Topology 與 independent Reviewer evidence JSON schema：兩個 JSON examples均可
  parse，required fields PASS。
- Tracked diff 與 non-ignored untracked union：exact 五檔，PASS。
- `git diff --check`、merge-marker 與 500 KiB file-size checks：PASS。
- Repository local-path guard：以 portable `uv run --no-project` 執行，PASS。
- Tester evidence顯示 ignored `.venv` 在 test time已存在；它不屬於 tracked／
  repo-visible artifact contract。Current rework Tester未建立該目錄，且 offline
  no-project guard執行前後 timestamp未變；其 provenance unknown，不歸因於本
  topic。未執行 live E2E 或任何 external mutation。
- Pre-commit topic implementation review（2026-07-23）：
  `/root/solo_governance_impl_reviewer` 回報 `APPROVED`，blocking findings
  `None`、scope `PASS`、contract scenarios `15/15 PASS`，且 plan fingerprint
  matched。
- Pre-commit topic implementation test（2026-07-23）：
  `/root/solo_governance_tester` 回報 `PASS`，scope 為 exact five approved
  paths；scenario、schema、hash 與 hygiene checks 全部 PASS，無 implementation
  或 environment blocker。
- 上述 review／test evidence 僅證明本 topic 的 pre-commit implementation；
  不等於未來 release PR 的 exact-head independent review evidence，也不等於
  GitHub `APPROVED`。
- READY PR：[#52](https://github.com/a129924/mlops-async/pull/52)。
- PR 建立時 head：`816ab30e8d1829593542da35f0024ae09b4f2a45`。
- Current PR head：
  `def877f0090c3057f37d4e0cfba677b880d5fc3e`。
- Actual current-head GitHub `python-ci`：success；此結果不取代 reviewer verdict、
  conversation resolution或其他 hard gates。
- Current-head review（2026-07-23）：
  exact-head Reviewer對
  `def877f0090c3057f37d4e0cfba677b880d5fc3e` 回報 `needs-rework`；single
  blocker是兩組 current thread IDs 的 schema／state labels swapped。該 review與
  `python-ci` 均不涵蓋本次 uncommitted audit-trace correction。
- Bounded rework Implementer（2026-07-23）：
  `/root/solo_governance_rework_implementer`；此 canonical run identity與前述
  Reviewer identity不同。
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
- 本次 planning rework尚未 commit，current-head review與 `python-ci` 均不涵蓋此
  working-tree diff；必須由獨立 Reviewer複審，publish後再以新 exact head取得
  current-head review與 `python-ci`。
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
  4. 三個 governance surfaces已統一使用
     `conversation resolution (unresolved review threads exactly 0)` naming；
  5. Topic plan evidence JSON已加入 `implementer_run_id`／`reviewer_run_id` 與
     non-opaque、traceable、different-actor requirement。
- Current thread inventory：
  - exact unresolved：`7`，由 `/root/pr52_comment_reviewer` thread-aware inventory
    證明；
  - new current phase/state：
    `PRRT_kwDOSTt_386TO1VJ`／`PRRC_kwDOSTt_387Y1BPI`；
  - new current reviewer schema／`implementer_run_id`：
    `PRRT_kwDOSTt_386TO1VR`／`PRRC_kwDOSTt_387Y1BPR`；
  - 舊五個 emergency／identity／naming／phase／duplicate-phase threads已是
    outdated、duplicate或 addressed evidence，但在 GitHub resolve前仍計入
    unresolved。
- Pending boundaries：
  1. PR body舊 SHA review仍須由 GitHub routing明確標示 stale，並在 publish後更新
     new exact-head review；
  2. PR #52 unresolved conversations exact `7`，仍待獨立
     triage／review／reply／resolve；
  3. 本次 planning diff仍待獨立 Reviewer複審，不得以
     `def877f0090c3057f37d4e0cfba677b880d5fc3e` 的 review evidence取代。
