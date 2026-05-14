# Language Policy Canonical Headings Requirements

## Status

- **Status**: frozen baseline for downstream planning
- **Topic**: `language-policy-canonical-headings`
- **Scope level**: repository governance policy

## Problem Statement

`mlops-async` 目前把繁體中文作為 repo 主要溝通語言，但現行規則過於籠統，容易把固定、可重用、需與既有模板或 workflow 對齊的英文標題也一併翻譯。這會讓 analysis / plan / governance 類文件失去可攜性，並降低跨 topic 重複使用同一套 canonical sections 的能力。

本 baseline 要先凍結的是：**repo 語言政策如何同時維持繁中預設與 canonical English headings 的可保留邊界**，而不是立即決定所有治理文件的最終文字或進入實作細節。

## Actors and Boundaries

### Primary actor

- **AI agent**
  - 在新增、改寫或延伸 repo 專屬治理文件、analysis 文件與 plan 文件時，需要一套不會誤翻固定標題的語言規則。

### Secondary actors

- **Human maintainer**
  - 需要能沿用既有固定章節與 canonical terms，而不必每次重新決定是否翻譯。
- **Human reviewer**
  - 需要能根據一致規則判定某個英文標題是否屬於允許保留原文的例外，而不是逐案臨場猜測。

### Out-of-scope actors

- **Commit / PR / Issue 標題撰寫者**
  - 本 baseline 不處理這些標題的語言政策。

## In-scope Requirements

每項 requirement 都以 actor、condition、observable outcome、decision rule 表達。

### R1. Traditional Chinese remains the default for non-fixed prose

- **Actor**: AI agent、human maintainer
- **Condition**: 新增或改寫 repo 專屬治理文件、analysis 文件、plan 文件或同類標準文件時
- **Observable outcome**: 一般敘述性內文、repo 專屬補充說明與使用者可見政策內容仍以繁體中文撰寫
- **Decision rule**: 除非內容屬於允許保留原文的固定類型，或使用者明確指定其他語言，否則不得把一般內文轉為英文
- **Failure meaning**: 若此 requirement 不成立，repo 的主要語言風格將逐步失去一致性

### R2. Canonical headings may remain in English only under strict enumeration

- **Actor**: AI agent、human reviewer
- **Condition**: 文件中出現固定、可重用、需與既有模板或 workflow 對齊的英文標題或術語時
- **Observable outcome**: 以下類型允許保留既有英文原文：
  1. canonical section headings
  2. plan / step tracker 固定章節名稱
  3. fixed labels
  4. workflow names
  5. 必要 canonical terms
- **Decision rule**: 僅限被明確列入允許類型，或已存在於既有模板 / 標準中的固定標題，才可保留英文；不採寬鬆案例式判斷
- **Failure meaning**: 若此 requirement 不成立，固定標題會持續被翻譯，降低模板與跨 topic 重用性

### R3. Uncertain cases default to preserving canonical English

- **Actor**: AI agent
- **Condition**: agent 無法可靠判定某個標題是否屬於允許保留原文的類型時
- **Observable outcome**: agent 預設保留既有 canonical English，而不是直接翻成繁中
- **Decision rule**: 這個預設只適用於標題、label、workflow name、canonical term 等疑似固定項目，不適用於一般敘述內文
- **Failure meaning**: 若此 requirement 不成立，agent 會在不確定時傾向過度翻譯，重現目前要修正的問題

### R4. Policy sources must not conflict

- **Actor**: AI agent、human maintainer、human reviewer
- **Condition**: repo 內有多份文件描述同一條語言政策時
- **Observable outcome**: 至少 `.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md` 對這條政策的描述不互相衝突
- **Decision rule**: 若其他治理文件也直接陳述這條語言政策，後續 topic work 必須同步檢查；不得只改一份正式來源就宣稱政策已一致
- **Failure meaning**: 若此 requirement 不成立，AI 與人類維護規則會分裂，review 判斷也會不一致

### R5. The policy change must not expand into broad bilingual freedom

- **Actor**: Human reviewer、human maintainer
- **Condition**: 審查或延伸這條語言政策時
- **Observable outcome**: 例外只用來保留 canonical English headings / terms，不被解讀成「所有標題都可自由切換英文」或「repo 一般內容可廣泛中英混用」
- **Decision rule**: 若某個英文內容不屬於 strict enumeration 範圍，就回到繁中預設，而不是被當成一般例外
- **Failure meaning**: 若此 requirement 不成立，語言政策會從精準放寬變成廣泛鬆綁

## Success Signals

當此 baseline 被滿足時，至少應能觀察到：

1. 新的 analysis / plan / governance 文件不再自動把允許類型的固定英文標題翻成繁中。
2. 一般敘述內文與 repo 專屬補充內容仍維持繁中。
3. reviewer 能用明確列舉規則判定某個英文標題是否可保留，而不是依主觀感覺裁量。
4. `.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md` 的描述能支持同一套語言政策，不產生明顯衝突。

## Extreme-boundary Checks

### No network or degraded dependency

- 本 baseline 不依賴外部服務；即使無網路，語言政策的判定規則仍必須自足可用。
- 不可把「需要外部上下文確認」當作保留 canonical heading 的必要前提。

### Wrong role or missing approval

- 若 contributor 不是 policy reviewer，也不得自行把 strict enumeration 擴大成更廣義的雙語政策。
- 若 reviewer 未明確接受新的例外類型，則仍回到既有列舉範圍。

### Interrupted or partial completion

- 若只更新 `.github/copilot-instructions.md` 而未同步檢查 `.github/CONTRIBUTING.md`，此 baseline 不視為完全滿足。
- 可接受的狀態是：明確標示尚未同步的正式來源，而不是把部分完成誤當完整完成。

### Lowest-volume and peak-volume conditions

- 在單一 topic 偶發新增一個固定英文標題時，與在多個 topic 大量重複使用相同 canonical sections 時，判定規則都必須一致。
- 不得因文件量增加，就退回案例式判斷或讓例外邊界變得鬆散。

### Time-window and audit reconstruction

- 後續 reviewer 應能從正式政策來源看出：哪些類型可保留英文、哪些內容仍應使用繁中。
- 這表示規則必須可回溯，不可只存在於口頭共識或單次對話。

## Surfaced Contradictions and Resolutions

### C1. Language consistency vs canonical portability

1. 一方需求是維持 repo 以繁中為預設的整體一致性。
2. 另一方需求是保留固定、可重用、與模板對齊的 canonical English headings。
3. 若沒有明確邊界，兩者會互相抵消：不是過度翻譯，就是過度放寬。
4. **Resolution**: 採 strict enumeration；一般內文維持繁中，只有列舉類型或既有模板固定標題可保留英文。

### C2. Agent autonomy vs reviewer control

1. agent 需要在日常產出時快速決定是否保留英文標題。
2. reviewer 需要避免 agent 把任何英文內容都當作例外。
3. 若完全交給 agent 主觀判斷，政策會漂移；若完全不給預設，則會持續過度翻譯。
4. **Resolution**: 不確定時預設保留 canonical English，但此預設僅限疑似固定項目，並受 strict enumeration 與 reviewer 審查約束。

### C3. AI-facing rule vs human-facing rule

1. `.github/copilot-instructions.md` 主要影響 AI agent。
2. `.github/CONTRIBUTING.md` 主要影響人類維護者與 reviewer。
3. 若兩者描述不同，將形成雙重標準。
4. **Resolution**: 兩份文件都視為正式政策來源，後續更新時至少同步對齊這兩處。

## Assumptions

- 本 topic 處理的是 repo 治理語言政策，而不是終端產品 UI 文案、多語系內容策略或對外市場溝通。
- 既有模板、標準文件與 workflow 已存在可辨識的固定英文章節或 canonical terms，可作為 strict enumeration 的實際參照來源。
- 本輪只建立 requirements baseline 與 topic plan，不在此階段擴充為 `technical-spec.md`。

## Non-goals

- 不處理 commit / PR / Issue 標題的語言政策。
- 不追溯翻修既有文件內容。
- 不把 repo 語言政策改成廣義中英雙語自由混用。
- 不在本 baseline 直接決定每一個具體英文標題的最終字串。

## Blockers

None.

## Handoff Boundary for Downstream Planning

後續 planning 階段可以開始處理：

- 如何把 strict enumeration 與正式政策來源映射成實際要修改的檔案與章節
- 如何在 topic plan 中安排同步檢查 `.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md`
- 如何記錄尚未產生 `technical-spec.md` 的現況與風險邊界

後續 planning 階段不得擅自改寫下列 business baseline：

- 繁體中文仍是一般內文的預設語言
- canonical English headings / terms 只能在 strict enumeration 下保留
- 不確定時預設偏向保留 canonical English
- `.github/copilot-instructions.md` 與 `.github/CONTRIBUTING.md` 至少都屬於正式政策來源
