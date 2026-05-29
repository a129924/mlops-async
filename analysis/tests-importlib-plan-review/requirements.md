# tests-importlib-plan-review — 正式需求基線

## Status

**Frozen**

---

## Goal / Outcome

本 topic 的正式目標如下：

1. 讓整個 `tests/` 移除以 `importlib` 取代一般引入的方式。
2. 唯一例外是：該測試本身就在驗證 importability，亦即驗證模組或套件是否能成功引入、應否引入失敗，或引入時應產生何種可觀測結果。
3. 除上述例外外，其餘測試一律改成絕對引入。
4. 改寫後必須維持語意一致，不得造成測試驗證目標偏移、fixture 行為改變、module identity 變動，或導致測試結果失真。

---

## 背景與問題定義

`tests/` 目前存在以 `importlib` 取代一般引入的寫法。這類寫法若只是為了取得 module、class、function 或常數來進行一般測試，會把原本可直接閱讀的依賴關係改寫成動態載入流程，增加判讀成本，也讓「測的是被測模組行為」與「測的是能否被引入」兩種目的混在一起。

本 topic 要解決的不是所有 `importlib` 使用，而是 **把原本屬於一般引入的場景，從動態載入改回可直接判讀的絕對引入**，同時保留真正以引入成功／失敗為測試目標的例外案例。

### 必須移除的 `importlib` 用法

下列用法只要其用途是在一般測試流程中取得被測對象或輔助模組，而不是把「引入本身」當成斷言主體，就屬於本 topic 的移除對象：

1. 使用 `importlib.import_module(...)` 取得可直接以絕對路徑引入的 module。
2. 使用 `importlib.util.spec_from_file_location(...)`、`module_from_spec(...)`、`exec_module(...)` 或同類載入鏈，只為了載入可直接絕對引入的測試目標。
3. 在 fixture、helper、setup 流程或測試主體中，以 `importlib` 延後或包裝一般引入行為，但實際斷言並不在驗證 importability。
4. 以字串拼接、路徑轉換或中介 helper 搭配 `importlib` 載入模組，而其目的是一般測試存取，不是驗證載入機制本身。

### 不屬於本 topic 的問題

下列事項不因本 topic 而自動成立，也不是本需求要處理的主體：

- `src/` 的 import 設計或封裝方式。
- 生產程式碼的 module layout、公開 API 或匯出策略調整。
- 與 `tests/` import rewrite 無直接關係的測試重構。

---

## 例外定義：什麼才算真正的 importability test

只有在「引入是否成功、如何失敗、引入時發生什麼結果」本身就是測試主題時，該測試才可保留 `importlib` 或其他動態載入手法。

### 真正的 importability test 必須同時符合

1. **引入動作本身是被驗證對象**：若移除動態引入後，測試主題就不成立，才可能屬於例外。
2. **斷言直接對準引入結果**：例如成功引入、拋出預期例外、出現預期 warning、載入後可見特定公開符號、或引入時的副作用本身就是預期結果。
3. **測試目的不是一般功能驗證**：若引入完成後，真正的斷言重心落在函式、類別、fixture 或業務邏輯行為，則不屬於例外。

### 不算例外的情況

下列情況即使使用了 `importlib`，也不算真正的 importability test：

- 只是想在測試內較晚拿到 module object。
- 只是想用字串決定要測哪個 module，但實際斷言的是 module 內函式或類別的行為。
- 只是為了方便 monkeypatch、mock、fixture setup 或避免一般引入寫法。
- 只是先動態引入，再對一般 API、資料模型或回傳值進行驗證。

---

## Scope

本 topic 的範圍僅限於 `tests/`：

1. 盤點 `tests/` 內以 `importlib` 取代一般引入的寫法。
2. 區分哪些屬於一般引入替代、哪些屬於真正的 importability test。
3. 將非例外案例改寫為絕對引入。
4. 只做維持原測試語意所必需的最小調整。

### 邊界限制

- 只改 `tests/`，不改 `src/`。
- 不改測試驗證目標，不把原本測 A 的測試改成測 B。
- 不因改寫 import 方式而擴張測試範圍、增加新行為或移除既有檢查。
- 不把真正的 importability test 強制改寫成一般絕對引入。

---

## 語意一致要求

改寫後必須維持下列語意不變：

### 1. Module identity 不得偏移

絕對引入後取得的 module 與符號，必須對應到原測試要驗證的同一個目標，不得因為路徑改寫而改到不同 module、不同公開符號，或不同載入來源。

### 2. Assertion intent 不得改變

每個測試原本在驗證什麼，就必須繼續驗證什麼。改寫 import 方式不能把「測引入」變成「測功能」，也不能把「測功能」變成「測引入」。

### 3. Fixture behavior 不得漂移

fixture 的建立時機、作用域、monkeypatch 目標、mock 綁定點與前置條件必須保持等價；若改寫後會改變這些行為，即不符合本需求。

### 4. Test outcome 不得失真

在相同測試前提下，改寫前後的通過／失敗意義必須一致。不可因改寫而引入新的 side effect、遮蔽原本例外、改變 warning 行為，或讓測試失去原本的失敗訊號。

---

## 驗收訊號

| ID | 驗收訊號 | 可觀測結果 |
| --- | --- | --- |
| **AS-1** | 非例外 `importlib` 用法已被界定 | 需求已明確指出哪些 `importlib` 用法只是一般引入替代，屬於必須移除的對象。 |
| **AS-2** | 例外條件可操作 | 需求已明確定義什麼才算真正的 importability test，足以區分保留與改寫案例。 |
| **AS-3** | 範圍與邊界清楚 | 文件已清楚限制只改 `tests/`，不改 `src/`，不改測試驗證目標。 |
| **AS-4** | 語意一致要求完整 | 文件已明確要求維持 module identity、assertion intent、fixture behavior 與 test outcome 一致。 |
| **AS-5** | 停止條件明確 | 文件已明確指出哪些情況不得自行判定，必須交人工 review。 |

### 需求層完成訊號

當且僅當下列條件同時成立時，可視為本 topic 的需求層已完成：

1. 讀者可直接從本文件理解主題是「`tests/` 中非必要 `importlib` 引入改寫為絕對引入」，不需依賴 prompt、meta 說明或其他文件反推主語。
2. 本文件已直接定義移除對象、唯一例外、範圍邊界、語意一致要求與停止條件。
3. 下游執行者可依本文件判斷單一案例應改寫、保留或停止交審，而不需要重新發明分類標準。

---

## 停止條件與人工 review

遇到下列任一情況時，不得自行宣告可安全改寫，必須停止並交人工 review：

1. 無法穩定判定某個測試到底是在驗證 importability，還是在驗證一般功能。
2. 改成絕對引入後，可能改變 `sys.modules` 互動、module cache、載入順序或 import-time side effect。
3. 原測試依賴 `importlib.reload(...)`、自訂 loader、`exec_module(...)`、動態 path 解析，且其必要性無法直接證明只是一般引入替代。
4. 改寫後可能改變 fixture 初始化時機、monkeypatch 綁定對象、mock 生效邊界，或例外／warning 觀測點。
5. 存在多個可能的絕對引入目標，無法確定哪一個才與原測試語意完全等價。

---

## Non-goals

本 topic 不包含以下事項：

- 不改 `src/` 中任何程式碼。
- 不重新設計產品模組的匯出介面。
- 不以 import rewrite 為名進行額外測試重構。
- 不修改真正 importability test 的驗證目標。
- 不為了消除 `importlib` 使用而接受語意偏移或測試失敗。
