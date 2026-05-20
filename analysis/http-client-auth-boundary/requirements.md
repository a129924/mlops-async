# http-client-auth-boundary requirements baseline

## Status

- `FROZEN` — ready for technical translation

## Problem Statement

`mlops-async` 需要一個可預期、可測試、且不把 auth lifecycle 混進 transport 的 internal auth/request composition baseline，讓 library consumer 在未來使用 `MlopsAsyncClient` 與各 domain clients 時，不需要自行猜測 `Authorization` header、token refresh、併發 refresh、與 failure path 的行為。

## Actors and Permission Boundaries

1. **Primary actor — library consumer developer**
   - 使用 `mlops-async` 撰寫應用程式或腳本。
   - 需要可預期的 request/auth 行為，不應直接接觸 token lifecycle internals。
2. **Secondary actor — internal domain client author**
   - 在 repo 內撰寫 domain client / namespace code。
   - 只能依賴 `Requester` request boundary，不應直接耦合 `TokenManager`、`TokenFetcher` 或 raw `HttpClient` auth behavior。

## Measurable Requirements

| ID | Actor | Condition | Observable Outcome | Metric / Decision Rule | Failure Meaning |
| --- | --- | --- | --- | --- | --- |
| BR-1 | Library consumer developer | 使用已配置 `AuthProvider` 的 domain call | request 在送出前只經過單一 request composition layer，且 transport 只收到 final request data | 文件與單元測試可共同證明 `Requester` 是唯一 request composition layer，`HttpClient` 只接收 final `method/path/headers/body/options` | 使用者無法預期 auth header 在哪一層被組裝，後續 auth bug 難以定位 |
| BR-2 | Library consumer developer | 已配置 `AuthProvider`，但 caller 仍傳入任意大小寫的 `Authorization` header | request 在送出前被拒絕，且不進入 domain request transport | 單元測試需覆蓋 `Authorization` / `authorization` / `AUTHORIZATION` 等 case-insensitive 衝突，並驗證 `HttpClient` 未被呼叫 | caller token 與 managed token 語意衝突，造成使用舊 token 或 silent override |
| BR-3 | Library consumer developer | 未配置 `AuthProvider` | caller 可透過 per-request headers 傳入 `Authorization` 作為 low-level / test 用途 | 單元測試可驗證在無 `AuthProvider` 情境下，`Requester` 允許 caller `Authorization` 通過 | 無法提供低階測試或特殊情境下的 direct auth header usage |
| BR-4 | Library consumer developer | token 具 expiry metadata，且 request 前需要判斷是否可直接使用 | token expiry 規則可預測且一致 | `AccessToken` expiry 判斷需支援 configurable skew，預設 60 秒；`now + skew >= expires_at` 視為過期 | request 前 refresh 行為不一致，造成非預期過期或過早 refresh |
| BR-5 | Library consumer developer | 同一個 shared `TokenManager` 下，至少 10 個 concurrent coroutines 同時遇到 expired/missing token | 最多只發生一次 refresh/fetch；其他 coroutine 等待並重用更新後 token | 單元測試以至少 10 個 concurrent coroutines 驗證 shared manager 只 refresh/fetch 一次 | 發生 refresh storm / race condition，造成重複 token calls 或不一致 token state |
| BR-6 | Library consumer developer | token fetch/refresh dependency 不可用、失敗、或回傳錯誤 | 呼叫端收到 auth-layer failure，而不是 transport-layer failure；domain request transport 不被呼叫 | 單元測試需驗證 failure surface 為 auth-layer exception，且 domain request `HttpClient` 未執行 | 使用者無法判斷錯誤發生在 auth lifecycle 還是 API transport，導致錯誤恢復策略錯誤 |
| BR-7 | Library consumer developer | refresh/fetch 過程中失敗或 coroutine 被取消 | 既有 token state 保留，不清空、不寫入 partial token | 單元測試需驗證 refresh success 之前不覆寫 `TokenStorage`；failure/cancellation 後 previous token 仍存在 | 失敗中的 refresh 汙染 token state，導致後續請求失去最後可用 token |
| BR-8 | Internal domain client author | 撰寫新的 domain client 或 namespace adapter | domain client 只依賴 `Requester` request boundary | repo-visible 文件與測試可共同證明依賴方向為 Domain client -> `Requester` -> `HttpClient` (+ optional `AuthProvider`) | 內部模組邊界漂移，形成 circular dependency 或 transport/auth scope creep |

## Assumptions

1. 目前主要使用情境是單一 Python process / 單一 event loop；本 baseline 不處理 distributed locking。
2. 本 topic 的成功訊號以 repo-visible 文件與單元測試為主，不要求 runtime demo。
3. 未來 public `MlopsAsyncClient` 會是 composition root，但本 baseline 不要求在此 topic 宣告 stable public API。

## Non-goals

1. 不實作完整 OAuth flow。
2. 不實作 credential persistence 或跨 process token cache。
3. 不實作 401 auto refresh/retry。
4. 不處理 upload/download/streaming。
5. 不在本 topic 決定 stable public facade release timing。

## Extreme-Boundary Checks

1. **No network / degraded token dependency**
   - 若 token endpoint 失敗或不可用，必須 surface auth-layer failure，且不得繼續呼叫 domain request transport。
2. **Wrong actor / wrong boundary**
   - 若 internal domain client author 直接繞過 `Requester` 依賴 auth lifecycle internals，視為違反 baseline，而不是可接受變體。
3. **Interrupted / partial completion**
   - refresh/fetch 成功前不得覆寫 `TokenStorage`；失敗或 cancellation 後保留 previous token state。
4. **Lowest-volume condition**
   - 單一 request 且 token 未過期時，不得觸發 refresh/fetch。
5. **Peak-volume condition**
   - 至少 10 個 concurrent coroutines 同時遇到 expired/missing token 時，shared manager 最多 refresh/fetch 一次。

## Contradiction Log

- None. 先前對於 `Authorization` collision policy、`Requester` 是否為唯一 composition layer、以及 `TokenManager` 是否擁有 refresh concurrency control 的分歧已在本 baseline 中明確決議。

## Blockers

- None for this business baseline.

## Handoff Boundary for Technical Translation

此 baseline 已凍結下列需求，不需要在 technical translation 階段重新發明：

1. `HttpClient` 為 pure transport。
2. `Requester` 為唯一 request composition layer。
3. `AuthProvider` 保持薄。
4. `TokenManager` 擁有 token lifecycle 與 in-process concurrency control。
5. `TokenStorage` 為 dumb storage。
6. `TokenFetcher` 為 token endpoint collaborator，且只走 raw `HttpClient`。
