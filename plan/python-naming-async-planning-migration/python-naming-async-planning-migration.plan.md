## Goal / Outcome

- 建立一份 repo 可見的遷移契約，將 `python-naming` 與 `python-async-planning` 引入 `mlops-async`，包含保持既有已安裝 skills 內部一致性所需的最小輔助 refresh。
- 語意警告：本 topic 在沒有 `analysis/python-naming-async-planning-migration/requirements.md` 與 `analysis/python-naming-async-planning-migration/technical-spec.md` 的情況下進行撰寫；範圍基於明確的人工指引與已完成的 review 發現。

## Scope

- **In scope**:
  - 將 `agent-skills` 中的 `.github/skills/python-naming/` 加入 `mlops-async`
  - 將 `agent-skills` 中的 `.github/skills/python-async-planning/` 加入 `mlops-async`
  - refresh `mlops-async/.github/skills/python-plan-authoring/` artifacts，使其與 async-planning 契約對齊
  - refresh `mlops-async/.github/skills/python-plan-review/` artifacts，使其與 async-planning 契約對齊
  - 更新 `mlops-async/.github/copilot-instructions.md`，使已安裝 skill 清單與直接引用在新 skills 落地後保持準確
  - 確認既有 `python-code-review` 與 `python-docstrings` 中指向 `python-naming` 的 signpost 現在可解析至已安裝的 skill

- **Out of scope**:
  - 遷移其他任何已 review 的 current-only skill
  - 變更 `README.md`、`VERSION`、git tags 或發布時機
  - 實作與本 topic 無關、已在先前批次 review 中處理的 shared-item refreshes
  - 變更 workflow agents，除非後續實作發現直接的契約依賴且已先修正本計畫

## Locked Decisions

- 本 topic 為 **review-ready-only，無 stable-library surfaces**；`README.md`、`VERSION` 或任何 release action 均不屬於本遷移 topic。
- 本 topic 維持為同時涵蓋 `python-naming` 與 `python-async-planning` 的**單一遷移 topic**；除非後續有明確的人工決策，否則不拆分為獨立 topic plans。
- `python-async-planning` 因明確的人工決策而納入本遷移 topic，即使它在先前的 review 追蹤中被刻意排除。
- `python-naming` 必須以完整的 skill folder 形式遷移，因為 `mlops-async` 中已有 repo-local signposts 指向 `python-naming`。
- `python-async-planning` 不得單獨遷移；遷移時必須同時 refresh `python-plan-authoring` 與 `python-plan-review`，使 async-planning 契約在 `mlops-async` 內可被執行。
- 實作必須在 branch `plan/andrew/python-naming-async-planning-migration` 的受管 topic worktree 中進行，基於 `dev`。

## Boundaries / Exclusions

- 本 topic 僅限於兩個選定 skills 的 skill 安裝與內部契約對齊。
- 不在本 topic 內重新啟動更廣泛的 candidate-review workflow。
- 未先更新本計畫，不得編輯已列出 artifact paths 以外的檔案。
- 不得將 `.github/copilot-instructions.md` 清單更新視為可變更 repo governance 或 contributor workflow 措辭的許可，超出新安裝 skills 的必要範圍。
- 不得推斷 `python-async-planning` 需要對 `python-implementation-workflow.agent.md` 進行無關變更；若確有必要，應停止並修正計畫，而非擴散範圍。

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: 遵循 canonical creator -> reviewer -> publish -> merge 路徑；本 topic 在 merge 後停止，不宣告 release action
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

- 本 topic 不規劃 release action。
- 若實作過程發現已列出 artifact paths 以外的額外依賴檔案，應停止並修正本計畫後再繼續。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/python-naming-async-planning-migration/python-naming-async-planning-migration.plan.md` | Planning actor | 本遷移 topic 的 repo 可見執行契約 |
| New skill | `.github/skills/python-naming/SKILL.md` | Creator | 將命名策略 skill 契約安裝至 `mlops-async` |
| New skill | `.github/skills/python-naming/reference.md` | Creator | 安裝 `python-naming` 使用的命名範例與邊緣案例參考 |
| New skill | `.github/skills/python-async-planning/SKILL.md` | Creator | 將 async-planning skill 契約安裝至 `mlops-async` |
| New skill | `.github/skills/python-async-planning/reference.md` | Creator | 安裝 async-planning 參考指引 |
| New skill | `.github/skills/python-async-planning/examples.md` | Creator | 安裝 skill folder 所需的 async-planning 範例 |
| Supporting refresh | `.github/skills/python-plan-authoring/SKILL.md` | Creator | 將 async-planning trigger/exemption 契約重新引入 plan authoring |
| Supporting refresh | `.github/skills/python-plan-authoring/examples.md` | Creator | 使 plan-authoring 範例與 async-planning 期望對齊 |
| Supporting refresh | `.github/skills/python-plan-authoring/templates/python-plan-template.md` | Creator | 加入 authored plans 使用的 repo 可見 async-planning scaffold |
| Supporting refresh | `.github/skills/python-plan-review/SKILL.md` | Creator | 將 async-planning review gates 重新引入 plan review |
| Supporting refresh | `.github/skills/python-plan-review/checklist.md` | Creator | 使 plan-review checklist 與 async-planning review checks 對齊 |
| Supporting refresh | `.github/skills/python-plan-review/examples.md` | Creator | 使 plan-review 範例與 async-planning review outcomes 對齊 |
| Inventory update | `.github/copilot-instructions.md` | Creator | 更新已安裝 skill 清單計數及遷移後所需的直接引用 |

Artifact path notes:

- 本 topic **不**修改 `README.md` 或 `VERSION`。
- 將已列出的路徑視為實作與 review 的可執行契約。
- 若後續工作需要觸及 `docs/ARCHITECTURE.md` 或其他未列出的檔案，應停止並修正計畫後再進行編輯。

## Implementation Steps

1. 檢視來源資料夾 `../agent-skills/.github/skills/python-naming/` 與 `../agent-skills/.github/skills/python-async-planning/`，然後將已列出的 skill artifacts 複製至 `mlops-async/.github/skills/` 下對應的目標路徑。
2. 從 `agent-skills` refresh `mlops-async/.github/skills/python-plan-authoring/SKILL.md`、`examples.md` 與 `templates/python-plan-template.md`，使 `mlops-async` 內 authored plans 能表達 `Async-planning status` 及所需的 async-planning subsections。
3. 從 `agent-skills` refresh `mlops-async/.github/skills/python-plan-review/SKILL.md`、`checklist.md` 與 `examples.md`，使 review 時的 async trigger、exemption 與 retrofit 檢查與新安裝的 async-planning 契約一致。
4. 更新 `mlops-async/.github/copilot-instructions.md`，反映新的已安裝 skill 計數及應提及新安裝 skills 的直接引用。
5. 確認既有 `mlops-async/.github/skills/python-code-review/` 與 `mlops-async/.github/skills/python-docstrings/` 中對 `python-naming` 的引用，現在可解析至真實已安裝的 skill 路徑，無需進一步文字變更。
6. 對照本計畫審查已變更的 artifact 集合，若有任何額外檔案路徑出現，則停止並修正計畫。

## Validation / Acceptance Checks

- `mlops-async/.github/skills/python-naming/` 存在且包含 `SKILL.md` 與 `reference.md`
- `mlops-async/.github/skills/python-async-planning/` 存在且包含 `SKILL.md`、`reference.md` 與 `examples.md`
- `mlops-async/.github/skills/python-plan-authoring/SKILL.md` 明確包含 async-planning 契約語言，且 plan template 包含 async-planning scaffold
- `mlops-async/.github/skills/python-plan-review/SKILL.md` 與 `checklist.md` 明確包含 async-planning trigger/exemption 覆蓋及 retrofit-required 行為
- `.github/copilot-instructions.md` 在新 skills 加入後不再包含過時的 `28 installed Agent Skills` 計數
- 既有已安裝 skill 中對 `python-naming` 的引用可解析至現在存在的已安裝資料夾
- 未修改 `Artifact Paths` 以外的任何未規劃檔案路徑

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

- 本 topic 不需要任何 repository release action。
- 合併後，一般的 local sync 或 worktree cleanup 可在獨立的 workflow routing 下進行，但任何 `VERSION` 或 tag action 均不屬於本遷移 topic。

## Open Questions / Unresolved Items

- 無。
