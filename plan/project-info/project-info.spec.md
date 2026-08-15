# Project Info Specification

## Primary Behavior Contract

此檔案是 `project-info` 的 primary behavior contract，供 `python-tdd-test-authoring` 以其撰寫 RED tests。它只規範 `modelRepository/projects` 現有 list/detail response 的 semantic value objects；不改變 request 或 release contract。

### Audit metadata fields

`ProjectSummary` 與 `ProjectDetail` 都必須保留既有 `id`、`name`，並新增下列 frozen/slotted dataclass fields，型別與 default 完全相同：

| Python field | Type and default | Exact JSON key |
| --- | --- | --- |
| `created_by` | `str | None = None` | `createdBy` |
| `modified_by` | `str | None = None` | `modifiedBy` |
| `creation_timestamp` | `str | None = None` | `creationTimeStamp` |
| `modified_timestamp` | `str | None = None` | `modifiedTimeStamp` |

List item parsing 與 detail parsing 必須有完全相同的四欄 mapping、acceptance 與 error behavior（list/detail parity）。timestamps 為 raw strings：不得 parse、normalize、timezone convert、format validate 或轉為 `datetime`。

### Presence and type rule

每個 audit key 皆獨立依下列唯一規則處理：

- key 缺失時，對應 Python field 為 `None`。
- key 存在且值為 `str` 時，對應 field 保留完全相同的 raw string；空字串也是 `str`，不新增 non-empty restriction。
- key 存在且值為 JSON `null` 時，必須拋出 `ProjectsResponseError`。
- key 存在且值為任何 non-string JSON value（包括 number、boolean、array、object）時，必須拋出 `ProjectsResponseError`。

只有 missing key 可 materialize 為 `None`；不得將 present JSON `null` 靜默映射為 `None`、coerce 為 string，或省略 error。

### Existing response policy retained

- `id` 與 `name` 仍採既有 Projects policy：兩者都是 required non-empty strings；missing、empty 或非字串均透過既有 semantic boundary 為 `ProjectsResponseError`。
- 未被 modeled 的 response keys 維持排除，不得成為 dataclass attributes 或改變既有 unknown-field exclusion。
- `ProjectsResponseError` 的既有 role 與其他 client JSON/transport error propagation contract 均不變。
- Champion 的既有 optional/nullable fields 不屬於此 contract，且不得因 audit metadata rule 改變。

## Behavioral Scenarios

### Scenario 1: List item with complete audit metadata

- **Given**: projects list response 的一個 item 含 `id`、`name` 與四個 exact audit keys，所有 audit values 都是 strings。
- **When**: `parse_projects_page` materializes `ProjectSummary`。
- **Then**: summary 保留 `id`/`name` 與四個 raw string values；沒有額外 datetime 或 unknown-field attributes。

### Scenario 2: Detail response with absent audit metadata

- **Given**: project detail response 只含符合既有 policy 的 `id` 與 `name`，沒有任一 audit key。
- **When**: `parse_project_detail` materializes `ProjectDetail`。
- **Then**: 四個 audit fields 都是 `None`，而不是 error。

### Scenario 3: Present malformed metadata is rejected

- **Given**: list item 或 detail response 的任一 audit key present，且值是 JSON `null` 或 non-string JSON value。
- **When**: respective Projects parser runs。
- **Then**: it raises `ProjectsResponseError`; no partial semantic object is accepted.

### Scenario 4: Client-observable parity

- **Given**: `ProjectsClient.list_projects` 與 `ProjectsClient.get_project` 收到各自含四個 valid audit strings 的 decoded response。
- **When**: caller awaits either operation。
- **Then**: returned `ProjectSummary`/`ProjectDetail` 對應 fields 完全一致，且 list/get request path、method、params、signatures 不變。

## Error / Edge Cases

- 每一四 audit key 都需獨立測試 missing、string、JSON `null`、number、boolean、array、object；前兩種是唯一成功 case。
- 同一 response 可缺少任意子集合的 audit keys；缺少的 keys 各自為 `None`，存在的 valid strings 各自保留。
- Present audit value 的 error 不可因它位於 list item 或 detail response 而不同。
- Existing `id`/`name` malformed behavior、unknown-field exclusion、frozen/slotted shape 維持不變。

## Non-Behavior Changes

- 不變更 `ProjectsClient` constructor 或公開 method signatures、HTTP method/path/query/header/body、pagination/name lookup、request-contract gate 或 exports。
- 不變更 README、VERSION、OpenAPI、legacy evidence、release notes、version bump、tag、publish 或 cleanup。此 topic 無 release action。
- 只允許 future implementation change `src/mlops_async/clients/projects/value_objects.py`、`tests/unit/clients/projects/test_value_objects.py`、`tests/unit/clients/projects/test_client.py`。

## Test Matrix

- `tests/unit/clients/projects/test_value_objects.py`: `ProjectSummary`/`ProjectDetail` field names/defaults/frozen-slotted shape；list/detail exact mapping parity；每 key missing/string/null/non-string matrix；raw timestamps；existing id/name and unknown-field behavior。
- `tests/unit/clients/projects/test_client.py`: list/get decoded response observability of four valid fields、list/detail malformed metadata `ProjectsResponseError` propagation、existing request recording/path/params assertions unchanged。
- `tests/unit/request_contract/projects_request_gate/test_list_projects_request_contract.py` 與 `tests/unit/request_contract/projects_request_gate/test_get_project_request_contract.py`: read-only gates; no change is permitted.
