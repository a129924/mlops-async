# Request Contract Testing — Topic Plan

## Goal / Outcome

建立並凍結 `request-contract-testing` 的 repo-visible planning contract，使本 topic 在不觸碰 `src/mlops_async/**` 與 `tests/**` 的前提下，具備可重複審查的規範、分析與計畫產物。

## Scope

- **In scope**:
  - `analysis/request-contract-testing/requirements.md`
  - `analysis/request-contract-testing/technical-spec.md`
  - `docs/standards/request-contract-testing.md`
  - `plan/agent-handoff-workflow.md`
  - `plan/request-contract-testing/request-contract-testing.plan.md`
  - `plan/request-contract-testing/request-contract-testing.step.md`

- **Out of scope**:
  - `src/mlops_async/**` production 實作
  - `tests/**` 測試實作
  - `.github/skills/api-client-porting-planner/**` 與 `.github/skills/api-client-porting-implementer/**` 的整合修改
  - runtime dependency 與 package configuration 變更

## Locked Decisions

- Snapshot scope 固定為 `full_observed_flow`。
- Capture artifact 固定拆分為 request-flow fixture 與 mock-response answer set。
- Auth divergence 必須保留 captured auth steps；若 target 故意不鏡像，必須標記 `intentionally_changed` 並保留理由。
- Capture evidence 與 source review 若衝突且影響 baseline semantics，固定升級 human decision，不可自動和解。
- 本 topic 為 non-stable planning/standards work，Stable-library intent 明確為 absent（不變更 `README.md`、`VERSION`、release notes）。

## Boundaries / Exclusions

- 僅處理本 topic 的 analysis/standard/plan artifact，不擴張為 downstream skill rollout。
- Creator、reviewer、Main Agent 職責不得混用；本檔不代替 reviewer 最終裁決。
- 若工作漂移到 `Artifact Paths` 之外，必須停止並回到 plan 對齊，而非隱式擴 scope。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: 使用 canonical creator -> reviewer -> publish -> merge 流程；本 topic 不含 release 動作。
- **Step-tracker alignment**: `plan/request-contract-testing/request-contract-testing.step.md` 的 `## Implementation Steps` 已完成，因此可由 `creator-in-progress` 前進到 `review-ready`。
- **Allowed transitions**:
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

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | Canonical section list 與狀態轉移基準，供 plan-reviewer/plan-creator 共用 |
| Business baseline | `analysis/request-contract-testing/requirements.md` | Planning actor | 凍結 request-contract-testing 需求與 acceptance 基線 |
| Technical translation | `analysis/request-contract-testing/technical-spec.md` | Planning actor | 需求到檔案範圍/驗證信號的技術映射 |
| Normative standard | `docs/standards/request-contract-testing.md` | Creator | Request Contract Gate 規範來源，供後續 workflow 引用 |
| Topic plan | `plan/request-contract-testing/request-contract-testing.plan.md` | Planning actor | 本 topic 的執行契約與 handoff 規則 |
| Step tracker | `plan/request-contract-testing/request-contract-testing.step.md` | Creator | Implementation Steps completion gate（供 `plan-step-tracker` 讀取） |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md`。
- `Artifact Paths` 視為可執行契約；若出現未列路徑變更，視為 plan drift，需先修正 plan 再繼續。

## Implementation Steps

1. 凍結 `analysis/request-contract-testing/requirements.md` 與 `analysis/request-contract-testing/technical-spec.md`。
2. 建立 `docs/standards/request-contract-testing.md`，完整覆蓋 gate / fixture / comparison / auth divergence / stop conditions。
3. 新增 `plan/agent-handoff-workflow.md`，提供 canonical sections 與 status transitions 依據。
4. 將本 topic plan 重構為 canonical sections，並維持已凍結決策。
5. 以精確、owner/role 標註的 `Artifact Paths` 取代鬆散 affected-files 描述。
6. 明確保留單一 JSON `Reviewer Handoff` 與 `Post-merge / release actions`，並同步 step tracker。

## Validation / Acceptance Checks

- 檔案存在檢查全部通過：
  - `analysis/request-contract-testing/requirements.md`
  - `analysis/request-contract-testing/technical-spec.md`
  - `docs/standards/request-contract-testing.md`
  - `plan/agent-handoff-workflow.md`
  - `plan/request-contract-testing/request-contract-testing.plan.md`
  - `plan/request-contract-testing/request-contract-testing.step.md`
- `plan/request-contract-testing/request-contract-testing.plan.md` 包含 canonical required sections。
- `Status / Allowed Transitions` 與 canonical status model 一致。
- `Artifact Paths` 全部為精確 repo-visible 路徑且含 Owner/Role。
- Stable-library intent 已明確宣告 absent。
- `Reviewer Handoff` 為單一 machine-readable JSON object。
- `Post-merge / release actions` 明確聲明「無 release action」。

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

- Merge 後由 Main Agent 走既有 post-merge local sync/cleanup 流程。
- 本 topic 無 release action；`merged` 為終態。
- 若未來要納入 stable-library 或 release timing，需另開新 topic plan 明確宣告。

## Open Questions / Unresolved Items

- None.
