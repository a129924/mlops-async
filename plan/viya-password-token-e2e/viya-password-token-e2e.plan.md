# Viya password token E2E

本計畫在 analysis layer strict mode 下維護：
`analysis/viya-password-token-e2e/technical-spec.md` 是 execution-facing source of
truth，`analysis/viya-password-token-e2e/requirements.md` 是 business-intent guardrail。
Human 已明確要求以現行 TLS implementation 與 post-merge evidence correction 覆蓋舊的
hard-coded `verify=True` 敘述，五個 parent planning artifacts 必須同步為 current truth。

## Goal / Outcome

- 在明確 process opt-in 時，以真實 HTTPS 呼叫 SAS Viya password-grant token endpoint；
  只在 HTTP `200`、非空 `access_token` 與 positive expiry 都成立時通過。
- framework 使用者明確控制 TLS mode；成功結果精確區分 HTTPS request success、TLS
  verification disabled 與 TLS trust verified。
- 核心 E2E goal 已由 post-merge live evidence 支持；topic branch merge 到 `dev` 仍是
  pending human boundary，不屬於已完成事項。

## Scope

- **In scope**:
  - `POST /SASLogon/oauth/token` 的單一 password grant 真實 E2E。
  - process-only `RUN_VIYA_E2E=1` opt-in、Git-ignored test config loader 與 redacted
    failure contract。
  - exact TLS mode `system`、`insecure`、`ca_bundle` 到 `HttpClient.verify` 的 mapping。
  - HTTP `200`、nonempty token、positive expiry、30 秒 total timeout 與 cancellation
    propagation。
  - 本計畫列出的 tests、analysis 與 plan artifacts。

- **Out of scope**:
  - protected proof endpoint、public `AuthClient`、refresh-token flow、client-credentials
    行為或 production auth flow。
  - mock、fake transport、fallback token、retry、fallback TLS mode、skip-as-success 或 CI
    live E2E 排程。
  - README、VERSION、release metadata、release action 或 dependency 變更。
  - 在本次 planning convergence 修改 `src/`、`tests/`、config 或 release files。

## Locked Decisions

- `VIYA_E2E_TLS_MODE` 是 required exact value：
  - `system` -> `verify=True`；
  - `insecure` -> `verify=False` 且固定警告 TLS verification 已明確停用；
  - `ca_bundle` -> 要求非空白 `VIYA_E2E_CA_BUNDLE`，以該 exact path 建立並傳入
    `ssl.SSLContext`。
- CA bundle 只允許在 `ca_bundle` mode；loader 不隱式讀取其他 CA environment
  variables，不 fallback 或切換 mode。
- 公司內部環境使用 `insecure` 是 framework 使用者的 explicit configuration，不是假
  success；真實 transport、HTTP、JSON 或 schema failure 仍必須 fail。
- `insecure` live success 的唯一正確摘要是
  `live password-token E2E passed with TLS verification explicitly disabled`；不得宣稱
  TLS trust verified。
- E2E 只接受非-loopback HTTPS origin、exact HTTP `200`、nonempty token 與 positive
  expiry；`RequestTimeouts(total=30)` 維持不變。
- config 中的 `RUN_VIYA_E2E` 必須忽略；只有 process environment 能啟用真實網路。
- `asyncio.CancelledError` 原樣傳播；其他 runtime failures 轉成不含敏感內容的 redacted
  failure。
- 本 topic 不新增 public API。`HttpClient` 的 `bool | ssl.SSLContext` contract 由
  `http-client-tls-trust` topic 提供，本 E2E topic 只消費該 contract，不重開其
  architecture／public contract decision。
- 本 topic 不影響 stable-library surfaces；沒有 README、VERSION、release notes 或
  release timing 變更。

## Boundaries / Exclusions

- 不得讀出、複製、提交、列印或在 evidence 中揭露 `config/.env.test` 內容。
- Evidence 不得包含 URL、username、password、client secret、Basic header、access
  token、response body 或 CA bundle path。
- HTTPS request success 只代表真實 HTTPS origin 回應且 token success contract 成立。
- `insecure` 表示 HTTPS request 執行時未驗證 server certificate trust／identity。
- TLS trust verified 只能由啟用 certificate verification 的成功 run 支持；本次 live
  evidence 使用 `insecure`，不支持此結論。
- Merge-to-dev、commit、push、PR、release 與 cleanup 由 Main Agent 在新的 human
  authorization 下路由，不是 Plan-Creator 或 Plan-Reviewer 的職責。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Reason**: bounded Plan-Creator convergence 已同步 current TLS contract 與已鎖定
  post-merge evidence；下一步只能由獨立 Plan-Reviewer 審查。
- **Execution model**: planning correction review 完成後，仍停在 merge-to-dev human
  boundary；review PASS 本身不授權 commit、push、PR、merge 或 release。
- **Allowed transitions**:
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`
  - `merged` -> terminal

Routing notes:

- Reviewer PASS 後，Main Agent 回報 planning artifacts 已收斂並停止在 merge-to-dev
  human boundary。
- Reviewer `needs-rework` 時，只能由 Plan-Creator bounded 修正，再交獨立
  Plan-Reviewer 複審。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business requirements | `analysis/viya-password-token-e2e/requirements.md` | Planning actor | Business guardrail 與 acceptance boundary |
| Technical specification | `analysis/viya-password-token-e2e/technical-spec.md` | Planning actor | Strict-mode execution truth 與 evidence semantics |
| Topic plan | `plan/viya-password-token-e2e/viya-password-token-e2e.plan.md` | Planning actor | Repo-visible execution與workflow contract |
| Behavior specification | `plan/viya-password-token-e2e/viya-password-token-e2e.spec.md` | Creator | E2E acceptance scenarios 與 edge cases |
| Step tracker | `plan/viya-password-token-e2e/viya-password-token-e2e.step.md` | Creator | Implementation completion evidence 與 pending merge boundary |
| Test package marker | `tests/__init__.py` | Creator | 支援 test package import |
| Pytest opt-in gate | `tests/conftest.py` | Creator | 註冊 marker 並強制 process-only opt-in |
| Test config loader | `tests/integration/viya_e2e_config.py` | Creator | 驗證 secret-safe config 與 explicit TLS mode mapping |
| Live E2E | `tests/integration/test_viya_password_token_e2e.py` | Creator | 執行單一真實 password grant 與 exact success assertions |
| Config unit tests | `tests/unit/integration/test_viya_e2e_config.py` | Creator | 驗證 config、TLS mapping 與 redaction contract |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md` 或 release
  notes，因此不加入 `Stable library metadata`。
- 本次 convergence 的 write scope 僅限上表前五個 planning artifacts；tests 是已完成
  topic implementation evidence，不得在本輪修改。
- 若後續工作需要超出上述 paths，必須先回到 plan alignment，不得自行擴張。

## Implementation Steps

1. 建立 test-only config parser，驗證 required fields、HTTPS origin、`sas.ec` empty
   secret exception 與 exact TLS mode mapping。
2. 建立 pytest marker 與 process-only `RUN_VIYA_E2E=1` gate；一般 pytest skip，明確
   選取 marker 卻未 opt-in 時 fail。
3. 建立單一真實 password-token E2E，使用 `RequestTimeouts(total=30)`、loader 提供的
   `bool | ssl.SSLContext`，並驗證 exact HTTP `200`、nonempty token、positive expiry。
4. 保留 anti-fake-success 與 redaction contract：不 mock、不 fallback、不切換 TLS
   mode；任何真實 failure 必須 fail，cancellation 原樣傳播。
5. 完成 implementation review、code review、post-merge non-E2E 與單次授權 live E2E。
6. 將五個 parent planning artifacts 回填為現行 TLS contract 與 validation evidence，
   交由獨立 Plan-Reviewer 審查。

Implementation step completion 由
`plan/viya-password-token-e2e/viya-password-token-e2e.step.md` 的 `[X]` / `[ ]`
contract 判定；merge-to-dev 不屬於已完成 implementation step。

## Validation / Acceptance Checks

Current accepted post-merge evidence（本輪 planning convergence 前的 clean baseline）：

- E2E branch `test/andrew/viya-password-token-e2e` @
  `86d0b34c5df0d6cc19696e4f00c1682cc76ce500`，ahead/behind upstream `0/0`。
- Non-E2E：pytest `311 passed, 9 skipped, 1 deselected`；Ruff passed；Pyright
  `0 errors, 0 warnings`。
- Live E2E：`1 passed, 320 deselected`；真實 network request、HTTP `200`、nonempty
  token、positive expiry；結果為
  `live password-token E2E passed with TLS verification explicitly disabled`。
- 此 live evidence 支持 HTTPS request success 與 explicit insecure mode success；不支持
  TLS trust verified。

Reviewer acceptance checks：

- 五個 parent planning artifacts 對 `system` / `insecure` / `ca_bundle` mapping 一致，
  且符合 current implementation。
- 沒有 hard-coded `verify=True` 作為唯一 E2E path，也沒有把 `verify=False` 一概描述為
  fake success。
- Anti-fake-success、secret redaction、30 秒 timeout 與 cancellation contract 未弱化。
- `.step.md` 使用 canonical `review-ready` phase，已驗證的 implementation steps 保持
  `[X]`，merge-to-dev 保持 `[ ]`。
- Branch 尚未 merge 到 `dev`，不得標記為 `merged` 或宣稱 release completed。
- Diff 僅包含五個授權 planning artifacts；未修改 `src/`、`tests/`、config 或 release
  files。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- E2E branch 尚未 merge 到 `dev`；此動作維持 pending，必須取得新的 human
  authorization，且不得由 planning convergence 或 reviewer PASS 隱式授權。
- Merge 到 `dev` 後，本 topic 沒有 VERSION、README、release notes 或其他 repository
  release action；`merged` 是本 topic terminal state。
- Worktree／branch cleanup 需由 Main Agent 依 human authorization 另行處理。

## Open Questions / Unresolved Items

- 唯一 unresolved item：是否授權將
  `test/andrew/viya-password-token-e2e` merge 到 `dev`。在 human 明確授權前保持
  pending，不影響本輪 planning artifact review。
