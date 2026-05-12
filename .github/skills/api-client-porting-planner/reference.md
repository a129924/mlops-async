# API client porting planner reference

## Required evidence

Every source API entry must be traceable before an implementer receives it:

- `sdk`: source package, SDK, or legacy client name
- `module`: import/module path or source package area
- `function`: function, method, or callable name
- `file`: repository-relative or absolute source file path
- `line_range`: line range covering the request behavior or wrapper call
- `commit`: commit SHA, tag, package version, or documented source snapshot

If any required field is missing, keep the API in the output but mark the affected contract fields `unknown` and add human-review notes. Block only when the missing evidence would make family boundaries, request contract, or risk classification misleading.

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

Capture semantic behavior, not transport noise. Do not require query parameter order, generated headers, host, content length, connection headers, or live service availability.

## Risk classification

Use `low` when the source function is a thin HTTP wrapper with clear method, path, auth, and payload behavior and no stop flags.

Use `medium` when the wrapper is mostly clear but has optional branches, light parameter normalization, partial fixture gaps, or one contained uncertainty that does not change the endpoint family.

Use `high` when source behavior includes a stop flag, unclear request construction, global session mutation, multi-step orchestration, or behavior that could materially alter implementation order or target API shape.

## Mandatory stop flags

Check every API for:

- upload/download
- streaming
- polling or job status wait
- retry behavior
- pagination expansion
- global session side effects
- conditional endpoint selection
- unclear source behavior
- non-wrapper complex behavior

A stop flag does not always block planning, but it must prevent automatic batch expansion and must create human-review notes.

## Batch recommendation rule

Recommend same-family batch candidates only when there is enough request-contract evidence to show a shared method/path pattern, auth behavior, and parameter semantics. Do not batch across endpoint families even if the same SDK client, host, or auth layer is shared.

For initial discovery, prefer ordering APIs so that two or more low-risk same-family wrappers can establish the request pattern before medium-risk variants are attempted.
