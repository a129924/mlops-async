# Viya Password Token E2E Technical Specification

## Execution Source of Truth

本 topic 以 `PasswordTokenEndpointClient` 的既有 password-grant contract 為 runtime baseline；不修改 production auth code。

## Design

- `tests/conftest.py` 動態註冊 `viya_e2e`，並以 process-level `RUN_VIYA_E2E=1` 保護真實網路。
- `tests/integration/viya_e2e_config.py` 只讀 worktree 的 `config/.env.test`，使用無 dependency 的 `KEY=value` parser；loader 忽略 `RUN_VIYA_E2E`。
- `tests/integration/test_viya_password_token_e2e.py` 直接將真實 `HttpClient` 傳給 password client，並以真實 httpx response event hook 只保留 status code；它不 mock 或替換 transport。
- framework 使用者必須以 `VIYA_E2E_TLS_MODE` 明確選擇 TLS 行為：
  - `system` -> `verify=True`；
  - `insecure` -> `verify=False`，並發出固定 `RuntimeWarning`；
  - `ca_bundle` -> 以非空白 `VIYA_E2E_CA_BUNDLE` 建立 `ssl.SSLContext`。
- 缺少、空白或非 exact TLS mode 必須 fail-fast；`VIYA_E2E_CA_BUNDLE` 只允許在
  `ca_bundle` mode 使用。loader 不 fallback、不切換 mode、不隱式探索其他 CA
  environment variables。
- `HttpClient` 接收 loader 解析後的 `bool | ssl.SSLContext` 與
  `RequestTimeouts(total=30)`；token response 只接受 exact status `200`。

## Security Contract

- config file 必須先通過 `git check-ignore`；不自動複製、建立或輸出。
- base URL 必須為非 loopback HTTPS origin。
- username、password、secret、Authorization header、access token 與 response body 不得出現在 failure evidence。
- `asyncio.CancelledError` 直接傳遞；其他 transport/status/JSON/schema failures 轉成已遮罩 pytest failure。
- `insecure` 是使用者的 explicit configuration，並非成功 fallback；成功報告必須明示
  TLS verification disabled，不得宣稱 TLS trust verified。

## Evidence Semantics

- HTTPS request 成功：真實 network request 到 HTTPS origin 並取得符合 contract 的
  HTTP response。
- TLS verification disabled：`insecure` mode 仍可執行 HTTPS request，但未驗證伺服器
  certificate trust／identity。
- TLS trust verified：僅能由 `system` 或 `ca_bundle` mode 下成功完成 certificate
  verification 的 run 支持；目前 post-merge live evidence 不支持此結論。

## Post-merge Validation Evidence

- Branch：`test/andrew/viya-password-token-e2e` @
  `86d0b34c5df0d6cc19696e4f00c1682cc76ce500`，worktree clean，ahead/behind upstream
  `0/0`。
- Non-E2E：pytest `311 passed, 9 skipped, 1 deselected`；Ruff passed；Pyright
  `0 errors, 0 warnings`。
- Live E2E：`1 passed, 320 deselected`；真實 network request、HTTP `200`、nonempty
  token、positive expiry。唯一正確摘要為
  `live password-token E2E passed with TLS verification explicitly disabled`。
- Topic 尚未 merge 到 `dev`；目前相對 `dev` ahead 3 commits，merge-to-dev 保持
  pending human boundary。
