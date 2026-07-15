# PasswordTokenEndpointClient Requirements Baseline

## Goal

將 token-endpoint 的兩個 OAuth grant concrete clients 收斂為同一 internal capability family，並新增可透過既有 `TokenEndpointClientProtocol` 使用的 password-grant client。

## In-Scope

- `core/token_endpoint/` 內的 shared logic、client-credentials implementation 與 password implementation。
- 保留 `token_endpoint_client.py` 作為既有 internal import 的 compatibility re-export。
- fake-transport unit tests、topic planning artifacts，以及 TDD verdict artifact。

## Out-Of-Scope

- 改動 `auth.py` 的 lifecycle/orchestration、`TokenManager`、`TokenEndpointClientProtocol`、`AuthProvider` 或 transport lifecycle。
- public `AuthClient`、package-root export、CLI、environment variable、credential persistence、real Viya E2E。
- OAuth refresh-token、authorization-code、Kerberos、browser login、retry、timeout 或 concurrency redesign。

## Functional Requirements

1. `PasswordTokenEndpointClient` 必須以 `POST /SASLogon/oauth/token` 取得既有 `AccessToken`。
2. password request 的 Basic authorization 承載 client ID/secret；form 僅含 `grant_type=password`、`username`、`password`。
3. PasswordTokenEndpointClient 的 username、password、client ID 必須於 construction 時拒絕空白或僅含空白字元的字串；client secret 亦同，但精確 `client_id` 為 `sas.ec` 時僅允許空字串 `""` 作為例外，僅含空白字元的 secret 仍須拒絕。此例外不得套用至 `TokenEndpointClient` 的 client-credentials flow。
4. PasswordTokenEndpointClient 的 `sas.ec` 例外 Basic authorization 必須以 `sas.ec:` 作為編碼前的 client credential 組合；任何非 `sas.ec` client ID 搭配空白或空的 client secret，以及 client-credentials flow 的任一空或空白 client secret，均必須失敗。
5. 兩個 grants 必須共用 endpoint、error、credential validation、token response parsing 與 expiry conversion 的純邏輯。
6. `TokenEndpointClient` 的 client-credentials request contract 與既有 internal import path 必須保持相容。
7. password refresh 必須重新執行 password obtain；不實作 OAuth refresh-token grant。
8. credentials、Basic header 與 access token 不得進入 log、exception、assertion message 或 fake transport record。

## P1 Corrective-Test Rework Routing

此 `sas.ec` exception 是 initial production implementation 後的 P1 corrective-test rework。既有 `plan/password-token-endpoint-client/password-token-endpoint-client.tdd-test-authoring.yaml` 是舊的 strict-non-empty contract 的 historical evidence，必須保留且不得重跑 `python-tdd-test-authoring`、不得產生新的 RED verdict 或修改該 YAML。

Plan-Reviewer 核准此 correction 後，Implementer 必須先在 fake-transport tests 新增並執行下列 concrete corrective cases，再修改 production implementation：

1. `PasswordTokenEndpointClient` 接受精確 `sas.ec` 與 `""` secret，並以 redacted structural evidence 驗證 Basic input `sas.ec:`。
2. PasswordTokenEndpointClient 拒絕所有非 `sas.ec` 的 empty/whitespace-only secret，並拒絕 `sas.ec` 的 whitespace-only secret。
3. `TokenEndpointClient` 對 `sas.ec` 與 empty secret 仍拒絕，維持 client-credentials strict regression。

接著才可修改 shared validation 與 password-grant implementation，執行 scoped/full validation，再依序進入 Implementation Review 與 Code Review。

## Release / PR Boundary

`README.md`、`VERSION`、`pyproject.toml`、release、commit、push、PR 與 PR comment 均屬 human authorization boundary。此 topic 可在 publish/release assessment 中讀取它們，但未獲獨立 human 指示不得修改或執行發佈動作。
