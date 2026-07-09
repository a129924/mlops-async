# Request Contract Evidence Matrix

## Purpose

- ???? `tests/unit/request_contract/**` ? request-shape evidence ????????
- ?? authority boundary ???????? implementer ????? test surface ??
  upstream endpoint truth?
- ??????? request truth consumption???? runtime proof?auth proof??
  response contract proof?

## Evidence Classes

| Class | Meaning | Authority class | Default allowed use |
| --- | --- | --- | --- |
| `sasctl-direct` | ??? `sasctl` service / session flow ??? outbound prepared request | `upstream-aligned` | `implementation-truth` |
| `repo-helper-direct-path` | ? repo-local helper ? direct-path helper ??? request??? named `sasctl` capture | `upstream-aligned` | `implementation-truth` |
| `custom-client-shape-only` | repo-local custom client / helper ??? request shape | `non-authoritative-shape-only` | `keep-as-shape-baseline` |
| `internal-wrapper-shape-only` | repo ? wrapper ? fallback client ? request shape | `non-authoritative-shape-only` | `keep-as-shape-baseline` |
| `superseded-fixed-path-mvp` | ?? fixed-path MVP artifact??? superseded | `historical-superseded` | `keep-as-historical-only` |

## Matrix

| Topic | Surface / API | Evidence class | Authority class | Allowed use | Current truth reading | Forbidden use |
| --- | --- | --- | --- | --- | --- | --- |
| `models_request_gate` | `modelRepository/models` -> `list_models`, `get_model` | `sasctl-direct` | `upstream-aligned` | `implementation-truth` | `sasctl` prepared-request evidence | ????? runtime/auth proof |
| `projects_request_gate` | `modelRepository/projects` -> `list_projects`, `get_project` | `sasctl-direct` | `upstream-aligned` | `implementation-truth` | `sasctl` prepared-request evidence | ????? runtime/auth proof |
| `projects_request_gate.get_champion_model` | `modelRepository/projects/champion` -> `get_champion_model` | `sasctl-direct` | `upstream-aligned` | `implementation-truth` | generic-path capture??? named champion helper proof | ??? legacy-source metadata ????? authority |
| `models_content_request_gate` | `modelRepository/models/content` -> `get_model_content` | `repo-helper-direct-path` | `upstream-aligned` | `implementation-truth` | repo docs + transport seam ??? direct-path truth | ????? direct `sasctl` endpoint truth |
| `job_requests_jobs_request_gate` | `jobExecution/jobRequests/jobs` -> `start_job` | `repo-helper-direct-path` | `upstream-aligned` | `implementation-truth` | repo docs + external evidence ??? request truth | ????? named `sasctl` capture |
| `casmanagement_tables_list_request_gate` | `casManagement/dataSources/tables` -> `list_tables` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? strict `limit=1000&start=0` repo-local baseline | ??? upstream endpoint truth |
| `casmanagement_table_get_request_gate` | `casManagement/dataSources/tables` -> `get_table` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? direct `{caslib} + {tableName}` repo-local baseline | ??? upstream endpoint truth |
| `casmanagement_table_state_change_request_gate` | `casManagement/caslibs/tables/state` -> `change_table_state` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? `value=loaded` repo-local baseline | ??? upstream endpoint truth |
| `saslogon_token_request_gate` | `SASLogon/oauth/token` -> `obtain_access_token` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? `client_credentials` request baseline | ??? upstream token truth |
| `saslogon_refresh_token_request_gate` | `SASLogon/oauth/token` -> `refresh_access_token` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? `refresh_token` request baseline | ??? upstream token truth |
| `job_execution_jobs_request_gate` | `jobExecution/jobs` -> `get_job` | `internal-wrapper-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? repo-local wrapper baseline | ??? upstream source truth |
| `job_execution_jobs_state_request_gate` | `jobExecution/jobs/state` -> `get_job_state` | `internal-wrapper-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ??? repo-local wrapper baseline | ??? upstream source truth |
| `projects_tables_link_request_gate` | `modelRepository/projects -> tables-link surface` -> `list_tables` | `superseded-fixed-path-mvp` | `historical-superseded` | `keep-as-historical-only` | ?? fixed-path MVP ?? | ??? current truth???? implementation baseline |

## Reading Rules

- ?? `Authority class` ? `Allowed use`????? test / fixture?
- `implementation-truth` ?????? implementation ? request baseline???????? runtime proof?
- `keep-as-shape-baseline` ?????? repo-local request shape??????? upstream endpoint truth?
- `keep-as-historical-only` ?????????????? current implementation routing?
- ????? `pseudo-endpoint-or-contract`??????? `delete-candidate` ??????? topic??????? current truth?
