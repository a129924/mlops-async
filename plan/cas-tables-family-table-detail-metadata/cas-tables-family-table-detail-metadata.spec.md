# CAS Tables Table Detail Metadata Specification

## Public Contract

`mlops_async.clients.cas_tables.value_objects.TableDetail` 維持 frozen/slotted
dataclass，保留既有 public fields 並新增以下 fields：

```text
name: str
caslib: str
state: TableState
created: str
last_modified: str
last_accessed: str | None
source_last_modified: str | None
```

既有三個 operation 的 public method signatures 與 request contract 不變：

- `list_tables(data_source_id: str, *, start: int = 0, limit: int = 20)`
- `get_table(data_source_id: str, table_name: str)`
- `change_table_state(server: str, caslib: str, table_name: str, state: str)`

## Response Mapping

| Wire key | Public field | Presence/type rule |
| --- | --- | --- |
| `name` | `name` | 既有 required non-empty string semantics 維持 |
| `caslib` | `caslib` | 只接受此 key；既有 required non-empty string semantics 維持 |
| `state` | `state` | 既有 `TableState` semantics 維持 |
| `created` | `created` | required；missing/null/non-string -> `CasTablesResponseError` |
| `lastModified` | `last_modified` | required；missing/null/non-string -> `CasTablesResponseError` |
| `lastAccessed` | `last_accessed` | missing/null -> `None`；non-null 必須為 string |
| `sourceLastModified` | `source_last_modified` | missing/null -> `None`；non-null 必須為 string |

所有日期 wire value 若為字串都原樣保留；不做 timestamp format、timezone、parse
或 normalization validation。Parser 只允許上述七個 wire keys；`caslibName`、
`createdBy`、`lastModifiedBy`、`label`、`rowCount`、`columnCount` 與任何未知 key
均為 extra field，必須 raise `CasTablesResponseError`。

## Request Unchanged Boundary

這個 follow-up 是 response contract drift，不是 request drift。以下 contract
必須與現有實作逐項相同：

1. list 仍是一個 `GET`，path、`start`/`limit` query、auth/Requester boundary
   與 one-request 行為不變。
2. get 仍是一個 `GET`，path、dynamic identifier encoding、auth/Requester
   boundary 與 one-request 行為不變。
3. state change 仍是一個 `PUT`，path、`value=<TableState.value>` query、empty
   JSON body、auth/Requester boundary 與 one-request 行為不變。
4. 不新增 pagination、retry、timeout、background task、session ownership 或
   shared requester/core/transport policy。

## Failure Semantics

- detail object 非 object、既有 `name/caslib/state` semantics 失敗、required
  date missing/null/non-string、optional date non-null wrong-type、unknown/extra
  key 或 `caslibName` 均為 `CasTablesResponseError`。
- Optional date missing 或 explicit JSON null 不是 error，而是 `None`。
- 任一合法日期字串不因內容不像 timestamp 而失敗，且回傳值與 wire string
  相同。
- transport exception 與 `asyncio.CancelledError` 維持既有原 instance propagation；
  parser 擴充不得 catch、translate、retry 或清理這些 caller-owned failures。

## Acceptance Criteria

1. 完整合法 detail response 能建立含七個 public fields 的 `TableDetail`，且
   四個日期欄位 mapping 正確。
2. `lastAccessed` 與 `sourceLastModified` 各自對 missing 與 explicit null
   產生 `None`。
3. `created` 與 `lastModified` 各自對 missing、null、非字串產生
   `CasTablesResponseError`；任意原始字串內容可保留。
4. optional 欄位若提供 non-null 非字串，產生 `CasTablesResponseError`。
5. exact allowlist 僅接受 `name`、`caslib`、`state`、`created`、`lastModified`、
   `lastAccessed`、`sourceLastModified`；`caslibName` 與其他未知欄位拒絕。
6. `TableDetail` 的 frozen/slotted 性質與既有 `name/caslib/state` public
   semantics 不變。
7. list/get/state 的 method/path/query/body/auth/Requester/one-request 行為、
   semantic error、transport failure 與 cancellation behavior 均無 request drift。
8. 變更僅落在 plan 列出的 source/test targets；不觸及 legacy package、其他
   endpoint、requester/core、analysis、README、VERSION 或 release surfaces。

## Test Cases

- **Happy path**：完整七欄 detail response 產生正確 `TableDetail`；list page
  中每個 item 都套用相同 parser。
- **Optional missing**：分別移除 `lastAccessed`、`sourceLastModified`，預期
  對應 public field 為 `None`。
- **Optional null**：分別令兩個 optional wire values 為 JSON null，預期為
  `None`。
- **Required missing/null/type**：對 `created` 與 `lastModified` 分別覆蓋
  missing、null、integer/object/array 等非字串，均預期 `CasTablesResponseError`。
- **Optional wrong type**：optional key 使用 non-null 非字串，預期
  `CasTablesResponseError`。
- **Raw string preservation**：使用空字串或不符合 timestamp format 的字串，
  仍以原字串回傳，不做 format validation。
- **Allowlist**：加入 `caslibName` 或任意未知 key，預期
  `CasTablesResponseError`；wire `caslib` 正常通過。
- **Immutability**：確認 `TableDetail` 仍為 dataclass、無 `__dict__` 且 frozen，
  新 fields 也包含在 dataclass fields 中。
- **Endpoint regression**：既有 client tests 的 list/get/state response payload
  補齊 required dates 後，method/path/query/body/auth/Requester/one-request
  assertions 維持通過。
- **Failure propagation**：既有 transport exception 與
  `asyncio.CancelledError` identity assertions 維持通過。

## Validation Commands

由後續 Creator 在 Windows-to-WSL project toolchain 執行：

```powershell
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 pytest --override-ini addopts="" tests/unit/clients/cas_tables/test_cas_tables_value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py -q'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 ruff check src/mlops_async/clients/cas_tables/value_objects.py tests/unit/clients/cas_tables/test_cas_tables_value_objects.py tests/unit/clients/cas_tables/test_cas_tables_client.py'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 pyright'
& "$env:USERPROFILE\.agents\skills\windows-wsl-dev\scripts\wsl-run.ps1" -Command 'uv run --no-sync --python 3.10.0 tach check'
git diff --check
```

本次 Plan-Creator 不執行上述會驗證未來 source/test implementation 的命令。
