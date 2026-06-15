# API client porting planner reference

## Required evidence

Every source API entry must be traceable before an implementer receives it:

- `sdk`
- `module`
- `function`
- `file`
- `line_range`
- `commit`

If any required field is missing, keep the API in the output, mark affected contract fields `unknown`, and add human-review notes. Block only when the missing evidence would make family boundaries, request behavior, or risk classification misleading.

## Request contract fields

Draft one request contract per source API:

```yaml
request_contract:
  method:
  path:
  required_headers:
  query_params:
  body:
  auth_behavior:
```

Capture semantic behavior, not transport noise. Do not require query order, generated headers, host, content length, or live service availability.

## Risk classification

- `low`: thin wrapper with clear method, path, auth, payload behavior, and no stop flags
- `medium`: mostly clear wrapper with one contained uncertainty that does not change the endpoint family
- `high`: stop flag, unclear request construction, global session mutation, multi-step orchestration, or behavior that could materially change implementation order

## Mandatory stop flags

Check every API for:

- upload/download
- streaming
- polling or job wait
- retry behavior
- pagination expansion
- global session side effects
- conditional endpoint selection
- unclear source behavior
- non-wrapper complex behavior

A stop flag does not always block planning, but it must block automatic batch expansion and create human-review notes.

## Batch recommendation rule

Recommend same-family batch candidates only when request-contract evidence shows a shared method/path pattern, auth behavior, and parameter semantics. Do not batch across endpoint families even if the same SDK client, host, or auth layer is shared.
