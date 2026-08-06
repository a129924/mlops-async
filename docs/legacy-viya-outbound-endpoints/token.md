# Token handoff

## Legacy observation

- Legacy 使用 `POST {base}/SASLogon/oauth/token`、HTTP Basic，以及 password 或
  refresh-token form grant；legacy transport 的 `verify=False` 不是可攜行為。

## Upstream/evidence

- `docs/api-endpoints/swagger-spec/upstream/SASLogon-openapi.yml` 是 SAS Logon 的
  raw upstream snapshot；其 path 為 service-root-relative `/oauth/token`。
- request evidence matrix 將舊 obtain/refresh gates 分類為
  `non-authoritative-shape-only`，不得以它們證明 upstream token contract。

## Current repo evidence

- `src/mlops_async/core/token_endpoint/password.py` 與
  `src/mlops_async/core/token_endpoint/client_credentials.py` 已提供 token runtime。
- `tests/unit/request_contract/saslogon_token_request_gate/` 與
  `saslogon_refresh_token_request_gate/` 只保存 request-shape baseline。

## Difference

- Legacy 的 TLS verification 取捨不可帶入；目前 runtime 與 legacy 之完整
  response/error/session compatibility 並未由本文件聲稱。

## Disposition

- 不重做 token runtime。只有確有 legacy 相容性缺口時，才建立 token-only topic。

## Human decision required

- 是否有具體的 token compatibility gap，且是否需要獨立於 endpoint MVP 排程？

## Target mapping
