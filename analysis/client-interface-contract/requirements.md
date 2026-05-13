# Client Interface Contract Requirements

## Status

- **Status**: frozen for technical translation
- **Topic**: `client-interface-contract`
- **Scope level**: internal library baseline

## Problem Statement

`mlops-async` 目前尚未有 production `Client`，但 package 內未來的 domain endpoints 需要一個一致、可觀察、可失敗的共同呼叫邊界。若在這個階段直接讓每個 domain endpoint 自行決定如何送 request、解析 response、暴露型別與表達失敗，後續將難以維持一致 contract、可追溯性與可維護性。

本 baseline 要先凍結的是：**internal-only Client contract 要對 package 內部提供什麼最小可信承諾**，而不是立即決定完整實作、最終 module skeleton，或對外公開 API。

## Actors and Boundaries

### Primary actor

- **Package 內部的 domain endpoint clients**
  - 這些呼叫者需要一個共同 `Client` 契約，以避免各自處理 request/response/error 行為。

### Secondary actor

- **使用本 package 開發下游功能的開發者**
  - 他們不一定直接依賴這個 internal `Client`，但會承受其錯誤語意是否一致、是否可追查的結果。

### Out-of-scope actor

- **外部 package 使用者直接依賴 internal `Client`**
  - 本 baseline 不承諾 `Client` 在這個階段是 public/stable API。

## In-scope Requirements

每項 requirement 都以 actor、condition、observable outcome、decision rule 表達。

### R1. JSON-first success path

- **Actor**: package 內部的 domain endpoint client
- **Condition**: 需要呼叫一般 JSON API 並取得成功結果
- **Observable outcome**: 呼叫者能透過共同 `Client` 的高層入口拿到 Python JSON value，而不需要自行接觸 transport library response object
- **Decision rule**: 成功回應若不能被解析成 JSON，則不可被視為成功結果；必須改以失敗語意呈現
- **Failure meaning**: 若這點不成立，domain endpoints 會重新各自實作 decode 邏輯，破壞共同 contract

### R2. Raw observability path

- **Actor**: package 內部的 domain endpoint client
- **Condition**: 需要保留 response metadata 以支援特殊錯誤處理、特殊 response 類型或後續觀察
- **Observable outcome**: 呼叫者能透過共同 `Client` 的低層入口取得 raw response envelope，並觀察至少 `status_code`、`headers`、`content`、`method`、`url`
- **Decision rule**: raw response 可觀察性必須保留，但不得直接要求上層依賴 `httpx` 型別
- **Failure meaning**: 若這點不成立，低層特殊情境會迫使呼叫者繞過共同 `Client`

### R3. Internal-only dependency boundary

- **Actor**: package 維護者
- **Condition**: 在 pre-stable 階段規劃 `Client` contract 時
- **Observable outcome**: `Client` contract 被明確標示為 internal-only，不被當作 package 對外穩定 API 承諾
- **Decision rule**: 本 topic 不得因實作方便而把 internal contract 提前包裝成 public/stable surface
- **Failure meaning**: 若這點不成立，後續必要的介面調整會被誤解成 breaking public API

### R4. Dependency exposure rule

- **Actor**: package 內部的 domain endpoint client 與 package 維護者
- **Condition**: 定義 `Client` interface 的輸入與輸出時
- **Observable outcome**: interface 僅使用 repo 自己的窄型別與基本 Python 型別；上層 contract 不直接暴露 `httpx` 型別
- **Decision rule**: 若某個呼叫情境只能透過直接暴露 `httpx` 型別才成立，則此 baseline 不視其為本輪完成條件
- **Failure meaning**: 若這點不成立，transport library 將滲透到上層 contract，增加後續替換與維護成本

### R5. Failure semantics

- **Actor**: 下游開發者與 package 維護者
- **Condition**: request 遇到 transport 失敗、不可恢復 HTTP 狀態、JSON 解析失敗、auth/retry exhaustion 等情境
- **Observable outcome**: 失敗會以一致、可理解的 `CustomException` 基底語意向上拋出，而不是 silent fallback、模糊狀態或假成功
- **Decision rule**: 失敗時允許先只凍結單一 `CustomException` 基底；但不得吞錯，也不得把失敗偽裝成可用結果
- **Failure meaning**: 若這點不成立，呼叫端將無法一致判斷錯誤與補救策略

### R6. Retry upper bound

- **Actor**: 下游開發者與 package 維護者
- **Condition**: 發生暫時性失敗時
- **Observable outcome**: `Client` 的失敗處理不會進入無上限 retry；當超過可恢復範圍時，失敗必須明確結束並向上拋出
- **Decision rule**: 429 不在本 baseline 的自動 retry 成功承諾內；若失敗不可恢復，必須如實 raise
- **Failure meaning**: 若這點不成立，呼叫方將無法預期等待時間、失敗完成點與錯誤責任歸屬

## Success Signals

當此 baseline 被滿足時，至少應能觀察到：

1. Package 內部的 domain endpoints 有明確共同的 `Client` contract，而不是各自定義 transport 行為。
2. 一般 JSON API 呼叫可以走共同高層入口並得到 Python JSON value。
3. 需要 raw response metadata 的情境不必直接暴露 `httpx`。
4. 失敗時不會 silent fallback，且可用單一一致錯誤語意向上傳遞。
5. 後續若要做 module placement、technical translation 或 implementation planning，不需要再重新猜測 actors、失敗語意與 dependency boundary。

## Extreme-boundary Checks

### No network or degraded dependency

- 在外部依賴不可用、過慢或 response 不完整時，本 baseline 不接受「看起來成功」的結果。
- 可接受的結果只有兩種：明確失敗，或在可恢復範圍內完成有限次處理後仍明確失敗。

### Wrong role or missing approval

- 若未來有外部使用者想直接依賴 internal `Client`，這不屬於本 baseline 的成功範圍。
- 任何需要 public API 穩定承諾的需求，必須回到 alignment 重新定義 actors 與 success criteria。

### Interrupted or partial completion

- 若 request 過程中斷、response body 不完整或成功 body 無法解析為 JSON，不得回傳半套可用結果。
- 必須以失敗語意結束，避免上層承擔不透明的部分完成狀態。

### Lowest-volume and peak-volume conditions

- 本 baseline 對低流量與高流量的差別，不在於改變 contract，而在於仍需維持相同的失敗終點與 retry 上限。
- 不允許以量大為理由把無上限等待或不透明失敗視為可接受行為。

### Audit or debug reconstruction

- 本 baseline 要求保留足夠的 raw response 可觀察性，使維護者未來能重建「這次 request 為何失敗、成功 body 為何不成立」。
- 這不是要求完整 observability 系統，而是要求共同 contract 不先把必要線索抹掉。

## Surfaced Contradictions and Resolutions

### C1. Convenience vs observability

1. 一方需求是讓大多數 JSON API 呼叫簡單一致。
2. 另一方需求是保留 raw response metadata 以處理特殊情境。
3. 這兩者若只保留單一路徑會互相衝突：只保留高層 JSON path 會失去低層可觀察性；只保留 raw path 會讓一般呼叫重新分散。
4. **Resolution**: baseline 同時承認高層 success path 與低層 observability path 都是必要的。

### C2. Internal-only vs future public reuse

1. 目前需求是把 `Client` 視為 internal-only contract。
2. 未來可能有人想直接把它當作 package public API。
3. 這兩者在 stable 承諾上互相衝突。
4. **Resolution**: 本 baseline 只凍結 internal-only；若未來要公開，必須回到 alignment 重談 actor 與承諾。

### C3. JSON-first success vs special non-JSON endpoints

1. 目前需求要求高層 success path 以 JSON 為成功條件。
2. 未來可能存在非 JSON 或空 body 的特殊 endpoint。
3. 若這些特殊 endpoint 被視為本 baseline 的一般成功情境，則目前成功條件會被推翻。
4. **Resolution**: 本 baseline 只把 JSON-success 視為一般高層成功路徑；特殊 endpoint 屬於後續技術與範圍決策，不算本輪 frozen success path。

## Assumptions

- 本 topic 目前只凍結 internal library baseline，不處理 public API 穩定性承諾。
- 一般成功路徑以 JSON API 為主；特殊 file / streaming / empty-body success case 不在本輪 success baseline 內。
- 單一 `CustomException` 基底足以先表達共同失敗語意；更細錯誤家族可在後續 topic 展開。

## Non-goals

- 不實作本 topic 的任何 production code。
- 不決定完整 package skeleton 或最終 module 檔名。
- 不討論其餘 domain endpoint 的 method 與 resource hierarchy。
- 不在本輪展開完整 error hierarchy、retry strategy 細節或 auth refresh 細節。
- 不在本輪宣告任何 ported API compatibility。

## Blockers

None.

## Handoff Boundary for Technical Translation

技術翻譯階段可以開始處理：

- 如何把 JSON-first success path 與 raw observability path 映射成最小技術 artifacts
- 如何在不暴露 `httpx` 的前提下定義 repo 內部 envelope 與型別
- `core/...` 與 top-level `client.py` 的 architecture-compliance 比較
- 單一 `CustomException` 基底在技術上足不足以支撐後續 error mapping

技術翻譯階段不得擅自改寫下列 business baseline：

- `Client` 目前是 internal-only
- 高層 success path 以可解析 JSON 為成功條件
- raw response 可觀察性必須保留
- `httpx` 不直接暴露到上層 interface
- 失敗不可 silent fallback，且 retry 必須有上限
