# Migration Map

## Purpose

?遢?辣??`mlops-async` ??銝?migration 撠銵剁??其???source SDK / legacy API
??皞撘璅?async method?????鈭箏極 review 閮餉??曉????嫘?

摰??格??臬鼠?抵??蕭頩方? handoff嚗??舐靘?隞?`docs/porting-ledger.md` ???痊隞颯?
憒???撌脩????? ledger entry嚗ource / request / response / error /
compatibility ???渲???隞?`docs/porting-ledger.md` ?箸?嚗??撠撱箇? ledger
entry ? API嚗igration map ?臭誑?????葉?????急? reference??

## Authoritative inputs

?湔?遢 migration map ??隢誑?? artifact ?箔?皞?

1. `analysis/api-client-porting-contract/requirements.md`
2. `analysis/api-client-porting-contract/technical-spec.md`
3. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
4. `.github/skills/api-client-porting-planner/`
5. `.github/skills/api-client-porting-implementer/`
6. `docs/porting-ledger.md`

隤芣?嚗docs/porting-ledger.md` ?冽??entry 摮?銝餉?雿?靘?嚗?舀 API嚗?
?臬???migration map 隞?`planned` / `TBD` 撱箇??急? `Ledger reference`嚗? ledger
entry 撱箇?敺?憛怠祕??anchor??

## When to update

隢?????湔嚗?

1. planner 摰???endpoint family ??source discovery ??request contract draft 敺?
2. implementer 摰? minimal implementation / response contract / decision 敺?
3. ledger entry ??霈?嚗?憒?`drafted -> tested -> implemented`
4. 隞餃?鋡急???`needs-human-review` ??`blocked` ??

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

1. ?遢?辣?????芾?餈質馱??銝?????request / response payload 蝝啁??券鞎澆?ㄐ??
2. 瘥???餈賢撠???source evidence嚗 ledger entry 撌脣??剁???撠? entry??
3. ??ledger entry 撠撱箇?嚗? `Ledger reference` 甈?憛?`planned` ??`TBD`嚗?
   蝑?`docs/porting-ledger.md` 鋆?敺??‵撖阡? anchor??
4. ??target async method 撠摮嚗????`planned` ??`TBD`嚗?銝??撌脣祕雿?
5. ?? endpoint family ?臭誑?葉?典?銝撘菔”嚗?? upload/download?treaming??
   polling?agination expansion?etry?lobal session side effects ??conditional
   endpoint selection ?????蝡?銝行?蝣箸?閮?review note??
6. 憒? planner ??implementer ??隢?銝?湛??? `needs-human-review`嚗?閬銵?閫??

## Recommended table

瘥?endpoint family 撱箄降雿輻銝撘菔”嚗?

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Starter template

```md
# Migration Map

## auth

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| auth | `sasctl.session.SASsession.__init__` | `sasctl/session.py:L10-L90` | `mlops_async.auth.AuthClient.[pending auth method]` | drafted | missing | unknown | continue | Public AuthClient is the fixed surface; exact method naming is still draft pending docs alignment | planned |
| auth | `legacy.auth.login` | `legacy/auth.py:L1-L40` | `mlops_async.auth.AuthClient.[pending auth method]` | tested | drafted | normalized | continue | Public AuthClient is fixed; exact method naming and session-state wording remain pending | `docs/porting-ledger.md#auth-login` |

> Note: `AuthClient.login` was an earlier draft placeholder. The current docs baseline fixes `AuthClient` as the public auth family while keeping runtime token resolution on the internal `TokenEndpointClient` path. Do not read the target shape as `TokenManager -> AuthClient`.
## model-repository

| Source family | Source module / function | Source file / lines | Target module / class / method | Request status | Response status | Compatibility | Decision | Stop reason / review note | Ledger reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model-repository | `sasctl.repositories.register_model` | `sasctl/repositories.py:L120-L210` | `TBD` | drafted | missing | unknown | needs-human-review | Upload behavior detected; do not batch-port; ledger entry not created yet | TBD |
```

## Current map

?桀?撠撱箇?隞颱?甇?? migration rows?洵銝??rows ???蝛拙???摰寞??賢 request
contract ??endpoint family ??嚗?憒?auth ??read-only metadata family??
