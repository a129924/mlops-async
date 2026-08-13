---
topic: mlops-async-client-facade
phase: plan-authoring
status: creator-in-progress
created: 2026-08-12
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# mlops-async-client-facade Step Tracking

> 已發布 baseline 是 PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d`。
> 本 tracker 只追蹤兩條新 action threads 的 pending correction；不可將 baseline 的
> 歷史 planning 或 publication 當作 correction validation/review/publish completed。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | resolved history at `9b51f95`; no future resolve |
| `PRRT_kwDOSTt_386YpagY` | transport doc | resolved history at `9b51f95`; no future resolve |

上述五條 thread 為已解決歷史，沒有 future resolve。本輪 pending correction 僅為
`PRRT_kwDOSTt_386YypkF`：concrete `HttpClient.aclose()` failure/cancellation 後必須保留
真實 cleanup retry，facade 不得將 underlying no-op retry 當作成功；及
`PRRT_kwDOSTt_386YypkJ`：README/architecture facade 現況敘述必須為繁體中文。

## Workflow Stages

- [X] plan-authoring — 原 topic artifacts 的歷史完成 gate；本次 correction plan 已更新。
- [X] plan-review — 原 topic 的獨立 approval 是歷史事實；本輪不重開 scope review。
- [X] tdd-test-authoring — lifecycle RED/regression tests 已完成並已作為 correction evidence。
- [X] implementation — `src/mlops_async/mlops_async_client.py`、
  `tests/unit/test_mlops_async_client.py` 與 `docs/standards/http-client-auth-boundary.md`
  的 correction 已完成。
- [X] tach-correction — 已完成 frozen root seven-target/transport two-target shape
  inspection 與 static evidence；本輪未改 `tach.toml`。
- [X] tdd-test-authoring — 已在 `tests/unit/transport/test_http_client.py` 補 concrete managed
  cleanup failure/cancellation 後真實 retry 的 RED/regression tests。
- [X] implementation — 已修改 `src/mlops_async/transport/http_client.py`，使 no-op retry 不得
  偽造 cleanup success；並已同步 `README.md` 與 `docs/ARCHITECTURE.md` 的繁體中文 facade 現況敘述。
- [X] full-validation — isolated ext4 correction snapshot 已通過 `uv sync --frozen`、full non-E2E
  `704 passed, 9 skipped, 1 deselected`、coverage `94.43%`、Ruff format/check、Pyright、Tach 與
  diff check。base `9b51f95` 加十個 correction files 的 manifest SHA-256 為
  `219b3593cb3213f035c728232d377eb2db55966b94ee967ba8532a3e755ce809`；transcript SHA-256 為
  `49487b86e22b2f31a189d9f8215d2c63e051acde6b7ec43603fc25e170c9a972`，temporary path 已刪除。
- [ ] implementation-review — 新 correction implementation-review evidence pending。
- [ ] code-review — 新 correction code-review evidence pending。
- [ ] pr-commit-and-fix — 待 independent implementation review 與 code review 均批准後，才可進行
  correction commit/push、GraphQL readback，並 resolve `PRRT_kwDOSTt_386YypkF` 與
  `PRRT_kwDOSTt_386YypkJ` 後再次 GraphQL readback；五條 historical threads 維持 resolved，
  不得再次 resolve。
- [ ] publish — 新 correction publication evidence pending；不含 merge/version/tag/release。

## Frozen Tach shape

本輪不得修改此 published baseline shape：root targets 依此精確順序為
`mlops_async.clients`、`mlops_async.core`、`mlops_async.transport`、
`mlops_async.clients.cas_tables`、`mlops_async.clients.job_execution`、
`mlops_async.clients.models`、`mlops_async.clients.projects`；transport targets
必須且僅為 `mlops_async.core`、`mlops_async.exceptions`。

## Implementation Steps

### 已完成的前輪 historical steps

- [X] 1. 已在 `src/mlops_async/mlops_async_client.py` 以 private in-progress shared task
  和 success-only closed state 修正 `aclose()`；close raise/cancellation 保持可 retry。
- [X] 2. 已以 shield 確保 concurrent/repeated callers 共享 one close operation，且 cancelled
  waiter 不取消 shared task；`__aexit__` 維持同一路徑。
- [X] 3. 已在 `tests/unit/test_mlops_async_client.py` 補 single-flight、success idempotence、
  failure retry、underlying cancellation retry、cancelled waiter isolation tests，並保留
  existing identity/lazy-auth/closed-transport coverage。
- [X] 4. 已在 `docs/standards/http-client-auth-boundary.md` 同步 facade 唯一 ownership、
  success-only closed/retry lifecycle 及 frozen Tach root/transport boundary。
- [X] 5. 已以 diff inspection 確認只改 authorized paths、Tach exact lists 未漂移，並完成
  focused tests、static checks 與 isolated ext4 full non-E2E validation。

### 本輪 correction steps

- [X] 6. 在 `src/mlops_async/transport/http_client.py` 以 managed cleanup 的真實成功決定
  concrete close state；failure/cancellation 後的 retry 必須再做 cleanup，no-op 回傳不得使
  facade 視為 closed。
- [X] 7. 在 `tests/unit/transport/test_http_client.py` 補 first cleanup raise、first cleanup
  cancellation、later real retry 與 no-op 不得偽造成功的 regression tests。
- [X] 8. 在 `README.md` 與 `docs/ARCHITECTURE.md` 寫入繁體中文 facade 現況敘述；保留
  canonical headings、fixed labels 與必要技術術語。
- [X] 9. 已在 isolated ext4 snapshot 以 focused facade/transport tests、full non-E2E、Ruff、Pyright、
  Tach 與 diff inspection 取得本輪 evidence；下一步送 independent implementation review、再送 code review。

## Review Gate

本輪 current transition 是 `needs-rework -> creator-in-progress`。原 main workflow 和
Python companion plan-review `approved` 是 historical evidence，不能勾選本輪
implementation review、code review 或 full-validation。Reviewer 必須檢查 close task
failure/cancellation path、concurrency tests、doc sync、Tach no-drift 及新 validation
transcripts，然後才可給新 verdict。

## Historical baseline

`ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d` 已推送且是 PR #70 head；這只標示
目前 published PR state。它不使本輪 review-fix 的 validation、reviews 或 correction
publish 完成，也不授權自行 resolve thread。
