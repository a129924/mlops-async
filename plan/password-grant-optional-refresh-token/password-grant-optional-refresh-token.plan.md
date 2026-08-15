# password-grant-optional-refresh-token 實作計畫

分析層採 strict mode：`analysis/password-grant-optional-refresh-token/technical-spec.md` 是 execution-facing source of truth，`analysis/password-grant-optional-refresh-token/requirements.md` 是 business-intent guardrail；本計畫 100% 對應 technical spec。

## Goal / Outcome

- **Goal**：password grant 首次 obtain 成功回應可以省略 `refresh_token`，並對所有 password client ID 一致適用；存在但 `None`、blank 或 non-string 的欄位仍為錯誤。
- **Outcome**：保留沒有 refresh token 的 legacy token 之 password re-obtain fallback，並以兩個 exact opt-ins 與 VPN human confirmation 保護 live E2E。

## Scope

- **In-Scope**：
  - 僅放寬 `PasswordTokenEndpointClient.fetch_access_token()` 對 omitted `refresh_token` 的 password-obtain 成功回應。
  - 僅修改兩個 scoped unit/guard test surfaces，及 live collection gate。
  - 為選取 `viya_e2e` 建立雙環境變數的 exact-value gate：`RUN_VIYA_E2E=1` 與 `VIYA_E2E_VPN_CONFIRMED=1`。

- **Out-Of-Scope**：
  - Protocol、AuthClient、TokenManager、AccessToken、public API、shared parser、refresh grant 行為、TLS/config schema、retry/timeout/transport lifecycle。
  - ReadOnly integration E2E 的修改；它只驗證 first obtain。
  - commit、push、PR、merge、release、tag、cleanup 與任何舊 worktree。

## Locked Decisions

- **所有** password client ID 的首次 obtain 成功回應都可省略 `refresh_token`；不得用 `client_id` 建立 allowlist 或特殊分支。
- 欄位「存在」時仍必須是 non-empty string；`None`、空白與 non-string 維持錯誤。
- `PasswordTokenEndpointClient.refresh_access_token()` 在 cached token 無 refresh token 時，必須保持既有 password re-obtain fallback。
- 不修改 `TokenEndpointClientProtocol`、`AuthClient`、`TokenManager`、`AccessToken` 或 public API；也不改 shared parser 的其他 call site。
- `tests/integration/test_viya_password_token_e2e.py` 是 ReadOnly，且 scope 只容許它作為 first-obtain live check，不新增 refresh-flow E2E。
- live selection 需要兩個 process env variables 同時且精確為 `1`：`RUN_VIYA_E2E=1`、`VIYA_E2E_VPN_CONFIRMED=1`；執行前另需當次人工 VPN 確認。
- Plan-Reviewer `approved` 後，TDD 與 implementation 只能在 Main Agent 依預期 base 新建的
  managed worktree 進行；現有 planning worktree 不得自動沿用為 implementation worktree。
- 開始 TDD 前必須有唯讀 Git preflight 證據，確認 managed-worktree registration、path、
  branch/expected-base 關係及 `git status --short`，並證明沒有未授權或不相關變更。
- planning artifacts 的保留、複製、stage 或 commit 均需要獨立 human authorization；不得由
  Tester/Implementer 或 implementation 流程自動處理或推論授權。
- 這是 stable-library-affecting topic，因 release `0.15.1` 被明確 deferred；實作、測試與 review 完成不構成 release 授權。

## Boundaries / Exclusions

- Planning actor 僅維護 planning artifacts；Tester 撰寫/驗證 tests；Implementer 僅在 `Modify` 路徑實作；Reviewer 獨立給出 handoff JSON；Main Agent 擁有 routing、PR 與 post-merge orchestration。
- `config/.env.test` 保持 opaque：不得讀取、列印、stage 或寫入。external token failure 為 stop condition，且只可回報 redacted error type。
- 若實作需求需要 `Modify` 以外的路徑，或要求改動 ReadOnly path，必須停止並要求重新規劃；不得碰舊 worktree 或不相關變更。

## Status / Allowed Transitions

- **Current**：`approved`（Plan-Reviewer、implementation review 與 code review 均已 approved；publication/PR ready 但尚未開始）
- **Execution model**：planning artifacts 已 materialize 且 Plan-Reviewer 已 `approved`；保留已完成的
  managed-worktree/preflight gate、TDD、implementation、non-live validation 與已授權的單次 live
  first-obtain assertion evidence；implementation review 與 code review 亦已 approved。下一個 gate 是
  publication/PR 的獨立 human authorization；commit、push、PR、merge 與 release 均尚未開始、未完成，
  也未因 review approval 自動獲得授權。
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
  - `merged` -> `released`（僅在 merge 後的人類 release gate 明確授權 `0.15.1` 時）
  - `merged` 或 `released` -> terminal（依是否另獲 release 授權）

Routing notes:

- 採標準 Phase 4.5：Plan-Reviewer 的 `approved` 是 Tester/Implementer 開始前置條件。
- Plan-Reviewer、implementation reviewer 與 code reviewer 的 verdict 均為 `approved`，無 topic blocker；
  handoff 改為 publication/PR human gate。
- publication/PR 是 ready 而非 started：不得因 ready 狀態宣告 commit、push、PR、merge 或
  `0.15.1` release 完成；release 仍僅可在 merge 後經獨立 human gate 處理。
- 任一 live gate 未滿足、外部 token failure、範圍漂移或未授權 release 都是 stop condition，不可用 skip/fallback/retry 取代。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Business requirements | `analysis/password-grant-optional-refresh-token/requirements.md` | Planning actor | Business guardrail 與精確 scope。 |
| Technical specification | `analysis/password-grant-optional-refresh-token/technical-spec.md` | Planning actor | Strict-mode execution truth。 |
| Topic plan | `plan/password-grant-optional-refresh-token/password-grant-optional-refresh-token.plan.md` | Planning actor | Repo-visible workflow/implementation contract。 |
| Step tracker | `plan/password-grant-optional-refresh-token/password-grant-optional-refresh-token.step.md` | Planning actor, then executor | Phase 與 implementation completion gate。 |
| Password client | `src/mlops_async/core/token_endpoint/password.py` | Implementer | 唯一 production 行為變更。 |
| Password client unit tests | `tests/unit/core/test_password_token_endpoint_client.py` | Tester then Implementer | Omitted-success、present-invalid 與 re-obtain regression contract。 |
| Pytest live gate | `tests/conftest.py` | Implementer | 雙 exact opt-in collection gate。 |
| Pytest gate unit tests | `tests/unit/test_viya_e2e_pytest_guard.py` | Tester then Implementer | 雙 variable collection-gate contract。 |
| Live first-obtain E2E | `tests/integration/test_viya_password_token_e2e.py` | N/A (ReadOnly) | 僅在人工 live gate 後驗證 first obtain。 |

Artifact path notes:

- **ReadOnly**：`tests/integration/test_viya_password_token_e2e.py`、`src/mlops_async/core/auth.py`、`src/mlops_async/core/token_storage.py`、`src/mlops_async/core/token_endpoint/_shared.py`、`README.md`、`VERSION`、`pyproject.toml`、`uv.lock`、`config/.env.test`。
- **Written**：兩個 `analysis/` artifacts、topic plan 與 step tracker。
- **Deleted**：無。
- **Modify**：僅 `src/mlops_async/core/token_endpoint/password.py`、`tests/unit/core/test_password_token_endpoint_client.py`、`tests/conftest.py`、`tests/unit/test_viya_e2e_pytest_guard.py`。
- 此清單是 executable contract；任何其他 path 是 plan-alignment 問題，需停下重新核准。

## Stable library metadata

- `README row`：no-change；本 topic 不更新 README。
- `VERSION bump`：PATCH 到 `0.15.1`，但不是 feature implementation 的 write target。
- `timing`：deferred to merge 後的獨立 human release gate。
- `rationale`：此行為修正可能需要 stable release，但 release decision 必須與 implementation success 分離，不能從 approved/merged 自動推論。
- `release-note expectations`：只有人類在 merge 後明確授權 release 時，才另外決定 release note 與版本 metadata；目前沒有 write authorization。

## Implementation Steps

1. TDD 入口前置：Plan-Reviewer 已 `approved`；Main Agent 已依預期 base 建立新的 managed
   worktree；並已完成唯讀 Git preflight，證明 registration/path、branch/base 關係及 status
   沒有未授權或不相關變更。未滿足時不得開始下一步。
2. TDD 入口前置：planning artifacts 的保留、複製、stage 或 commit 已取得獨立 human
   authorization；沒有該決定時，Tester/Implementer 不得自動搬移、保留或提交 artifacts。
3. Tester 先於 `tests/unit/core/test_password_token_endpoint_client.py` 建立 RED cases：一般 client ID 與 `sas.ec` 的 omitted-success、present `None`/blank/non-string rejection，以及 legacy no-refresh-token 的 password re-obtain。
4. Implementer 只修改 `src/mlops_async/core/token_endpoint/password.py`，讓 `fetch_access_token()` 使用既有 parser 的 optional-refresh path；保留 present-value 驗證與 `refresh_access_token()` 的 re-obtain branch。
5. Tester 在 `tests/unit/test_viya_e2e_pytest_guard.py` 建立 RED cases，覆蓋兩 variables 都為 `1` 才允許 collection，及缺失、非 `1`、只設一個的拒絕情形。
6. Implementer 只修改 `tests/conftest.py`，將 collection/runtime opt-in 改為 `RUN_VIYA_E2E=1` 加 `VIYA_E2E_VPN_CONFIRMED=1`；錯誤訊息必須指示雙前置條件。
7. Tester/Implementer 在已 preflight 的新 managed worktree 透過 WSL 做 scoped 與 non-E2E validation，並僅在成功後更新 step tracker；不得藉由 live E2E 改動 ReadOnly integration 檔。
8. 若 human 明確授權 live run，先記錄當次 VPN human confirmation，再確認兩 env vars 精確為 `1`，以 ReadOnly first-obtain E2E 蒐集 redacted evidence；外部失敗立即停止。

## Validation / Acceptance Checks

- **TestCase P1/P2**：任一 password client ID 的 first obtain 缺少 `refresh_token` 時成功；`AccessToken.refresh_token is None`。
- **TestCase P3**：欄位存在但值為 `None`、blank、non-string 時失敗，並保持 credential redaction。
- **TestCase P4**：legacy token 沒有 refresh token 時只發 password grant re-obtain，不發 refresh grant。
- **TestCase G1/G2**：只有 `RUN_VIYA_E2E=1` 與 `VIYA_E2E_VPN_CONFIRMED=1` 同時成立才允許選取 `viya_e2e`；所有其他組合拒絕。
- **Worktree gate**：TDD 前的唯讀 Git preflight 證明新 managed worktree 建於 expected base、
  registration/path/branch 正確，且 `git status --short` 沒有未授權或不相關變更。
- **Planning-artifact gate**：preflight 若發現 planning artifacts，必須有獨立 human authorization
  說明保留、複製、stage 或 commit 的處置；implementation 不得自動處理它們。
- 實作後透過 WSL 執行 scoped unit tests、`pytest -m "not viya_e2e"`、Ruff、Pyright、Tach 與 `uv lock --check`；不可把 Windows/WDAC 問題誤報為 code success。
- **完成的 non-live evidence**：Ruff format/check、Pyright、Tach 與 `uv lock --check` 均通過；
  透過暫時 WSL `GIT_DIR`/`GIT_WORK_TREE` workaround 執行 `pytest -m "not viya_e2e"`，結果為
  `403 passed, 9 skipped, 1 deselected`，coverage `95.04%`。此 workaround 僅記錄為該次
  validation execution 的環境相容處置，不授權 Git 寫入、native fallback 或後續 live run。
- live E2E 只在兩 exact values、當次 VPN human confirmation、secret-safe config 與明確人類 opt-in 全部成立後執行；驗證 only first obtain 的實際 request/token result。
- **完成的 live assertion evidence**：唯一一次已授權 external request 執行
  `test_password_token_e2e_validates_exact_success_contract`，assertion 為 `1 passed`；未出現
  redacted failure、retry 或 secret 輸出。該 pytest process 的 overall exit `1` 僅因 single-file
  全專案 coverage `64.96% < 90%`，不是 E2E assertion 失敗；不得重跑 live。
- `git diff --check` 必須通過，且 diff 只含 artifact contract 允許的 paths。

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

- merge 不自動發布。只有 merge 後的人類明確 release gate 才可處理 `0.15.1`、版本 metadata、tag 或 release notes。
- 在沒有該授權時，topic 到 `merged` 為止；worktree/branch cleanup 仍須 Main Agent 與人類另行授權。

## Open Questions / Unresolved Items

- 無。live run 是否執行及 `0.15.1` 是否發布均是明確的人類 gate，不是規格未決事項。

## Workflow State Contract

- `current_step`: publication-pr-ready
- `next_step`: human authorization for commit, push, and Ready PR
- `status`: IN_PROGRESS
