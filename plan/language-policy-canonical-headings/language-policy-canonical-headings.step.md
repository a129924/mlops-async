# Step Tracker — language-policy-canonical-headings

## Status

- **Topic status**: `review-ready`
- **Cycle**: 1

## Implementation Steps

- [x] Step 1: 建立本 step tracker 檔案，與計畫的實作步驟對齊。
- [x] Step 2: 更新 `.github/copilot-instructions.md`——保持繁體中文為一般段落文字的預設語言；明確允許嚴格列舉的 canonical 英文標題／術語保留英文。
- [x] Step 3: 在 `.github/copilot-instructions.md` 中編碼對不確定類標題情況預設保留 canonical 英文，僅限候選固定標題／標籤／workflow 名稱／canonical 術語，不適用於一般段落文字。
- [x] Step 4: 更新 `.github/CONTRIBUTING.md`，使其面向貢獻者的措辭不與相同政策邊界相衝突。
- [x] Step 5: 檢查是否有其他治理文件直接描述相同的語言政策。結果：**未發現其他治理文件**；本計畫無需進一步動作。
- [x] Step 6: 重新閱讀最終措辭以確認：一般段落文字預設為繁體中文；嚴格列舉限制英文標題例外；commit／PR／Issue 標題政策保持不變；沒有措辭暗示廣泛的雙語自由。

## Acceptance Evidence

- `.github/copilot-instructions.md` 的 `Language Requirement` 區段現已區分一般段落文字（繁體中文預設）與嚴格列舉的 canonical 英文標題／術語。
- 不確定情況的預設規則已明確編碼，且僅限類標題項目。
- `.github/CONTRIBUTING.md` 在 `Git conventions` 下新增了 `Language policy` 子區段，內容呼應 `.github/copilot-instructions.md` 且不相衝突。
- 未發現其他直接描述此政策的治理文件；無需修復計畫。
