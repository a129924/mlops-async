---
topic: mlops-async-client-facade
phase: plan-authoring
status: creator-in-progress
created: 2026-08-12
pr_baseline: ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d
---

# mlops-async-client-facade Step Tracking

> 已發布 baseline 是 PR #70 head `ed29e8370d2f945e1b0f754ef70bd314a5f8bc0d`。
> 本 tracker 只追蹤五條 action threads 的 pending correction；不可將 baseline 的
> 歷史 planning 或 publication 當作 correction validation/review/publish completed。

## PR #70 thread traceability

| Thread ID | 已實作或待交接的修正範圍 | Handoff trace link |
| --- | --- | --- |
| `PRRT_kwDOSTt_386YpZ_Q` | close failure/cancel retry | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 implementation handoff |
| `PRRT_kwDOSTt_386Ypaf_` | shared task/shield concurrency | `src/mlops_async/mlops_async_client.py` 與 `tests/unit/test_mlops_async_client.py` 的 implementation handoff |
| `PRRT_kwDOSTt_386Ypaf3` | 繁中 artifacts | 六份 topic artifacts 的 correction evidence |
| `PRRT_kwDOSTt_386YpagN` | workflow evidence | 六份 topic artifacts 的 workflow/evidence handoff |
| `PRRT_kwDOSTt_386YpagY` | transport doc | `docs/standards/http-client-auth-boundary.md` 的文件 handoff |

上述五條 threads 全部仍未 resolved；本表僅補正可追溯性，不勾選任何 stage，且 correction validation/review/publish 仍為 pending。

## Workflow Stages

- [X] plan-authoring — 原 topic artifacts 的歷史完成 gate；本次 correction plan 已更新。
- [X] plan-review — 原 topic 的獨立 approval 是歷史事實；本輪不重開 scope review。
- [X] tdd-test-authoring — lifecycle RED/regression tests 已完成並已作為 correction evidence。
- [X] implementation — `src/mlops_async/mlops_async_client.py`、
  `tests/unit/test_mlops_async_client.py` 與 `docs/standards/http-client-auth-boundary.md`
  的 correction 已完成。
- [X] tach-correction — 已完成 frozen root seven-target/transport two-target shape
  inspection 與 static evidence；本輪未改 `tach.toml`。
- [ ] full-validation — focused/static evidence 已完成；完整 non-E2E validation 仍因 WSL
  environment exception pending。
- [ ] implementation-review — correction implementation-review evidence pending。
- [ ] code-review — correction code-review evidence pending。
- [ ] publish — correction commit/push/readback，以及五個已 ADDRESS PR threads 的
  GraphQL resolve/readback pending；不含 merge/version/tag/release。

## Frozen Tach shape

本輪不得修改此 published baseline shape：root targets 依此精確順序為
`mlops_async.clients`、`mlops_async.core`、`mlops_async.transport`、
`mlops_async.clients.cas_tables`、`mlops_async.clients.job_execution`、
`mlops_async.clients.models`、`mlops_async.clients.projects`；transport targets
必須且僅為 `mlops_async.core`、`mlops_async.exceptions`。

## Implementation Steps

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
  focused tests 與 static checks；完整 non-E2E validation 仍因 WSL environment exception
  pending，維持於 `full-validation` stage。

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
