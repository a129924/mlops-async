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

目前尚未建立任何正式 migration rows。第一批 rows 應從最穩定、最容易抽出 request
contract 的 endpoint family 開始，例如 auth 或 read-only metadata family。
