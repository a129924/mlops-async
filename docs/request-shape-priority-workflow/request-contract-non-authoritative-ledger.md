# Request Contract Non-Authoritative Ledger

## Purpose

- This table centralizes the authority class, allowed use, and forbidden use for
  non-authoritative request-contract topics.
- Its purpose is to let an implementer know, before opening a test surface,
  which topics are only shape baselines and which are historical-only traces.

## Handling Table

| Topic | Authority class | Allowed use | Default handling | Forbidden use |
| --- | --- | --- | --- | --- |
| `projects_tables_link_request_gate` | `historical-superseded` | `keep-as-historical-only` | Keep the files as audit trace; skip by default outside explicit topic-scoped runs. | Do not treat it as current endpoint truth or implementation baseline. |
| `job_execution_jobs_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the wrapper request-shape baseline. | Do not treat it as upstream source truth. |
| `job_execution_jobs_state_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the wrapper request-shape baseline. | Do not treat it as upstream source truth. |
| `casmanagement_tables_list_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the custom-client request baseline. | Do not treat it as upstream endpoint truth. |
| `casmanagement_table_get_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the custom-client request baseline. | Do not treat it as upstream endpoint truth. |
| `casmanagement_table_state_change_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the custom-client request baseline. | Do not treat it as upstream endpoint truth. |
| `saslogon_token_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the auth-helper request baseline. | Do not treat it as upstream token truth. |
| `saslogon_refresh_token_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | Keep the auth-helper request baseline. | Do not treat it as upstream token truth. |

## Consumption Rule

1. Read the upstream raw spec, the repo-local normalized spec, and `request-contract-evidence-matrix.md` first.
2. Only `implementation-truth` may directly feed an implementation request baseline.
3. `keep-as-shape-baseline` preserves repo-local request shape only; it must not be used to derive upstream endpoints.
4. `keep-as-historical-only` preserves audit history only; reactivation requires a new topic and a fresh truth-source justification.
