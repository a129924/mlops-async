---
topic: core-concrete-client-minimal
type: correction-plan
parent_plan: plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md
created: 2026-05-15
status: review-ready
---

# core-concrete-client-minimal — Object Typehint Correction Plan

## Purpose

本檔記錄這一輪 **object type-hint tightening** 的分類規則。目的不是做全 repo type cleanup，
而是只處理本 topic touched files 中，會弱化 contract 的 `object` 用法。

## Correction Trigger

目前 touched files 中的 `object` 用法並不完全等價：

1. 有些 `object` 是合理的 unknown runtime boundary，例如 `_is_json_value(value: object)`
2. 有些 `object` 只是 internal narrowing 的 cast，仍可接受
3. 但有些 helper 明明只會 raise，卻被標成 `-> object` 或其他一般回傳型別，會弱化測試與 typing contract

因此這次 correction 需要做**分類式 tightening**，而不是一刀切移除所有 `object`。

## Scope

- **In scope**
  - 本 topic touched files 中的 `object` 用法分類
  - `src/mlops_async/transport/http_client.py`
  - `tests/unit/transport/test_http_client.py`

- **Out of scope**
  - 全 repo `object` cleanup
  - 與本 topic 無關的型別整理
  - 將所有 unknown boundary 強行改成過度精細型別

## Keep vs Tighten Rules

### Keep

下列 `object` 用法可保留：

1. `_is_json_value(value: object) -> TypeGuard[JSONValue]`
   - 這裡的 `object` 是 unknown decoded runtime value 的正當入口
2. `cast(list[object], value)` / `cast(dict[object, object], value)`
   - 只要用途是 internal narrowing，且目前沒有更可信的來源型別，可保留
3. test 中刻意產生 non-JSON runtime value 的 `object()`
   - 若用途是驗證 invalid runtime value boundary，可保留

### Tighten

下列 `object` 應收斂：

1. 任何永遠 raise 的 helper，卻標成 `-> object` 或其他一般回傳型別
2. 任何本可精確表達，卻被降成 `object` 讓 contract 變模糊的 helper return type
3. 對這類 helper，優先收斂為 `NoReturn`

## Acceptance Criteria Delta

### Must pass

1. touched files 中合理的 unknown boundary `object` 仍保留
2. touched files 中會弱化 contract 的 `object` / general return type 已收斂成更精確型別（例如 `NoReturn`）
3. correction-plan 清楚記錄哪些 `object` 是刻意保留、哪些是刻意收斂
4. 不把這次 correction 擴張成全 repo type cleanup

### Must fail

1. 把所有 `object` 一刀切移除，連 unknown runtime boundary 也一起刪掉
2. 永遠 raise 的 helper 仍保留 `-> object` 或 `-> bool` 等模糊回傳型別
3. 以此次 correction 為藉口清理與 topic 無關的檔案

## Reviewer Guidance

reviewer 應優先檢查：

1. `src/mlops_async/transport/http_client.py` 的 `object` boundary 是否仍合理
2. `tests/unit/transport/test_http_client.py` 中 always-raise helpers 是否已收斂為 `NoReturn`
3. test 中刻意使用 `object()` 的 case 是否仍保留其測試意圖

## Historical Retention Note

即使 touched files 已完成回補，本檔仍保留，作為這次 object type-hint tightening 的歷史紀錄。
