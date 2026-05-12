# API client porting planner examples

## Positive example: same-family source discovery

Input:

- Source SDK: `sasctl`
- Endpoint family: model repository
- Source version: installed package version or repository commit
- Goal: plan request-contract extraction only

Good output behavior:

- Lists each source function with SDK, module, function, file, line range, and version.
- Groups functions by endpoint family instead of target class guesses.
- Drafts request contracts with method, path, required headers, query params, body, and auth behavior.
- Classifies simple GET/POST wrappers as `low` only when request construction is fully visible.
- Marks pagination, upload/download, polling, or conditional endpoint selection as stop flags.
- Recommends same-family batch candidates only after multiple request contracts show a shared pattern.
- Leaves implementation, tests, response schemas, and ledger updates to downstream workflows.

## Negative example: inferred implementation plan

Bad behavior:

- Writes target async method names and pseudocode before source evidence is recorded.
- Infers REST paths from function names without file and line references.
- Treats source global session behavior as a target design requirement.
- Groups unrelated model, folder, and job APIs into one batch because they use the same base URL.
- Marks APIs as low risk even though they include polling or upload/download behavior.

Correct response:

- Mark the affected APIs `high` risk or `needs-human-review`.
- Remove cross-family batch recommendations.
- Ask for or record source file/version evidence before implementation starts.

## Positive example: legacy repository handoff

Input:

- Source SDK: legacy `sas-api` repository
- Endpoint family: deployment endpoints
- Source location: `<path-to-legacy-sas-api-checkout>`

Good output behavior:

- Uses repository paths and commit/version evidence to cite source functions.
- Separates deployment CRUD wrappers from job wait or status polling helpers.
- Marks polling/job wait as a stop flag even when the underlying endpoint path is clear.
- Produces a porting order that starts with clear request wrappers and defers orchestration helpers.
- Adds human-review notes for any behavior that is business logic rather than an HTTP wrapper.

## Negative example: over-broad batching

Bad recommendation:

> The SDK has a consistent session object, so port all folder, model, deployment, and job APIs in one implementation batch.

Why this is wrong:

- Shared auth or session infrastructure is not an endpoint family boundary.
- Request contracts may differ by resource, method, path, body shape, pagination, and lifecycle semantics.
- The planner must not batch across endpoint families.

Correct recommendation:

- Keep one endpoint family per map.
- Recommend only same-family candidates with request-contract evidence.
- Add human-review notes when evidence is insufficient.

## Minimal planner output sketch

```yaml
family: model-repository
source_version: sasctl 1.x or commit <sha>
family_boundary_reason: same source module and shared model repository route pattern
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
porting_order:
  - list_models after pagination behavior is reviewed
same_family_batch_candidates: []
```
