# Porting Ledger

## Purpose

This ledger records evidence for APIs ported into `mlops-async` from `sasctl`, the legacy `sas-api` repository, or another source SDK. Every implemented API must leave enough source, request, response, error, compatibility, and validation evidence for a reviewer to understand what was preserved, normalized, intentionally changed, or blocked.

## Authoritative workflow

API porting work must start from:

1. `analysis/api-client-porting-contract/requirements.md`
2. `analysis/api-client-porting-contract/technical-spec.md`
3. `plan/api-client-porting-contract/api-client-porting-contract.plan.md`
4. `.github/skills/api-client-porting-planner/`
5. `.github/skills/api-client-porting-implementer/`

## Compatibility labels

Use only these labels:

- `equivalent`
- `normalized`
- `intentionally_changed`
- `not_supported`
- `unknown`

Do not mark a response as `equivalent` when `mlops-async` converts raw SDK output into a typed Pydantic schema. Use `normalized`.

## Decision labels

Use only these final decisions:

- `continue`
- `stable`
- `needs-human-review`
- `blocked`

## Entry template

Copy this template for each API or safe same-family batch.

```md
## <endpoint-family>: <source-function-or-api-name>

### Source

- Source SDK:
- Source module:
- Source function:
- Source file:
- Source line range:
- Source commit, tag, or package version:

### Request Contract

- HTTP method:
- Path:
- Required headers:
- Query params:
- Body:
- Auth behavior:
- Status: missing | drafted | tested | implemented | blocked

### Target

- Target module:
- Target class:
- Target method:
- Async: true | false

### Response Contract

- Success status codes:
- Schema model:
- Extra policy:
- Nullable fields:
- Optional fields:
- Aliases:
- Transformations:
- Pagination:
- Empty response behavior:
- Status: missing | drafted | tested | implemented | blocked

### Error Contract

- Error schema model:
- Extra policy:
- Error status handling:
- Status: missing | drafted | tested | implemented | blocked

### Compatibility

- Request: equivalent | normalized | intentionally_changed | not_supported | unknown
- Response: equivalent | normalized | intentionally_changed | not_supported | unknown
- Error: equivalent | normalized | intentionally_changed | not_supported | unknown
- Session: equivalent | normalized | intentionally_changed | not_supported | unknown

### Tests

- Request tests:
- Response tests:
- Error tests:
- Validation commands:
- Validation not run / why:

### Divergences and Review Notes

- Known divergences:
- Stop flags observed:
- Human-review notes:

### Decision

- Decision: continue | stable | needs-human-review | blocked
```

## Ledger entries

No APIs have been ported under this workflow yet.
