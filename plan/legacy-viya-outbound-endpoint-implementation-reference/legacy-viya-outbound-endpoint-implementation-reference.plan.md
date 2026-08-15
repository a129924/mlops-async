# legacy-viya-outbound-endpoint-implementation-reference

> **Analysis-layer routing: incomplete.** `analysis/legacy-viya-outbound-endpoint-implementation-reference/requirements.md`
> 與 `technical-spec.md` 均不存在；本 plan 依已核准的文件 scope 與 repository evidence
> 撰寫，不產生或假設分析層內容。

## Goal / Outcome

建立可審查的 legacy outbound Viya endpoint reference：一份只供 inventory/navigation 的
`migration-map` 更新，以及六份 family handoff，讓後續 endpoint topic 在不誤用
shape-only evidence 的前提下決定是否進入 formal porting ledger。

## Scope

- **In-Scope**：本 plan、matching step tracker、`docs/migration-map.md` 的 legacy inventory、
  以及 `docs/legacy-viya-outbound-endpoints/` 的 README 與六份 handoff。
- **Out-Of-Scope**：`src/**`、`tests/**`、runtime contract、response/error implementation、
  formal migration rows、`docs/porting-ledger.md`、commit、push、PR、merge、release。

## Locked Decisions

- **Goal**：留下可供實作 planner 使用、但不會升格 legacy observation 的文件 evidence。
- **Non-Goal**：不建立 client、test、ledger entry 或 public API。
- **ReadOnly**：所有 runtime、tests、OpenAPI snapshots、request evidence matrix、porting ledger，
  以及 `.github/agents/*`；後者僅是 frozen provenance，不是 runtime dependency。
- **Written**：本 plan、matching `.step.md`、README、token/models/model-content/
  projects-champion/job-execution/cas-tables handoffs。
- **Modify**：僅 `docs/migration-map.md`，且只加入 inventory/navigation；不新增 formal
  migration row 或 ledger。
- **Deleted**：無。
- 此為 review-ready-only 的純文件 topic，沒有 stable-library surface；不加
  `Stable library metadata`，也不改 `README.md`、`VERSION` 或 release notes。
- 每份 family handoff 必須有 `Legacy observation`、`Upstream/evidence`、
  `Current repo evidence`、`Difference`、`Disposition`、`Human decision required`、
  `Target mapping`；最後一項在正式 endpoint topic 前保持空白。
- authority class 以 request-contract evidence matrix 為準；shape-only 與
  historical-superseded evidence 不得升格為 implementation truth。

## Boundaries / Exclusions

- Creator 僅撰寫列出的 documentation artifacts；Reviewer 僅判定文件範圍與 evidence
  classification；Main Agent 處理任何後續 publication 與 human routing。
- 不得把 projects name lookup、champion contents orchestration、job polling/state machine、
  CAS mutation 或 legacy `verify=False` 偷渡為 MVP。
- 若需要 response/error/session contract、target client name 或 ledger mapping，停止並另開
  已核准的 single-family endpoint topic。

## Status / Allowed Transitions

- **Current**：`review-ready`；文件已完成，等待獨立 reviewer。
- **Execution model**：creator -> reviewer；本次交付止於 review-ready，沒有 publish 或
  release 授權。
- **Allowed transitions**：`planned` -> `creator-in-progress` -> `review-ready` ->
  `reviewer-in-progress` -> (`approved` | `needs-rework`); `needs-rework` ->
  `creator-in-progress`; `approved` -> (`creator-in-progress` | `publish-in-progress`);
  `publish-in-progress` -> (`pr-open` | `merged`); `pr-open` -> (`needs-rework` | `merged`);
  `merged` -> terminal。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/legacy-viya-outbound-endpoint-implementation-reference/legacy-viya-outbound-endpoint-implementation-reference.plan.md` | Planning actor | Canonical documentation-topic contract |
| Step tracker | `plan/legacy-viya-outbound-endpoint-implementation-reference/legacy-viya-outbound-endpoint-implementation-reference.step.md` | Creator | Completion evidence |
| Inventory | `docs/migration-map.md` | Creator | Legacy endpoint navigation only |
| Reference index | `docs/legacy-viya-outbound-endpoints/README.md` | Creator | Family routing and authority reminder |
| Token handoff | `docs/legacy-viya-outbound-endpoints/token.md` | Creator | Existing token runtime boundary |
| Models handoff | `docs/legacy-viya-outbound-endpoints/models.md` | Creator | Read-only MVP candidate |
| Model-content handoff | `docs/legacy-viya-outbound-endpoints/model-content.md` | Creator | Link/path decision boundary |
| Projects/champion handoff | `docs/legacy-viya-outbound-endpoints/projects-champion.md` | Creator | Separate endpoint/orchestration boundary |
| Job-execution handoff | `docs/legacy-viya-outbound-endpoints/job-execution.md` | Creator | Start vs detail/state authority boundary |
| CAS-tables handoff | `docs/legacy-viya-outbound-endpoints/cas-tables.md` | Creator | Shape-only and mutation boundary |

任何不在此表的寫入都是 scope drift，必須停止並重新規劃。

## Implementation Steps

1. 將 root 已存在的 `docs/migration-map.md` topic diff 原樣帶入 managed feature
   worktree，僅作 endpoint inventory/navigation。
2. 建立 reference index，說明 ledger 與 evidence matrix 的權威順序。
3. 為六個 family 各建立具備所有 required headings 的 handoff，明確區分 legacy、
   upstream、current repo evidence 與 human decision。
4. 檢查所有 handoff 都不填入 formal target mapping、不宣稱 response/runtime proof，並確認
   filescope 未碰到 runtime/tests。

## Validation / Acceptance Checks

- `git diff --check` 成功。
- `git diff --name-only` 只列 Artifact Paths 中的十個文件。
- `docs/migration-map.md` 只有 inventory/navigation，且無 `docs/porting-ledger.md` diff。
- 六份 handoff 各含七個 locked headings，並正確保留 evidence-class 的限制。
- plan 含十一個 canonical sections、literal scope labels、明確 analysis-layer warning，且
  Reviewer Handoff 是單一 machine-consumable JSON object。

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

沒有 repository release action。若日後選擇 publication，Main Agent 必須取得新的
commit/push/PR authorization；本 plan 不授權它們。

## Open Questions / Unresolved Items

- 每個 candidate 的 response/error/session contract、public client surface 與 target mapping
  都有待各自的 human-approved endpoint topic 決定；這些問題不阻擋本 reference topic。
