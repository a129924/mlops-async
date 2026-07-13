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
3. username、password、client ID、client secret 必須於 construction 時拒絕空白字串。
4. 兩個 grants 必須共用 endpoint、error、credential validation、token response parsing 與 expiry conversion 的純邏輯。
5. `TokenEndpointClient` 的 client-credentials request contract 與既有 internal import path 必須保持相容。
6. password refresh 必須重新執行 password obtain；不實作 OAuth refresh-token grant。
7. credentials、Basic header 與 access token 不得進入 log、exception、assertion message 或 fake transport record。

## Release / PR Boundary

`README.md`、`VERSION`、`pyproject.toml`、release、commit、push、PR 與 PR comment 均屬 human authorization boundary。此 topic 可在 publish/release assessment 中讀取它們，但未獲獨立 human 指示不得修改或執行發佈動作。
