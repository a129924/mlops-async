# TokenManager 測試嚴謹度補強需求基準

## Status

- **FROZEN**（已由 analysis-only topic 升級為 implementation topic，用於關閉已識別的三個測試缺口）

## Problem Statement

- 使用者已接受先前 analysis verdict 的缺口判定，現在要在**不擴大 scope**的前提下，補齊 `TokenManager` 測試證據，關閉三個已識別 gaps，並把 analysis artifacts 同步回當前 repo 狀態。

## Actors / Boundaries

- **Primary actor**: executor / reviewer
- **In-scope implementation files**:
  - `tests/unit/core/test_token_manager.py`
  - `analysis/token-manager-test-rigor-review/testcase-inventory.md`
  - `analysis/token-manager-test-rigor-review/rigor-matrix.md`
  - `analysis/token-manager-test-rigor-review/verdict.md`
  - `analysis/token-manager-test-rigor-review/technical-spec.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.plan.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.step.md`
  - `plan/token-manager-test-rigor-review/token-manager-test-rigor-review.spec.md`
- **Contingency-only implementation file**:
  - `src/mlops_async/core/auth.py`（僅當新測試揭露既有行為與分析結論矛盾時，才允許最小修補）
- **Inspect-only related files**:
  - `tests/unit/core/test_token_storage.py`
  - `tests/unit/core/test_auth_provider.py`
  - `tests/unit/core/test_auth_contract.py`

## Measurable Requirements

| ID | Actor | Condition | Observable outcome | Metric / decision rule | Failure meaning |
| --- | --- | --- | --- | --- | --- |
| IR-1 | Executor | 關閉 `C-004-auth-exception-pass-through` | 新增 `AuthException` 直接透傳測試 | 測試必須驗證 `exc_info.value is original_error`、`__cause__ is None`，且既有 token state 不變 | 仍可能誤把 `AuthException` 包裝成 `TokenFetchException` |
| IR-2 | Executor | 關閉 `C-005-custom-expiry-skew-at-manager-level` | 新增 manager-level custom skew 決策測試 | 對同一 near-expiry token，`expiry_skew=0` 必須 reuse，`expiry_skew=5 minutes` 必須 refresh | 無法證明 `TokenManager` 真的使用自訂 skew |
| IR-3 | Executor | 關閉 `C-006-empty-storage-concurrency-fetch-dedup` | 新增 empty-storage 高併發 fetch 去重測試 | 10 個 concurrent waiters 僅觸發 1 次 fetch、0 次 refresh，且都拿到相同 token | 無法證明 fetch path 的併發協調正確 |
| IR-4 | Executor | 完成 gap closure 實作 | 變更範圍維持可審查 | 若新測試直接通過，`src/**` diff 必須為 0；若失敗，只允許最小修補 `src/mlops_async/core/auth.py` 且不得改 public contract | scope creep 或偷改非必要檔案 |
| IR-5 | Reviewer | human check 或 workflow review | analysis artifacts 可重現當前結論 | inventory 要納入新測試；matrix/verdict 要保留 baseline audit trail，並明示 gap 已由具體測試關閉 | analysis 與 repo 現況脫節，review 無法重現 |

## Assumptions

1. `src/mlops_async/core/auth.py` 現況理應已支援三個缺口，只是缺測試證據。
2. 本 topic 以 tests-first 關閉 rigor gaps；若新測試直接 GREEN，屬 characterization / coverage-closure success，不視為 workflow 錯誤。
3. 若新測試揭露實際行為與先前 analysis 矛盾，可在同一 topic 內做最小 production 修補，但僅限 `src/mlops_async/core/auth.py`。

## Non-goals

1. 不修改 `tests/unit/core/test_token_storage.py`、`test_auth_provider.py`、`test_auth_contract.py`。
2. 不做 `TokenManager` 廣義重構、API 擴張或 async boundary redesign。
3. 不執行 commit、push、PR、merge、release。

## Contradictions surfaced

1. **tests-first** vs **既有 production 可能已正確**
   - 衝突點：新測試可能直接 GREEN，而不是典型 TDD RED。
   - 決議：本 topic 將其視為 rigor coverage closure；通過條件是行為證據齊備，而非一定先 RED。
2. **保持原 topic** vs **analysis-only baseline 已寫死不改碼**
   - 衝突點：若只改 plan，不改 requirements，workflow 會持續把 topic 判成 analysis-only。
   - 決議：同步更新 requirements / technical-spec / plan / spec / step，讓 implementation contract 一致。

## Extreme-boundary checks

1. **No unrelated drift**: 若 diff 出現 `tests/unit/core/test_token_storage.py`、`test_auth_provider.py`、`test_auth_contract.py` 內容變更，視為超出 topic 邊界。
2. **Contradicting production behavior**: 若任一新測試失敗且需要超出 `src/mlops_async/core/auth.py` 的修補，必須停止自動擴展。
3. **Partial closure**: 若只關掉部分 gaps，`verdict.md` 不得宣告「足夠嚴謹」。
4. **Audit trail loss**: 若更新 matrix / verdict 時抹掉 baseline gap 記錄，視為 evidence regression。

## Blockers

- 無硬阻塞；可進入 implementation workflow。
