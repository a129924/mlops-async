# Request Contract Non-Authoritative Ledger

## Purpose

- ???? non-authoritative request-contract topics ? authority class?allowed use???????
- ? implementer ?????? tests ????? surface ??? shape baseline??????????

## Handling Table

| Topic | Authority class | Allowed use | Default handling | Forbidden use |
| --- | --- | --- | --- | --- |
| `projects_tables_link_request_gate` | `historical-superseded` | `keep-as-historical-only` | ??????????? topic-scoped run ?? skip | ??? current endpoint truth???? implementation baseline |
| `job_execution_jobs_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? wrapper request-shape baseline | ??? upstream source truth |
| `job_execution_jobs_state_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? wrapper request-shape baseline | ??? upstream source truth |
| `casmanagement_tables_list_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? custom-client request baseline | ??? upstream endpoint truth |
| `casmanagement_table_get_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? custom-client request baseline | ??? upstream endpoint truth |
| `casmanagement_table_state_change_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? custom-client request baseline | ??? upstream endpoint truth |
| `saslogon_token_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? auth helper request baseline | ??? upstream token truth |
| `saslogon_refresh_token_request_gate` | `non-authoritative-shape-only` | `keep-as-shape-baseline` | ?? auth helper request baseline | ??? upstream token truth |

## Consumption Rule

1. ?? upstream raw spec?repo-local normalized spec?`request-contract-evidence-matrix.md`?
2. ?? `implementation-truth` ?????? implementation ? request baseline?
3. `keep-as-shape-baseline` ????? repo-local request shape?????? endpoint?
4. `keep-as-historical-only` ??????????????? surface????? topic ????? truth source?
