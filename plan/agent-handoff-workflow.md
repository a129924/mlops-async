# 代理交接工作流程合約

## 目的

定義 creator / reviewer workflow gate 使用的標準主題計畫合約。

## 必要計畫章節

每個 `plan/<topic>/<topic>.plan.md` 都必須包含下列章節：

1. `Goal / Outcome`
2. `Scope`
3. `Locked Decisions`
4. `Boundaries / Exclusions`
5. `Status / Allowed Transitions`
6. `Artifact Paths`
7. `Implementation Steps`
8. `Validation / Acceptance Checks`
9. `Reviewer Handoff`
10. `Post-merge / release actions`
11. `Open Questions / Unresolved Items`

### 穩定函式庫中繼資料（條件式）

若主題會影響穩定函式庫介面（`README.md`、`VERSION`、release timing 或 release notes），必須新增 `## Stable library metadata`，並宣告 README action、VERSION bump、timing 與 rationale。

## 標準狀態模型

| 狀態 | 意義 | 擁有者 | 允許下一步 |
| --- | --- | --- | --- |
| `planned` | 主題計畫已可進入執行路由 | 規劃角色 | `creator-in-progress` |
| `creator-in-progress` | 建立者正在起草或套用必要修正 | 建立者 | `review-ready` |
| `review-ready` | 建立者已完成最新版草稿並請求獨立審查 | 建立者 | `reviewer-in-progress` |
| `reviewer-in-progress` | 審查者正在評估最新版草稿 | 審查者 | `approved`, `needs-rework` |
| `needs-rework` | 審查者找到阻擋性的合約問題 | 審查者 | `creator-in-progress` |
| `approved` | 審查者接受此草稿 | 審查者 -> 主代理 | `creator-in-progress`, `publish-in-progress` |
| `publish-in-progress` | 已核准工作正在 commit / push，並準備進入 PR 或直接 merge | 主代理 | `pr-open`, `merged` |
| `pr-open` | PR 已開啟且正在進行 triage | 主代理 | `needs-rework`, `merged` |
| `merged` | 變更已完成 merge | 主代理 | terminal |
| `released` | 選擇性的 release / version 動作已完成 | 主代理 | terminal |

## 標準允許轉移

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

條件式規則：

- 若 `Post-merge / release actions` 宣告了實際的 release action，需補上 `merged` -> `released`。

## 步驟追蹤對齊規則

- 標準步驟檔案路徑：`plan/<topic>/<topic>.step.md`。
- Completion gate 只能讀取 `## Implementation Steps` 的核取方塊。
- 標記語意：`[X]` 表示完成、`[ ]` 表示待完成（`[x]` 視為待完成）。
- 狀態對齊：
  - 只要仍有任何 implementation step 待完成，或 rework 尚未結束，就維持 `creator-in-progress`
  - 只有當本輪 creator pass 的 implementation steps 全部完成後，才能移到 `review-ready`
  - 若 reviewer 回傳 `needs-rework`，就必須回到 `creator-in-progress`

## 審查交接 JSON 合約

`Reviewer Handoff` 必須包含一個可供機器消費的 JSON 物件，格式如下：

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

## 合併後 / 發版規則

- 每個主題計畫都必須明確說明 post-merge 行為。
- 若不需要 release action，必須明確寫出不需要。
- 若需要 release，必須宣告具體 release actions，並確認狀態轉移包含 `merged` -> `released`。
