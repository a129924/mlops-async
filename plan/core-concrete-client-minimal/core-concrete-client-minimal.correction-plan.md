---
topic: core-concrete-client-minimal
type: correction-plan
parent_plan: plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md
created: 2026-05-15
status: review-ready
---

# core-concrete-client-minimal — Correction Plan

## Purpose

本檔不是第二份主 plan，也不取代：

- `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md`
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md`

本檔的角色是 **needs-rework 差異修正層**，專門記錄這一輪 reviewer / human feedback 對既有
topic contract 的修正理由、差異 severity、保留項目、移除項目、architecture rule 調整方向、
以及 acceptance criteria 的補強方式。

本檔需 **保留作歷史差異紀錄**；即使後續主 plan / step 回補完成，也不應直接刪除。

## Correction Trigger

本次 correction 由下列 drift 觸發：

1. 既有 analysis / plan 仍把 `src/mlops_async/exceptions.py` 描述成 package-level
   exception entry layer，甚至保留未來 re-export 的語意空間。
2. 使用者進一步澄清後，最終決策已改為：
   - `src/mlops_async/exceptions.py` **只放** `MlopsAsyncBaseException`
   - subsystem-specific exceptions 由各自 domain / subsystem 直接暴露
   - 本 topic **不做** root re-export
3. transport module placement 雖已大致修正為 `transport/http_client.py`，但 correction
   仍需把「哪些舊敘述應視為錯誤、哪些新敘述應視為保留」明確寫成差異契約，避免後續 review
   只看到結果、看不到修正原因。

## Scope

- **In scope**
  - exception placement drift
  - transport module placement drift
  - 與上述兩項直接相連的 architecture rule 修正
  - 與上述兩項直接相連的 acceptance criteria 修正
  - 與上述兩項直接相連的 implementation / test / docs 對齊要求

- **Out of scope**
  - auth、retry、public facade、planner family 選擇
  - `request()` / `request_json()` failure boundary 本身的重新設計
  - default headers / params / options merge 規則重談
  - release、README、VERSION、migration-map、porting-ledger

## Delta Summary

| Area | Parent plan / spec state | Corrected state |
| --- | --- | --- |
| Root exceptions role | `src/mlops_async/exceptions.py` 被描述為 base/entry layer，保留入口層語意 | `src/mlops_async/exceptions.py` 僅為 package-level base home，只放 `MlopsAsyncBaseException` |
| Root re-export policy | 對 root re-export 保留模糊空間 | 本 topic 明確 **不做** root re-export |
| Transport exception home | 已多半放在 `src/mlops_async/transport/exceptions.py` | 保留此決策，不變 |
| Transport hierarchy | 已多半採分層 hierarchy | 保留此決策，不變 |
| Concrete client placement | 已鎖定 `src/mlops_async/transport/http_client.py` | 保留此決策，不變 |
| Old import transition | 原本仍可能被誤解為保留入口/別名空間 | 本 topic 明確 **不保留** alias / transition layer |

## Severity Decisions

| ID | Issue | Severity | Why |
| --- | --- | --- | --- |
| CP-01 | root `exceptions.py` 被寫成 entry layer | high | 這會模糊依賴方向，並讓 implementer 誤以為 root 可回頭 import transport exceptions |
| CP-02 | root re-export policy 未被明確禁止 | high | 會導致循環引入風險、root file 膨脹、public/import surface 模糊 |
| CP-03 | 既有 acceptance criteria 仍驗證「root entry layer」 | medium | reviewer 可能依錯誤標準放行，造成 contract 與最終決策分裂 |
| CP-04 | transport placement 的舊路徑漂移未被集中記錄 | medium | 雖已有主決策，但缺少一份差異檔說明哪些舊敘述應視為失效 |

## Why This Must Be Fixed

1. 若 root `exceptions.py` 仍被視為 entry layer，後續實作很容易再次把 transport-specific
   exceptions 拉回 package root。
2. 這會直接違反最新已凍結的 exception 準則：
   - base exceptions live at package root
   - concrete subsystem exceptions live beside the subsystem
   - 本 topic 不做 root re-export
3. 若 correction 不把「錯在哪裡」寫清楚，之後主 plan 即使被同步修正，也只會留下結果，不會留下
   決策脈絡；未來回顧流程時將難以重建 needs-rework 的真正原因。

## What Stays

下列決策 **保留**，不因 correction 而重談：

1. concrete HttpClient 繼續放在 `src/mlops_async/transport/http_client.py`
2. `core/` 保持 repo-owned contract / types / options，不承擔第三方 transport integration
3. transport-specific concrete exceptions 繼續放在 `src/mlops_async/transport/exceptions.py`
4. transport hierarchy 繼續採：
   - `MlopsAsyncBaseException`
   - `HttpTransportException`
   - `HTTPStatusException`
   - `InvalidJSONResponseException`
5. `HttpErrorContext` 繼續放在 `src/mlops_async/transport/exceptions.py`
6. `CustomException` 繼續退場，且不保留 alias / transition layer

## What Must Be Removed or Rewritten

下列敘述應視為 **錯誤或過時**，必須移除或改寫：

1. `src/mlops_async/exceptions.py` 是 package-level exception entry layer
2. root `exceptions.py` 可在本 topic 承接 transport concrete exceptions 的入口責任
3. root `exceptions.py` 可在本 topic 內 re-export `HttpTransportException` /
   `HTTPStatusException` / `InvalidJSONResponseException`
4. 為了相容舊 import path，本 topic 應保留 alias / transition layer
5. 舊的 `core/http_client.py` 路徑只要仍出現在 spec / docs / tests 中就算可接受

## Corrected Architecture Rules

本 correction 將 architecture rule 鎖定如下：

1. `src/mlops_async/exceptions.py` = **package-level base home only**
   - 本 topic 只放 `MlopsAsyncBaseException`
   - 不承接 subsystem-specific concrete exceptions
   - 不承接 re-export responsibility
2. `src/mlops_async/transport/exceptions.py` = **transport-local exception home**
   - 放置 `HttpErrorContext`
   - 放置 `HttpTransportException`
   - 放置更細的 semantic subclasses
3. 依賴方向必須單向：
   - `transport/exceptions.py` 可 import `MlopsAsyncBaseException`
   - root `exceptions.py` 不得回頭 import transport exceptions
4. `src/mlops_async/transport/http_client.py` 是 concrete transport integration 的唯一正確位置
5. `core/` 與 root package 不作為 transport-specific implementation 的暫存區或入口層

## Acceptance Criteria Delta

在主 plan / review contract 被同步回補前，reviewer 應以本 correction 的 acceptance criteria
為準，而不是沿用舊的「entry layer」敘述。

### Must pass

1. `src/mlops_async/exceptions.py` 只保留 `MlopsAsyncBaseException`
2. `src/mlops_async/exceptions.py` 不 re-export transport exceptions
3. `src/mlops_async/transport/exceptions.py` 承接全部 transport-specific concrete exceptions
4. `HttpErrorContext` 位於 `src/mlops_async/transport/exceptions.py`
5. hierarchy 為：
   - `MlopsAsyncBaseException`
   - `HttpTransportException`
   - finer semantic exceptions
6. 不保留 root-level alias / transition import path
7. `src/mlops_async/transport/http_client.py` 仍是唯一正確的 concrete client module path
8. 若 `docs/ARCHITECTURE.md`、tests、spec、plan 仍提及 `core/http_client.py` 或 root entry
   exception layer，則必須一併修正

### Must fail

1. root `exceptions.py` 重新變成 transport exception 入口
2. root `exceptions.py` 為 convenience 而 re-export transport exceptions
3. transport-specific exceptions 被移回 root 或 `core/`
4. 為了保留舊 import surface 而新增 alias / transition layer

## Affected Artifacts

本 correction 直接影響下列 repo-visible artifacts 的 review 標準：

- `analysis/core-concrete-client-minimal/requirements.md`
- `analysis/core-concrete-client-minimal/technical-spec.md`
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md`
- `plan/core-concrete-client-minimal/core-concrete-client-minimal.step.md`

若進入 creator work，還會連帶影響：

- `src/mlops_async/exceptions.py`
- `src/mlops_async/transport/exceptions.py`
- `src/mlops_async/transport/http_client.py`
- `tests/unit/transport/test_exceptions.py`
- `tests/unit/transport/test_http_client.py`
- `tests/unit/core/test_client_contract.py`
- `docs/ARCHITECTURE.md`

## Reviewer Guidance

reviewer 在處理本 correction 時，應優先回答：

1. 主 plan / spec 哪些敘述只是「還沒跟上最新決策」，而不是整個 topic 要推翻重來？
2. 哪些 drift 屬於 blocking contract error，哪些只是待同步 wording？
3. correction 是否已把：
   - 保留內容
   - 移除內容
   - architecture rule
   - acceptance criteria
   - historical rationale
   都寫清楚，足以支持後續 needs-rework 修補？

## Historical Retention Note

本 correction 檔的價值之一，是保留這次 needs-rework 的來龍去脈。即使後續主 plan / step /
analysis 都回補完成，本檔仍應保留，以支援之後的流程改善與 decision audit。
