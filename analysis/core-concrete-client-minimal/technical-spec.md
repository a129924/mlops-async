# Core Concrete Client Minimal Technical Spec

## Status

- **Status**: review-ready technical baseline
- **Topic**: `core-concrete-client-minimal`
- **Source baseline**: `analysis/core-concrete-client-minimal/requirements.md`
- **Translation scope**: minimal internal HttpClient technical decomposition only; no implementation
- **Parent artifact role**: 本檔已回補 merged final contract；correction / delta artifacts 保留為歷史決策軌跡與 reviewer evidence，不覆寫本 parent spec

## Source Baseline Summary

本 topic 的 business baseline 已凍結下列不可自行改寫的前提：

1. 目標是第一個 **internal-only minimal concrete HttpClient**，不是 public facade。
2. concrete transport implementation 必須落在 `src/mlops_async/transport/http_client.py`，而不是 `core/`；若舊的 `src/mlops_async/core/http_client.py` 存在，最終狀態必須刪除且不可保留 alias。
3. `HttpClient` 必須以 `class HttpClient(Client): ...` 顯式繼承 internal `Client` contract；review evidence 不能只靠 structural compatibility。
4. `request()` 只在 HTTP 2xx 成功時回傳 `RawClientResponse`。
5. `request_json()` 對 non-2xx、non-JSON success body、以及 `NaN` / `Infinity` / `-Infinity` 這類 non-finite success body 都必須失敗。
6. low-level failure 由 minimal HttpClient 擁有，且只限 transport / HTTP / JSON parsing 層級。
7. `MlopsAsyncBaseException` 留在 package root，且 root `exceptions.py` 只承接 base home；transport-specific concrete exceptions 留在 `src/mlops_async/transport/exceptions.py`，本 topic 不做 root re-export。
8. default headers 只允許最小 content negotiation 語意。
9. 禁止 client-level default params 與 client-level default options merge。
10. constructor surface 只接受 minimal transport substrate 所需參數，並保留 low-level transport injection 作測試 seam。
11. type-hint tightening 採分類式規則：保留合理 unknown boundary 的 `object`（例如
    `_is_json_value(value: object) -> TypeGuard[JSONValue]`、internal narrowing casts、測試中的
    `object()`），但把永遠 raise 的 helper 收斂為 `NoReturn` 等精確型別。

## Historical Decision Lifecycle

- parent artifacts（analysis / technical-spec / plan / step）是 merged final contract 的 execution-facing
  source of truth
- correction / delta artifacts 保留 repo-visible，作為 needs-rework 脈絡、decision trail、未來流程範例、
  與 reviewer acceptance evidence
- correction / delta artifacts 說明 drift 是如何被發現與修正；本 technical spec 則說明現在應實作與驗證的最終 contract

## Requirement Traceability

| Requirement | Technical realization | Dependencies | Cost / burden | Status |
| --- | --- | --- | --- | --- |
| R1 Internal-only transport implementation beside subsystem | 在 `src/mlops_async/transport/http_client.py` 定義 concrete HttpClient，並維持 `core/` 純 contract 層；若有 `src/mlops_async/core/http_client.py` 則移除 | 現有 `Client` Protocol、module-boundary discipline | 中：需同時補 implementation 缺口、處理舊路徑退場、並維持 boundary 清楚 | feasible |
| R1a Nominal inheritance of `Client` | 在 `src/mlops_async/transport/http_client.py` 以 `class HttpClient(Client): ...` 定義 concrete client，並用 `__bases__` / `__mro__` 類 nominal evidence 驗證 contract | `Client` Protocol、contract tests、review acceptance wording | 低到中：實作成本不高，但若只留 structural evidence，review 仍會放錯 contract | feasible |
| R2 Success-only raw path | `request(...)` 將 transport response 映射為 success-only `RawClientResponse`，並在 non-2xx 時改走 exception path | `RawClientResponse`、HTTP status classification | 中：需明確切分 success path 與 error path，避免 ambiguous raw contract | feasible |
| R3 JSON-first high-level path | `request_json(...)` 以 shared execution 為基礎，並在 parse failure、runtime JSON guard failure、或 non-finite JSON constants 時映射 low-level exception | JSON alias、decode rule、shared failure translation、runtime JSON guard | 中：需避免雙重判斷邏輯漂移，且 Python decoder 對 non-finite constants 的寬鬆行為不能滲入 contract | feasible |
| R4 Low-level failure ownership | 定義 transport / HTTP / JSON parsing failure translation boundary | transport adapter behavior、subsystem-local exceptions | 中到高：需把失敗責任固定在此層，但不可擴張成 domain semantics | feasible |
| R5 Base/root vs subsystem exception placement | root `exceptions.py` 只保留 `MlopsAsyncBaseException`；`transport/exceptions.py` 定義 concrete transport exceptions，且不做 root re-export | package boundary rule、exception import discipline | 中：需重構既有 baseline 並避免 root exceptions 肥大 | feasible with prerequisites |
| R6 Shallow exception structure | 以單一 `transport/exceptions.py` 承載 subsystem exceptions，暫不建立更深 exception package | file-size / complexity threshold discipline | 低：主要是結構控制而非複雜建設 | feasible |
| R6a Layered semantic hierarchy | transport exception hierarchy 採 `MlopsAsyncBaseException` -> `HttpTransportException` -> finer semantic subclasses | exception inheritance discipline、test typing expectations | 低到中：主要是 hierarchy 設計清楚而非額外大量檔案 | feasible |
| R7 Minimal default header policy | constructor-level default headers validation / normalization 與 request-level merge rule | header normalization policy、request builder logic | 中：需嚴格限制 header semantics，避免 scope drift | feasible |
| R8 No client-level implicit params or options | constructor surface 不提供 default params / default options；request path 僅接受 per-request params / options | constructor API discipline、request builder separation | 低到中：主要是明確禁止而非複雜建設 | feasible |
| R9 Constructor-level lifecycle and testing seam | 定義 `base_url`、`RequestTimeouts`、`verify`、transport injection、ownership 邊界 | `httpx.AsyncClient` 建立規則、transport injection testing pattern | 中：需同時兼顧 lifecycle clarity 與 testability | feasible |
| R9a Targeted type-hint tightening | 保留 `_is_json_value(value: object) -> TypeGuard[JSONValue]` 與 internal narrowing casts 等合理 `object` boundary；將 always-raise helper 收斂為 `NoReturn` | runtime JSON guard、strict typing discipline、negative-path tests | 低：主要是把 accepted typing rule 明文化，避免 blanket cleanup 或模糊回傳型別殘留 | feasible |

## Technical Workstreams

### Workstream 1: Transport module placement and concrete client surface

**Goal**
- 在 `transport/` 新增第一個 concrete HttpClient，同時維持 `core/` 為純 contract / types / options 層，且不留下 `core/http_client.py` 舊路徑殘留。

**Artifacts**
- `src/mlops_async/transport/http_client.py`
- `src/mlops_async/transport/__init__.py`
- constructor signature
- async context manager / close behavior contract

**Technical tasks**
- 定義 concrete client class 如何以 `class HttpClient(Client): ...` 顯式繼承既有 `Client` contract。
- 讓 contract tests 與 reviewer wording 同時承認 nominal evidence（例如 `__bases__` / `__mro__`），而不是只靠 `isinstance(...)` 類 structural pass。
- 固定 constructor 參數：`base_url`、`RequestTimeouts`、`verify`、`transport`、`default_headers`。
- 明確規則：不接受 `AsyncClient` injection。
- 明確規則：若 injected transport 存在，caller 擁有其生命週期；client 只關閉自己建立的 `AsyncClient`。
- 若 `src/mlops_async/core/http_client.py` 存在，於 implementation 內刪除，不保留 alias / transition path。

**Dependencies**
- `src/mlops_async/core/client.py`
- `src/mlops_async/core/request_options.py`
- existing async-first lifecycle rules

**Cost / burden**
- **Build effort**: 中
- **Sequencing pressure**: 高；surface 與 placement 不先凍結，後續 request builder 與 tests 會漂移
- **Operational burden**: 低；主要是 lifecycle clarity 與 package-boundary clarity

### Workstream 2: Request building and merge policy

**Goal**
- 把 default headers、per-request headers、params、options 的邊界轉成一致可測的 request build 規則。

**Artifacts**
- request builder / normalization logic
- header merge rule tests
- constructor validation rules

**Technical tasks**
- 實作 default headers normalization，只允許最小 content negotiation 行為。
- 定義 per-request headers override default headers 的精確規則。
- 禁止 client-level default params。
- 禁止 client-level default options merge；`ClientRequestOptions` 只從 request surface 進入。

**Dependencies**
- request input mapping strategy
- constructor API discipline

**Cost / burden**
- **Build effort**: 中
- **Integration burden**: 低到中；主要是 merge semantics 與 validation
- **Ongoing burden**: 中；若後續 auth / observability 想擴張 headers，需另立 topic

### Workstream 3: Success-only response mapping

**Goal**
- 讓 `request()` 成為 success-only raw path，而不是 generic HTTP passthrough。

**Artifacts**
- response classification and mapping logic
- `RawClientResponse` preservation tests
- HTTP status translation tests

**Technical tasks**
- 將 HTTP 2xx response 映射成 `RawClientResponse`。
- 在 non-2xx 時改走 `HTTPStatusException` path，而不是回傳 raw envelope。
- 保留必要 response context：`status_code`、`headers`、`content`、`method`、`url`。

**Dependencies**
- `RawClientResponse`
- `src/mlops_async/transport/exceptions.py`

**Cost / burden**
- **Build effort**: 中
- **Sequencing pressure**: 高；若 success-only raw path 不先釘清，後續 family 會各自依賴不同 error handling 方式
- **Operational burden**: 低

### Workstream 4: JSON path, parse-failure translation, and runtime JSON validity

**Goal**
- 讓 `request_json()` 的 success / failure 邊界建立在同一套 low-level transport contract 上。

**Artifacts**
- JSON decode path
- invalid JSON failure translation
- JSON contract tests

**Technical tasks**
- 以 shared request execution 取得 2xx raw success response。
- 將 success body decode 成 Python JSON value。
- 在 decode failure 時映射為 `InvalidJSONResponseException`。
- 將 `NaN`、`Infinity`、`-Infinity` 視為 invalid JSON success body，不得沿用 Python decoder 的寬鬆成功結果。
- 保留 `_is_json_value(value: object) -> TypeGuard[JSONValue]` 與 internal narrowing casts 作為合理 unknown boundary。
- 將 touched files 中永遠 raise 的 helper 收斂成 `NoReturn` 等精確型別，不再用 `object` / `bool` 這類會弱化 contract 的回傳型別。
- 明確規則：non-2xx 不得被 JSON path 吞掉或改寫成假成功。

**Dependencies**
- shared execution boundary
- JSON alias / decode helpers

**Cost / burden**
- **Build effort**: 中
- **Integration burden**: 中；需避免 request/raw/json 路徑重複判斷
- **Ongoing burden**: 中；特殊 non-JSON endpoints 必須另走 raw path 或後續 topic

### Workstream 5: Exception placement and hierarchy replacement

**Goal**
- 以 package root base exception + subsystem-local concrete exceptions 取代既有 `CustomException` baseline，並移除 root entry-layer / re-export 假設。

**Artifacts**
- `src/mlops_async/exceptions.py`
- `src/mlops_async/transport/exceptions.py`
- `MlopsAsyncBaseException`
- `HttpTransportException`
- `HTTPStatusException`
- `InvalidJSONResponseException`

**Technical tasks**
- 將 `MlopsAsyncBaseException` 定義在 package root `exceptions.py`，並讓該檔只承擔 base home。
- 將 `HttpErrorContext` 與 transport-specific concrete exceptions 定義在 `transport/exceptions.py`。
- 將 hierarchy 固定為：
  - `MlopsAsyncBaseException`
  - `HttpTransportException`
  - 其下再細分 `HTTPStatusException`、`InvalidJSONResponseException` 等語意子類
- 明確規則：此 topic 不建立更深 exception package；單一 file 足夠前不再細分。
- 將舊 `CustomException` 參照移除，不保留 alias、transition layer、或 root re-export。

**Dependencies**
- existing `src/mlops_async/exceptions.py`
- unit tests that currently reference `CustomException`

**Cost / burden**
- **Build effort**: 中
- **Sequencing pressure**: 高；exception shape 與 placement 會影響 request/raw/json tests 與 import boundaries
- **Operational burden**: 低到中；主要是 naming migration 與 module-boundary consistency

## Candidate Technical Artifacts

- `analysis/core-concrete-client-minimal/requirements.md`
- `analysis/core-concrete-client-minimal/technical-spec.md`
- `src/mlops_async/exceptions.py`
- `src/mlops_async/transport/__init__.py`
- `src/mlops_async/transport/http_client.py`
- `src/mlops_async/transport/exceptions.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/core/test_client_contract.py`
- `docs/ARCHITECTURE.md`（僅在新 transport placement 會讓敘事失真時更新）

## Feasibility Assessment

### Overall verdict

- **Verdict**: feasible with prerequisites

### Why feasible

- repo 已有 internal `Client` Protocol、repo-owned types、`RequestTimeouts`、以及 async-first 原則，適合接著補第一個 concrete substrate。
- 使用者已明確凍結 package boundary：`core/` 不承擔第三方 transport integration，`transport/` 才是 concrete integration 層。
- subsystem-local `transport/exceptions.py` 能避免 root exceptions file 持續肥大，同時維持 root `exceptions.py` 只承擔 base home。

### Why not free

- `CustomException` -> `MlopsAsyncBaseException` + `transport/exceptions.py` 代表既有 exception baseline 與對應測試需要同步重寫。
- success-only raw path 會改變「raw path 是否包含 error response」的直覺，必須有明確 tests 支撐。
- 新增 `transport/` module path 代表 docs、tests、與 import boundaries 都要一起對齊，不能只改單一檔案。
- Python decoder 會接受 `NaN` / `Infinity` / `-Infinity`，因此 `request_json()` 仍需額外 runtime JSON validity guard 才能符合本 topic contract。

## Architecture-compliance Self-check

| Dimension | Result | Notes |
| --- | --- | --- |
| Async-first I/O only | fits existing architecture | concrete client 仍以 `httpx.AsyncClient` 為基礎且只走 async lifecycle |
| Strict typing | fits existing architecture | constructor surface、request paths、exception hierarchy 都可沿用 strict typing discipline |
| Public API / internal boundary separation | fits existing architecture | baseline 明確禁止 public facade 與 package-root promotion |
| Import-safe modules | fits with prerequisites | constructor / exception definitions 可 import-safe，但 transport module 需避免 import side effects |
| Dependency direction and ownership boundaries | fits existing architecture | `core/` 保持 repo-owned contract 層，`transport/` 承擔第三方 integration |
| Observability and rollback support | fits with prerequisites | low-level exception context 需保留足夠重建 failure 原因，但不是完整 observability system |
| Porting workflow governance | fits existing architecture | 本 topic 是 transport substrate，不宣告任何 API compatibility，也不跳過 migration workflow |
| Retry behavior governance | fits existing architecture | retry 被明確排除在 topic 外，符合 stop-condition 保守策略 |

## Conflicts, Constraints, and Prerequisites

### Constraint 1: Core layer must stay third-party-free

- **Technical fact**: 使用者已明確要求 `core/` 不得出現第三方套件 integration。
- **Impact**: concrete HttpClient 不能放在 `core/http_client.py`，也不能把 transport-specific exceptions 放進 `core/`。
- **Consequence**: implementation plan 必須把 concrete client 與 transport exceptions 都鎖定到 `transport/`，且舊 core path 必須退場。

### Constraint 2: Root exceptions should stay slim

- **Technical fact**: 使用者已明確要求 base exception live at package root，而 concrete subsystem exceptions live beside the subsystem。
- **Impact**: `src/mlops_async/exceptions.py` 不應承擔 transport-specific concrete exceptions，也不應保留本 topic 的 re-export 入口責任。
- **Consequence**: implementation plan 必須同時更新 root `exceptions.py` 與 `transport/exceptions.py` 的責任分工，且 root file 最終只保留 `MlopsAsyncBaseException`。

### Constraint 2a: Subsystem exception hierarchy must preserve a middle-layer exception

- **Technical fact**: 使用者已明確要求採用 BaseException -> 大主題 Exception -> 更細語意 Exception 的分層。
- **Impact**: `HTTPStatusException`、`InvalidJSONResponseException` 等語意 exception 不應直接平鋪繼承 `MlopsAsyncBaseException`。
- **Consequence**: implementation 必須讓 `HttpTransportException` 成為 transport hierarchy 的中間層，供下游一次攔截整個 transport 類 failure。

### Constraint 3: Exception structure must stay shallow until it earns more depth

- **Technical fact**: 使用者不接受過早建立深層 exception packages。
- **Impact**: 此 topic 只能建立單一 `transport/exceptions.py`，不能再拆成更深 package 結構。
- **Consequence**: 若單一 file 還未達可維護性上限，implementation 不得擴張 exception tree 目錄層級。

### Constraint 4: Type-hint tightening is targeted, not blanket `object` removal

- **Technical fact**: 本 topic 已接受「保留合理 unknown boundary `object`，但收斂會弱化 contract 的模糊回傳型別」的分類式規則。
- **Impact**: `_is_json_value(value: object)`、internal narrowing casts、與測試中的 `object()` 不能被誤刪；但 always-raise helper 不得繼續標成 `object` / `bool` 等一般回傳型別。
- **Consequence**: typing work 必須停留在 touched files 與 accepted contract 範圍內，不能擴張成全 repo cleanup。

## Rollback-to-alignment Triggers

以下任一情況成立時，必須回到 business alignment，而不是硬做技術擴張：

1. **Failing business assumption**: `transport/` 能乾淨承接 concrete HttpClient integration
   **Contradicting technical fact**: 現有 architecture 或 import boundaries 使 `transport/` placement 不可行
   **Needed renegotiation**: 重新定義 internal package boundaries，而不是把第三方整合塞回 `core/`

2. **Failing business assumption**: success-only raw path 足以支撐後續 family
   **Contradicting technical fact**: 多數 family 需要把 error response 當成 raw data 交由上層自行判讀
   **Needed renegotiation**: 重新定義 raw path contract，而不是在 implementation 中偷偷放寬

3. **Failing business assumption**: root-base + subsystem-local exceptions 可在同 topic 一次完成
   **Contradicting technical fact**: 現有 repo contract 或 downstream tests 無法在同 topic 安全替換它
   **Needed renegotiation**: 重新決定 exception migration 是否需要過渡 topic

4. **Failing business assumption**: constructor surface 足以不暴露完整 `AsyncClient`
   **Contradicting technical fact**: 特定必要能力只能靠 `AsyncClient` injection 才能安全測試或運作
   **Needed renegotiation**: 重新討論 testing seam 與 lifecycle ownership，而不是在 minimal surface 內悄悄加入 `AsyncClient` injection

## Validation and Handoff

後續 implementation planning 應至少承接下列驗證面：

- request path tests：驗證 2xx 才回傳 `RawClientResponse`，non-2xx 轉為 `HTTPStatusException`
- nominal inheritance tests：驗證 `HttpClient` 顯式繼承 `Client`，且 evidence 包含 `__bases__` / `__mro__`
- JSON path tests：驗證 non-JSON success body 與 `NaN` / `Infinity` / `-Infinity` 皆轉為 `InvalidJSONResponseException`
- transport failure tests：驗證 timeout / network / invalid URL 轉為 `HttpTransportException`
- header merge tests：驗證 default headers 與 per-request headers 的合併與同名覆蓋規則
- constructor tests：驗證 `base_url`、`RequestTimeouts`、`verify`、transport injection ownership surface
- exception placement tests：驗證 `MlopsAsyncBaseException` 只留在 package root，而 transport concrete exceptions 留在 `transport/exceptions.py`，且沒有 root re-export
- hierarchy tests：驗證 `HTTPStatusException`、`InvalidJSONResponseException` 等語意 exception 皆繼承 `HttpTransportException`
- path cleanup tests / checks：驗證 `src/mlops_async/core/http_client.py` 不再作為 concrete client path 存在
- typing gates：驗證 concrete client 不把 `httpx.AsyncClient` 直接暴露到上層 surface，並維持「保留合理 `object` boundary、收斂 always-raise helper 為 `NoReturn`」的 accepted rule
- governance note：implementation 計畫不得把本 topic 分析文件誤當成任何 ported API compatibility evidence

本 technical spec 不授權開始實作；它只提供後續 implementation plan 所需的技術基線。
