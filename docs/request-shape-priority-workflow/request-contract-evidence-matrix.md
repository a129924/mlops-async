# Request Contract Evidence Matrix

## Purpose

- This table normalizes the request-shape evidence types under `tests/unit/request_contract/**`.
- Its first job is to make the authority boundary explicit before an implementer reads any single test surface.
- This table only governs request-truth consumption. It does not claim runtime proof, auth proof,
  session or refresh proof, or response-contract proof.

## Evidence Classes

| Class | Meaning | Authority class | Default allowed use |
| --- | --- | --- | --- |
| `sasctl-direct` | Observed outbound prepared requests produced directly by upstream `sasctl` service or session flows. | `upstream-aligned` | `implementation-truth` |
| `repo-helper-direct-path` | Observed requests driven by a repo-local helper or direct-path helper; may reuse the `sasctl.Session` transport seam but is not an upstream named positive-entry capture. | `upstream-aligned` | `implementation-truth` |
| `custom-client-shape-only` | Request shapes frozen by a repo-local custom client or helper; preserves a shape baseline but is not direct `sasctl` capture. | `non-authoritative-shape-only` | `keep-as-shape-baseline` |
| `internal-wrapper-shape-only` | Request shapes frozen by an internal repo wrapper or fallback client; only a repo-local baseline. | `non-authoritative-shape-only` | `keep-as-shape-baseline` |
| `superseded-fixed-path-mvp` | Historical fixed-path MVP artifact retained for audit, but already superseded. | `historical-superseded` | `keep-as-historical-only` |

## Matrix

| Topic | Surface / API | Evidence class | Authority class | Allowed use | Current truth reading | Forbidden use |
| --- | --- | --- | --- | --- | --- | --- |
| `models_request_gate` | `modelRepository/models` -> `list_models`, `get_model` | `sasctl-direct` | `upstream-aligned` | `implementation-truth` | Valid `sasctl` prepared-request evidence. | Do not expand into runtime or auth proof. |
| `projects_request_gate` | `modelRepository/projects` -> `list_projects`, `get_project` | `sasctl-direct` | `upstream-aligned` | `implementation-truth` | Valid `sasctl` prepared-request evidence. | Do not expand into runtime or auth proof. |
| `projects_request_gate.get_champion_model` | `modelRepository/projects/champion` -> `get_champion_model` | `sasctl-direct` | `upstream-aligned` | `implementation-truth` | Read only as generic-path prepared-request capture. | Do not inflate legacy-source metadata into named champion-helper truth. |
| `models_content_request_gate` | `modelRepository/models/content` -> `get_model_content` | `repo-helper-direct-path` | `upstream-aligned` | `implementation-truth` | Direct-path request truth supported by repo docs and the transport seam. | Do not describe it as direct `sasctl` endpoint truth. |
| `job_requests_jobs_request_gate` | `jobExecution/jobRequests/jobs` -> `start_job` | `repo-helper-direct-path` | `upstream-aligned` | `implementation-truth` | Request truth supported by repo docs and external evidence. | Do not describe it as a named `sasctl` capture. |
| `casmanagement_tables_list_request_gate` | `casManagement/dataSources/tables` -> `list_tables` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the strict `limit=1000&start=0` repo-local baseline. | Do not treat it as upstream endpoint truth. |
| `casmanagement_table_get_request_gate` | `casManagement/dataSources/tables` -> `get_table` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the direct `{caslib} + {tableName}` repo-local baseline. | Do not treat it as upstream endpoint truth. |
| `casmanagement_table_state_change_request_gate` | `casManagement/caslibs/tables/state` -> `change_table_state` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the `value=loaded` repo-local baseline. | Do not treat it as upstream endpoint truth. |
| `saslogon_token_request_gate` | `SASLogon/oauth/token` -> `obtain_access_token` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the `client_credentials` request baseline. | Do not treat it as upstream token truth. |
| `saslogon_refresh_token_request_gate` | `SASLogon/oauth/token` -> `refresh_access_token` | `custom-client-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the `refresh_token` request baseline. | Do not treat it as upstream token truth. |
| `job_execution_jobs_request_gate` | `jobExecution/jobs` -> `get_job` | `internal-wrapper-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the repo-local wrapper baseline. | Do not treat it as upstream source truth. |
| `job_execution_jobs_state_request_gate` | `jobExecution/jobs/state` -> `get_job_state` | `internal-wrapper-shape-only` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep only the repo-local wrapper baseline. | Do not treat it as upstream source truth. |
| `projects_tables_link_request_gate` | `modelRepository/projects -> tables-link surface` -> `list_tables` | `superseded-fixed-path-mvp` | `historical-superseded` | `keep-as-historical-only` | Keep only the historical fixed-path MVP trace. | Do not treat it as current truth or implementation baseline. |

## Reading Rules

- Read `Authority class` and `Allowed use` before reading any single test or fixture.
- `implementation-truth` can feed an implementation request baseline, but it is not runtime proof by itself.
- `keep-as-shape-baseline` preserves repo-local request shape only and must not be used to invent upstream endpoints.
- `keep-as-historical-only` preserves audit history only and must not re-enter current implementation routing.
- If a future topic is classified as `pseudo-endpoint-or-contract`, it can only become a `delete-candidate`
  or move into a new historical-governance topic; it cannot be promoted back to current truth directly.
