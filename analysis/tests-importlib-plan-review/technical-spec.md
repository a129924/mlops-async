# tests-importlib-plan-review — Technical Specification

## Status

**Ready**

---

## Technical Objective

本文件直接定義 `tests/` 內 **以 `importlib` 取代一般引入** 的改寫技術規格。

正式目標如下：

1. 讓整個 `tests/` 移除以 `importlib` 取代一般引入的方式。
2. 唯一可保留的例外，是該測試本身就在驗證 importability，也就是驗證模組或套件能否成功引入、應否失敗、或引入時會產生何種可觀測結果。
3. 除上述例外外，其餘案例一律改成絕對引入。
4. 改寫後必須維持語意一致，不得造成 module identity 偏移、fixture 行為改變、monkeypatch / mock 綁定點漂移、assertion intent 改寫，或導致測試結果失真。

---

## Technical Scope / Boundary

本 technical-spec 只處理 `tests/` 中的 import rewrite 決策與改寫約束。

### In Scope

- 盤點 `tests/` 內所有以 `importlib` 取得 module、class、function、constant 或 helper module 的寫法。
- 區分哪些屬於一般引入替代、哪些屬於真正的 importability test。
- 定義非例外案例改寫為絕對引入的分類規則。
- 定義改寫時必須維持的語意等價條件。
- 定義遇到不穩定案例時的停止條件與人工 review 邊界。

### Out of Scope

- `src/` 的 module layout、公開 API 或匯出設計調整。
- 與 import rewrite 無直接關係的測試重構。
- 為了配合改寫而新增測試目標、移除既有斷言，或重定義驗證主題。
- 把真正的 importability test 強制改寫成一般絕對引入。

---

## `importlib` 用法技術分類

執行層必須先分類，再決定改寫或保留；不得先假設所有 `importlib` 用法都應直接替換。

| 類型 | 典型模式 | 技術判定 | 預設動作 |
| --- | --- | --- | --- |
| **A. 一般 module 取得** | `importlib.import_module("pkg.mod")` 後讀取 module attr、呼叫函式、建立類別 | `importlib` 只是在取得原本可直接絕對引入的 module，斷言主體不是引入本身 | 改寫為絕對引入 |
| **B. 一般 symbol 取得** | 動態載入後只為了取得 class / function / constant 進行一般功能測試 | 測試主體是 symbol 行為，不是載入成功或失敗 | 改寫為絕對引入 |
| **C. fixture / helper / setup 內延後引入** | 在 fixture、helper、setup 中用 `importlib` 取得 module 供後續測試使用 | 若延後引入只是一般存取手段，而非驗證 importability，本質仍屬一般引入替代 | 改寫為絕對引入，但必須保留原時機與綁定語意 |
| **D. 檔案路徑 loader 鏈** | `spec_from_file_location(...)`、`module_from_spec(...)`、`exec_module(...)` | 若目標其實有穩定的 package import path，且測試主體不是 loader 行為，可視為一般引入替代 | 只有在可穩定對應到唯一絕對引入時才改寫；否則停止交審 |
| **E. 真正 importability test** | 驗證成功引入、預期引入失敗、warning、import-time side effect、可用符號暴露 | 引入動作本身就是被測對象；移除動態引入後測試主題會消失 | 保留原設計 |
| **F. 載入機制敏感案例** | `reload(...)`、自訂 loader、動態 `sys.path`、`sys.modules` 操作、字串或路徑組裝後載入 | 測試語意可能依賴 module cache、載入順序、loader 邏輯或 import-time side effect | 無法穩定判定時停止並交人工 review |

### 分類判定順序

每個案例至少依序回答下列問題：

1. `importlib` 取得的是 module、symbol，還是整段 loader 行為。
2. 測試斷言是在驗證「引入結果」，還是在驗證「引入後的功能或資料」。
3. 原測試是否依賴特定載入時機、module cache、patch 綁定點或 import-time side effect。
4. 是否存在唯一且穩定的絕對引入路徑，可對應原本同一個被測對象。

只要第 2 題答案不是「引入結果本身」，且第 3、4 題沒有不確定因素，預設就應朝絕對引入改寫。

---

## 可安全改寫為絕對引入的模式

### 1. 固定字串 module import

若 `importlib.import_module(...)` 的目標是固定且可直接引入的 package path，且測試只是一般使用該 module，應改為絕對引入。

**適用條件：**

- 模組路徑固定且可直接解析。
- 斷言主體是 module 內 API 的一般行為。
- 不依賴 import failure、warning 或 import-time side effect 作為測試主題。

### 2. 取得單一公開 symbol 的一般功能測試

若動態載入只是為了取得單一 class、function 或 constant，且後續只驗證該 symbol 的一般行為，可改為直接絕對引入該 symbol。

**適用條件：**

- 原測試不依賴 module object 本身的 identity。
- monkeypatch / mock 不需要綁在 module object 上。
- 改成 `from ... import ...` 不會改變被 patch 的名稱解析路徑。

### 3. fixture / helper 內的延後引入

若延後引入只是為了在 fixture 或 helper 執行時才取得 module，而不是在驗證 importability，可改為在**相同作用域與相同時機**使用一般絕對引入。

**關鍵要求：**

- 不得為了省事就把原本 fixture 內的載入直接提升到 module top-level。
- 若原測試依賴環境變數、monkeypatch、warnings filter 或其他前置條件先設好，再執行引入，則絕對引入也必須留在相同時機點。

### 4. 路徑 loader 其實只是在繞路載入既有 package module

若 `spec_from_file_location(...)` / `exec_module(...)` 最終對應的是 repo 內已有穩定 import path 的模組，而且測試並未驗證 loader 邏輯本身，可改為該模組的絕對引入。

**前提：**

- 可明確證明原目標與絕對引入指向同一個 module identity。
- 改寫後不會失去原本對 import-time side effect、patch timing 或 cache 行為的控制。

---

## 必須保留的模式

下列情況不得因「看起來也像 import」就直接改為絕對引入：

### 1. 引入成功或失敗本身就是斷言主體

例如：

- 驗證某模組可被成功引入。
- 驗證缺少依賴時應拋出指定例外。
- 驗證引入時會產生指定 warning、log 或 side effect。
- 驗證模組引入完成後，公開符號是否存在或初始化是否完成。

### 2. 測試明確依賴 loader / reload / cache 行為

例如：

- 使用 `importlib.reload(...)` 驗證重新載入效果。
- 驗證自訂 loader、`exec_module(...)` 或 path-based loading 行為。
- 驗證 `sys.modules`、載入順序、module cache 命中與否。

### 3. 無唯一穩定絕對引入路徑

若原測試是經由字串、路徑、參數或組態決定目標，而執行層無法穩定判定唯一等價的絕對引入目標，則不得自行改寫。

---

## 絕對引入形式選擇規則

改寫不是只決定「改不改」，還必須決定「改成哪種 import 形式」；形式錯誤也會造成語意偏移。

| 原測試需要保留的語意 | 優先形式 | 原因 |
| --- | --- | --- |
| 需要 module object 本身 | `import package.module as module_alias` | 可保留 module-level state、attribute access 與 patch 綁定點 |
| 只需要單一 symbol，且不依賴 module identity | `from package.module import Symbol` | 可直接表達被測對象，但前提是不影響 patch 路徑 |
| 需要延後到 fixture / helper / test function 執行時才引入 | 在相同 scope 內使用一般 `import` / `from ... import ...` | 保留引入時機與前置條件 |
| 需要多個 symbol 且原測試以 module namespace 存取 | `import package.module as module_alias` | 避免把 namespace 存取拆散後改變 monkeypatch / mock 目標 |

### 形式選擇的保守原則

1. 只要原測試對 module object 做 patch、state 觀測、namespace 存取或 identity 比對，就不要改成 `from ... import symbol`。
2. 只要原測試對 symbol 的 patch 路徑依賴某個 module namespace，就必須保留該 namespace。
3. 若無法證明改成 symbol import 後 patch 綁定點仍完全等價，預設改成 module import，或停止交審。

---

## 語意一致與等價約束

### 1. Module identity

改寫後取得的 module 或 symbol，必須對應到原測試要驗證的同一個對象。

**必須維持：**

- 相同 canonical module path。
- 相同 module namespace 或 symbol 來源。
- 相同 `sys.modules` 可觀測對象（若測試一般行為仍受其影響）。

**不得發生：**

- 把原本指向具體 module 的測試改成經由不同 re-export 路徑取得對象。
- 把需要 module object 的場景改成單一 symbol import，導致 identity 或 patch 對象改變。

### 2. Fixture behavior

改寫前後，fixture 的建立時機、scope、依賴條件與可觀測副作用必須一致。

**必須檢查：**

- import 是否仍在 fixture / helper 的同一層級發生。
- autouse fixture 是否仍先於 import 設定環境。
- parametrized fixture 是否仍對每個 case 產生相同前置條件。
- fixture teardown 是否仍對同一個 module object 或 patched target 生效。

### 3. Monkeypatch / mock 綁定點

`monkeypatch.setattr(...)`、`unittest.mock.patch(...)`、spy 或 stub 的綁定點必須保持等價。

**保留規則：**

- 若原測試 patch 的是 module attribute，改寫後仍要 patch 同一個 module namespace。
- 若 patch 使用字串路徑，改寫後不得讓程式實際讀取的名稱解析路徑改變。
- 若 helper 或 fixture 回傳的是 module object，改寫後不得改成回傳單一 symbol，導致 patch 無法命中。

### 4. Assertion intent

每個測試原本在驗證什麼，改寫後就必須繼續驗證什麼。

**禁止的偏移：**

- 把原本的功能測試改成 importability 測試。
- 把原本的 importability 測試改成一般功能測試。
- 因引入方式重寫而順便增減 assertion 或改變 failure signal。

### 5. Test outcome

在相同測試前提下，改寫前後的 pass / fail 意義必須一致。

**不得引入：**

- 額外 import-time side effect。
- 不同的 warning / exception 觀測點。
- 因提早或延後引入造成的狀態污染。

---

## 需要特別小心的 helper / fixture / setup 模式

### 1. `conftest.py` 或共用 helper 先做環境設定，再動態引入

若原流程是在設定環境變數、patch 全域狀態、替換依賴後才載入 module，改寫時必須保留這個順序；不能把 import 提前到測試模組 import time。

### 2. autouse fixture 影響 import-time side effect

若 autouse fixture 的目的之一是控制 import-time 行為，則任何改寫都必須保留引入發生於 fixture 生效之後；若無法保證，停止交審。

### 3. helper 回傳 module object 供多個測試共用

此時要先辨識測試是否依賴該 module object 的共享 state、patch 或 namespace。若依賴存在，改寫形式必須仍回傳對等的 module object，而不是拆成 symbol import。

### 4. 先 patch 再 import 的 setup

若測試是先 patch 某些依賴，再引入被測 module 以觸發 import-time 綁定，改寫時仍需維持「先 patch、後 import」；不能單純把 import 提到檔案頂端。

### 5. 參數化決定載入目標

若 fixture 或 helper 依參數決定 module path，必須先確認每個 case 是否都有唯一穩定的絕對引入方案。只要其中一個 case 不穩定，就不得批次套用單一改寫策略。

### 6. 涉及 `sys.modules`、`sys.path`、warnings capture、logging capture

若原測試會觀測這些 import 相關副作用，應先判斷測試是否其實屬於 importability 或載入機制敏感案例；不能只因目標模組可引入就直接改寫。

---

## 停止條件與人工 review

遇到下列任一情況時，不得自行判定可安全改寫，必須停止並交人工 review：

1. 無法穩定判定測試是在驗證 importability，還是在驗證一般功能。
2. 無法確定唯一且等價的絕對引入路徑。
3. 改寫可能改變 `sys.modules`、module cache、reload、loader、載入順序或 import-time side effect。
4. 改寫可能改變 fixture 初始化時機、scope、teardown、生效順序，或 monkeypatch / mock 綁定點。
5. 原測試使用 `spec_from_file_location(...)`、`exec_module(...)`、自訂 loader、動態 path 解析，而其必要性無法證明只是一般引入替代。
6. 原測試透過 helper / fixture 間接回傳 module 或 symbol，且無法證明改寫後 assertion intent 完全不變。
7. 改寫若要成立，必須連帶修改 `src/`、大幅重構測試、或重新定義驗證目標。

停止條件一旦成立，執行層只能標記為需人工判讀，不得以「先改再看測試有沒有壞」作為判定方式。

---

## 執行層 case-by-case 決策流程

執行層應依下列順序逐案判定：

1. **定位 importlib 用法**：記錄使用位置、scope、目標字串或 loader 鏈。
2. **辨識被測對象**：確認測試真正驗證的是 import 結果、module 行為，還是 symbol 行為。
3. **辨識綁定點**：列出 fixture、helper、monkeypatch、mock、warnings capture、logging capture 與 state 依賴。
4. **檢查絕對引入候選**：確認是否存在唯一且等價的 import path。
5. **選擇改寫形式**：依 module identity 與 patch 綁定需求，決定使用 module import、symbol import，或保留在原 scope 延後引入。
6. **套用最小改寫**：只改 import 取得方式與其必要配套，不改 assertion intent。
7. **重新驗證語意**：確認 module identity、fixture behavior、patch 綁定點與測試結果意義皆未改變。
8. **無法證明等價時停止**：只要任何一步無法穩定成立，即交人工 review。

### 批次改寫限制

- 不得只因多個案例長得相似，就忽略 fixture / helper / patch 差異而批次套用同一種 import 形式。
- 可批次處理的前提，是這批案例在被測對象、引入時機、綁定點與等價條件上都一致。
- 一旦出現例外案例，該案例必須拆出獨立判定。

---

## Technical Acceptance Criteria

| ID | 對應需求訊號 | 技術判定標準 |
| --- | --- | --- |
| **TS-1** | AS-1 | 文件已明確定義 `importlib` 用法分類，足以區分一般引入替代、真正 importability test 與載入機制敏感案例。 |
| **TS-2** | AS-2 | 文件已明確定義哪些模式可安全改成絕對引入、哪些必須保留，以及形式選擇規則。 |
| **TS-3** | AS-4 | 文件已明確定義 module identity、fixture behavior、monkeypatch / mock 綁定點、assertion intent 與 test outcome 的等價約束。 |
| **TS-4** | AS-5 | 文件已明確列出 helper / fixture / setup 敏感模式與停止條件，足以阻止不穩定改寫。 |
| **TS-5** | AS-3, AS-5 | 執行層可依本文件對單一案例做 case-by-case 判定，決定改寫、保留或停止交審，而不需依賴額外 meta 說明。 |

---

## Blockers

**目前無 blocker。**

若後續案例落入停止條件，應將其視為個案判定 blocker，而不是放寬本 technical-spec 的語意一致要求。
