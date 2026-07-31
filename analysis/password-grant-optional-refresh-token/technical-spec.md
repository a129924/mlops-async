# password-grant-optional-refresh-token 技術規格

## Analysis routing

本文件是 execution-facing source of truth；`analysis/password-grant-optional-refresh-token/requirements.md` 是 business-intent guardrail。本 topic plan 必須 100% 對應本規格。

## Goal

將 password-grant 的首次 obtain parser 呼叫改為「`refresh_token` 可省略」，不改變有提供欄位時的型別與非空白驗證，也不改變 refresh 行為。

## Non-Goal

- 不修改 `TokenEndpointClientProtocol`、`AuthClient`、`TokenManager`、`AccessToken` 或任何 public API。
- 不改動 `parse_token_response()` 的通用預設、refresh grant 的 parser 呼叫，或 cached token replacement 邏輯。
- 不修改 ReadOnly integration E2E，不執行 release `0.15.1`。

## Locked Decisions

- `approved` 是 TDD/implementation 的必要而非充分條件：之後只能在由 Main Agent 依預期 base
  新建的 managed worktree 工作，不得把本 planning worktree 自動轉作 implementation worktree。
- TDD 開始前必須保留唯讀 Git preflight 證據：managed-worktree registration/path、branch 與
  expected-base 關係，以及乾淨或只有已獲授權項目的 `git status --short`；任何未授權或不相關
  變更都是 stop condition。
- planning artifacts 的保留、複製、stage 或 commit 是獨立 human authorization；Tester 或
  Implementer 不得自動執行或以其完成推論實作授權。

## In-Scope

### Production behavior

- 在 `src/mlops_async/core/token_endpoint/password.py` 的 `PasswordTokenEndpointClient.fetch_access_token()`，以既有 shared parser 接受省略的 `refresh_token`；成功時 `AccessToken.refresh_token` 為 `None`。
- 保持 shared parser 對已存在的 `refresh_token` 使用既有非空白 string 驗證，因此值為 `None`、blank 或 non-string 仍拋出既有 token-endpoint error。
- `refresh_access_token()` 的 `token.refresh_token is None` 分支繼續直接呼叫 `fetch_access_token()`，保留 password re-obtain fallback；不得新增 refresh-grant request。

### Test and live gate behavior

- `tests/unit/core/test_password_token_endpoint_client.py` 將原本「missing refresh token 必須失敗」的 obtain case 改為成功 contract，並保留 present-but-invalid cases。
- `tests/conftest.py` 的 `viya_e2e` opt-in 判斷必須同時滿足 `RUN_VIYA_E2E == "1"` 與 `VIYA_E2E_VPN_CONFIRMED == "1"`。
- `tests/unit/test_viya_e2e_pytest_guard.py` 覆蓋兩變數的 exact-value、缺失與只設一個的 collection gate contract。
- live E2E 只可在人工確認當次 VPN 後執行；ReadOnly `tests/integration/test_viya_password_token_e2e.py` 只驗證 first obtain。

## Out-Of-Scope

- `src/mlops_async/core/auth.py`、`src/mlops_async/core/token_storage.py`、`src/mlops_async/core/token_endpoint/_shared.py`。
- integration config schema、TLS mode、`config/.env.test`、network retry 或 timeout。
- 所有未列在下列 `Modify` 的 source/test 檔案、舊 worktree、Git/GitHub 與 release metadata。

## ReadOnly

- `tests/integration/test_viya_password_token_e2e.py`：首次 obtain live assertion 的既有 contract；不可修改。
- `tests/integration/viya_e2e_config.py` 與 `config/.env.test`：不讀取、不列印、不寫入。
- `src/mlops_async/core/auth.py`、`src/mlops_async/core/token_storage.py`、`src/mlops_async/core/token_endpoint/_shared.py`：契約與 storage/parser 邊界保持不變。

## Written

- `analysis/password-grant-optional-refresh-token/requirements.md`
- `analysis/password-grant-optional-refresh-token/technical-spec.md`
- `plan/password-grant-optional-refresh-token/password-grant-optional-refresh-token.plan.md`
- `plan/password-grant-optional-refresh-token/password-grant-optional-refresh-token.step.md`

## Deleted

- 無。

## Modify

| Path | 責任 | 精確變更 |
| --- | --- | --- |
| `src/mlops_async/core/token_endpoint/password.py` | Implementer | 僅放寬 password obtain 的 omitted refresh token；保留 present-invalid rejection 與 re-obtain fallback。 |
| `tests/unit/core/test_password_token_endpoint_client.py` | Tester then Implementer | RED/validation cases：omitted-success、present-invalid rejection、legacy re-obtain。 |
| `tests/conftest.py` | Implementer | 將 live collection opt-in 收緊為兩個 exact `1` environment variables。 |
| `tests/unit/test_viya_e2e_pytest_guard.py` | Tester then Implementer | 驗證雙變數 collection gate，含所有拒絕組合。 |

## TestCase

| ID | Given | When | Then |
| --- | --- | --- | --- |
| P1 | 一般 password client ID，response 有有效 access token/expiry、沒有 `refresh_token` | `fetch_access_token()` | 成功且 `refresh_token is None`。 |
| P2 | `sas.ec` password client，等同 P1 response | `fetch_access_token()` | 同 P1；沒有 client-ID 特例。 |
| P3 | response 有 `refresh_token: None`、blank 或 non-string | `fetch_access_token()` | 每一案例都保留 `TokenEndpointClientError`。 |
| P4 | legacy expired `AccessToken` 沒有 refresh token；re-obtain response 省略欄位 | `refresh_access_token()` 或 TokenManager consumer contract | 只發 password grant，成功且不要求 refresh token。 |
| G1 | `RUN_VIYA_E2E=1` 且 `VIYA_E2E_VPN_CONFIRMED=1` | `pytest -m viya_e2e` collection | 允許 collection，仍須人工 VPN 確認才可 live run。 |
| G2 | 任一 variable 缺失、非 `1` 或僅另一個為 `1` | `pytest -m viya_e2e` collection | `pytest.UsageError` 清楚指出兩個 required opt-ins。 |

## Implementation Steps

1. 在任何 RED test 前，確認 Plan-Reviewer `approved`、預期 base 的新 managed worktree，以及
   唯讀 Git preflight；未有這三項證據不得開始 TDD。
2. 僅在獨立 human authorization 決定 planning artifacts 的保留/複製/stage/commit 後，才可使
   新 worktree 帶有該 artifacts；此決定不由 implementation 自動完成。
3. 通過入口 gate 後，才依 `Modify` 清單完成 RED tests、production 最小變更、guard tests 與
   validation。

## Validation contract

- 實作者在 managed worktree 透過 WSL 執行 scoped unit tests、非 E2E suite、Ruff、Pyright、Tach 與 lock check；本 planning 階段不執行它們。
- TDD/implementation 的驗收前置必須包含唯讀 Git preflight：以 `git worktree list --porcelain`、
  `git status --short`、branch/path/base 讀取命令證明新 worktree 由 expected base 建立，且沒有
  未授權或不相關變更。
- preflight 發現 planning artifacts 時，證據必須連同獨立 human authorization 說明其保留、複製、
  stage 或 commit 的處置；沒有該授權時不得由實作角色自行處理。
- live command 是獨立人類 gate：兩個 variables 精確為 `1`、當次 VPN 人工確認、已遮蔽 config 與 ReadOnly first-obtain E2E 全數成立後才可執行。
- 只以實際 live request 的 HTTP/token contract 為 E2E 證據；route reachability、skip 或 mock 不是成功證據。
- release `0.15.1` 僅在 PR merge 後，由人類另行授權；不得由 implementation 或 validation 自動修改版本檔、tag 或 publish。
