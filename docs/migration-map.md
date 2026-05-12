# Migration Map

## Purpose

這份文件是 `mlops-async` 的集中 migration 對照表，用來把 source SDK / legacy API
的來源函式、目標 async method、目前狀態與人工 review 註記放在同一個地方。

它的目標是幫助規劃、追蹤與 handoff；不是用來取代 `docs/porting-ledger.md` 的證據責任。
如果需要 source / request / response / error / compatibility 的完整證據，仍以
`docs/porting-ledger.md` 為準。

## Authoritative inputs

更新這份 migration map 時，請以這些 artifact 為來源：

1. `analysis/api-client-porting-contract/requirements.md`
2. `analysis/api-client-porting-contract/technical-spec.md`
3. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
4. `.github/skills/api-client-porting-planner/`
5. `.github/skills/api-client-porting-implementer/`
6. `docs/porting-ledger.md`

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
2. 每一列都應能追到對應的 source evidence 與 ledger entry。
3. 若 target async method 尚未存在，可先保留 `planned` 或 `TBD`，但不可假裝已實作。
4. 同一 endpoint family 可以集中在同一張表，但遇到 upload/download、streaming、
   polling、pagination expansion、retry、global session side effects 或 conditional
   endpoint selection 時，應拆成獨立列並明確標記 review note。
5. 如果 planner 與 implementer 的結論不一致，先標 `needs-human-review`，不要自行消解。

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
| auth | `sasctl.session.SASsession.__init__` | `sasctl/session.py:L10-L90` | `mlops_async.auth.AuthClient.login` | drafted | missing | unknown | continue | Waiting for request-contract tests | `docs/porting-ledger.md#auth-login` |
| auth | `legacy.auth.login` | `legacy/auth.py:L1-L40` | `mlops_async.auth.AuthClient.login` | tested | drafted | normalized | continue | Session side effects need explicit note | `docs/porting-ledger.md#auth-login` |

## model-repository

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-repository | `sasctl.repositories.register_model` | `sasctl/repositories.py:L120-L210` | `TBD` | drafted | missing | unknown | needs-human-review | Upload behavior detected; do not batch-port | `docs/porting-ledger.md#model-repository-register-model` |
```

## Current map

目前尚未建立任何正式 migration rows。第一批 rows 應從最穩定、最容易抽出 request
contract 的 endpoint family 開始，例如 auth 或 read-only metadata family。
