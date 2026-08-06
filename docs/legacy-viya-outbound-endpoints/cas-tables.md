# CAS tables handoff

## Legacy observation

- Legacy list 使用 `casManagement/dataSources/.../tables` 的 `limit` 與 `start=0`，
  並有 direct table GET；另有 table-state `PUT .../state?value={state}` mutation。

## Upstream/evidence

- list/get 的 raw upstream source 是 `dataTables-v3-openapi.yml`；table state 是
  `casManagement-openapi.yml`。兩者的 repo-local mapping 與 path normalization 見
  upstream README。
- 現有 list/get/state gates 全是 `custom-client-shape-only` /
  `non-authoritative-shape-only`。

## Current repo evidence

- `tests/unit/request_contract/casmanagement_tables_list_request_gate/`、
  `casmanagement_table_get_request_gate/` 與 `casmanagement_table_state_change_request_gate/`
  僅保存 request shape；沒有 production CAS tables client。

## Difference

- custom gateway path、data source identifier 與 raw upstream service-root path 尚未完成
  target compatibility decision；mutation 的安全與 state semantics 未證實。

## Disposition

- list/get 在證據升級前不實作；table state 是非 MVP mutation，read-only MVP 穩定前不排程。

## Human decision required

- 提供 upstream 或 human-confirmed list/get contract，並明確授權任何 mutation topic。

## Target mapping
