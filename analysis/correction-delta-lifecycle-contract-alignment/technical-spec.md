# Correction / Delta Lifecycle Contract Alignment — Technical Spec

## Status

- **Status**: 凍結的技術基線
- **Topic**: `correction-delta-lifecycle-contract-alignment`
- **Source baseline**:
  `analysis/correction-delta-lifecycle-contract-alignment/requirements.md`
- **Upstream source of truth**: 已發布的 `agent-skills` `0.58.0` lifecycle
  contract
- **This round**: 本輪包含 analysis baseline、topic plan 與 governance workflow/planning surfaces 的對齊（已執行）；不含 `src/**`、`tests/**`、release / tag 或 sample payload rewrite。

## Baseline Summary

`mlops-async` 已經包含應承載此 contract 的本地 workflow surfaces：

- `plan/agent-handoff-workflow.md`
- `.github/agents/python-implementation-workflow.agent.md`
- `.github/skills/plan-creator/**`
- `.github/skills/plan-reviewer/**`

它也已在 `v0.9.2` 中保留一個具體 sample：

- parent artifacts 已回填為 current truth
- correction / delta artifacts 被保留為 decision trail
- repo-visible `review-log`
- sample topic 中的三輪 creator / reviewer loop

技術上的問題是 governance drift：本地 workflow / planning surfaces
尚未完整編碼 `agent-skills` `0.58.0` 現已明確表達的 lifecycle 規則。

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 將本地 workflow surfaces 與 released contract 對齊 | 更新 topic plan 中列出的精確本地 workflow / planning files，讓它們直接編碼 lifecycle contract | 已發布的 `agent-skills` `0.58.0`；`mlops-async` 中現有的本地副本 | 中等程度的 wording 與一致性工作；沒有 runtime burden | 可行 |
| R2 讓 workflow body 維持精簡 | 將 field-level correction artifact guidance 放在 `plan-creator` / `plan-reviewer` 的 reference 與 examples，而不是把 `plan/agent-handoff-workflow.md` 擴成 schema dump | 現有的本地 `plan-creator` 與 `plan-reviewer` 資料夾 | 低到中等 | 可行 |
| R3 編碼 current truth 與 historical truth 的區分 | 更新 `plan/agent-handoff-workflow.md`、`plan-creator` 與 `plan-reviewer` 的 wording，使這個區分明確 | `v0.9.2` 中既有的 sample evidence | 低 | 可行 |
| R4 讓 `review-log` 成為條件性要求 | 更新本地 artifact-path 與 review guidance，使 `review-log` 只在控制 routing 或 multi-round 的情況下才需要 | 本地 plan-authoring 與 review surfaces | 低 | 可行 |
| R5 讓 round caps 維持 topic-scoped | 加入 wording 與 examples，允許宣告 topic caps，但不把 sample cap 提升為 repo-wide law | 本地 plan-authoring 與 review surfaces | 低 | 可行 |
| R6 強制 exact artifact paths | 更新本地 artifact-path guidance 與 review checks，使模糊的 evidence labels 會被拒絕 | 本地 plan-authoring 與 review surfaces | 低 | 可行 |
| R7 保留角色分離 | 更新本地 role-boundary rules、checklists 與 examples，讓 creator steps 排除 reviewer-owned logging 與 Main Agent routing | 本地 workflow 與 planning surfaces | 低 | 可行 |
| R8 排除 domain payload 內化 | 讓 implementation topic 嚴格限制在 workflow surfaces，並拒絕 `src/**`、`tests/**` 或 release files | Topic plan 的 scope boundary | 低 | 可行 |

## Implementation-facing Workstreams

### Workstream 1 — Workflow contract refresh

更新 `plan/agent-handoff-workflow.md`，使其明確表示：

1. workflow body 只包含 lifecycle / routing rules；
2. parent artifacts 在 accepted backfill 後會成為 current truth；
3. correction artifacts 維持為 historical truth；
4. `review-log` 取決於 routing control 或 multi-round rework；
5. round caps 是 topic-scoped policy，而不是 repository-wide law。

### Workstream 2 — Workflow-agent consumer refresh

更新 `.github/agents/python-implementation-workflow.agent.md`，使其持續作為
repo-level lifecycle contract 的 consumer，而不是獨立或相互衝突的 owner。

### Workstream 3 — Plan-authoring contract refresh

更新精確列出的本地 `plan-creator` surfaces，使其要求：

1. 精簡的 workflow-body wording；
2. 在使用時提供精確的 parent / correction / review-log artifact paths；
3. current-truth 與 historical-truth 的分離；
4. topic-scoped round-cap policy；
5. 將詳細 correction artifact contract 放在 reference / examples，而不是
   workflow body。

### Workstream 4 — Plan-review contract refresh

更新精確列出的本地 `plan-reviewer` surfaces，使 reviewers 可以阻擋：

1. 模糊的 evidence paths；
2. 出現在 creator implementation steps 內的 reviewer-owned work；
3. 無條件要求 `review-log`；
4. repo-wide 的 round-cap wording；
5. 在 workflow body 中塞入冗長 correction schemas 的膨脹寫法。

## Exact Planned Artifact Surface

本 topic 的對齊工作限定於以下這些檔案：

1. `plan/agent-handoff-workflow.md`
2. `.github/agents/python-implementation-workflow.agent.md`
3. `.github/skills/plan-creator/reference.md`
4. `.github/skills/plan-creator/checklist.md`
5. `.github/skills/plan-creator/examples.md`
6. `.github/skills/plan-creator/references/artifact-path-rule.md`
7. `.github/skills/plan-creator/references/role-boundary-rule.md`
8. `.github/skills/plan-creator/templates/topic-plan-template.md`
9. `.github/skills/plan-reviewer/reference.md`
10. `.github/skills/plan-reviewer/checklist.md`
11. `.github/skills/plan-reviewer/examples.md`

## Architecture-compliance Self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Repo positioning | fits | 這是現有本地 workflow surfaces 內的 governance-only repo 工作 |
| Local skill model | fits | `mlops-async` 已經保留 plan-authoring 與 plan-review surfaces 的本地副本 |
| Sample preservation | fits | 被保留的 `v0.9.2` sample 可以繼續作為 evidence，而 contract 進入 workflow surfaces |
| Code / test boundary | fits with scope control | 此 topic 不應授權任何 `src/**` 或 `tests/**` 工作 |
| Release timing | fits | 此 topic 應明確維持為非 release、非 stable-library |
| Role separation | fits with prerequisites | Planner、creator、reviewer 與 Main Agent 的邊界可在既有 workflow files 中表達 |

## Constraints and Risks

| Issue | Type | Handling |
| --- | --- | --- |
| sample topic 在 README 與 repo history 中很顯眼 | generalization risk | 在 analysis 與 plan artifacts 中維持清楚、不可內化的 payload boundary |
| sample 中存在 `review-log` | overreach risk | 將其編碼為條件性，而不是通用要求 |
| sample 中存在三輪 loop | policy drift risk | 只將其編碼為可選的 topic policy |
| 本地檔案可能與上游 release wording 有些微差異 | merge risk | 對齊 contract meaning，而不是逐行文字相同 |
| 共享 governance files 會跨 worktrees 被編輯 | coordination risk | 將此 topic 的所有執行限定在受管理的 `mlops-async` worktree 內 |

## Rollback-to-alignment Triggers

若發生以下情況，本 topic 應停止並回報，而非繼續執行：

1. 必要變更會觸及 `src/**`、`tests/**`、`README.md`、`VERSION` 或
   release/tag artifacts；
2. `mlops-async` 需要對已發布的上游 lifecycle contract 做出刻意偏離，
   但這個偏離尚未在 repo-visible analysis 中表達；
3. 本地 workflow body 若不先建立獨立的 shared lifecycle reference，
   就無法維持精簡；
4. 這項變更開始暗示需要建立新的 standalone skill，而不是對既有
   workflow surfaces 進行有邊界的 refresh。

## Recommended Implementation Topic

- **Topic**: `correction-delta-lifecycle-contract-alignment`
- **Shape**: governance-only workflow-surface refresh
- **Excluded in this topic**: 不含 `src/**`、`tests/**`、`README.md`、`VERSION`、tag、release notes 或 sample payload rewrite

## Final Technical Verdict

這項下游對齊在技術上可行且風險低，因為它只刷新 `mlops-async` 既有的
本地 governance surfaces。安全的 implementation shape 是一個有邊界的
11-file workflow-contract refresh，而不是 code change，也不是新的
standalone skill。
