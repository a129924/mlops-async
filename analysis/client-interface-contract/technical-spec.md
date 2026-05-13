# Client Interface Contract Technical Spec

## Status

- **Status**: review-ready technical baseline
- **Topic**: `client-interface-contract`
- **Source baseline**: `analysis/client-interface-contract/requirements.md`
- **Translation scope**: interface contract and technical decomposition only; no implementation

## Source Baseline Summary

本 topic 的 business baseline 已凍結下列不可自行改寫的前提：

1. `Client` 目前是 **internal-only** contract，不是 package 對外 stable API。
2. 一般成功路徑以 **可解析 JSON** 為成功條件。
3. 必須同時保留 **高層 convenience path** 與 **低層 raw observability path**。
4. 上層 interface **不得直接暴露 `httpx` 型別**。
5. 失敗不可 silent fallback，且需以一致的 **`CustomException` 基底語意** 向上傳遞。
6. retry 不得無上限；**429 不在自動 retry 成功承諾內**。

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 JSON-first success path | 定義 `request_json(...)` contract、JSON 型別別名、success-body JSON parse failure mapping | repo 內部 JSON alias、error mapping baseline | 中：需處理 JSON parsing boundary 與未來特殊 endpoint 排除 | feasible |
| R2 Raw observability path | 定義 `request(...)` contract 與 `RawClientResponse` envelope | raw response field selection、header/content preservation policy | 中：欄位過少會導致後續擴充成本 | feasible |
| R3 Internal-only dependency boundary | 將 contract 放在 internal-first module boundary，並禁止 package root re-export | module boundary 決策、`__init__.py` discipline | 低到中：主要是文件與 export 約束成本 | feasible |
| R4 Dependency exposure rule | 所有 interface 輸入輸出改用 repo 自有窄型別，不暴露 `httpx` | typed alias、wrapper mapping、pyright strict discipline | 中：增加一層適配與測試維護成本 | feasible |
| R5 Failure semantics | 先定義單一 `CustomException` 基底與 error translation boundary | exception module、transport/HTTP/JSON failure mapping | 中：先簡化，但後續細分錯誤家族有重構成本 | feasible |
| R6 Retry upper bound | 在 contract 層只凍結 failure boundary，不把 retry engine 混入本 topic implementation | project stop conditions、後續 retry policy topic | 中到高：具體 retry behavior 受治理規則限制 | fits with prerequisites |

## Technical Workstreams

### Workstream 1: Interface surface freeze

**Goal**
- 將 baseline 轉為可執行的 internal contract，最少包含兩個 async methods：`request(...)` 與 `request_json(...)`。

**Artifacts**
- internal `Client` contract module（檔名待 module-boundary 決策）
- `JSONScalar` / `JSONValue` 型別別名
- method signature contract

**Technical tasks**
- 凍結 `request(...)` 為低層 raw path，不直接回傳 JSON。
- 凍結 `request_json(...)` 為高層 convenience path，並以 JSON parsing 作為成功判定的一部分。
- 明確規則：不得用單一 `request(...)` 配 flag 改變回傳型別。

**Dependencies**
- strict typing baseline
- 後續 `python-api-signature` / `python-type-hints-strict` 規範

**Cost / burden**
- **Build effort**: 中
- **Sequencing pressure**: 高；若不先凍結 surface，後續 error/model/module 決策會漂移
- **Operational burden**: 低；主要是 contract 維護而非 runtime burden

### Workstream 2: Response envelope and type isolation

**Goal**
- 在不暴露 `httpx` 的前提下保留 raw response 可觀察性。

**Artifacts**
- `RawClientResponse`
- internal type module or colocated contract types
- type-check rules preventing `httpx.Response` leakage

**Technical tasks**
- 選定 `RawClientResponse` 最小欄位集合：`status_code`、`headers`、`content`、`method`、`url`
- 決定 `headers` 的 contract 僅承諾映射語意，暫不擴張為完整 case-insensitive API surface
- 建立型別邊界，確保上層 interface 只看到 repo-defined 與 builtin types

**Dependencies**
- strict typing
- serialization boundary discipline

**Cost / burden**
- **Build effort**: 中
- **Integration burden**: 中；需將 transport library shape 映射到自有 envelope
- **Ongoing burden**: 中；未來如需更多 raw metadata，可能擴張 envelope

### Workstream 3: Error baseline and failure translation

**Goal**
- 將 business baseline 的 failure semantics 轉成最小可實作的技術邊界。

**Artifacts**
- `CustomException` 基底
- error translation notes / future mapping table

**Technical tasks**
- 定義哪些失敗在此 topic 必須映射到 `CustomException`：transport failure、不可恢復 HTTP 狀態、success-body JSON parse failure、auth/retry exhaustion
- 說明本 topic 不展開完整錯誤家族；細分 exception tree 屬後續 topic
- 明確禁止 silent fallback 與 success-shaped defaults

**Dependencies**
- error-handling policy
- auth/retry policy topics

**Cost / burden**
- **Build effort**: 中
- **Sequencing pressure**: 中；若 error baseline 太模糊，interface tests 無法穩定
- **Operational burden**: 低到中；主要是 failure diagnosis 與後續 exception tree 演進成本

### Workstream 4: Module placement and architecture fit

**Goal**
- 在不過早公開 internal contract 的前提下，決定第一個實作位置的技術方向。

**Artifacts**
- module boundary decision record
- `core/...` vs `src/mlops_async/client.py` comparison note

**Technical tasks**
- 比較 internal-first `core/...` 與 top-level `client.py` 的 dependency direction
- 定義決策規則：若此 phase 仍為 internal-only，則不得由 package root re-export
- 若未來要公開 `Client`，需再增加 facade / re-export topic，不得直接把 internal contract 視為現成 public API

**Dependencies**
- `docs/ARCHITECTURE.md` 的 planned package shape
- module boundary governance

**Cost / burden**
- **Build effort**: 低到中
- **Integration burden**: 中；若與未來 public facade 脫節，後續需二次遷移
- **Ongoing burden**: 中；需維持 internal module 與 future public module 的敘事一致

### Workstream 5: Validation and governance integration

**Goal**
- 讓後續 implementation planning 有明確驗證面，且不誤宣告 compatibility。

**Artifacts**
- request contract tests plan
- response JSON contract tests plan
- error mapping tests plan
- governance note for migration map / ledger update boundaries

**Technical tasks**
- 為 `request(...)` / `request_json(...)` 規劃 unit test 類型
- 保留 `pyright --strict`、`ruff check`、`pytest` 作為驗證入口
- 明確聲明：本 topic 只是 interface contract，不得把 planning/contract 文檔本身視為 ported API compatibility evidence

**Dependencies**
- `pyproject.toml`
- `docs/project-guidelines.md`
- 未來 implementation plan / tests

**Cost / burden**
- **Build effort**: 中
- **Integration burden**: 低
- **Ongoing burden**: 中；需避免 interface contract 與實作/測試逐步偏離

## Candidate Technical Artifacts

下列是實作階段的候選 artifacts，不代表本輪已決定最終檔名：

- `src/mlops_async/core/<client-contract-module>.py`
- `src/mlops_async/core/<client-contract-types-module>.py`
- `src/mlops_async/exceptions.py`
- `tests/unit/client/test_interface_contract.py`
- `docs/ARCHITECTURE.md`（僅在 module placement 決策完成後更新敘事）

## Feasibility Assessment

### Overall verdict

- **Verdict**: feasible with prerequisites

### Why feasible

- repo 已有明確 async-first、strict typing、module boundary 的設計原則，適合先凍結 internal contract
- 這個 topic 不要求立即實作 transport engine，因此可以先把 interface/typing/error boundary 文檔化
- `core/...` 優先可降低 internal contract 被誤判為 public API 的風險

### Why not free

- 不暴露 `httpx` 代表必須自建 envelope/type alias，這會帶來額外映射與維護成本
- `request_json(...)` 與 `request(...)` 兩層結構若規範不嚴，後續呼叫方可能濫用低層 path
- retry 行為在 repo 治理中本來就是高風險區域；即使此 topic 只定 contract，後續落地仍需要單獨審視

## Architecture-compliance Self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Async-first I/O only | fits existing architecture | `Client` contract 預設為 async methods，符合 repo 原則 |
| Strict typing | fits existing architecture | 本 spec 明確要求 JSON alias、repo-defined envelope、禁止 `Any`/直接暴露 `httpx` |
| Public API / transport / data model separation | fits with prerequisites | 需先保持 internal-only placement；若未來公開，應新增 facade 層而非直接提升 internal contract |
| Import-safe modules | fits existing architecture | contract / types / exceptions 均可在 import-safe 條件下定義 |
| Dependency direction and ownership boundaries | fits with prerequisites | 需要 module-boundary 決策來避免 `core/...` 與 future top-level `client.py` 互相污染 |
| Observability and rollback support | fits with prerequisites | 本 spec 只保留 raw observability contract，不等於完整 observability 系統 |
| Porting workflow governance | fits with prerequisites | 本 topic 不得直接宣告 compatibility；若日後把此 contract 用在實際 endpoint family，仍需走 request tests → migration-map → ledger 順序 |
| Retry behavior governance | fits with prerequisites | 具體 retry engine 仍受 stop condition 約束；本 spec 只能凍結上限與失敗邊界，不能直接擴張實作承諾 |

## Conflicts, Constraints, and Prerequisites

### Constraint 1: Retry behavior is a governed stop area

- **Technical fact**: `docs/project-guidelines.md` 將 retry behavior 列為 stop condition。
- **Impact**: 此 topic 可以定義「不得無上限 retry、429 不在自動 retry 承諾內」的 contract boundary，但不應在沒有額外 human review 的情況下展開完整 retry implementation。
- **Consequence**: 後續若要實作 retry engine，需另立 topic 或在 implementation plan 中標記 human-review gate。

### Constraint 2: Planned package shape still names top-level `client.py`

- **Technical fact**: `docs/ARCHITECTURE.md` 目前把 `client.py` 視為未來 public-facing design target。
- **Impact**: 若本 topic 先採 `core/...`，需補一層敘事：internal contract 與 future public module 不是同一件事。
- **Consequence**: module-boundary 決策若落 `core/...`，後續需要更新 architecture 文檔，避免產生表面矛盾。

### Constraint 3: JSON-first success excludes some future endpoint families

- **Technical fact**: file/download/streaming/empty-body success case 可能存在，但不在本 baseline 內。
- **Impact**: `request_json(...)` 不能被誤宣告為所有 endpoint 的通用成功路徑。
- **Consequence**: resource/domain clients 預設走 `request_json(...)`，但特殊 endpoint 需透過 `request(...)` 或另立 topic 處理。

## Rollback-to-alignment Triggers

以下任一情況成立時，必須回到 business alignment，而不是硬做技術擴張：

1. **Failing business assumption**: 一般成功回應以 JSON 為主
   **Contradicting technical fact**: 多數目標 endpoint 的成功 body 其實是空 body、binary 或其他非 JSON 形式
   **Needed renegotiation**: 重新定義高層 success path 是否仍以 JSON 為核心，或改分多種 success contract

2. **Failing business assumption**: `Client` 是 internal-only
   **Contradicting technical fact**: 下游使用者或其他模組必須直接依賴它，且需要 public stability
   **Needed renegotiation**: 重新定義 actor 與 public API 邊界，再決定是否改走 top-level `client.py`

3. **Failing business assumption**: 單一 `CustomException` 基底已足夠
   **Contradicting technical fact**: 呼叫方需要依錯誤類型做不同控制流，單一 base exception 無法支撐可處理性
   **Needed renegotiation**: 重新確認業務上是否要求可分辨的錯誤家族，而不只是統一 raise

4. **Failing business assumption**: 不暴露 `httpx` 的成本可接受
   **Contradicting technical fact**: 特定必要能力只能靠直接暴露 transport library types 才能保持正確或可維護
   **Needed renegotiation**: 重新定義 dependency exposure rule，或接受更厚的 internal abstraction cost

## Validation and Handoff

後續 implementation planning 應至少承接下列驗證面：

- request contract tests：驗證 `request(...)` 對 raw response envelope 的保真度
- response JSON contract tests：驗證 `request_json(...)` 只接受可解析 JSON 的成功 body
- error mapping tests：驗證 transport/HTTP/JSON parse failure 會映射到 `CustomException`
- typing gates：驗證 interface annotations 不直接暴露 `httpx`
- governance gates：避免把本 topic 的文件產出誤當成 migration-map / porting-ledger compatibility evidence

本 technical spec 不授權開始實作；它只提供後續 implementation plan 所需的技術基線。
