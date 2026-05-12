# API client porting implementer reference

## Gated implementation order

Use this order for every API:

1. Source discovery evidence
2. Request contract extraction
3. Request contract test first
4. Minimal implementation
5. Response contract extraction
6. Pydantic external schema definition
7. Response contract test
8. Error contract test
9. Porting ledger update
10. Stop / continue decision

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

For repeated query keys or encoded values, assert semantic equivalence rather than raw URL string ordering.

## Schema and compatibility policy

Default Pydantic external-boundary policy:

| Model type | Default `extra` policy |
| --- | --- |
| Request model | `extra="forbid"` |
| Response model | `extra="ignore"` or `extra="allow"` |
| Error response model | `extra="allow"` |
| Internal normalized model | may be strict |
| Public API return model | strict only after stable behavior is proven |

Allowed compatibility labels:

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

If target code converts raw SDK output into typed Pydantic schema, response compatibility is `normalized`, not `equivalent`.

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

- `continue`: implementation is safe but more APIs or validation remain
- `stable`: request, response, error, tests, and ledger are complete enough for handoff
- `needs-human-review`: implementation or batching needs a human decision before proceeding
- `blocked`: missing evidence or unsafe ambiguity prevents implementation
