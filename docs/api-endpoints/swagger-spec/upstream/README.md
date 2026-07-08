# 官方 OpenAPI YAML 上游對照

本目錄保存從 SAS Developer Portal 下載的官方原始 `openapi.yml`。

- 只保存上游原始 YAML。
- 不在此目錄做 merge、改寫、JSON 轉檔、或 path normalization。
- 既有 `docs/api-endpoints/swagger-spec/*.yaml` 仍是 repo-local 整理版，不被本目錄覆寫。

## 下載來源

| Local file | REST API page | Download URL | Repo-local mapping |
| --- | --- | --- | --- |
| `modelRepository-openapi.yml` | [Model Repository](https://developer.sas.com/rest-apis/modelRepository) | [openapi.yml](https://developer.sas.com/api/apis/modelRepository/specifications/openapi.yml) | `models-spec.yaml`、`projects-spec.yaml` |
| `jobExecution-openapi.yml` | [Job Execution](https://developer.sas.com/rest-apis/jobExecution) | [openapi.yml](https://developer.sas.com/api/apis/jobExecution/specifications/openapi.yml) | `jobs-spec.yaml` |
| `SASLogon-openapi.yml` | [SAS Logon](https://developer.sas.com/rest-apis/SASLogon) | [openapi.yml](https://developer.sas.com/api/apis/SASLogon/specifications/openapi.yml) | `authentication-spec.yaml` |
| `dataTables-v3-openapi.yml` | [Data Tables](https://developer.sas.com/rest-apis/dataTables) | [openapi.yml](https://developer.sas.com/api/apis/dataTables-v3/specifications/openapi.yml) | `tables-spec.yaml` 的 list/get table 路徑 |
| `casManagement-openapi.yml` | [CAS Management](https://developer.sas.com/rest-apis/casManagement) | [openapi.yml](https://developer.sas.com/api/apis/casManagement/specifications/openapi.yml) | `tables-spec.yaml` 的 table state 路徑 |

## 凍結 mapping 規則

- `models-spec.yaml` 與 `projects-spec.yaml` 的 upstream source-of-truth 都是 `modelRepository-openapi.yml`，不是獨立的 Projects API。
- `tables-spec.yaml` 不是單一 upstream family：
  - list/get table 對照 `dataTables-v3-openapi.yml`
  - table state 對照 `casManagement-openapi.yml`
- 歷史 `modelRepository/projects/{project_id}/tables` fixed-path MVP 不在此目錄下載，也不得映射為官方 current truth。

## Path Normalization Notes

官方 raw spec 若使用 service-root-relative path，保持原樣，不回寫成 repo 現在的 gateway-prefixed path。

| Official raw path shape | Repo-local path shape | Note |
| --- | --- | --- |
| `/oauth/token` | `/SASLogon/oauth/token` | repo-local 版本補上 gateway/service prefix |
| `/jobs/...`、`/jobRequests/...` | `/jobExecution/...` | repo-local 版本補上 `jobExecution` prefix |
| `/models/...`、`/projects/...` | `/modelRepository/...` | repo-local 版本補上 `modelRepository` prefix |
| `/dataSources/{dataSourceId}/tables...` | `/casManagement/dataSources/cas~fs~cas-shared-default~fs~{caslib}/tables...` | repo-local 版本把 `dataSourceId` 具體化，且保留現有 gateway path |
| `/servers/{serverName}/caslibs/{caslibName}/tables/{tableName}/state` | `/casManagement/servers/cas-shared-default/caslibs/{caslib}/tables/{tableName}/state` | repo-local 版本把 `serverName` 具體化為 `cas-shared-default` |

## Divergence 與 Historical Notes

- `projects-spec.yaml` 不應透過下載 Projects API 來對照；目前 repo 的 projects / champion surface 已由 `modelRepository-openapi.yml` 承載。
- `tables-spec.yaml` 故意把兩個 upstream family 整理到同一份 repo-local spec；本目錄保留拆開的官方原始來源。
- `request-gate-projects-tables-fixed-path-mvp` 仍是 superseded historical artifact，僅保留 implementation-facing fixed-path draft 的歷史語境；不可視為 upstream official endpoint truth。
- 本輪不重建 `openapi-complete.yaml`，也不回寫既有 repo-local 拆分 spec。
