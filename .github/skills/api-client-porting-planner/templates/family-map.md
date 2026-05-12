# Endpoint family map template

Use this template for `api-client-porting-planner` output. Keep unknown values explicit; do not infer missing source behavior.

## Planner metadata

- Planner skill: `api-client-porting-planner`
- Source SDK / repository:
- Source commit, tag, or package version:
- Endpoint family:
- Family boundary reason:
- Target repository / project:
- Planning date:
- Planner status: `COMPLETE` | `INCOMPLETE` | `BLOCKED`

## Source API list

| SDK | Module | Function | File | Line range | Commit/version | Notes |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Request contract drafts

### `<source function>`

```yaml
source:
  sdk:
  module:
  function:
  file:
  line_range:
  commit:
request_contract:
  method:
  path:
  required_headers:
  query_params:
  body:
  auth_behavior:
risk: low | medium | high
stop_flags:
  upload_download: false
  streaming: false
  polling_job_wait: false
  retry: false
  pagination_expansion: false
  global_session_side_effects: false
  conditional_endpoint_selection: false
  unclear_source_behavior: false
  non_wrapper_complex_behavior: false
human_review_notes:
  -
```

## Endpoint family map

| Source function | Endpoint family | Method | Path pattern | Request pattern | Risk | Stop flags |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Porting order

1.
2.
3.

## Same-family batch candidates

List only candidates with sufficient request-contract evidence. Leave empty when evidence is insufficient.

- Candidate:
  - Evidence:
  - Exclusions:

## Human-review notes

- Missing source evidence:
- Ambiguous behavior:
- Stop flags requiring review:
- APIs intentionally excluded from batching:

## Workflow state

- current_step:
- next_step:
- status: `IN_PROGRESS` | `COMPLETE` | `INCOMPLETE` | `BLOCKED`
