# http-client TLS trust 與使用者控制 Plan

> 語意警告：`analysis/http-client-tls-trust/requirements.md` 與
> `analysis/http-client-tls-trust/technical-spec.md` 皆不存在。本 plan 依 human-locked
> decisions、已核准的 verify-control replacement、locked base ref 與目前 repository
> source truth authoring；不存在可優先套用的 analysis layer。

D1 verdict：

```json
{"verdict":"non-trivial","reason":"變更 HttpClient TLS verify 型別契約、E2E config schema、錯誤契約與 live acceptance mode，涉及多檔案與 framework-facing behavior。"}
```

## Goal / Outcome

### Goal

讓 framework 使用者明確控制 `HttpClient` 的 TLS verification：安全預設維持
`True`，並支援 explicit `True`、explicit `False` 與 caller-provided
`ssl.SSLContext`。公司內部自建 Viya 環境可透過 Git-ignored config 明確選擇
`insecure` mode 執行真實 password-token E2E；該成功只證明 auth live contract
在明確停用 TLS verification 下成立，不宣稱 TLS trust 已驗證。

## Scope

### In-Scope

- 將 `HttpClient.__init__.verify` 定義為 `bool | ssl.SSLContext = True`。
- 保留 explicit bool 行為並支援 SSLContext identity propagation。
- 在建立 `httpx.AsyncClient` 前拒絕 `str`、`Path` 與其他 unsupported type。
- E2E config 新增 required `VIYA_E2E_TLS_MODE`，只接受 exact lowercase
  `system|insecure|ca_bundle`。
- `ViyaE2EConfig` 新增 `verify: bool | ssl.SSLContext`。
- Mode mapping：`system -> True`、`insecure -> False`、`ca_bundle -> SSLContext`。
- `insecure` mode 每次 loader invocation 發出一次固定 `RuntimeWarning`。
- Live E2E 改為 `HttpClient(..., verify=config.verify)`。
- 以 internal `insecure` mode 執行真實 password-token E2E。
- 新增 transport 與 E2E config contract tests。
- 通過獨立 implementation review 與 code review 後 merge 回 E2E feature branch。

### Out-Of-Scope

- 不建立 diagnosis-first gate或 temporary diagnostic test。
- 不要求先分類 `SSLCertVerificationError`。
- 不把公司環境以 `verify=True` 失敗視為 implementation blocker。
- 不自動將 `True` fallback 為 `False`。
- 不把 internal `insecure` E2E pass 宣稱為 TLS-verifying success。
- 不要求 trusted-CA live success 作為本 topic completion gate。
- 不修改 password-grant form body、endpoint、token schema、refresh-token 或
  client-credentials flow。
- 不新增公開 `AuthClient`、dependency 或 production TLS environment discovery。
- 不修改 production `HttpTransportException` contract、async lifecycle、retry、
  timeout、proxy、DNS、TCP 或 VPN routing。
- 不修改 `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`，不建立 release、
  tag或 merge 到 `dev`。

## Locked Decisions

### Non-Goal

本 topic 不會自行替使用者判定何時應停用 TLS verification，也不會把公司內部
`insecure` acceptance 擴張成一般 framework 的安全建議。

- Base ref：`origin/test/andrew/viya-password-token-e2e`。
- Base SHA：`cef7092f66c07af707c29738e652c15985f91676`。
- Fix branch：`fix/andrew/http-client-tls-trust`。
- Managed worktree：`managed topic worktree`。
- Merge target：`test/andrew/viya-password-token-e2e`，不得直接 merge 到 `dev`。
- Worktree 已先由 exact base SHA 建立；plan authoring 發生於 prepared fix worktree，
  不得重新建立或切換 worktree/branch。
- 本 topic 為 non-stable topic；stable-library/release surfaces 明確不變。
- Production contract：`verify: bool | ssl.SSLContext = True`。
- Default 維持 `True`；explicit `True`／`False` 原樣傳給 `httpx.AsyncClient`。
- SSLContext 以相同 object identity 傳遞；`HttpClient` 不複製、不修改、不關閉。
- Unsupported type 在任何 `httpx.AsyncClient` 建立前 raise
  `TypeError("verify must be bool or ssl.SSLContext")`。
- 不允許 implicit fallback、path/string coercion 或 sasctl TLS environment discovery。
- `VIYA_E2E_TLS_MODE` 是 `config/.env.test` required key，沒有 default；只接受
  exact lowercase `system`、`insecure`、`ca_bundle`，不 trim、不 normalize。
- `system` 解析為 `True`。
- `insecure` 解析為 `False`，每次 loader invocation 發出一次：
  `RuntimeWarning("Viya E2E is running with TLS verification explicitly disabled")`。
- `ca_bundle` 要求 non-blank `VIYA_E2E_CA_BUNDLE`，使用
  `ssl.create_default_context(cafile=ca_bundle)` 建立 SSLContext。
- `system`／`insecure` 若 CA key 是 non-blank value 必須 fail；blank 視為未提供。
- 固定 config errors：
  - `ViyaE2EConfigError("Viya E2E TLS mode is required")`
  - `ViyaE2EConfigError("Viya E2E TLS mode is invalid")`
  - `ViyaE2EConfigError("Viya E2E CA bundle is required")`
  - `ViyaE2EConfigError("Viya E2E CA bundle could not be loaded")`
  - `ViyaE2EConfigError("Viya E2E CA bundle is only valid in ca_bundle mode")`
- CA load 的 `OSError`（包含 `ssl.SSLError`）轉譯為固定 load error並
  `raise ... from exc`；公開 message 不得含 path、config value 或 cause message。
- `RUN_VIYA_E2E=1` 維持唯一 process opt-in；loader 不讀取或依它分支。
- Internal acceptance 使用 `VIYA_E2E_TLS_MODE=insecure`。
- Internal success 的唯一允許結論：
  `live password-token E2E passed with TLS verification explicitly disabled`。
- 只有 `system` 或 `ca_bundle` 的真實成功才可宣稱 TLS-verifying E2E passed。
- Trusted-CA live success不是本 topic completion gate；unit contract仍須完整覆蓋。

## Boundaries / Exclusions

- Plan-Creator只建立本 topic 的 plan/spec/step artifacts。
- Plan-Reviewer核准後才可派 Tester建立 RED tests。
- Tester只建立或執行 tests，不修改 production implementation。
- RED evidence完成後才可派獨立 Implementer修改 production與 E2E support。
- `python-implementation-review` 必須先於 `python-code-review`。
- Reviewer rework一律交回獨立 Implementer，不由 Dispatcher或 Reviewer實作。
- `tests/conftest.py` 維持 read-only；`RUN_VIYA_E2E` hook contract不變。
- `config/.env.test` 由 human安全 provision；agent不得讀取、列印、stage、copy或提交。
- `verify=False` 只能由 framework caller或 explicit `insecure` mode選擇；library不得自行降級。
- Internal `insecure` E2E仍須使用真實 network，驗證 exact HTTP 200、nonempty
  access token與 positive expiry；transport/config failure必須 hard fail，不得 mock、
  fallback或 skip。
- Evidence不得輸出 URL、credential、header、token、response body、config value、
  CA path、PEM content或 raw exception message。
- 若需修改 `Artifact Paths` 以外的 tracked file，停止並交 Dispatcher分類 scope drift。

## Status / Allowed Transitions

- **Current workflow gate**：`Publish preflight`；最新 authorized framework live已成功，
  下一步先由 Explorer唯讀確認 bounded publish safety。
- **Planning review state**：`review-ready`；本次只同步已完成 phases與 current gate，交
  Plan-Reviewer確認 workflow metadata。
- **Completed phases**：plan-review、TDD test authoring、bounded implementation、
  implementation review、code review與 pre-live non-E2E/static validation皆已完成；
  implementation review與code review正式 verdict均為 `approved`且 zero blocking issues。
- **Next execution role**：Explorer執行 publish preflight；preflight通過前不得 commit、
  push或 merge。
- **Worktree-first timing**：exact-SHA branch/worktree preparation、plan materialization、
  plan-review、TDD與 bounded implementation皆已在 prepared worktree完成；本次
  `creator-in-progress`只修正 implementation-review handoff metadata，完成即回到
  `review-ready`並交 Reviewer。
- **Allowed transitions**：
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes：

- Plan-Reviewer approval後先派 Tester建立 transport/config RED tests，並建立
  `plan/http-client-tls-trust/http-client-tls-trust.tdd-test-authoring.yaml` 記錄
  machine-readable verdict、plan-to-test mapping與 RED evidence。
- RED tests後派 Implementer進行 bounded implementation。
- Review順序固定為 implementation review後 code review。
- `blocked`／`human-check` 是 Dispatcher routing result，不是 canonical status。

## Artifact Paths

### ReadOnly

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Repo governance | `AGENTS.md` | Repository Governance | authority與scope boundary |
| Workflow contract | `plan/agent-handoff-workflow.md` | Repository Workflow | canonical transitions |
| Topic-plan contract | `plan/topic-plan-contract.md` | Repository Workflow | canonical plan shape |
| Request options | `src/mlops_async/core/request_options.py` | Production | timeout/caller inspection |
| Password endpoint | `src/mlops_async/core/token_endpoint/password.py` | Production | transport caller inspection |
| E2E opt-in hook | `tests/conftest.py` | Test Infrastructure | 保留 process opt-in contract |
| Secret config | `config/.env.test` | Human | Git-ignored live input；不得讀取或提交 |

### Written

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/http-client-tls-trust/http-client-tls-trust.plan.md` | Plan-Creator | execution contract |
| Specification | `plan/http-client-tls-trust/http-client-tls-trust.spec.md` | Plan-Creator | acceptance contract |
| Step tracker | `plan/http-client-tls-trust/http-client-tls-trust.step.md` | Plan-Creator及後續執行角色 | workflow與implementation tracking |
| TDD authoring record | `plan/http-client-tls-trust/http-client-tls-trust.tdd-test-authoring.yaml` | Tester | machine-readable `python-tdd-test-authoring` verdict、plan-to-test mapping與 RED evidence |
| HTTP client | `src/mlops_async/transport/http_client.py` | Implementer | framework TLS verify contract |
| Transport tests | `tests/unit/transport/test_http_client.py` | Tester | verify RED/contract tests |
| E2E config | `tests/integration/viya_e2e_config.py` | Implementer | exact TLS mode resolution |
| Live E2E | `tests/integration/test_viya_password_token_e2e.py` | Implementer | 使用 `config.verify` |
| Config tests | `tests/unit/integration/test_viya_e2e_config.py` | Tester | mode/warning/CA/error tests |

### Deleted

None。不得新增或刪除 temporary diagnostic test；`.write-test` 不是 topic artifact，
已在 plan authoring時移除。

`README.md`、`VERSION`、`pyproject.toml`、`uv.lock` 與
`.github/copilot-instructions.md` 均不修改。若後續工作超出 Written paths，停止並
交 Dispatcher處理，不得自行擴張。

## Implementation Steps

1. Implementer在 `src/mlops_async/transport/http_client.py` 將 constructor annotation
   改為 `bool | ssl.SSLContext`，並在所有 AsyncClient construction branch前加入固定
   `TypeError` validation與合法值原樣傳遞。
2. Implementer在 `tests/integration/viya_e2e_config.py` 加入 required
   `VIYA_E2E_TLS_MODE`、exact resolver、conditional `VIYA_E2E_CA_BUNDLE`、固定 warning/
   errors與 `ViyaE2EConfig.verify`。
3. Implementer在 `tests/integration/test_viya_password_token_e2e.py` 將 hard-coded
   `verify=True` 改為 `verify=config.verify`，並保留 HTTP 200、token、expiry與
   anti-fake-success assertions。
4. Implementer執行 focused transport/config/password-token/client-credentials tests，
   確認 RED cases轉 GREEN；正式 evidence為 focused與auth共 `90 passed`。
5. Implementer執行 targeted Pyright、Ruff與 bounded diff-check；正式 evidence為
   targeted Pyright `0` errors、Ruff passed、diff-check passed，且未執行 live E2E。

### Post-implementation workflow / gates

- **Implementation review — completed**：獨立 Reviewer已使用
  `python-implementation-review` 對照 plan完成審查，正式 verdict為 `approved`。
- **Code review — completed**：獨立 Reviewer已使用 `python-code-review` 完成審查，
  正式 verdict為 `approved`、zero blocking issues。
- **Pre-live non-E2E/static validation — completed**：Tester已在 code review後執行
  non-E2E pytest、Ruff與 full configured Pyright；正式 evidence為 pytest
  `311 passed / 9 skipped / 1 deselected`、Ruff all passed、Pyright
  `0 errors / 0 warnings`。此 evidence不包含 network connection、live E2E或 secret read。
- **Rework routing — completed/not required**：implementation review與code review均
  `approved`且 zero blocking issues，因此本輪不需派 Implementer rework。
- **Human config provision — completed**：來源為最新 human confirmation：
  `strict config 已確認，授權重新執行一次 framework live E2E`。歷史 failures保留；
  secret file保持 opaque，agent未讀取、未列印、未diff、未stage。
- **Live E2E — completed**：latest authorized framework live為 exit `0`、
  `1 passed / 320 deselected`，驗證 exact HTTP 200、nonempty token、positive expiry與
  fixed insecure warning。Exact statement：
  `live password-token E2E passed with TLS verification explicitly disabled`。此結果不宣稱
  TLS trust verified；pre/post inventory `unexpected=0`，且無 retry、fallback、mode switch、
  mock或skip。Secret保持 opaque。
- **Publish — pending**：全部 gates通過後，Implementer bounded commit並push
  `fix/andrew/http-client-tls-trust`，不得納入 secret或scope外檔案。
- **Merge — pending**：Implementer將 fix branch merge並push到
  `test/andrew/viya-password-token-e2e`，不得 merge到 `dev`。
- **Post-merge validation — pending**：Tester在 E2E branch merge result重跑 non-E2E、
  Ruff、Pyright與 explicit insecure live E2E。
- **Finalization — pending**：Dispatcher彙整 review與validation evidence，若無 blocker
  則交 human check；不執行 release或 `dev` merge。

## Validation / Acceptance Checks

- Branch為 `fix/andrew/http-client-tls-trust`，HEAD與 locked base SHA一致，managed
  worktree path正確。
- `.env.test` 被 Git ignore且未 staged、未讀取、未輸出。
- `HttpClient` default仍為 `True`；explicit bool原樣傳遞。
- SSLContext以相同 identity傳遞且不由 `HttpClient`管理 lifecycle。
- Invalid verify type在 AsyncClient建立前得到固定 `TypeError`。
- 沒有 `True -> False` fallback、path coercion或隱式 environment discovery。
- TLS mode只接受 exact lowercase三值；`insecure`發出 exact warning並產生 `False`。
- `system`產生 `True`；`ca_bundle`只在 valid CA key時建立 SSLContext。
- CA config errors固定且不洩漏 path/value/raw cause；load error保留 exception chaining。
- Loader不讀 process `RUN_VIYA_E2E`；pytest hook仍是唯一 opt-in owner。
- Live test使用 `config.verify`並維持真實 HTTP 200、token與expiry contract。
- Internal insecure結果只使用限定結論，不標示 TLS verified。
- Trusted-CA live success不作 completion gate。
- Stable-library/release surfaces未修改。

### TestCase

- Happy path：default/explicit bool、SSLContext identity、三種 TLS mode與 internal
  insecure live E2E成功。
- Invalid input：unsupported verify type、missing/blank/invalid mode、missing CA、
  non-ca mode提供CA、CA load failure。
- Edge case：blank CA在 system/insecure視為未提供、mode不 trim/normalize、warning每次
  loader invocation一次、messages不含敏感值、loader不讀 process opt-in。
- Regression：transport request/status/JSON/timeout、password-token、client-credentials、
  non-E2E suite、Ruff與Pyright。
- Backward compatibility：omitted verify仍為 `True`、explicit bool不變、一般 pytest
  run skip live E2E、未 opt-in live marker仍fail、production exception contract不變。

## Reviewer Handoff

```json
{"verdict":"approved|needs-rework","blocking_issues":[],"copilot_feedback_triage":{"ADDRESS":[],"DISCUSS":[],"SKIP":[]}}
```

## Post-merge / release actions

- Fix branch只 merge到 `test/andrew/viya-password-token-e2e`。
- Merge後重跑 non-E2E、Ruff、Pyright與 internal insecure E2E。
- 不 merge `dev`，不修改 stable-library surfaces，不建立 tag或 release。
- Evidence handoff後由 Dispatcher交 human check；本 topic在 E2E branch驗證完成後停止。

## Open Questions / Unresolved Items

None。

---

# Python Implementation Contract

## Goal

讓 framework 使用者透過 `HttpClient.verify` 明確控制 TLS verification；E2E config以
無 fallback的 `system|insecure|ca_bundle` mode解析成 `bool | ssl.SSLContext`。公司
內部 acceptance以 explicit `insecure` mode完成真實 password-token E2E，但不宣稱
TLS trust已驗證。

## Non-goals

- 不新增 diagnosis-first gate或 temporary diagnostic。
- 不將公司環境 `verify=True` 失敗視為 blocker。
- 不自動 fallback為 `False`或接受 path/string作為 production verify。
- 不隱式讀取 sasctl TLS environment variables。
- 不修改其他 auth flows、async boundary、client lifecycle、concurrency、cancellation、
  retry、timeout或 production transport exception。
- 不新增 dependency、stable-library或release change。
- 不要求 trusted-CA live pass。

## Current Context

- `src/mlops_async/transport/http_client.py` 現有 constructor使用安全 default
  `verify=True`，尚未凍結 SSLContext與 invalid type contract。
- `tests/integration/test_viya_password_token_e2e.py` 目前 hard-code `verify=True`。
- `tests/integration/viya_e2e_config.py` 尚無 TLS mode或 resolved verify value。
- `RUN_VIYA_E2E=1` 由 `tests/conftest.py` pytest hook管理。
- 公司內部自建環境預期使用 explicit `insecure`，因此 `verify=True` live failure本身
  不阻擋此 topic。

## Requirements

1. `HttpClient.verify` contract是 `bool | ssl.SSLContext = True`。
2. 所有合法值原樣傳至每個 `httpx.AsyncClient` construction branch。
3. Unsupported type在任何 client建立前raise固定 `TypeError`。
4. `VIYA_E2E_TLS_MODE` required且只接受 exact lowercase modes。
5. `system`解析為 `True`；`insecure`解析為 `False`並發出 exact warning。
6. `ca_bundle`要求 CA key並以 `ssl.create_default_context(cafile=...)` 建立 context。
7. `system/insecure` 的 non-blank CA value fail-fast；blank視為未提供。
8. TLS config errors使用 Locked Decisions中的固定 messages。
9. Loader不讀 process opt-in；live test使用 `config.verify`。
10. Internal E2E必須真實驗證 HTTP 200、nonempty token與positive expiry。
11. Insecure success不得標示為 TLS-verifying；trusted-CA live pass不是 completion gate。
12. Unit tests覆蓋所有 modes、errors、warning、identity與backward compatibility。
13. Production exception、async ownership、timeouts與其他 auth flows維持不變。

## Decisions

- Async-planning status: exempt — cite exemption evidence: 本 topic只在同步 constructor
  驗證 TLS verify value，並在同步 E2E config loader解析 mode；不修改 async boundary、
  AsyncClient ownership/closure、resource lifecycle、concurrency、failure propagation、
  cancellation、retry或 timeout。
- Module/package placement：production change只位於
  `src/mlops_async/transport/http_client.py`；E2E trust resolution留在既有 test support。
- New public API：否；不新增 public symbol。
- Interface changes：是；`HttpClient.__init__.verify` 擴充為
  `bool | ssl.SSLContext`，private `ViyaE2EConfig` 新增同型別 `verify`。
- Breaking changes allowed：否；既有 omitted/explicit bool behavior必須維持。
- New dependencies：否；只使用 Python `ssl` standard library。
- Error handling strategy：unsupported production value raise固定 `TypeError`；E2E mode與
  CA problems raise固定 `ViyaE2EConfigError`；CA load failure保留 chaining但不公開 raw
  cause message。
- Typing strategy：strict fully typed；不使用 `Any`、fallback cast、path/string coercion或
  untyped helper。

## Public Contract / API Changes

`HttpClient` constructor contract變更為：

```python
verify: bool | ssl.SSLContext = True
```

- Default為 `True`；explicit bool原樣傳遞。
- SSLContext以相同 object identity傳遞；`HttpClient`不修改、不複製、不關閉。
- Unsupported type不轉換、不fallback，並在任何 AsyncClient建立前raise固定
  `TypeError("verify must be bool or ssl.SSLContext")`。
- Production request與`HttpTransportException` contracts不變。

E2E private config新增：

```python
verify: bool | ssl.SSLContext
```

- `system -> True`
- `insecure -> False`加固定 warning
- `ca_bundle -> ssl.SSLContext`
- 無 implicit default、normalization或fallback。

## Affected Files / Modules

Likely affected files:

- `src/mlops_async/transport/http_client.py`
- `tests/unit/transport/test_http_client.py`
- `tests/integration/viya_e2e_config.py`
- `tests/integration/test_viya_password_token_e2e.py`
- `tests/unit/integration/test_viya_e2e_config.py`

Planning and TDD artifacts:

- `plan/http-client-tls-trust/http-client-tls-trust.plan.md`
- `plan/http-client-tls-trust/http-client-tls-trust.spec.md`
- `plan/http-client-tls-trust/http-client-tls-trust.step.md`
- `plan/http-client-tls-trust/http-client-tls-trust.tdd-test-authoring.yaml`

Candidate files to inspect:

- `src/mlops_async/core/request_options.py`
- `src/mlops_async/core/token_endpoint/password.py`
- `tests/conftest.py`

## Implementation Steps

1. Implementer在 `src/mlops_async/transport/http_client.py` 將 constructor annotation
   改為 `bool | ssl.SSLContext`，並在所有 AsyncClient construction branch前加入固定
   `TypeError` validation與合法值原樣傳遞。
2. Implementer在 `tests/integration/viya_e2e_config.py` 加入 required
   `VIYA_E2E_TLS_MODE`、exact resolver、conditional `VIYA_E2E_CA_BUNDLE`、固定 warning/
   errors與 `ViyaE2EConfig.verify`。
3. Implementer在 `tests/integration/test_viya_password_token_e2e.py` 將 hard-coded
   `verify=True` 改為 `verify=config.verify`，並保留 HTTP 200、token、expiry與
   anti-fake-success assertions。
4. Implementer執行 focused transport/config/password-token/client-credentials tests，
   確認 RED cases轉 GREEN；正式 evidence為 focused與auth共 `90 passed`。
5. Implementer執行 targeted Pyright、Ruff與 bounded diff-check；正式 evidence為
   targeted Pyright `0` errors、Ruff passed、diff-check passed，且未執行 live E2E。

### Post-implementation workflow / gates

- **Implementation review — completed**：獨立 Reviewer已使用
  `python-implementation-review` 對照 plan完成審查，正式 verdict為 `approved`。
- **Code review — completed**：獨立 Reviewer已使用 `python-code-review` 完成審查，
  正式 verdict為 `approved`、zero blocking issues。
- **Pre-live non-E2E/static validation — completed**：Tester已在 code review後執行
  non-E2E pytest、Ruff與 full configured Pyright；正式 evidence為 pytest
  `311 passed / 9 skipped / 1 deselected`、Ruff all passed、Pyright
  `0 errors / 0 warnings`。此 evidence不包含 network connection、live E2E或 secret read。
- **Rework routing — completed/not required**：implementation review與code review均
  `approved`且 zero blocking issues，因此本輪不需派 Implementer rework。
- **Human config provision — completed**：來源為最新 human confirmation：
  `strict config 已確認，授權重新執行一次 framework live E2E`。歷史 failures保留；
  secret file保持 opaque，agent未讀取、未列印、未diff、未stage。
- **Live E2E — completed**：latest authorized framework live為 exit `0`、
  `1 passed / 320 deselected`，驗證 exact HTTP 200、nonempty token、positive expiry與
  fixed insecure warning。Exact statement：
  `live password-token E2E passed with TLS verification explicitly disabled`。此結果不宣稱
  TLS trust verified；pre/post inventory `unexpected=0`，且無 retry、fallback、mode switch、
  mock或skip。Secret保持 opaque。
- **Publish — pending**：全部 gates通過後，Implementer bounded commit並push
  `fix/andrew/http-client-tls-trust`，不得納入 secret或scope外檔案。
- **Merge — pending**：Implementer將 fix branch merge並push到
  `test/andrew/viya-password-token-e2e`，不得 merge到 `dev`。
- **Post-merge validation — pending**：Tester在 E2E branch merge result重跑 non-E2E、
  Ruff、Pyright與 explicit insecure live E2E。
- **Finalization — pending**：Dispatcher彙整 review與validation evidence，若無 blocker
  則交 human check；不執行 release或 `dev` merge。

## Test Plan

Test files：`tests/unit/transport/test_http_client.py`、
`tests/unit/integration/test_viya_e2e_config.py`、
`tests/integration/test_viya_password_token_e2e.py`。

### TestCase

- Happy path：omitted/default與explicit bool傳遞；SSLContext identity傳遞；
  `system -> True`、`insecure -> False`加 warning、`ca_bundle -> SSLContext`；internal
  insecure E2E取得 HTTP 200、nonempty token與positive expiry。
- Invalid input：unsupported verify type得到固定 `TypeError`且 AsyncClient未建立；
  missing/blank mode得到 required error；unsupported mode得到 invalid error；missing CA、
  CA用於 non-ca mode、unreadable/invalid CA各得到固定 error。
- Edge case：blank CA在 system/insecure視為未提供；exact mode不 trim/normalize；warning
  每次 loader invocation只發出一次；messages不含 mode value、path、PEM或 raw cause；
  loader不讀 process `RUN_VIYA_E2E`。
- Regression：現有 transport request/status/JSON/timeout tests、E2E config既有 tests、
  password-token、client-credentials與全部 non-E2E suite維持通過。
- Backward compatibility：omitted verify仍為 `True`、explicit bool不變、一般 run仍skip
  live E2E、未 opt-in marker仍fail、production exception contract不變；insecure pass與
  TLS-verifying pass結論嚴格分離。

## Validation Commands

```powershell
git check-ignore config/.env.test
uv run pytest --no-cov tests/unit/transport/test_http_client.py -q
uv run pytest --no-cov tests/unit/integration/test_viya_e2e_config.py -q
uv run pytest --no-cov tests/unit/core/test_password_token_endpoint_client.py -q
uv run pytest --no-cov tests/unit/core/test_token_endpoint_client.py -q
uv run pytest --no-cov -m "not viya_e2e" -q
uv run ruff check src tests
uv run pyright
```

Internal live acceptance前由 human在 ignored config設定：

```text
VIYA_E2E_TLS_MODE=insecure
```

然後由 Tester明確 opt in：

```powershell
$env:RUN_VIYA_E2E = '1'
uv run pytest --no-cov -m viya_e2e tests/integration/test_viya_password_token_e2e.py -q
```

成功報告只能使用：

```text
live password-token E2E passed with TLS verification explicitly disabled
```

## Risks

- Explicit `False`停用 certificate與hostname verification；若文件或報告語意不精確，
  可能讓 insecure pass被誤報為 TLS verified。
- Conditional CA key若錯誤實作成 universally required，會阻斷 internal insecure mode。
- CA exception raw traceback可能包含 local path，evidence必須維持 sanitized。
- Validation若發生在 AsyncClient建立後可能產生資源副作用並違反 fail-fast contract。
- Exact mode不 normalize會使大小寫或額外空白配置 fail；這是已鎖定的明確行為。

## Rollback Plan

- Revert fix branch中 `src/mlops_async/transport/http_client.py`、
  `tests/unit/transport/test_http_client.py`、`tests/integration/viya_e2e_config.py`、
  `tests/integration/test_viya_password_token_e2e.py`、
  `tests/unit/integration/test_viya_e2e_config.py` 的 bounded commits。
- 若已 merge到 E2E branch，revert該 merge commit並重跑原有 non-E2E gates。
- Human自行移除 Git-ignored TLS config values；不得將 config納入 rollback artifact。
- Rollback不得引入 implicit fallback、弱化 anti-fake-success gate或修改 release surfaces。

## Open Questions

None。
