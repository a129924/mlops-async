# tests-importlib-plan-review — Topic Acceptance Specification

## Acceptance Subject

本 spec 驗收的對象，是 **`tests/` 內將非必要 `importlib` 引入改寫為絕對引入** 的 topic 執行結果本身。

reviewer 應以本 spec 判斷：

- `tests/` 內的 `importlib` 使用是否已完整盤點並正確分類。
- 唯一例外是否只保留真正驗證 importability 的測試。
- 其餘案例是否都已改寫為絕對引入。
- 改寫是否維持語意一致，沒有造成測試偏移、fixture 行為改變或失敗意義失真。
- 遇到無法穩定判定的載入機制敏感案例時，是否正確停止並交人工 review。

## Alignment Sources

| Source | Path | Role |
| --- | --- | --- |
| Workflow contract | `plan/agent-handoff-workflow.md` | 提供 canonical status model 與 reviewer handoff JSON contract |
| Requirements baseline | `analysis/tests-importlib-plan-review/requirements.md` | 定義正式目標、唯一例外、範圍邊界與語意一致要求 |
| Technical contract | `analysis/tests-importlib-plan-review/technical-spec.md` | 定義 `importlib` 用法分類、改寫規則、等價約束與停止條件 |
| Topic plan | `plan/tests-importlib-plan-review/tests-importlib-plan-review.plan.md` | 定義實作步驟、artifact paths、validation 與 reviewer handoff |
| Step tracker | `plan/tests-importlib-plan-review/tests-importlib-plan-review.step.md` | 追蹤盤點、分類、改寫、驗證與 review-ready 進度 |

## Acceptance Criteria

### AC-1：`tests/` 內的 `importlib` 用法已完整盤點並可追溯

執行結果必須能指出 `tests/` 內每個 `importlib` 用法屬於哪一類案例，以及其對應處置。

**合格條件**：reviewer 可追溯每個 `importlib` 使用點的分類結果：改寫、保留例外、或停止交審。

**不合格條件**：仍有 `importlib` 使用未被盤點，或只憑肉眼 diff 無法得知某個保留案例為何存在。

---

### AC-2：唯一例外只保留真正的 importability tests

保留動態引入的案例，必須是引入成功／失敗、warning、import-time side effect 或可觀測引入結果本身就是測試主題。

**合格條件**：每個保留案例都能說明其 assertion 直接對準 import 結果，移除動態引入後測試主題即不成立。

**不合格條件**：只是為了較晚取得 module、方便 monkeypatch、fixture setup、字串決定模組、或一般功能驗證而保留 `importlib`。

---

### AC-3：所有非例外案例都改寫為絕對引入

凡屬一般引入替代的案例，都必須改寫為一般絕對引入，而不是留下動態載入捷徑。

**合格條件**：`importlib.import_module(...)`、loader 鏈或 helper / fixture 內的延後載入，只要不在測 importability，都已改成等價的絕對引入形式。

**不合格條件**：任何一般功能測試仍保留 `importlib`；或雖已改寫，但使用的 import 形式無法對應原本同一個被測對象。

---

### AC-4：改寫後維持語意一致

改寫前後的 module identity、fixture behavior、monkeypatch / mock 綁定點、assertion intent 與 test outcome 必須一致。

**合格條件**：

- 被測 module 或 symbol 仍指向相同目標。
- fixture / helper 的引入時機與前置條件保持等價。
- monkeypatch / mock 命中的 namespace 與名稱解析路徑未改變。
- 每個測試原本驗證的內容與 pass / fail 意義維持不變。

**不合格條件**：

- 改成不同 module path 或不同 re-export 路徑。
- 把需要 module namespace 的測試拆成 symbol import，導致 patch 對象改變。
- 把延後引入提前到 module import time，造成 fixture / setup 語意漂移。
- 因改寫而新增、移除或改寫 assertions，導致測試主題偏移。

---

### AC-5：topic scope 保持在 `tests/` import rewrite

本 topic 只接受與 `tests/` import rewrite 直接相關的修改。

**合格條件**：變更集中於 `tests/`，且只包含盤點、分類、絕對引入改寫與維持語意一致所必需的最小配套。

**不合格條件**：修改 `src/`、重新設計模組匯出、進行無關測試重構，或把真正 importability test 一併改寫掉。

---

### AC-6：不確定案例有正確失敗路徑與 reviewer evidence

遇到無法穩定證明等價的案例時，執行層必須停止並交人工 review，而不是硬改或靜默略過。

**合格條件**：loader-sensitive、reload-sensitive、`sys.modules` / `sys.path` 敏感、路徑不唯一或 import-time side effect 不明的案例，都被明確標記並交 reviewer 判讀。

**不合格條件**：以「先改再跑測試看看」取代等價性判定、未記錄阻塞案例、或在 handoff 時省略保留理由與驗證結果。

---

## Behavioral Scenarios

### Scenario 1：一般功能測試使用固定字串 `import_module`

- **Given**：某測試以 `importlib.import_module("package.module")` 取得 module，後續只驗證該 module 內函式的回傳值
- **When**：執行本 topic
- **Then**：該案例應改寫為對同一 module 的絕對引入，而不是保留動態載入

### Scenario 2：測試主題是引入失敗或 warning

- **Given**：某測試斷言某模組引入時必須拋出特定例外或 warning
- **When**：執行本 topic
- **Then**：該案例屬於真正的 importability test，可保留動態引入方式

### Scenario 3：fixture 先做 monkeypatch，再引入被測 module

- **Given**：某 fixture 先設定環境、patch 依賴，再於 fixture 內使用 `importlib` 載入 module
- **When**：該案例不屬於 importability test 且可安全改寫
- **Then**：改寫後的絕對引入仍必須留在相同 fixture / helper scope，以保留引入時機與 patch 綁定點

### Scenario 4：loader 鏈案例無法證明唯一等價路徑

- **Given**：某測試使用 `spec_from_file_location(...)` 與 `exec_module(...)` 載入模組，且無法穩定證明唯一等價的 package import path
- **When**：執行本 topic
- **Then**：該案例必須停止並交人工 review，不得自行改寫為任意絕對引入

### Scenario 5：改寫完成後驗證語意一致

- **Given**：某非例外案例已改寫為絕對引入
- **When**：reviewer 檢查驗證結果與受影響測試執行情形
- **Then**：reviewer 應能確認 assertion intent、fixture behavior 與 pass / fail 意義未因改寫而改變

---

## Review Verdict Rules

- **`approved`**：僅在 AC-1 至 AC-6 全部成立、保留與阻塞案例皆有明確理由，且驗證結果足以證明語意一致時才可發出。
- **`needs-rework`**：只要存在未分類 `importlib`、誤保留非例外案例、誤改真正 importability test、語意漂移、scope 漂移，或 blocker / validation evidence 不完整時都必須發出。

## Error / Failure Cases

- `tests/` 中仍有一般功能測試保留 `importlib`，卻沒有 importability 或人工 review 理由。
- 真正的 importability test 被改成一般絕對引入，導致測試不再驗證引入結果本身。
- 改寫把 import 提前或延後，導致 fixture、生效順序、warning capture、logging capture 或 monkeypatch 命中點改變。
- 改寫後指向不同 module path、不同 re-export、不同 namespace，造成 module identity 偏移。
- 為了讓改寫成立而修改 `src/`、擴張測試範圍或調整與 import rewrite 無關的 assertions。
- 對 loader-sensitive / reload-sensitive / `sys.modules` 敏感案例未停下來交審，而是直接套用一般絕對引入。
