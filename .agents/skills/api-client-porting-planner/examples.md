# API client porting planner examples

## Positive example: same-family source discovery

Good planner output:

- lists each source function with SDK, module, function, file, line range, and version evidence
- groups APIs by endpoint family instead of target class guesses
- drafts request contracts with method, path, required headers, query params, body, and auth behavior
- marks pagination, upload/download, polling, or conditional endpoint selection as stop flags
- recommends same-family batching only after multiple request contracts show a shared pattern
- leaves implementation, tests, and response schemas to downstream workflows

## Negative example: inferred implementation plan

Bad behavior:

- writes target async method names or pseudocode before source evidence is recorded
- infers REST paths from names without file and line references
- treats source global session behavior as a target design requirement
- batches unrelated families because they share the same base URL

Correct response:

- mark affected APIs `high` risk or `needs-human-review`
- remove cross-family batch recommendations
- request or record source file and version evidence before implementation starts

## Minimal planner output sketch

```yaml
family: model-repository
source_version: sasctl 1.x or commit <sha>
family_boundary_reason: same source module and shared route pattern
apis:
  - source:
      sdk: sasctl
      module: sasctl.services.model_repository
      function: list_models
      file: path/to/source.py
      line_range: 10-45
      commit: <version-or-sha>
    request_contract:
      method: GET
      path: /modelRepository/models
      required_headers: [Authorization]
      query_params:
        limit: optional integer
      body: none
      auth_behavior: bearer token from source session
    risk: medium
    stop_flags:
      pagination_expansion: true
      upload_download: false
      streaming: false
      polling_job_wait: false
      retry: false
      global_session_side_effects: false
      conditional_endpoint_selection: false
      unclear_source_behavior: false
      non_wrapper_complex_behavior: false
    human_review_notes:
      - Pagination semantics require review before batch expansion.
```
