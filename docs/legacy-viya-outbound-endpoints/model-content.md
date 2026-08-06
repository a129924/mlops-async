# Model content handoff

## Legacy observation

- Legacy model-file content 優先依 response link；另有
  `GET /modelRepository/models/{model_id}/contents/{file_id}/content` 的 project flow。

## Upstream/evidence

- `docs/api-endpoints/swagger-spec/upstream/modelRepository-openapi.yml` 與 repo-local
  `docs/api-endpoints/swagger-spec/models-spec.yaml` 是 path evidence。
- `models_content_request_gate` 為 `repo-helper-direct-path` /
  `upstream-aligned`，可作 direct-path request baseline，不能稱作 named `sasctl` capture。

## Current repo evidence

- `tests/unit/request_contract/models_content_request_gate/` 有 direct-path request gate；
  沒有 runtime client 或 response payload parser。

## Difference

- legacy 的 hypermedia link 行為與 fixed path 的優先序尚未決定；request header subset
  `If-Range`、`Range`、`Access-Quarantine` 已由 evidence matrix 凍結；下載 payload、
  content type 與檔案類型語意仍未有 target contract。

## Disposition

- 獨立 topic；不得與 models list/get 或 content parsing 合併成未界定的 batch。

## Human decision required

- 指定 link vs fixed path compatibility、成功 payload representation 與 content-type policy。

## Target mapping
