# http-client-auth-boundary-context-doc requirements baseline

## Status

- `FROZEN` — ready for topic-plan authoring

## Problem Statement

`mlops-async` 已經有 auth/request boundary 的既有實作、測試與部分架構描述，但缺少一份可被後續 Agent 與 repo maintainer 穩定引用的單一 context 文件。若依賴圖、元件職責、禁止事項、與未來 `MlopsAsyncClient` facade 定位仍分散在 plan、PR 討論與零散文件中，後續 auth/request boundary 相關 topic 仍會反覆要求人類重新說明同一套設計。

## Actors and Consumption Boundary

1. **Primary actor — 後續處理 auth/request boundary 相關 topic 的 Agent**
   - 在分析、規劃、review、或實作前需要先取得固定上下文。
   - 不應重新發明 `HttpClient` / `Requester` / auth collaborators 的邊界定義。
2. **Secondary actor — repo maintainer / reviewer**
   - 在 review 後續 topic 時，需要可引用的單一依據來判斷 scope creep、責任漂移、與依賴方向是否仍正確。

## Measurable Requirements

| ID | Actor | Condition | Observable Outcome | Metric / Decision Rule | Failure Meaning |
| --- | --- | --- | --- | --- | --- |
| BR-1 | 後續 Agent | topic 牽涉 `HttpClient`、`Requester`、`AuthProvider`、`TokenManager`、`TokenStorage`、`TokenFetcher` 或未來 `MlopsAsyncClient` facade 邊界 | Agent 在分析或規劃階段先讀並引用固定的 auth-boundary context 文件 | 若 Agent 未先引用該文件就開始改動相關邊界，視為未滿足此需求 | 人類仍需重複解釋相同設計，邊界定義容易重新漂移 |
| BR-2 | Agent、repo maintainer / reviewer | 需要理解或審查 auth/request boundary 相關變更時 | 可從單一文件讀到固定依賴方向與禁止循環依賴規則 | 文件必須明確覆蓋 `Domain client -> Requester -> HttpClient` 與 `Requester -> AuthProvider -> TokenManager -> {TokenStorage, TokenFetcher -> HttpClient}` | 後續 topic 會各自帶入不同依賴模型 |
| BR-3 | Agent、repo maintainer / reviewer | 需要判斷某個 auth/request 行為應落在哪一層時 | 文件能明確說明各元件的職責與非職責 | 文件至少要能回答：`HttpClient` 為 pure transport、`Requester` 為唯一 request composition layer、`AuthProvider` 為薄 adapter、`TokenManager` 擁有 lifecycle/lock/decision、`TokenStorage` 為 dumb storage、`TokenFetcher` 為 token endpoint collaborator | token lifecycle、auth semantics 或 retry 邏輯會被重新塞回錯誤層級 |
| BR-4 | 後續實作 facade 或 domain client 的 Agent | topic 牽涉未來 `MlopsAsyncClient` | 文件明確記錄 `MlopsAsyncClient` 未來只負責 wiring / orchestration，不直接承擔 token lifecycle | 文件必須把 future facade role 與 auth/request boundary role 分開敘述 | future facade topic 容易重新吸收 token lifecycle，破壞分層 |
| BR-5 | 後續 Agent、repo maintainer / reviewer | 需要從既有文件入口找到 auth-boundary 細節時 | 可從 `docs/ARCHITECTURE.md` 導到細部 context doc | 若細部 context doc 已建立，`docs/ARCHITECTURE.md` 必須有明確連結或指示；只有細部文件存在但無總覽入口，不算完成 | 文件存在但不易發現，後續 Agent 仍回到口頭提醒流程 |
| BR-6 | 後續 Agent、repo maintainer / reviewer | 細部 context doc、`docs/ARCHITECTURE.md`、程式碼或 `tach.toml` 出現不一致時 | Agent 不自行平均解讀衝突，而是停下來交給人工決策 | `docs/ARCHITECTURE.md` 為總覽、細部 context doc 為細節；若與 code / `tach.toml` 衝突，必須視為 blocker | repo 會累積互相衝突的設計來源 |
| BR-7 | Repo maintainer / reviewer | 同一 topic 選擇一併補 `tach.toml` guardrail | guardrail 只固定 auth/request boundary 相關的單向模組依賴，不擴張成全面模組重整 | 若新增 `tach.toml` 規則，只能表達 `mlops_async.transport` 可依賴 `mlops_async.core`、`mlops_async.core` 不可反向依賴 `mlops_async.transport`，且需與文件敘述一致 | 模組邊界 topic scope 漂移，影響與 auth/request boundary 無關的模組 |

## Assumptions

1. auth/request boundary 會持續作為後續 topic 的共享上下文，而不是一次性說明。
2. 後續 Agent 的行為可透過文件引用與規劃 / review 回應觀察，而不需要額外 runtime instrumentation。
3. `tach.toml` 若在同一 topic 一起更新，只是 guardrail 補強，不改變這份 baseline 的核心 business intent。

## Non-goals

1. 不重新設計 auth implementation 本體。
2. 不處理 OAuth flow、401 retry、distributed lock、credential persistence 或 public facade API 定稿。
3. 不在本 topic 內做與 auth/request boundary 無關的廣泛模組邊界重整。
4. 不要求修改 `README.md`、`VERSION`、release notes、或其他 stable-library surfaces。

## Extreme-Boundary Checks

1. **Wrong actor**
   - 非 auth/request boundary topic 的 Agent 不要求先讀這份文件；first-read 範圍只限相關 topic。
2. **Partial completion**
   - 若只建立細部 context doc，但沒有在 `docs/ARCHITECTURE.md` 加入口，視為 discoverability requirement 未完成。
3. **Guardrail mismatch**
   - 若文件與 `tach.toml` 或程式碼不一致，Agent 必須停下並要求人工決策，不得自行選一個版本當準。
4. **Future drift**
   - 若未來 facade/topic 變更導致這份文件過期，reviewer 應視其為需更新的設計來源，而不是保留過期文件繼續沿用。

## Contradiction Log

1. **文件存在即可 vs 必須被後續 Agent 先讀與引用**
   - Statement A：只要文件存在，Agent 就應該能自行找到。
   - Statement B：使用者的真正需求是「不用每次提醒」，因此不只要存在，還要被後續 Agent 先讀與引用。
   - Decision：成功訊號採 **後續相關 topic 的 Agent 必須先讀並引用該文件**。
2. **文件 topic vs `tach` topic**
   - Statement A：此 topic 的核心目的是固定 context 與可讀設計基線。
   - Statement B：使用者希望把 `tach` 設定一起補上。
   - Decision：`tach` 可作為 **同 topic 的最小 guardrail 補強**，但只能限於 auth/request boundary 相關的單向模組依賴，不得擴張成全面模組重整。

## Blockers

- None for this business baseline.

## Handoff Boundary for Plan Authoring

此 baseline 已凍結下列需求，不需要在後續 topic plan 中重新發明：

1. 後續 auth/request boundary 相關 topic 的 Agent 必須先讀並引用細部 context doc。
2. 細部 context doc 必須固定依賴圖、元件職責與非職責、future facade guidance、與 source-of-truth 規則。
3. `docs/ARCHITECTURE.md` 必須作為總覽入口指向該細部 context doc。
4. 若同 topic 補 `tach.toml`，只能做最小單向 guardrail，且必須與文件敘述一致。
