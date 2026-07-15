# PasswordTokenEndpointClient 規格

## 驗收條件

1. `core/token_endpoint/` 含有 locked files；`auth.py` 保持僅負責 lifecycle 且不變更。
2. `_shared.py` 承擔 AuthTokenEndpoint、token-endpoint errors、credential validation、response parsing 與 expiry conversion support。
3. TokenEndpointClient 移至 `client_credentials.py`，並保留既有 request contract。
4. PasswordTokenEndpointClient 對 `/SASLogon/oauth/token` 發送 password grant，以 Basic auth 傳遞 client credentials，form body 僅含 `grant_type=password`、`username`、`password`。
5. Compatibility module re-export legacy symbols，且不實作 grant request。
6. 兩個 clients 皆以既有 error model 拒絕無效 credentials/responses、回傳 AccessToken，且不暴露 sensitive values；唯一 credential 例外為 PasswordTokenEndpointClient 的精確 `client_id == "sas.ec"` 搭配空字串 `client_secret`。
7. password refresh 透過 password grant 重新取得 token，不使用 OAuth refresh-token。
8. P1 corrective-test rework 必須先新增並執行 `sas.ec` empty-secret acceptance、non-`sas.ec`/whitespace-secret rejection、client-credentials strict-regression cases，再修改 implementation；historical TDD YAML 不得重跑或更新。

## 行為情境

### 情境 1：client-credentials 遷移維持相容

- **Given** 已注入 fake transport 與有效 client credentials。
- **When** TokenEndpointClient 透過 compatibility import 取得 token。
- **Then** 它將既有 client-credentials form POST 至既有 endpoint，並回傳 AccessToken。

### 情境 2：password grant 取得 token

- **Given** 已注入 fake transport 與有效 user/client credentials。
- **When** PasswordTokenEndpointClient 取得 token。
- **Then** 它 POST urlencoded password form，使用 Basic client auth，並回傳已解析的 AccessToken。

### 情境 3：password refresh 重新取得 token

- **Given** 既有 AccessToken 與 password client。
- **When** 呼叫 refresh_access_token。
- **Then** 它再次發送 password obtain，且不使用 refresh-token grant。

### 情境 4：`sas.ec` 空 secret 的精確 Basic 例外

- **Given** 已注入 fake transport、有效 username/password，以及精確 `client_id` `sas.ec` 與空字串 client secret。
- **When** PasswordTokenEndpointClient 取得 token。
- **Then** 它接受此唯一例外，以 `sas.ec:` 作為 Basic 的編碼前組合，並在 redacted structural record 中驗證行為而不保存 raw header。

### 情境 5：TokenManager 使用 protocol lifecycle

- **Given** 既有 storage 中有過期 token，且以 PasswordTokenEndpointClient 作為 fetcher。
- **When** TokenManager 解析 token。
- **Then** 它呼叫 Protocol refresh 並儲存新的 AccessToken，且不變更 auth.py。

### 情境 6：P1 corrective-test 的 client-credentials strict regression

- **Given** TokenEndpointClient 使用精確 `client_id` `sas.ec` 與空字串 client secret。
- **When** 建構 client-credentials client。
- **Then** 它仍以既有 `TokenEndpointClientError` 失敗；此 exception 不得套用至 client-credentials flow。

## 錯誤與邊界情況

- username、password、client ID 的空白或僅含空白字元值在建構時失敗，且不回顯其值。
- PasswordTokenEndpointClient 的 client secret 空白或僅含空白字元值在建構時失敗；唯一例外是精確 `client_id == "sas.ec"` 搭配精確空字串 secret。`sas.ec` 的僅含空白字元 secret，以及所有其他 client ID 的空或空白 secret 均失敗且不回顯其值。TokenEndpointClient 的 client-credentials flow 對所有 client ID（含 `sas.ec`）均維持拒絕空或空白 secret。
- 非 object response、缺失或空白的 access_token，以及值為零、負數、string 或 bool 的 expires_in，均以 TokenEndpointClientError 失敗。
- user credential 的保留字元必須正確 encode；client credentials 不得進入 password form。
- fake records、assertions、exceptions、logs 與 reviewer evidence 不得包含任何 raw sensitive values。
- CancelledError 與 transport failures 保持既有 TokenManager 行為；不得新增 timeout/retry handling。

### P1 corrective-test routing

- `tdd-test-authoring.yaml` 是 immutable historical evidence：P1 將它視為 ReadOnly，禁止 rewrite，亦禁止 rerun `python-tdd-test-authoring`。
- P1 讓 `client_credentials.py` 維持 ReadOnly 與 diff-free，且 `require_non_empty_string()` 不變。僅 `test_token_endpoint_client.py` 可為 client-credentials strict regression 修改。
- `sas.ec` exception helper 僅屬 password，只能由 `password.py` 使用；P1 production diff 僅限 `_shared.py` 與 `password.py`。

- 既有 `tdd-test-authoring.yaml` 是 initial strict-non-empty contract 的 historical evidence，不得更新或重跑 `python-tdd-test-authoring`，也不要求新的 RED verdict。
- Plan Review 核准後，Implementer 先於 password tests 新增/執行 `sas.ec` acceptance 與 non-`sas.ec`/whitespace rejection，並於 client-credentials tests 新增/執行 strict regression；再做 minimal shared/password implementation change、scoped/full validation、Implementation Review、Code Review。
