---
topic: http-client-tls-trust
phase: plan-authoring
created: 2026-07-16
---

# http-client-tls-trust — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/http-client-tls-trust/http-client-tls-trust.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Implementer在 `src/mlops_async/transport/http_client.py` 將 constructor annotation改為 `bool | ssl.SSLContext`，並在所有 AsyncClient construction branch前加入固定 `TypeError` validation與合法值原樣傳遞。
- [X] 2. Implementer在 `tests/integration/viya_e2e_config.py` 加入 required `VIYA_E2E_TLS_MODE`、exact resolver、conditional `VIYA_E2E_CA_BUNDLE`、固定 warning/errors與 `ViyaE2EConfig.verify`。
- [X] 3. Implementer在 `tests/integration/test_viya_password_token_e2e.py` 將 hard-coded `verify=True` 改為 `verify=config.verify`，並保留 HTTP 200、token、expiry與 anti-fake-success assertions。
- [X] 4. Implementer執行 focused transport/config/password-token/client-credentials tests，確認 RED cases轉 GREEN；正式 evidence為 focused與auth共 `90 passed`。
- [X] 5. Implementer執行 targeted Pyright、Ruff與 bounded diff-check；正式 evidence為 targeted Pyright `0` errors、Ruff passed、diff-check passed，且未執行 live E2E。

## Post-implementation Workflow / Gates

- [X] Implementation review：獨立 Reviewer已使用 `python-implementation-review` 對照 plan完成審查，正式 verdict為 `approved`。
- [X] Code review：獨立 Reviewer已使用 `python-code-review` 完成審查，正式 verdict為 `approved`、zero blocking issues。
- [X] Pre-live non-E2E/static validation：Tester已在 code review後執行 non-E2E pytest、Ruff與 full configured Pyright；正式 evidence為 pytest `311 passed / 9 skipped / 1 deselected`、Ruff all passed、Pyright `0 errors / 0 warnings`；未執行 network connection、live E2E或 secret read。
- [X] Rework routing（conditional）— completed/not required：implementation review與code review均 `approved`且 zero blocking issues，因此本輪不需派 Implementer rework。
- [X] Human config provision：來源為最新 human confirmation：`strict config 已確認，授權重新執行一次 framework live E2E`。歷史 failures保留；secret file保持 opaque，agent未讀取、未列印、未diff、未stage。
- [X] Live E2E：latest authorized framework live為 exit `0`、`1 passed / 320 deselected`，驗證 exact HTTP 200、nonempty token、positive expiry與 fixed insecure warning。Exact statement：`live password-token E2E passed with TLS verification explicitly disabled`。此結果不宣稱 TLS trust verified；pre/post inventory `unexpected=0`，且無 retry、fallback、mode switch、mock或skip。Secret保持 opaque。
- [ ] Publish：全部 gates通過後，Implementer bounded commit並push `fix/andrew/http-client-tls-trust`，不得納入 secret或scope外檔案。
- [ ] Merge：Implementer將 fix branch merge並push到 `test/andrew/viya-password-token-e2e`，不得 merge到 `dev`。
- [ ] Post-merge validation：Tester在 E2E branch merge result重跑 non-E2E、Ruff、Pyright與 explicit insecure live E2E。
- [ ] Finalization：Dispatcher彙整 review與validation evidence，若無 blocker則交 human check；不執行 release或 `dev` merge。
