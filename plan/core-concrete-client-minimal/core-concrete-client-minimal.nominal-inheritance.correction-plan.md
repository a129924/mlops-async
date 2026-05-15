---
topic: core-concrete-client-minimal
type: correction-plan
parent_plan: plan/core-concrete-client-minimal/core-concrete-client-minimal.plan.md
created: 2026-05-15
status: review-ready
---

# core-concrete-client-minimal — Nominal Inheritance Correction Plan

## Purpose

本檔記錄這一輪 **nominal inheritance tightening** 的差異契約。它不取代 parent plan，
而是保留「為什麼要從只滿足 `Client` Protocol，升級成必須顯式繼承 `Client`」的歷史脈絡。

## Correction Trigger

目前 `HttpClient` 雖然在 structural typing 上滿足 `mlops_async.core.client.Client`，但這仍允許未來
實作者只靠 runtime-checkable protocol 通過測試，而不在 class header 中明確宣告 internal contract。

本次最終 tightening 決策是：

1. `HttpClient` 必須顯式繼承 `Client`
2. 這是 **internal implementation contract tightening**，不是 public API widening
3. reviewer 必須看到 nominal evidence，而不是只看到 `isinstance(client, Client)` 之類的 structural evidence

## Scope

- **In scope**
  - `src/mlops_async/transport/http_client.py` 的 class header
  - 與 nominal inheritance 直接相關的 contract tests
  - 與 nominal inheritance 直接相關的 reviewer acceptance criteria

- **Out of scope**
  - public facade
  - package-root re-export
  - auth / retry
  - `request()` / `request_json()` failure boundary 重談
  - 全 repo class inheritance cleanup

## What Stays

下列既有決策維持不變：

1. `HttpClient` 仍是 internal-only concrete client
2. concrete client 仍只放在 `src/mlops_async/transport/http_client.py`
3. `Client` 仍是 `src/mlops_async/core/client.py` 的 internal contract
4. 不新增 public export，不把 nominal inheritance 誤做成 public promotion

## What Must Be Rewritten

下列舊敘述或測試標準已不夠：

1. 「只要 `HttpClient` 在 structural typing 上滿足 `Client` 就足夠」
2. 「只驗證 `isinstance(client, Client)` 就算 nominal contract 成立」
3. 「只要 runtime-checkable protocol 沒報錯，就算 tightening 已落地」

## Why This Is Blocking

1. 若只接受 structural compatibility，未來 implementer 可能移除 `Client` 直接基類而不自知
2. 這會讓 internal transport boundary 的 nominal contract 再次變成隱性規則，而不是 repo-visible 規則
3. 本次 review 明確要求 `class HttpClient(Client): ...`，因此這不是偏好，而是 blocking requirement

## Acceptance Criteria Delta

### Must pass

1. `src/mlops_async/transport/http_client.py` 的 class header 為 `class HttpClient(Client):`
2. 測試明確驗證 nominal inheritance，例如：
   - `HttpClient.__bases__ == (Client,)`，或
   - `Client in HttpClient.__mro__`
3. 既有 structural compatibility 仍成立，但不再作為唯一證據
4. nominal inheritance 不引入 public export、public facade、或 root re-export

### Must fail

1. `HttpClient` 沒有直接或名義上繼承 `Client`
2. 測試只剩 `isinstance(client, Client)`，沒有 nominal evidence
3. 為了滿足 nominal inheritance 而把 `HttpClient` 提升成 package-root public API

## Reviewer Guidance

reviewer 應優先檢查：

1. `HttpClient` 的 class header 是否已明確寫成 nominal inheritance
2. nominal inheritance 證據是否來自 `__bases__` / `__mro__` 等明確檢查，而不是只靠 structural pass
3. 此 tightening 是否仍維持 internal-only 邊界

## Historical Retention Note

即使 parent plan 之後同步回補，本檔仍保留，作為這次 nominal inheritance tightening 的歷史差異紀錄。
