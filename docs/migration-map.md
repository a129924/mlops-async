# Migration Map

## Purpose

這份文件是 `mlops-async` 的集中 migration 對照表，用來把 source SDK / legacy API
的來源函式、目標 async method、目前狀態與人工 review 註記放在同一個地方。

它的目標是幫助規劃、追蹤與 handoff；不是用來取代 `docs/porting-ledger.md` 的證據責任。
如果某列已經有對應的 ledger entry，source / request / response / error /
compatibility 的完整證據仍以 `docs/porting-ledger.md` 為準；如果是尚未建立 ledger
entry 的新 API，migration map 可以先保留規劃中的狀態與暫時 reference。

## Authoritative inputs

更新這份 migration map 時，請以這些 artifact 為來源：

1. `analysis/api-client-porting-contract/requirements.md`
2. `analysis/api-client-porting-contract/technical-spec.md`
3. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
4. `.github/skills/api-client-porting-planner/`
5. `.github/skills/api-client-porting-implementer/`
6. `docs/porting-ledger.md`

說明：`docs/porting-ledger.md` 在既有 entry 存在時是主要佐證來源；若是新 API，
可先在 migration map 以 `planned` / `TBD` 建立暫時 `Ledger reference`，待 ledger
entry 建立後回填實際 anchor。

## When to update

請在這些時點更新：

1. planner 完成某個 endpoint family 的 source discovery 與 request contract draft 後
2. implementer 完成 minimal implementation / response contract / decision 後
3. ledger entry 狀態改變時，例如 `drafted -> tested -> implemented`
4. 任務被標成 `needs-human-review` 或 `blocked` 時

## Status fields

### Request status

- `missing`
- `drafted`
- `tested`
- `implemented`
- `blocked`

### Response status

- `missing`
- `drafted`
- `tested`
- `implemented`
- `blocked`

### Compatibility labels

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

### Decision labels

- `continue`
- `stable`
- `needs-human-review`
- `blocked`

## Update rules

1. 這份文件偏向「導航與追蹤」，不要把完整 request / response payload 細節全部貼在這裡。
2. 每一列都應能追到對應的 source evidence；若 ledger entry 已存在，應連到對應 entry。
3. 若 ledger entry 尚未建立，可先在 `Ledger reference` 欄位填 `planned` 或 `TBD`，
   等 `docs/porting-ledger.md` 補上後再回填實際 anchor。
4. 若 target async method 尚未存在，可先保留 `planned` 或 `TBD`，但不可假裝已實作。
5. 同一 endpoint family 可以集中在同一張表，但遇到 upload/download、streaming、
   polling、pagination expansion、retry、global session side effects 或 conditional
   endpoint selection 時，應拆成獨立列並明確標記 review note。
6. 如果 planner 與 implementer 的結論不一致，先標 `needs-human-review`，不要自行消解。

## Recommended table

每個 endpoint family 建議使用一張表：

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Starter template

```md
# Migration Map

## auth

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| auth | `sasctl.session.SASsession.__init__` | `sasctl/session.py:L10-L90` | `client.auth.[待定 auth method]` (`AuthClient`) | drafted | missing | unknown | continue | Public auth surface 已固定為 `client.auth`（對應 `AuthClient`）；具體 method naming 仍待後續文件與實作 topic 定案 | planned |
| auth | `legacy.auth.login` | `legacy/auth.py:L1-L40` | `client.auth.[待定 auth method]` (`AuthClient`) | tested | drafted | normalized | continue | Public auth surface 已固定為 `client.auth`（對應 `AuthClient`）；method naming 與 session-state wording 仍待後續 topic 定案 | `docs/porting-ledger.md#auth-login` |

## model-repository

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-repository | `sasctl.repositories.register_model` | `sasctl/repositories.py:L120-L210` | `TBD` | drafted | missing | unknown | needs-human-review | Upload behavior detected; do not batch-port; ledger entry not created yet | TBD |
```

補充：`AuthClient.login` 是較早期的 draft placeholder。當前 docs baseline 固定的是
`PackageLevelClient` 對外提供 `client.auth` public surface，而 `client.auth` 對應
`AuthClient` family；runtime token resolution 仍走 internal `TokenEndpointClient` path；
不得把目標形狀讀成 `TokenManager -> AuthClient`。

## Current map

## Legacy `sas-docker-api` MVP endpoint inventory（2026-08-06）

本清單只整理 legacy `sas-docker-api` 已觀察到的 outbound Viya request，供 MVP
排序使用；它不代表 live Viya 驗證、response contract 完整性，或立即實作授權。
來源 commit 為 `a5a8c74fdb105f50b2b27d9edd2a841a32691177`。

| MVP 階段 | Endpoint family / API | Legacy request evidence | 目前 `mlops-async` 狀態 | 決策與停止條件 |
| --- | --- | --- | --- | --- |
| 已完成基礎 | `SASLogon/oauth/token` obtain / refresh | `POST {base}/SASLogon/oauth/token`；HTTP Basic；form 的 password 或 refresh grant | `PasswordTokenEndpointClient` 已有 runtime 實作 | 不重做。若需調整 legacy 相容性，另開 token-only topic；不得沿用 legacy `verify=False`。 |
| MVP-1 | `modelRepository/models` list / get | `GET /modelRepository/models`；`GET /modelRepository/models/{model_id}`；Bearer 與 model JSON Accept header | 僅有 upstream-aligned request-contract gates，尚無 production endpoint client | 優先候選。list 與 get 可同 family 規劃；先完成 response/error contract，再實作。 |
| MVP-2 | model content | legacy model file content 以 response link 為準；project flow 另有 `/modelRepository/models/{model_id}/contents/{file_id}/content` | 只有 direct-path request gate，尚無 runtime client | 獨立 topic。先決定 hypermedia link 與 fixed path 的相容性；下載／content-type 行為不可猜測。 |
| MVP-3 | `modelRepository/projects` list | `GET /modelRepository/projects?limit={limit}` | 只有 upstream-aligned request-contract gate，尚無 production endpoint client | 可在 models read-only 穩定後進行。 |
| MVP-3 | project lookup / champion | legacy 先 list projects 後以名稱篩選，再 `GET /modelRepository/projects/{project_id}/champion` | champion 有 request gate；lookup-by-name 不是獨立 Viya endpoint | champion 與 lookup 分開；champion contents 的多 request / `gather()` 編排不屬於 MVP thin wrapper。 |
| MVP-4 | `jobExecution/jobRequests/{id}/jobs` start | `POST` 到 job start path；Bearer 與 job JSON Accept header | 有 repo-helper direct-path request gate，尚無 runtime client | 可單獨規劃。不得把 start 自動擴成 polling、wait 或 state machine。 |
| 延後審查 | `jobExecution/jobs/{id}` / `state` | legacy 有 `GET` detail 與 `GET .../state` | 現有 gate 是 internal-wrapper shape-only | 需先取得可作 implementation-truth 的來源；不得以 shape-only fixture 直接實作。 |
| 延後審查 | `casManagement/dataSources/.../tables` list / get | legacy 構成 list（`limit`、`start=0`）與 direct table GET | 現有 gate 是 custom-client shape-only | legacy 需求可作 future candidate，但先以 upstream OpenAPI 或 human-confirmed contract 升級證據。 |
| 非 MVP | table state change | `PUT /casManagement/servers/.../tables/{table}/state?value={state}` 加 JSON output table body | 僅有 custom-client shape baseline | mutation endpoint；在 read-only MVP 穩定前不排程。 |
| 排除 | project tables link | 舊 fixed-path MVP `/modelRepository/projects/{project_id}/tables` 已被 superseded | historical-only | 不重新放回 queue，除非有新的 human decision。 |
| 排除 | champion model execution / SWAT CAS | legacy 透過 `swat.CAS(...)` 與 SAS model manager 執行 | 不是 HTTP endpoint client | 保持在 HTTP MVP 之外。 |

### 建議 MVP 順序

1. 保持既有 token runtime 不動。
2. 僅規劃並實作 `modelRepository/models` 的 list / get read-only family。
3. 再分別處理 model content、projects list、champion；每個仍保有自己的 request / response gate。
4. Job start、job state 與 CAS tables 依證據強度與實際業務需要另開 topic；不作跨 family batch。

### 證據閱讀規則

- `docs/request-shape-priority-workflow/request-contract-evidence-matrix.md` 的 authority
  class 優先於任何單一 historical fixture。
- `request-contract` 的 `[X]` 只表示 request shape 已被擷取，不表示 production client、
  response parsing、live endpoint 或 session behavior 已完成。
- 每個實作 topic 在進入程式碼前都要在 `docs/porting-ledger.md` 新增該 API 的來源、
  request、response、error 與相容性決策。

目前尚未建立任何正式 migration rows。第一批 rows 應從最穩定、最容易抽出 request
contract 的 endpoint family 開始，例如 auth 或 read-only metadata family。
