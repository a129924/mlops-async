# Core Concrete Client Minimal Requirements

## Status

- **Status**: frozen for technical translation
- **Topic**: `core-concrete-client-minimal`
- **Scope level**: internal transport substrate baseline
- **Parent artifact role**: 本檔已回補 merged final contract；correction / delta artifacts 保留為歷史決策軌跡與 reviewer evidence，不取代本 parent baseline

## Problem Statement

`mlops-async` 已經有 internal-only `Client` contract、repo-owned request/response types、
以及 timeout baseline，但仍沒有第一個 concrete async HTTP client implementation。
若直接跳到 auth family 或其他 endpoint family 平移，後續每個 family 都可能各自決定
lifecycle、default headers、transport failure boundary、testing seam、與 exception shape，
導致 contract 與 implementation 漂移。

本 baseline 要先凍結的是：**第一個 minimal internal HttpClient 應提供什麼最小可信承諾，
以及它應該落在哪個 package boundary**。本輪明確採用 `transport/` 作為第三方 transport
整合層，而不是把 `httpx` 依賴放進 `core/`；同時把 package-level base exception 與
subsystem-local concrete exceptions 分離，避免把所有 infra exceptions 全塞在 package root。

## Actors and Boundaries

### Primary actor

- **Package 內部的 domain endpoint clients**
  - 需要一個共同的 internal transport substrate，避免每個 family 各自建立
    `httpx.AsyncClient`、各自處理 default headers、以及各自定義 low-level failure boundary。

### Secondary actor

- **Package 維護者**
  - 需要一個可測、可 mock、可維持 async lifecycle ownership 的最小 HttpClient，
    並且維持 `core/` 與 `transport/` 的 boundary 清楚。

### Supporting actor

- **Unit / contract test 作者**
  - 需要穩定的 testing seam，讓 low-level transport 可以被 fake / mock，而不是依賴注入
    完整 `httpx.AsyncClient`。

### Out-of-scope actor

- **直接依賴 public client surface 的外部使用者**
  - 本 baseline 不承諾 public facade，也不把這個 minimal HttpClient 視為穩定 public API。

## In-scope Requirements

每項 requirement 都以 actor、condition、observable outcome、decision rule 表達。

### R1. Internal-only transport implementation lives beside the transport subsystem

- **Actor**: package 維護者
- **Condition**: 需要新增第一個 concrete HttpClient implementation
- **Observable outcome**: concrete HttpClient 落在 `src/mlops_async/transport/http_client.py`
- **Decision rule**:
  - `core/` 僅保留 repo-owned contract / types / options；第三方 transport 整合不得放進 `core/`
  - 若 `src/mlops_async/core/http_client.py` 存在，implementation 完成時必須刪除，不得保留 alias /
    transition layer
- **Failure meaning**: 若這點不成立，`core/` 會開始承擔第三方 integration 責任，並留下雙重路徑 drift

### R1a. Concrete client must nominally inherit the internal `Client` contract

- **Actor**: package 維護者與 contract test 作者
- **Condition**: 需要把第一個 concrete transport client 鎖定成 repo-visible internal contract
- **Observable outcome**: `src/mlops_async/transport/http_client.py` 以
  `class HttpClient(Client): ...` 定義 concrete client
- **Decision rule**:
  - `HttpClient` 不得只靠 structural compatibility 滿足 `mlops_async.core.client.Client`
  - reviewer 與測試證據必須承認 nominal evidence，例如 `__bases__` / `__mro__`
  - 此 tightening 只屬於 internal implementation contract，不得因此把 `HttpClient` 提升成 public API
- **Failure meaning**: 若這點不成立，`Client` 會再次退回隱性的 structural 規則，未來 drift 難以及早被測試抓到

### R2. Success-only raw path

- **Actor**: package 內部的 domain endpoint client
- **Condition**: 需要取得低層 raw response envelope
- **Observable outcome**: `request()` 只在 HTTP 2xx 成功情境回傳 `RawClientResponse`
- **Decision rule**: 非 2xx response 不得作為可用 raw result 回傳；必須以 low-level semantic
  exception 向上結束
- **Failure meaning**: 若這點不成立，上層仍需在每次呼叫後自行判斷 HTTP status

### R3. JSON-first high-level path

- **Actor**: package 內部的 domain endpoint client
- **Condition**: 需要取得一般 JSON API 的成功結果
- **Observable outcome**: `request_json()` 只在 2xx 且 success body 可解碼成符合 `JSONValue`
  contract 的 Python 值時回傳結果
- **Decision rule**:
  - 非 2xx 與 non-JSON success body 都不得被視為成功
  - `NaN`、`Infinity`、`-Infinity` 對本 topic 的 `request_json()` contract 而言都屬於
    invalid JSON success body，不得當成功值回傳
- **Failure meaning**: 若這點不成立，family clients 仍會分散處理 JSON parse failure

### R4. Low-level failure ownership

- **Actor**: package 維護者與下游 family authors
- **Condition**: request 遇到 transport failure、非 2xx HTTP status、或 success body 非 JSON
- **Observable outcome**: minimal HttpClient 以 package-owned low-level semantic exception 結束，
  而不是把 transport failure 或 non-2xx 判斷責任丟給上層
- **Decision rule**: 此層只處理 transport / HTTP / JSON parsing 層級失敗，不得擴張成
  resource-specific、domain-specific 或 auth refresh 行為
- **Failure meaning**: 若這點不成立，後續每個 family 都要重新定義 low-level error boundary

### R5. Root exceptions contain only the package base; concrete subsystem exceptions live beside the subsystem

- **Actor**: package 維護者與測試作者
- **Condition**: 需要定義 low-level failure 的 exception hierarchy
- **Observable outcome**:
  - package root `src/mlops_async/exceptions.py` 只保留 `MlopsAsyncBaseException`
  - transport-specific concrete exceptions 放在 `src/mlops_async/transport/exceptions.py`
- **Decision rule**:
  - transport-specific exceptions 不得放在 `core/`
  - package root `exceptions.py` 不得承擔 transport-specific concrete exceptions 的實作細節
  - package root `exceptions.py` 不得作為本 topic 的 re-export 入口
  - 不得保留 root-level alias / transition layer 來維持舊 import path
- **Failure meaning**: 若這點不成立，package root exceptions 會快速肥大，且 subsystem boundary 與依賴方向失真

### R6. Keep exception structure shallow until it earns more depth

- **Actor**: package 維護者
- **Condition**: 需要為 transport subsystem 放置 concrete exceptions
- **Observable outcome**: `transport/exceptions.py` 作為單一 subsystem exception file 即可承載
  transport-specific hierarchy
- **Decision rule**: 不得先建立深層 exception package；只有當單一 `exceptions.py` 實質過大
  （例如超過約 150 行並持續成長）時，才可再細分
- **Failure meaning**: 若這點不成立，exception structure 會過早複雜化

### R6a. Exception hierarchy must preserve semantic layering

- **Actor**: package 維護者與測試作者
- **Condition**: 需要對 transport subsystem 的 failure 進行可辨識、可測試的分類
- **Observable outcome**: transport exception hierarchy 至少採用三層語意：
  - `MlopsAsyncBaseException`
  - `HttpTransportException`
  - 更細的 semantic exceptions，例如 `HTTPStatusException`、`InvalidJSONResponseException`
- **Decision rule**:
  - subsystem-level exception 應先表達「大主題」語意，再由更細 exception 繼承
  - `HTTPStatusException` 與 `InvalidJSONResponseException` 都應繼承 `HttpTransportException`
- **Failure meaning**: 若這點不成立，exception typing 會過平，難以在測試與下游控制流中辨識層級

### R7. Minimal default header policy

- **Actor**: package 維護者與下游 family authors
- **Condition**: constructor-level default headers 與 per-request headers 同時存在
- **Observable outcome**: client 只保留最小 content negotiation 類 default headers
- **Decision rule**:
  - 預設 `Accept: application/json`
  - 僅在 request 存在 JSON body 時補 `Content-Type: application/json`
  - per-request 同名 header 覆蓋 default header
  - 不得把 `Authorization`、Bearer token、session、`User-Agent`、tracing、
    correlation 或其他 auth/state/observability 語意放入 default headers
- **Failure meaning**: 若這點不成立，底層 client 會偷偷帶入 SAS auth 或 session semantics

### R8. No client-level implicit params or options

- **Actor**: package 維護者與 request-contract test 作者
- **Condition**: 建立 HttpClient 並執行不同 endpoint family 的 request
- **Observable outcome**: 所有 endpoint query params 都由 per-request `params` 明確提供；
  `ClientRequestOptions` 只接受 per-request 傳入
- **Decision rule**: 禁止 client-level default params；也不做 client-level default options merge
- **Failure meaning**: 若這點不成立，query contract 與 request option 邊界會被隱性 state 汙染

### R9. Constructor-level lifecycle and testing seam

- **Actor**: package 維護者與測試作者
- **Condition**: 建立 minimal HttpClient 並管理 async lifecycle
- **Observable outcome**:
  - `base_url` 為必填，且接受字串或 URL 物件
  - constructor-level timeout 允許存在，且重用 `RequestTimeouts`
  - constructor-level `verify` 允許存在
  - 允許 low-level transport injection
- **Decision rule**:
  - 不允許直接注入完整 `httpx.AsyncClient`
  - HttpClient 必須自己建立並擁有 `AsyncClient` lifecycle
  - 若存在 injected transport，其生命週期由 caller 擁有，HttpClient 不主動關閉
- **Failure meaning**: 若這點不成立，lifecycle ownership、testing seam 與 constructor surface 會混亂

### R9a. Type-hint tightening must preserve justified unknown boundaries while removing contract-weakening ambiguity

- **Actor**: package 維護者與測試作者
- **Condition**: runtime JSON validation 與負向測試 helper 需要表達 unknown value boundary 或
  always-raise 行為
- **Observable outcome**:
  - 合理 unknown boundary 可保留 `object`，例如 `_is_json_value(value: object) -> TypeGuard[JSONValue]`
  - internal narrowing casts 與 test 中刻意產生 invalid runtime value 的 `object()` 可保留
  - 永遠 raise 的 helper 以 `NoReturn` 等精確型別表達，不再用 `object` / `bool` 之類模糊回傳型別
- **Decision rule**:
  - 不是看到 `object` 就一律移除
  - 只收斂會弱化 contract 的模糊型別，而不是把本 topic 擴張成全 repo type cleanup
- **Failure meaning**: 若這點不成立，strict typing 不是變成教條式清除，就是繼續容忍會模糊 contract 的型別

## Historical Decision Lifecycle

- parent artifacts（analysis / technical-spec / plan / step）是 merged final contract 的 execution-facing
  source of truth
- correction / delta artifacts 保留 repo-visible，作為 needs-rework 脈絡、decision trail、未來流程範例、
  與 reviewer acceptance evidence
- 後續讀者若要理解「為什麼曾經 drift」應回看 correction / delta artifacts；若要理解
  「現在 accepted contract 是什麼」應以 parent artifacts 為準

## Success Signals

當此 baseline 被滿足時，至少應能觀察到：

1. repo 內有第一個 internal-only minimal HttpClient baseline，且它位於 `transport/` 而不是 `core/`，
   並以 `class HttpClient(Client):` 明確宣告 internal contract。
2. `request()` 的成功/失敗邊界對所有 family 一致：只有 2xx 才回傳 `RawClientResponse`。
3. `request_json()` 的成功條件對所有 family 一致：只有符合 `JSONValue` contract 的 2xx body 才回傳值；
   `NaN`、`Infinity`、`-Infinity` 不得被當成成功值。
4. default headers、merge rules、constructor surface、transport injection ownership 都已固定，
   不再由每個 family 各自決定。
5. package root exception 與 transport-specific concrete exceptions 的邊界已固定：root 只保留
   `MlopsAsyncBaseException`，transport-local file 承接全部 concrete exceptions，且沒有 root re-export /
   alias residual。
6. runtime JSON guard 與相關測試 helper 採分類式 type tightening：保留合理 `object` 邊界，並把
   always-raise helper 收斂成 `NoReturn` 等精確型別。

## Extreme-boundary Checks

### No network or degraded dependency

- 在 network failure、DNS 失敗、connection timeout、TLS verify failure 等情境下，minimal
  HttpClient 不得回傳看似成功的結果。
- 可接受結果只有明確 low-level exception，而不是假成功或 silent fallback。

### Wrong role or missing approval

- 若有人要求把 minimal HttpClient 直接當 public API，這超出本 baseline 的 actor 邊界。
- 若有人要求把 transport-specific exceptions 放進 `core/`，這也違反本 baseline 的 boundary。

### Interrupted or partial completion

- 若 response 是 non-2xx，或 success body 無法解析為 JSON，minimal HttpClient 不得交付半套成功結果。
- 若 success body 為 `NaN`、`Infinity`、或 `-Infinity`，也必須視為 invalid JSON success body，
  不得被當成成功結果。
- injected transport 若由 caller 持有，其資源管理責任不得在 HttpClient 內被靜默接管。

### Lowest-volume and peak-volume conditions

- 不論低流量或高流量，minimal HttpClient 的成功/失敗 decision rule 不得改變。
- 不允許以流量壓力為由，讓 non-2xx 或 parse failure 變成 ambiguous result。

### Audit or test reconstruction

- 本 baseline 要求 low-level exception 至少保留足夠 context，使測試與維護者可以重建
  transport failure、HTTP status failure、或 invalid JSON failure 的原因。
- 這不是要求完整 observability 系統，而是要求不把 low-level failure boundary 模糊掉。

## Surfaced Contradictions and Resolutions

### C1. Thin substrate vs hidden convenience state

1. 一方需求是讓 minimal HttpClient 盡量薄。
2. 另一方誘惑是把 auth header、session、client-level params、或 retry state 偷放進去，讓上層看起來更方便。
3. 這兩者會互相衝突，因為 convenience state 會讓底層 substrate 失去可測與可追蹤性。
4. **Resolution**: 本 baseline 固定 thin substrate，只允許最小 content negotiation headers，
   並禁止 client-level params 與 client-level options merge。

### C2. Core contract purity vs third-party transport integration

1. `core/` 需要保留 repo-owned contract / types / options。
2. concrete HttpClient 實作必然會接觸 `httpx` 這類第三方 transport integration。
3. 若把 concrete implementation 放進 `core/`，就會讓 `core/` 同時承擔 contract 與 integration。
4. **Resolution**: concrete HttpClient 移到 `transport/http_client.py`；`core/` 保持純 repo-owned contract 層，
   且舊的 `core/http_client.py` 路徑不得保留為 alias。

### C3. Global base exception vs subsystem-local concrete exceptions

1. 一方需求是保留單一 package base exception。
2. 另一方如果把所有 concrete infra exceptions 都放進 root `exceptions.py`，會讓 root file 持續肥大。
3. 這兩者若不切分，未來新增 subsystem exception 時 root layer 會失去焦點。
4. **Resolution**: `MlopsAsyncBaseException` 留在 package root，transport-specific concrete exceptions 置於
   `transport/exceptions.py`，且本 topic 不做 root re-export 或 transition layer。

### C4. Flat exception list vs layered semantic hierarchy

1. 一方需求是把 low-level failures 做可辨識分類。
2. 另一方若只建立平面的 sibling exceptions，會缺少「大主題 exception」層級。
3. 沒有中間層時，測試與呼叫方難以一次攔截整個 transport 類 failure。
4. **Resolution**: transport exceptions 採 layered hierarchy：`MlopsAsyncBaseException` ->
   `HttpTransportException` -> 更細語意 exceptions。

## Assumptions

- `Client` internal contract 與 repo-owned types 已足夠作為本 topic 的上游 baseline。
- 一般 family 的成功回應以 JSON API 為主；非 JSON、streaming、download、empty-body 特殊成功情境不在本輪 general success path 內。
- constructor-level timeout 與 per-request timeout 分層存在是可接受的，且都可用同一個 `RequestTimeouts` 表達。
- package root `exceptions.py` 可以只保留 `MlopsAsyncBaseException`，而不需要再承接 transport exception 入口或 re-export 責任。

## Non-goals

- 不實作 auth、token state、refresh flow、retry/backoff、session persistence。
- 不提供 public `client.py` facade。
- 不決定第一個 planner family。
- 不在本輪宣告任何 ported API compatibility。
- 不建立深層 exception package 結構。

## Blockers

None.

## Handoff Boundary for Technical Translation

技術翻譯階段可以開始處理：

- 如何把 minimal HttpClient baseline 映射成 `transport/http_client.py`
- 哪些 low-level exception context 欄位屬於必要 technical contract
- root `exceptions.py` 與 `transport/exceptions.py` 的邊界如何落地
- testing seam、transport ownership、與 async lifecycle 在技術上如何落地

技術翻譯階段不得擅自改寫下列 baseline：

- minimal HttpClient 仍是 internal-only
- `request()` 只回傳成功可用的 `RawClientResponse`
- `HttpClient` 必須顯式繼承 `Client`，且 nominal evidence 不可只靠 structural pass 取代
- `request_json()` 對 non-2xx、non-JSON success body、以及 `NaN` / `Infinity` / `-Infinity`
  都必須失敗
- `MlopsAsyncBaseException` 留在 package root，transport-specific concrete exceptions 留在 `transport/`，且本 topic 不做 root re-export
- transport exception hierarchy 採 `MlopsAsyncBaseException` -> `HttpTransportException` -> 更細 semantic exceptions
- default headers 必須維持極薄，且禁止 client-level default params / options merge
- type-hint tightening 採分類式規則：保留合理 `object` unknown boundary，收斂會弱化 contract 的
  always-raise helper 型別
