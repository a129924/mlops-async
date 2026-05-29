# tests-importlib-plan-review

> **Analysis-layer routing**：`analysis/tests-importlib-plan-review/requirements.md` 提供需求邊界，`analysis/tests-importlib-plan-review/technical-spec.md` 提供執行規格；本 plan 直接描述 `tests/` import rewrite topic 本身。

## Goal / Outcome

本 topic 的正式目標如下：

1. 讓整個 `tests/` 移除以 `importlib` 取代一般引入的方式。
2. 唯一例外是：該測試本身就是在驗證 importability，也就是驗證模組或套件能否成功引入、是否應引入失敗，或引入時會產生何種可觀測結果。
3. 除上述例外外，其餘案例一律改成絕對引入。
4. 改寫後必須維持語意一致，不得造成 module identity 偏移、fixture 行為改變、monkeypatch / mock 綁定點漂移、assertion intent 改寫，或導致測試失敗與通過意義失真。

完成後，reviewer 應能在 `tests/` 內看到：

- 非例外 `importlib` 用法已被盤點並改寫為絕對引入。
- 真正的 importability tests 仍保留其必要的動態引入方式。
- 任一保留案例或停止案例都有明確理由，而不是因為未完成分類。
- 驗證結果足以證明改寫前後的測試語意與結果一致。

## Scope

- **In scope**:
  - 盤點 `tests/` 內所有以 `importlib` 取代一般引入的寫法。
  - 區分一般引入替代、真正 importability tests、以及需要人工 review 的載入機制敏感案例。
  - 將非例外案例改寫為絕對引入，並依個案選擇能保留語意的 import 形式。
  - 執行維持語意一致所必需的最小調整與驗證。

- **Out of scope**:
  - 修改 `src/`、module layout、公開 API 或匯出策略。
  - 以 import rewrite 為名進行無關的測試重構、命名整理或 coverage 擴張。
  - 把真正的 importability test 改寫成一般功能測試。
  - 接受任何會造成語意偏移、fixture 行為改變或測試結果失真的改寫。

## Locked Decisions

- 執行層只處理 `tests/` 內的 import rewrite；不得把議題擴張到 `src/` 或其他 repo surface。
- 是否屬於例外，必須依 `requirements.md` 與 `technical-spec.md` 的 importability 定義逐案判定；不得以「看起來像 import」直接批次改寫。
- 非例外案例預設改成絕對引入，但 import 形式必須以保留 module identity、namespace 存取、patch 綁定點與引入時機為優先。
- 若原測試依賴 fixture、helper、setup 或 monkeypatch 先成立再引入，改寫後仍必須在相同時機與相同 scope 發生。
- 只要無法穩定證明唯一且等價的絕對引入路徑，或無法證明改寫後語意完全一致，就必須停止並交人工 review。
- 驗收標準是語意一致與測試結果一致；不是單純追求把 `importlib` 全數刪除。

## Boundaries / Exclusions

- 不改 `src/` 中任何生產程式碼。
- 不重新設計產品模組的匯出介面，也不為了方便絕對引入而新增 re-export。
- 不把 loader-sensitive、reload-sensitive、`sys.modules` / `sys.path` 敏感案例硬改成一般引入。
- 不順手改寫與 import 方式無關的 assertions、fixtures、helpers 或測試結構。
- 不以「先改再跑測試看看」取代 case-by-case 的等價性判定。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: 本 topic 的 plan artifacts 已完成 review 並取得可執行 verdict；目前 managed worktree 內承載的是後續 `tests/` import rewrite execution 結果，用於 `python-implementation-workflow` 依 `0 -> 5` phase 重新驗證 implementation / review gates。git commit / PR / merge 仍由 repo-level lifecycle 處理，不在本 workflow scope。
- **Step-tracker alignment**: `plan/tests-importlib-plan-review/tests-importlib-plan-review.step.md` 的 canonical `## Workflow Stages` 與 `## Implementation Steps` 皆以本 topic 的 implementation workflow 為準：前者提供 Phase 0 resume source，後者提供 Phase 3 completion gate。`.step.md` 所記錄的是 `tests/` import rewrite 的盤點、分類、改寫、驗證與 reviewer evidence，而不是早期 planning-artifact-only gate。
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

Routing notes:

- reviewer 的 verdict 針對的是「這份 tests import rewrite plan 是否可安全執行」，不是對任何 `src/` 變更的預先核准。
- `implementation review`、`code review` 與 merge 準備只作為後續執行說明；正式 workflow status 一律回到 canonical 狀態模型，不另立狀態名稱。
- 若 reviewer 發現步驟設計不足以維持語意一致、例外邊界不清楚，或 scope 漂移到 `tests/` 之外，必須回到 `needs-rework`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | Planning actor | canonical workflow、status model 與 reviewer handoff JSON contract |
| Requirements baseline | `analysis/tests-importlib-plan-review/requirements.md` | Analysis author | 定義 tests import rewrite 的需求邊界、唯一例外、語意一致要求與停止條件 |
| Technical contract | `analysis/tests-importlib-plan-review/technical-spec.md` | Technical spec author | 定義分類規則、改寫形式選擇、等價約束與人工 review 邊界 |
| Topic plan | `plan/tests-importlib-plan-review/tests-importlib-plan-review.plan.md` | Planning actor | 定義本 topic 的執行目標、範圍、步驟與 handoff contract |
| Acceptance spec | `plan/tests-importlib-plan-review/tests-importlib-plan-review.spec.md` | Planning actor | 定義本 topic 的完成條件、例外條件、失敗情境與 acceptance criteria |
| Step tracker | `plan/tests-importlib-plan-review/tests-importlib-plan-review.step.md` | Planning actor | 追蹤本輪 creator pass 的 planning artifact 凍結、status 對齊與 reviewer gate completion |

Artifact path notes:

- 本 topic 的主要執行面是 repository `tests/`；具體受影響檔案由盤點步驟決定。
- `Artifact Paths` 保持上述 exact paths；若後續工作需要額外工件或超出 `tests/`，必須先重新對齊本 plan。
- analysis artifacts 與 plan-layer artifacts 共同服務於同一個 tests import rewrite topic，並分別承接需求、技術規格與執行追蹤。

## Implementation Steps

1. 盤點 `tests/` 內所有 `importlib` 用法，記錄檔案位置、scope、載入形式、被測對象，以及候選絕對引入路徑。
2. 逐案分類每個使用情境是「一般引入替代」、「真正 importability test」，還是「需要人工 review 的載入機制敏感案例」，並留下判定理由。
3. 將所有非例外案例改寫為絕對引入；必要時保留 module namespace、延後引入時機與 fixture / helper scope，以維持原本測試語意。
4. 驗證改寫前後的 module identity、fixture behavior、monkeypatch / mock 綁定點、assertion intent 與 test outcome 一致，並執行受影響測試的必要驗證。
5. 彙整保留案例、人工 review 案例與驗證結果，確認本 topic 已達到可交 reviewer 的 `review-ready` 狀態。

## Validation / Acceptance Checks

- `tests/` 內所有非例外 `importlib` 用法都已被盤點，且其判定結果可追溯。
- 只有真正驗證 importability 的測試，或已明確標記需人工 review 的載入機制敏感案例，才可保留動態引入方式。
- 所有已改寫案例都使用絕對引入，且 import 形式與引入時機足以維持原本 module identity 與 patch 綁定點。
- 改寫未造成 `src/` 變更，也未引入與 import rewrite 無關的測試重構。
- 驗證結果必須顯示 assertion intent、fixture behavior 與測試 pass / fail 意義維持一致。
- 若存在無法安全改寫的案例，必須在 review-ready handoff 中明確列出，而不是靜默略過。

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

- 本 topic 屬於 `tests/` 內部改寫，不涉及 release metadata 或版本釋出動作。
- merge 後若仍有人工 review 保留案例，應另開後續 topic 處理，不得回填成「本次已完成改寫」。
- Main Agent 依既有 workflow 處理 commit / PR / merge / post-merge cleanup；本 plan 不額外宣告 release 流程。

## Open Questions / Unresolved Items

- None.
