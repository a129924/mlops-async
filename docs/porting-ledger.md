# Porting Ledger

## Purpose

這份 ledger 用來記錄從 `sasctl`、legacy `sas-api` repository 或其他 source SDK
平移到 `mlops-async` 的 API 證據。每個已實作的 API 都必須留下足夠的 source、
request、response、error、compatibility 與 validation 證據，讓 reviewer 能理解
哪些行為被 preserved、normalized、intentionally changed 或 blocked。

## Authoritative workflow

API porting work 必須從下列 artifact 開始：

1. `analysis/api-client-porting-contract/requirements.md`
2. `analysis/api-client-porting-contract/technical-spec.md`
3. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
4. `.github/skills/api-client-porting-planner/`
5. `.github/skills/api-client-porting-implementer/`
6. `docs/migration-map.md`

`docs/migration-map.md` 用來集中追蹤 source API -> target async API 的 mapping、
目前狀態與 review notes；`docs/porting-ledger.md` 則保留完整證據與 compatibility
判斷依據。
當兩份文件都在同一項 porting 工作範圍內時，請先更新 `docs/migration-map.md`
（狀態與對照），再更新 `docs/porting-ledger.md`（完整證據與相容性判斷）。

## Compatibility labels

只允許使用下列 labels：

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

如果 `mlops-async` 把 raw SDK output 轉成 typed Pydantic schema，就不能把
response 標成 `equivalent`；應使用 `normalized`。

## Decision labels

只允許使用下列 final decisions：

- `continue`
- `stable`
- `needs-human-review`
- `blocked`

## Entry template

每個 API 或安全的 same-family batch 都請複製這份模板。

```md
## <endpoint-family>: <source-function-or-api-name>

### Source

- Source SDK：
- Source module：
- Source function：
- Source file：
- Source line range：
- Source commit、tag 或 package version：

### Request Contract

- HTTP method：
- Path：
- Required headers：
- Query params：
- Body：
- Auth behavior：
- Status：missing | drafted | tested | implemented | blocked

### Target

- Target module：
- Target class：
- Target method：
- Async：true | false

### Response Contract

- Success status codes：
- Schema model：
- Extra policy：
- Nullable fields：
- Optional fields：
- Aliases：
- Transformations：
- Pagination：
- Empty response behavior：
- Status：missing | drafted | tested | implemented | blocked

### Error Contract

- Error schema model：
- Extra policy：
- Error status handling：
- Status：missing | drafted | tested | implemented | blocked

### Compatibility

- Request：equivalent | normalized | intentionally_changed | not_supported | unknown
- Response：equivalent | normalized | intentionally_changed | not_supported | unknown
- Error：equivalent | normalized | intentionally_changed | not_supported | unknown
- Session：equivalent | normalized | intentionally_changed | not_supported | unknown

### Tests

- Request tests：
- Response tests：
- Error tests：
- Validation commands：
- Validation not run / why：

### Divergences and Review Notes

- Known divergences：
- Stop flags observed：
- Human-review notes：

### Decision

- Decision：continue | stable | needs-human-review | blocked
```

## Ledger entries

目前還沒有任何 API 依這份 workflow 完成 porting。
