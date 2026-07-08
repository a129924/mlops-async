# Request Contract Evidence Matrix

## Purpose

- 本表只分類 `tests/unit/request_contract/**` 的 request-shape 證據型態。
- 它回答兩個問題：
  - 哪些 topic 真的直接執行 `sasctl` 並攔截 outbound prepared request。
  - 哪些 topic 只是 repo-local helper、custom client、draft fixture、或 shape-only baseline。
- 本表只處理 request-shape evidence，不提供 auth proof、session/refresh proof、real transport proof、或 target runtime behavior proof。

## Evidence Classes

| Class | Meaning |
| --- | --- |
| `sasctl-direct` | 直接 import upstream `sasctl` service / session flow，並攔截其 outbound prepared request。 |
| `repo-helper-direct-path` | 使用 repo-local helper 或 direct-path helper 驅動 request；可能重用 `sasctl.Session` transport seam，但不是 upstream named positive entry。 |
| `custom-client-shape-only` | 使用 repo-local custom client 或 helper 凍結 request shape；fixture 可標 `source-observed draft`，但不等於 direct `sasctl` capture。 |
| `internal-wrapper-shape-only` | 驗 repo 內部 wrapper 或 fallback client 的 request shape，不代表 upstream source truth。 |
| `superseded-fixed-path-mvp` | 歷史 MVP artifact；保留審計痕跡，但已 superseded，不可當 current truth。 |

## Matrix

| Topic | Surface / API | Class | Upstream Evidence | Invokes `sasctl` Directly | Fixture Posture | Current Truth Reading | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `models_request_gate` | `modelRepository/models` -> `list_models`, `get_model` | `sasctl-direct` | `sasctl.ModelRepository` + `sasctl.Session` | yes | `sdk: sasctl`, `layer1-source-observed-request-shape` | 可視為 `sasctl` prepared-request evidence | 只到 prepared request semantics；不是 runtime/auth proof。 |
| `projects_request_gate` | `modelRepository/projects` -> `list_projects`, `get_project`, `get_champion_model` | `sasctl-direct` | `sasctl.ModelRepository` + `sasctl.Session` | yes | `layer1-source-observed-request-shape` | 可視為 `sasctl` prepared-request evidence | `get_champion_model` 走 `ModelRepository.get(...)` generic path，不是 named champion helper。 |
| `models_content_request_gate` | `modelRepository/models/content` -> `get_model_content` | `repo-helper-direct-path` | repo-local `invoke_get_model_content(...)` + repo docs + `sasctl.Session` transport seam | no | `abstract repository evidence`, `direct-path-only` | 不可當 direct `sasctl` endpoint truth | 它驗 direct GET path；不是 `sasctl` upstream positive entry oracle。 |
| `job_requests_jobs_request_gate` | `jobExecution/jobRequests/jobs` -> `start_job` | `repo-helper-direct-path` | repo docs + human-confirmed external source evidence + `sasctl.Session` transport seam | no | `abstract repository evidence` | 不可當 direct `sasctl` endpoint truth | baseline 來自抽象外部證據與 repo docs，不是 named `sasctl` method capture。 |
| `casmanagement_tables_list_request_gate` | `casManagement/dataSources/tables` -> `list_tables` | `custom-client-shape-only` | repo-local custom client | no | `source-observed draft`, `tests-only request gate`, `shape-only` | 不可當 `sasctl` endpoint truth | 凍結 strict `limit=1000&start=0` baseline。 |
| `casmanagement_table_get_request_gate` | `casManagement/dataSources/tables` -> `get_table` | `custom-client-shape-only` | repo-local custom client | no | `source-observed draft`, `tests-only-request-shape`, `shape-only` | 不可當 `sasctl` endpoint truth | direct `{caslib} + {tableName}` baseline only。 |
| `casmanagement_table_state_change_request_gate` | `casManagement/caslibs/tables/state` -> `change_table_state` | `custom-client-shape-only` | repo-local custom client | no | `source-observed draft`, `tests-only-request-shape`, `shape-only` | 不可當 `sasctl` endpoint truth | 只凍結 `value=loaded` direct-identifiers branch。 |
| `saslogon_token_request_gate` | `SASLogon/oauth/token` -> `obtain_access_token` | `custom-client-shape-only` | repo-local auth helper | no | `source-observed draft`, `tests-only-request-shape`, `shape-only` | 不可當 `sasctl` endpoint truth | 只凍結 `client_credentials` request shape。 |
| `saslogon_refresh_token_request_gate` | `SASLogon/oauth/token` -> `refresh_access_token` | `custom-client-shape-only` | repo-local auth helper | no | `source-observed draft`, `tests-only-request-shape`, `shape-only` | 不可當 `sasctl` endpoint truth | 只凍結 `refresh_token` request shape。 |
| `job_execution_jobs_request_gate` | `jobExecution/jobs` -> `get_job` | `internal-wrapper-shape-only` | `mlops_async._api.job_execution_jobs` or fallback client | no | minimal topic-local fixture | 不可當 upstream source truth | 這是內部 wrapper request gate，不是 `sasctl` capture。 |
| `job_execution_jobs_state_request_gate` | `jobExecution/jobs/state` -> `get_job_state` | `internal-wrapper-shape-only` | `mlops_async._api.job_execution_jobs_state` or fallback client | no | minimal topic-local fixture | 不可當 upstream source truth | 這是內部 wrapper request gate，不是 `sasctl` capture。 |
| `projects_tables_link_request_gate` | `modelRepository/projects -> tables-link surface` -> `list_tables` | `superseded-fixed-path-mvp` | repo-local fixed-path client | no | `implementation-facing draft`, `implementation-facing-fixed-path-request-shape`, `intentionally_changed` | 不可當 current truth；已 superseded | 歷史 fixed-path MVP artifact；不代表 upstream `sasctl` endpoint。 |

## Reading Rules

- 只有 `Class = sasctl-direct` 的 rows 可以被描述成「直接執行 `sasctl` 並攔截 prepared request」。
- `repo-helper-direct-path` 仍可能有攔截到 outbound request，但它不是 upstream named source truth。
- `custom-client-shape-only` 與 `internal-wrapper-shape-only` 只能描述成 repo-defined request baseline。
- `projects_tables_link_request_gate` 僅保留為 superseded 歷史 artifact，不應再作為 merge、porting、或 runtime alignment 的依據。