> **Analysis-layer routing: INCOMPLETE LAYER**
>
> - Available business guardrail: `analysis/language-policy-canonical-headings/requirements.md`
> - Missing companion artifact: `analysis/language-policy-canonical-headings/technical-spec.md`
> - 目前沒有人工 `override` 指令改變本主題的 analysis-layer 優先順序。
> - 本主題計畫可繼續推進，但 creator 工作不得在 frozen requirements baseline 之外自行擴充 technical-spec 層級的範圍。

## Goal / Outcome

- 為 `language-policy-canonical-headings` 主題產生 repo 可見的執行契約，使後續 creator 工作得以在不將 repo 擴展為廣泛雙語使用的前提下，讓 repo 語言政策圍繞 canonical 英文標題進行對齊。
- 本主題完成後，`.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md` 將呈現不相衝突的政策：繁體中文仍為一般段落文字的預設語言，嚴格列舉的 canonical 標題／術語可保留英文。

## Scope

- **In scope**:
  - 維護本主題在 `plan/language-policy-canonical-headings/` 下的規劃產物。
  - 以 `analysis/language-policy-canonical-headings/requirements.md` 作為 creator 與 reviewer 工作的 frozen business baseline。
  - 更新 `.github/copilot-instructions.md` 以編碼：
    - 繁體中文作為非固定段落文字的預設語言
    - canonical 英文標題／術語的嚴格列舉規則
    - 對不確定類標題情況採用保留 canonical 英文的行為
  - 更新 `.github/CONTRIBUTING.md`，使其面向貢獻者的指引不與 `.github/copilot-instructions.md` 中編碼的政策相衝突。
  - 檢查是否有其他治理文件直接描述相同的語言政策；若在以下精確產物路徑之外發現此類文件，則停止並修復本計畫後再進行修改。

- **Out of scope**:
  - Commit、PR 或 Issue 標題語言政策的變更
  - 對既有 repo 文件的回溯清理
  - 一般段落文字的廣泛雙語政策變更
  - 本主題的 `technical-spec.md` 撰寫工作
  - README 更新、VERSION 遞增、release notes、tag／release 工作或 stable-library 發布任務

## Locked Decisions

- 本主題為**僅限 review-ready，無 stable-library 表面**。不修改 `README.md`、`VERSION`、release notes 或 release 時間中繼資料。
- frozen business baseline 為 `analysis/language-policy-canonical-headings/requirements.md`；對話時意圖不得覆蓋此 baseline。
- 繁體中文仍為 repo 自有治理、分析與規劃文件中一般段落文字的預設語言。
- Canonical 英文僅可在**嚴格列舉**下保留：
  - canonical 區段標題
  - plan／step tracker 固定區段名稱
  - 固定標籤
  - workflow 名稱
  - 必要的 canonical 術語
- 若 agent 無法自信地分類某類標題項目，預設為保留現有 canonical 英文形式，而非自動翻譯。
- `.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md` 皆為本主題的正式政策來源，主題完成時兩者不得相衝突。
- 本主題不得擴展為通用的混合語言或全英文標題政策。

## Boundaries / Exclusions

- Planning actor 僅擁有本計畫與 requirements baseline。
- Creator 負責在以下精確產物路徑範圍內起草允許的政策措辭變更。
- Reviewer 負責獨立裁決，不得在 review 過程中執行 creator 工作。
- Main Agent 負責 publish routing、PR flow、merge follow-up 及後續 worktree 清理；這些動作不屬於 creator 範圍。
- 若工作需要編輯另一個直接描述此政策的治理文件，請停止並修復本計畫（補充精確產物路徑）後再繼續。
- 若實作偏向 commit／PR／Issue 標題政策、回溯文件清理或廣泛雙語治理，請停止並將其拆分為獨立主題。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: 遵循 canonical creator -> reviewer -> publish -> merge 路徑；本主題在 `merged` 時終止，不宣告 release 動作。
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

- 在 publish 前使用標準 Phase 4.5 planner-alignment 規則。
- 由於 analysis layer 不完整，creator 工作必須保持在 frozen requirements baseline 的邊界內，不得自行新增額外政策表面。
- STOP POINT 1 仍適用於 commit／push／PR 建立之前。
- STOP POINT 2 仍適用於 merge 交接後；merge 後的本地同步需要新的明確人工繼續訊息。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/language-policy-canonical-headings/language-policy-canonical-headings.plan.md` | Planning actor | 本主題的 repo 可見執行契約 |
| Topic step tracker | `plan/language-policy-canonical-headings/language-policy-canonical-headings.step.md` | Planning actor -> Creator | locked creator steps 的機器可讀追蹤 |
| Requirements baseline | `analysis/language-policy-canonical-headings/requirements.md` | Planning actor | 本政策主題的 frozen business guardrail |
| AI policy source | `.github/copilot-instructions.md` | Creator | 主要 AI 導向語言政策來源，必須編碼嚴格列舉例外 |
| Contributor policy source | `.github/CONTRIBUTING.md` | Creator | 面向貢獻者的指引，必須與 AI 導向政策來源保持不衝突 |

Artifact path notes:

- `README.md`：本主題不做變更。
- `VERSION`：本主題不做變更。
- `.github/copilot-instructions.md`：本主題中修改。
- 若後續工作偏離這些精確路徑，請停止並更新本計畫後再繼續。
- 若檢查發現另一個直接描述相同語言政策的文件，請勿在本計畫修復（補充精確路徑項目）前對其進行編輯。

## Implementation Steps

1. 建立 `plan/language-policy-canonical-headings/language-policy-canonical-headings.step.md`，包含對應以下步驟及 canonical workflow 契約的 creator 導向實作核取方塊。
2. 更新 `.github/copilot-instructions.md`，使 `Language Requirement` 區段保持繁體中文為一般段落文字的預設語言，同時明確允許嚴格列舉的 canonical 英文標題／術語保留英文。
3. 在 `.github/copilot-instructions.md` 中，編碼對不確定類標題情況預設保留 canonical 英文，僅限候選固定標題／標籤／workflow 名稱／canonical 術語，不適用於一般段落文字。
4. 更新 `.github/CONTRIBUTING.md`，使其面向貢獻者的措辭不與相同政策邊界相衝突，並在不擴展 repo 語言政策的前提下明確非衝突範圍。
5. 檢查是否有其他治理文件直接描述相同的語言政策。若不存在，透過正常 review 證據記錄無需進一步動作。若在產物清單之外發現，則停止並修復本主題計畫後再進行編輯。
6. 重新閱讀 `.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md` 的最終措辭以確認：
   - 一般段落文字仍預設為繁體中文
   - 嚴格列舉限制了英文標題例外的範圍
   - commit／PR／Issue 標題政策保持不變
   - 沒有措辭暗示廣泛的雙語自由

## Validation / Acceptance Checks

- 修改的文件保持在上方列出的精確產物路徑內，否則在繼續前修復本計畫。
- `analysis/language-policy-canonical-headings/requirements.md` 仍為 creator 與 reviewer 決策的 business guardrail。
- `.github/copilot-instructions.md` 明確區分一般段落文字與嚴格列舉的 canonical 英文標題／術語。
- `.github/CONTRIBUTING.md` 在本主題上不與 `.github/copilot-instructions.md` 相衝突。
- 最終措辭保留以下 locked decisions：
  - 繁體中文仍為一般段落文字的預設語言
  - 僅列舉的 canonical 類別可保留英文
  - 不確定類標題情況預設保留 canonical 英文
  - commit／PR／Issue 標題政策不變
- Reviewer 確認沒有措辭將政策擴展為廣泛的混合語言許可。

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

- merge 後，Main Agent 僅可在收到明確人工繼續訊息後執行正常本地同步流程。
- 本主題不涉及 README 更新、VERSION 遞增、release note 工作、tag 建立或 repo release 動作。
- 本主題在 `merged` 時終止。

## Open Questions / Unresolved Items

- `analysis/language-policy-canonical-headings/technical-spec.md` 在本流程中刻意缺席；若後續工作需要技術翻譯而非直接政策編輯，請停止並在擴展實作範圍前建立該產物。
