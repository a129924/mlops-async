# request-gate-projects-tables-fixed-path-mvp - Behavior Spec

> Status: `SUPERSEDED`
>
> 本 spec 僅保留 fixed-path MVP 行為記錄，不再作為 current truth。
## Purpose

本 spec 定義 `modelRepository/projects -> tables-link surface / list_tables`
的 fixed-path MVP request-shape contract。

此 spec 明確屬於：

- `fixed-path MVP`
- `implementation-facing draft`
- `intentionally_changed`

它不是 upstream source-observed single truth。

---

## Canonical request

### Allowed case

| Case ID | Method | Path | Query | Body |
| --- | --- | --- | --- | --- |
| `direct_project_identifier` | `GET` | `/modelRepository/projects/{project_id}/tables` | `{}` | `null` |

### Required input

- `project_id`
  - required
  - non-empty string

### Request-shape focus

本 topic 只驗證：

- method
- path
- query absence
- body absence

本 topic 不驗證 response schema。

---

## Blocked variants

| Variant | Example | Expected result |
| --- | --- | --- |
| non-string `project_id` | `123` | fast-fail |
| empty string `project_id` | `""` | fast-fail |
| blank string `project_id` | `"   "` | fast-fail |
| extra query params | `?limit=10` | contract failure |
| request body present | `{}` | contract failure |

---

## Out-of-scope variants

- HATEOAS link parsing
- project fetch pre-step
- `links[].href` follow-up
- `casManagement/dataSources/tables`
- pagination / filter / search / sort / limit / offset
- response / error contract

---

## Fixture expectations

### Request-flow fixture

- file:
  `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.request-flow.json`
- cases:
  - `direct_project_identifier`

### Mock-response fixture

- file:
  `tests/unit/request_contract/projects_tables_link_request_gate/fixtures/list_tables.mock-responses.json`
- response body:
  - minimal JSON object only
  - no response-schema assertion in this topic

---

## Test expectations

### Positive

- `list_tables("project-id-abc-123")` emits:
  - method `GET`
  - path `/modelRepository/projects/project-id-abc-123/tables`
  - query `{}`
  - no body

### Negative

- non-string `project_id`
- empty `project_id`
- blank `project_id`

### Guard

- any query params cause failure
- any request body cause failure
- any path other than `/modelRepository/projects/{project_id}/tables` causes failure
- any attempt to introduce HATEOAS discovery is topic drift

---

## Divergence note

本 spec 明確偏離 upstream 的 HATEOAS endpoint discovery，改採 fixed-path：

- `/modelRepository/projects/{project_id}/tables`

此偏離是 deliberate MVP contract choice，標記為 `intentionally_changed`。
若未來要恢復 HATEOAS-faithful contract，必須另開新 topic，不能在本 spec 內擴充。
