# API client porting implementer reference

## Gated implementation order

Use this order for every API:

1. source discovery evidence
2. request contract extraction
3. request contract test first
4. minimal implementation
5. response contract extraction
6. external-boundary schema definition
7. response contract test
8. error contract test
9. tracker update or tracker-ready handoff
10. stop / continue decision

Never start implementation from intuition, endpoint naming, or target architecture preference.

## Request test contract

Request tests must assert:

- HTTP method
- endpoint path
- required header subset
- query parameter key-value semantics
- request body shape

Request tests must not assert:

- query parameter order
- transport-generated headers
- content length
- host
- connection headers

## Schema and compatibility policy

Default external-boundary policy:

| Schema artifact type | Default `extra` policy |
| --- | --- |
| Request schema artifact | `extra="forbid"` |
| Response schema artifact | `extra="ignore"` or `extra="allow"` |
| Error schema artifact | `extra="allow"` |

Allowed compatibility labels:

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

If target code converts raw SDK output into a typed schema artifact, response compatibility is `normalized`, not `equivalent`.

## Stop conditions and final labels

Stop automated implementation and use `needs-human-review` or `blocked` for:

- upload/download
- streaming
- polling or job wait
- retry behavior
- pagination expansion
- global session side effects
- conditional endpoint selection
- unclear response schema
- unclear source behavior

Final decision labels are exactly:

- `continue`
- `stable`
- `needs-human-review`
- `blocked`

## Optional tracker rule

Repo-local tracker artifacts are optional examples, not unconditional prerequisites. If task scope excludes them, emit tracker-ready content in the implementation result instead of inventing a new path.
