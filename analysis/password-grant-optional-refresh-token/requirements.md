# password-grant-optional-refresh-token 需求基準

## Goal

讓 `PasswordTokenEndpointClient` 在 password grant 的首次 obtain 成功回應未提供
`refresh_token` 時仍能取得可用的 access token；此規則對所有 password
`client_id` 一致適用。

## Non-Goal

- 不新增或變更 public API。
- 不將此議題擴大為 refresh grant、TokenManager、AuthClient 或 Protocol 的行為重設計。
- 不在本議題執行、重寫或擴充 live integration E2E。

## In-Scope

- 首次 password-grant obtain 回應缺少 `refresh_token` 時接受成功回應，並保留
  `AccessToken.refresh_token is None` 的既有表示。
- 若回應含有 `refresh_token`，仍拒絕值為 `None`、空白字串或非字串的回應。
- 保持 password client 對 legacy token 缺少 refresh token 時的 re-obtain fallback。
- 將 live E2E 的執行前置條件收緊為兩個 process environment variables 都精確為
  `1`：`RUN_VIYA_E2E=1` 與 `VIYA_E2E_VPN_CONFIRMED=1`；並要求當次人工確認 VPN。

## Out-Of-Scope

- `TokenEndpointClientProtocol`、`AuthClient`、`TokenManager`、`AccessToken` 及其 public API。
- client credentials grant、refresh grant response 的 fallback/preserve/rotation 規則、retry、timeout、transport lifecycle 與 credential policy。
- `tests/integration/test_viya_password_token_e2e.py` 的內容修改；它只作為 ReadOnly 的首次 obtain live 驗證目標。
- commit、push、PR、merge、worktree cleanup、tag 與 release。

## ReadOnly

- `tests/integration/test_viya_password_token_e2e.py`：只驗證首次 obtain，不得改寫為 refresh-flow 驗證，也不得因本議題改動。
- `src/mlops_async/core/auth.py`、`src/mlops_async/core/token_storage.py`、`src/mlops_async/core/token_endpoint/_shared.py`：維持現有 Protocol、TokenManager、AccessToken 與 shared parser 邊界。
- `README.md`、`VERSION`、`pyproject.toml`、`uv.lock`：本 implementation 不改動。

## Written

- `analysis/password-grant-optional-refresh-token/requirements.md`
- `analysis/password-grant-optional-refresh-token/technical-spec.md`
- `plan/password-grant-optional-refresh-token/password-grant-optional-refresh-token.plan.md`
- `plan/password-grant-optional-refresh-token/password-grant-optional-refresh-token.step.md`

## Deleted

- 無。

## Modify

- `src/mlops_async/core/token_endpoint/password.py`
- `tests/unit/core/test_password_token_endpoint_client.py`
- `tests/conftest.py`
- `tests/unit/test_viya_e2e_pytest_guard.py`

## TestCase

1. 任一 password `client_id` 的首次 obtain 回應省略 `refresh_token` 時成功回傳 access token；以一般 client ID 與 `sas.ec` 覆蓋沒有 client-ID 分支的規則。
2. 首次 obtain 回應若存在 `refresh_token`，其值為 `None`、空白字串或非字串時仍失敗，且錯誤不洩漏 credential。
3. legacy expired token 沒有 refresh token 時仍走 password re-obtain；re-obtain 回應即使省略 refresh token 也成功，且沒有轉成 refresh grant。
4. 選取 `viya_e2e` 時，只有兩個 variables 都精確為 `1` 才通過 collection gate；缺少、其他值或僅有其中一個時拒絕。
5. live 執行前，人工確認當次 VPN 已連線；ReadOnly integration E2E 僅證明首次 password obtain 的真實端點契約。

## 實作入口 gate

- Plan-Reviewer 給出 `approved` 後，TDD 與 implementation 只能在由 Main Agent 依預期
  base 新建的 managed worktree 進行；目前承載 planning artifacts 的 worktree 不是自動可用的
  implementation worktree。
- Tester 開始 TDD 前，必須有唯讀 Git preflight 證據，確認該 worktree 的 registration、path、
  branch/expected-base 關係與 `git status --short`，並證明沒有未授權或不相關變更。
- planning artifacts 是否保留在原處、複製至新 worktree、stage 或 commit，均需獨立 human
  authorization；Implementer 不得把它們當作 implementation 的自動前置或自動處理。

## 驗收與停止條件

- 任何擬議變更超出 `Modify` 清單，或要求改動 ReadOnly 路徑時停止並重新規劃。
- live E2E 未同時具備兩個精確 opt-in 值及當次 VPN 人工確認時停止；不得以 skip、mock 或 cached token 宣告成功。
- 外部端點失敗只能輸出已遮蔽的錯誤類型；不得重試以尋求成功，也不得輸出 secret。
- 未有 Plan-Reviewer `approved`、新 managed worktree 的唯讀 Git preflight，或 planning
  artifacts 的必要 human authorization 時，TDD/implementation 必須停止。
- 版本 `0.15.1` 只可在 merge 後、另經人工 release gate 授權時處理；不是本 implementation 的完成條件。
